import xml.etree.ElementTree as ET
import requests
from datetime import datetime, timezone
from html import escape
import os

NS_ATOM = "http://www.w3.org/2005/Atom"
NS_XHTML = "http://www.w3.org/1999/xhtml"
ET.register_namespace('', NS_ATOM)
# ET.register_namespace('xhtml', NS_XHTML)
FEED_ID = "tag:danbooru.donmai.us,2025:/feed"
FEED_TITLE = "Ace's Danbooru Feed"
FEED_LINK = "https://danbooru.donmai.us"

image_info = {
  "https://danbooru.donmai.us/posts/9416965":[("9498ac2f52b24df4b52260a1e9bc6ec1","png"),("d91087f546ea4d402a3ec49f47e41f64","jpg")],
  "https://danbooru.donmai.us/posts/9402123":[("c77c28c2731d77637573604c2344048d","jpg"),("d5f004a6e39b6f54fa1660a7432890f0","png")],
  "https://danbooru.donmai.us/posts/9386232": ("7fc35a56d0cca8b957616fad43e9afa6","jpg"),
  "https://danbooru.donmai.us/posts/9343884": ("5d48620689d4dc5a40ef5ab44a5c6ea2", "jpg"),
  "https://danbooru.donmai.us/posts/4624471": ("44de7554b8287cad2630646996125b95", "jpg"),
}
def get_custom_image_urls(post_url):
  """
  Return custom (thumb_url, full_url) tuples for a given post.
  Supports both single (md5, ext) and multiple [(md5, ext), ...] entries.
  """
  entry = image_info.get(post_url)
  if not entry:
    return []
  image_entries = entry if isinstance(entry, list) else [entry]
  result = []
  cdnString = "https://cdn.donmai.us"
  for md5, ext in image_entries:
    compiledMD5 = f"{md5[0:2]}/{md5[2:4]}/{md5}"
    thumb_url = f"{cdnString}/360x360/{compiledMD5}.{ext}"
    full_url = f"{cdnString}/{compiledMD5}.{ext}"
    thumb_response = requests.head(thumb_url)
    if thumb_response.status_code != 200 and ext != "jpg":
        thumb_ext = "jpg"
        thumb_url = f"{cdnString}/360x360/{compiledMD5}.{thumb_ext}"
    result.append((thumb_url, full_url))
  return result

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
        feed = ET.Element(f"{{{NS_ATOM}}}feed")
        ET.SubElement(feed, f"{{{NS_ATOM}}}title").text = FEED_TITLE
        ET.SubElement(feed, f"{{{NS_ATOM}}}link", href=FEED_LINK)
        # ET.SubElement(feed, "updated").text = datetime.utcnow().isoformat() + 'Z'
        ET.SubElement(feed, f"{{{NS_ATOM}}}updated").text = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
        ET.SubElement(feed, f"{{{NS_ATOM}}}id").text = FEED_ID
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
def indent_element(elem, level=0, indent_per_level=2, base_indent=10):
    """Recursively indent an ElementTree element for pretty-printing."""
    i = '\n' + ' ' * (base_indent + indent_per_level * level)
    j = '\n' + ' ' * (base_indent + indent_per_level * (level + 1))

    # Skip indenting <content> inner XHTML
    if elem.tag.endswith('content'):
        if len(elem):  # has children
            for e in elem:
                indent_element(e, level + 1, indent_per_level, base_indent)
            elem.text = j
            elem[-1].tail = i
        elem.tail = '\n' + ' ' * (base_indent + indent_per_level * level)
        return

    if len(elem):
        if elem.text is None or not elem.text.strip():
            elem.text = j
        for e in elem:
            indent_element(e, level + 1, indent_per_level, base_indent)
        elem[-1].tail = i
    else:
        # Don't overwrite text content of leaf nodes
        if elem.text is not None:
            elem.text = elem.text.strip()
    elem.tail = i

def create_entry_element(post_id, url, data):
    md5 = data["md5"]
    ext = data["file_ext"]
    compiledMD5 = f"{md5[0:2]}/{md5[2:4]}/{md5}"
    thumb_url = f"https://cdn.donmai.us/360x360/{compiledMD5}.{ext}"
    img_url = f"https://cdn.donmai.us/{compiledMD5}.{ext}"

    try:
        resp = requests.head(thumb_url)
        if resp.status_code != 200 and ext != "jpg":
            thumb_url = f"https://cdn.donmai.us/360x360/{compiledMD5}.jpg"
    except:
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
    try:
        created_dt = datetime.fromisoformat(created_at.rstrip("Z")).replace(tzinfo=timezone.utc)
        updated = created_dt.isoformat().replace('+00:00', 'Z')
    except Exception:
        updated = "2025-01-01T00:00:00Z"

    # Build the new entry
    entry = ET.Element(f"{{{NS_ATOM}}}entry")
    ET.SubElement(entry, "title").text = escape(title)
    ET.SubElement(entry, "link", href=url, rel="alternate")
    ET.SubElement(entry, "link", href=related_url, rel="related")
    ET.SubElement(entry, "link", href=thumb_url, rel="preview")
    ET.SubElement(entry, "id").text = url
    ET.SubElement(entry, "updated").text = updated

    content_el = ET.SubElement(entry, "content", type="xhtml")
    div = ET.SubElement(content_el, "div")
    div.set("xmlns", NS_XHTML)
    a = ET.SubElement(div, "a", href=img_url)
    ET.SubElement(a, "img", src=thumb_url)
    custom_images = get_custom_image_urls(url)
    if custom_images:
        for custom_thumb, custom_full in custom_images:
            if custom_thumb and custom_full:
                a_tag = ET.SubElement(div, "a", href=custom_full)
                ET.SubElement(a_tag, "img", src=custom_thumb)

    author_el = ET.SubElement(entry, "author")
    ET.SubElement(author_el, "name").text = "Ace2k1"
    return entry

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
    indent_element(new_entry, level=0, indent_per_level=2, base_indent=10)
    new_entry.tail = '\n\n' + ' ' * 10
    root.append(new_entry)
    entries = list(root.findall(f"{{{NS_ATOM}}}entry"))
    def sort_key(e):
        return get_entry_post_id(e, default_post_id=int(post_id_from_url) if e is new_entry else 0)
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
    indent_element(root, level=0, indent_per_level=2, base_indent=0)
    xhtml_prefix = f"{{{NS_XHTML}}}"
    for elem in root.iter():
        if elem.tag.startswith(xhtml_prefix):
            elem.tag = elem.tag.replace(xhtml_prefix, '')
    # 3. Fix missing xmlns on <div> inside <content type="xhtml">
    for content_el in root.findall(".//{http://www.w3.org/2005/Atom}content"):
        if content_el.attrib.get("type") == "xhtml":
            div = content_el.find("div")
            if div is not None:
                div.set("xmlns", NS_XHTML)
    tree.write(feed_path, encoding="utf-8", xml_declaration=True, short_empty_elements=True)
    print(f"Appended post {post_id_from_url} and saved feed to {feed_path}")

#################################################################################
def append_multiple_entries(feed_file, post_urls):
    for url in post_urls:
        append_danbooru_entry(feed_file, url)

if __name__ == "__main__":
    feed_file = "danbooru_ref_fav.xml"
    post_urls = ["https://danbooru.donmai.us/posts/9402123", "https://danbooru.donmai.us/posts/9416965"]
    append_multiple_entries(feed_file, post_urls)