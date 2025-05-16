import requests
from datetime import datetime
from html import escape
import xml.etree.ElementTree as ET
import sys
import re
# how to update :
# python update_danbooru_feed.py https://danbooru.donmai.us/posts/9309999 https://danbooru.donmai.us/posts/9310000
ATOM_NS = "http://www.w3.org/2005/Atom"
ET.register_namespace("", ATOM_NS)  # Required for pretty output with default namespace

def extract_post_id(url):
    match = re.search(r"/posts/(\d+)", url)
    return match.group(1) if match else None

def generate_entry(post_id: str) -> ET.Element:
    api_url = f"https://danbooru.donmai.us/posts/{post_id}.json"
    r = requests.get(api_url)
    r.raise_for_status()
    data = r.json()

    md5 = data["md5"]
    ext = data["file_ext"]
    thumb_url = f"https://cdn.donmai.us/360x360/{md5[0:2]}/{md5[2:4]}/{md5}.{ext}"
    if requests.head(thumb_url).status_code != 200 and ext != "jpg":
        thumb_url = f"https://cdn.donmai.us/360x360/{md5[0:2]}/{md5[2:4]}/{md5}.jpg"

    full_url = data.get("large_file_url") or data.get("file_url")
    if full_url and full_url.startswith("/"):
        full_url = "https://danbooru.donmai.us" + full_url

    related_url = data.get("source") if data.get("source", "").startswith("https://i.pximg.net") else full_url
    characters = data.get("tag_string_character", "")
    artist = data.get("tag_string_artist", "")
    title = f"{characters} drawn by {artist}".strip() or f"Post {post_id}"
    created_at = data.get("created_at", "2025-01-01T00:00:00Z")

    entry = ET.Element("entry")
    ET.SubElement(entry, "title").text = escape(title)
    ET.SubElement(entry, "link", {"href": f"https://danbooru.donmai.us/posts/{post_id}", "rel": "alternate"})
    ET.SubElement(entry, "link", {"href": related_url, "rel": "related"})
    ET.SubElement(entry, "link", {"href": thumb_url, "rel": "preview"})
    ET.SubElement(entry, "id").text = f"https://danbooru.donmai.us/posts/{post_id}"
    ET.SubElement(entry, "updated").text = datetime.fromisoformat(created_at.rstrip("Z")).isoformat() + "Z"

    content = ET.SubElement(entry, "content", {"type": "xhtml"})
    div = ET.SubElement(content, "div", {"xmlns": "http://www.w3.org/1999/xhtml"})
    a = ET.SubElement(div, "a", {"href": f"https://danbooru.donmai.us/posts/{post_id}"})
    ET.SubElement(a, "img", {"src": thumb_url})

    author = ET.SubElement(entry, "author")
    ET.SubElement(author, "name").text = "Ace2k1"

    return entry

def update_feed(file_path, post_ids):
    try:
        tree = ET.parse(file_path)
        root = tree.getroot()
        ns = {'atom': ATOM_NS}

        for post_id in post_ids:
            print(f"Adding post {post_id}...")
            entry = generate_entry(post_id)
            root.append(entry)

        updated_elem = root.find("atom:updated", ns)
        if updated_elem is not None:
            updated_elem.text = datetime.utcnow().isoformat() + 'Z'

        tree.write(file_path, encoding="utf-8", xml_declaration=True)
        print(f"\n✅ Feed updated with {len(post_ids)} new post(s).")
    except Exception as e:
        print(f"❌ Error updating feed: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python update_danbooru_feed.py <danbooru_post_url_1> [<danbooru_post_url_2> ...]")
        sys.exit(1)

    post_ids = [extract_post_id(url) for url in sys.argv[1:]]
    post_ids = [pid for pid in post_ids if pid]

    if not post_ids:
        print("❌ No valid post IDs found.")
        sys.exit(1)

    update_feed("danbooru_fav.xml", post_ids)
