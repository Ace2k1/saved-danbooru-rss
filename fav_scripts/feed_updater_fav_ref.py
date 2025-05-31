import xml.etree.ElementTree as ET
import requests
from datetime import datetime, timezone
from html import escape
import os

NS_ATOM = "http://www.w3.org/2005/Atom"
NS_XHTML = "http://www.w3.org/1999/xhtml"
ET.register_namespace('', NS_ATOM)

FEED_ID = "tag:danbooru.donmai.us,2025:/feed"
FEED_TITLE = "Ace's Danbooru Feed"
FEED_LINK = "https://danbooru.donmai.us"
def get_entry_post_id(entry, default_post_id=0):
    id_elem = entry.find(f"{{{NS_ATOM}}}id")
    if id_elem is None or id_elem.text is None:
        return default_post_id
    url = id_elem.text.strip()
    try:
        post_id_str = url.rstrip("/").split("/")[-1]
        return int(post_id_str)
    except (ValueError, IndexError):
        try:
            return int(url)
        except ValueError:
            return default_post_id
def load_feed(filepath):
    if not os.path.isfile(filepath):
        # Create minimal feed XML root
        feed = ET.Element(f"{{{NS_ATOM}}}feed")
        ET.SubElement(feed, "title").text = FEED_TITLE
        ET.SubElement(feed, "link", href=FEED_LINK)
        ET.SubElement(feed, "updated").text = datetime.utcnow().isoformat() + 'Z'
        ET.SubElement(feed, "id").text = FEED_ID
        return ET.ElementTree(feed)
    else:
        return ET.parse(filepath)

def get_post_id_from_url(url):
    return url.rstrip("/").split("/")[-1]

def entry_exists(root, post_id):
    for entry in root.findall(f"{{{NS_ATOM}}}entry"):
        id_elem = entry.find(f"{{{NS_ATOM}}}id")
        if id_elem is not None and id_elem.text.endswith(post_id):
            return True
    return False

def create_entry_element(post_id, url, data):
    md5 = data["md5"]
    ext = data["file_ext"]
    compiledMD5 = f"{md5[0:2]}/{md5[2:4]}/{md5}"
    thumb_url = f"https://cdn.donmai.us/360x360/{compiledMD5}.{ext}"
    # Validate thumb_url exists, else fallback to jpg
    try:
        resp = requests.head(thumb_url)
        if resp.status_code != 200 and ext != "jpg":
            thumb_url = f"https://cdn.donmai.us/360x360/{compiledMD5}.jpg"
    except:
        # On any error, keep thumb_url as is
        pass

    full_url = data.get("large_file_url") or data.get("file_url") or ""
    if full_url.startswith("/"):
        full_url = FEED_LINK + full_url

    source = data.get("source") or ""
    related_url = source if source.startswith("https://i.pximg.net") else full_url

    characters = data.get("tag_string_character", "").strip()
    artist = data.get("tag_string_artist", "").strip()
    characterExist = bool(characters.strip())
    prefixTitle = characters if characterExist else f"Post {post_id}"
    title = f"{prefixTitle} drawn by {artist}".strip()
    if characterExist:
        title += f" - ID {post_id}"

    created_at = data.get("created_at", "2025-01-01T00:00:00Z")
    # Format updated to preserve timezone if present
    # updated = created_at
    try:
        # Handle timezone-aware or naive datetime
        dt = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
        updated = dt.astimezone(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
    except Exception:
        updated = "2025-01-01T00:00:00Z"

    # Build entry element
    entry = ET.Element(f"{{{NS_ATOM}}}entry")

    title_el = ET.SubElement(entry, "title")
    title_el.text = escape(title)

    ET.SubElement(entry, "link", href=url, rel="alternate")
    ET.SubElement(entry, "link", href=related_url, rel="related")
    ET.SubElement(entry, "link", href=thumb_url, rel="preview")

    id_el = ET.SubElement(entry, "id")
    id_el.text = url

    updated_el = ET.SubElement(entry, "updated")
    updated_el.text = updated

    content_el = ET.SubElement(entry, "content", type="xhtml")
    div = ET.SubElement(content_el, "div", xmlns=NS_XHTML)
    a = ET.SubElement(div, "a", href=thumb_url)
    ET.SubElement(a, "img", src=thumb_url)
    ET.SubElement(div, "a", href=url).text = "Source"


    author_el = ET.SubElement(entry, "author")
    name_el = ET.SubElement(author_el, "name")
    name_el.text = "Ace2k1"

    return entry

def normalize_entries_content(root):
    for entry in root.findall(f"{{{NS_ATOM}}}entry"):
        content = entry.find(f"{{{NS_ATOM}}}content")
        if content is not None and content.get("type") == "xhtml":
            # Clear children
            for child in list(content):
                content.remove(child)

            # Rebuild content as clean div/a/img based on links inside entry
            div = ET.SubElement(content, "div", xmlns=NS_XHTML)

            # Get alternate link and preview link hrefs
            alternate_link = None
            preview_link = None
            for link in entry.findall(f"{{{NS_ATOM}}}link"):
                rel = link.get("rel")
                if rel == "alternate":
                    alternate_link = link.get("href")
                elif rel == "preview":
                    preview_link = link.get("href")

            if alternate_link and preview_link:
                a = ET.SubElement(div, "a", href=alternate_link)
                ET.SubElement(a, "img", src=preview_link)
            # else leave empty div if missing

def append_danbooru_entry(feed_path, post_url):
    tree = load_feed(feed_path)
    root = tree.getroot()

    post_id_from_url = get_post_id_from_url(post_url)

    if entry_exists(root, post_id_from_url):
        print(f"Entry for post {post_id_from_url} already exists, skipping append.")
        return

    api_url = f"https://danbooru.donmai.us/posts/{post_id_from_url}.json"
    try:
        resp = requests.get(api_url)
        resp.raise_for_status()
        data = resp.json()
    except Exception as e:
        print(f"Error fetching data for post {post_id_from_url}: {e}")
        return

    new_entry = create_entry_element(post_id_from_url, post_url, data)

    # # Assert the ID inside new_entry matches post_id_from_url
    # post_id_from_entry = str(get_entry_post_id(new_entry))
    # assert post_id_from_entry == post_id_from_url, f"Post ID mismatch: entry {post_id_from_entry} vs url {post_id_from_url}"

    root.append(new_entry)

    # Sort entries by post ID descending (integer)
    entries = list(root.findall(f"{{{NS_ATOM}}}entry"))

    def sort_key(e):
        # For the newly appended entry, fallback to post_id_from_url
        if e is new_entry:
            return get_entry_post_id(e, default_post_id=int(post_id_from_url))
        else:
            return get_entry_post_id(e, default_post_id=0)
    entries_sorted = sorted(entries, key=sort_key, reverse=True)

    # Clear old entries and re-append in order
    for e in root.findall(f"{{{NS_ATOM}}}entry"):
        root.remove(e)
    for e in entries_sorted:
        root.append(e)

    # Update feed updated timestamp to now UTC
    updated_el = root.find(f"{{{NS_ATOM}}}updated")
    if updated_el is not None:
        updated_el.text = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
        # updated_el.text = datetime.utcnow().isoformat() + "Z"

    # Normalize all entries' content for consistent format
    normalize_entries_content(root)

    tree.write(feed_path, encoding="utf-8", xml_declaration=True)
    print(f"Appended post {post_id_from_url} and saved feed to {feed_path}")



# Example usage:
# if __name__ == "__main__":
#     feed_file = "danbooru_ref_fav.xml"
#     post_url_to_add = "https://danbooru.donmai.us/posts/5666182"
#     append_danbooru_entry(feed_file, post_url_to_add)
#################################################################################
def append_multiple_entries(feed_file, post_urls):
    for url in post_urls:
        append_danbooru_entry(feed_file, url)

if __name__ == "__main__":
    feed_file = "danbooru_ref_fav.xml"

    # You can replace this with reading from a .txt file or another source
    post_urls = []
    append_multiple_entries(feed_file, post_urls)