import requests
from datetime import datetime, timezone
from html import escape
urls = list(
  [
    "https://danbooru.donmai.us/posts/9709944",
    "https://danbooru.donmai.us/posts/9693414",
    "https://danbooru.donmai.us/posts/9531976",
    "https://danbooru.donmai.us/posts/9283962",
    "https://danbooru.donmai.us/posts/9264134",
    "https://danbooru.donmai.us/posts/8990014",
    "https://danbooru.donmai.us/posts/8810587",
    "https://danbooru.donmai.us/posts/8789440",
    "https://danbooru.donmai.us/posts/8615298",
    "https://danbooru.donmai.us/posts/8615229",
    "https://danbooru.donmai.us/posts/7976258",
    "https://danbooru.donmai.us/posts/6956999",
    "https://danbooru.donmai.us/posts/6642033",
    "https://danbooru.donmai.us/posts/6010737",
    "https://danbooru.donmai.us/posts/5971170",
    "https://danbooru.donmai.us/posts/5961313",
    "https://danbooru.donmai.us/posts/5680998",
    "https://danbooru.donmai.us/posts/5620823",
    "https://danbooru.donmai.us/posts/5468926",
    "https://danbooru.donmai.us/posts/4673987",
    "https://danbooru.donmai.us/posts/4571092",
    "https://danbooru.donmai.us/posts/4123098",
    "https://danbooru.donmai.us/posts/4019700",
    "https://danbooru.donmai.us/posts/3931046",
    "https://danbooru.donmai.us/posts/3876765",
    "https://danbooru.donmai.us/posts/3676571",
    "https://danbooru.donmai.us/posts/2966214"
  ]
)
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
    subpath = f"{md5[0:2]}/{md5[2:4]}/{md5}"
    thumb_url = f"{cdnString}/360x360/{subpath}.jpg"
    full_url = f"{cdnString}/{subpath}.{ext}"
    thumb_response = requests.head(thumb_url)
    if thumb_response.status_code != 200 and ext != "jpg":
      thumb_ext = "jpg"
      thumb_url = f"{cdnString}/360x360/{compiledMD5}.{thumb_ext}"
    result.append((thumb_url, full_url))
  return result

indent_spaces = 8
indent = ' ' * indent_spaces
feed = '''<?xml version="1.0" encoding="utf-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">
  <title>Ace's Danbooru Official Feed Reference</title>
  <link href="https://danbooru.donmai.us"/>
  <updated>{}</updated>
  <id>tag:danbooru.donmai.us,2025:/feed</id>
'''.format(datetime.utcnow().replace(tzinfo=timezone.utc).isoformat().replace('+00:00', 'Z'))

for url in urls:
    post_id = url.split("/")[-1]
    api_url = f"https://danbooru.donmai.us/posts/{post_id}.json"

    try:
        r = requests.get(api_url)
        r.raise_for_status()
        data = r.json()
        md5 = data["md5"]
        ext = data["file_ext"]
        compiledMD5 = f"{md5[0:2]}/{md5[2:4]}/{md5}"
        cdnString = "https://cdn.donmai.us"
        thumb_url = f"{cdnString}/360x360/{compiledMD5}.{ext}"
        thumb_response = requests.head(thumb_url)
        if thumb_response.status_code != 200 and ext != "jpg":
          # Try fallback to jpg
          thumb_ext = "jpg"
          thumb_url = f"{cdnString}/360x360/{compiledMD5}.{thumb_ext}"
        img_url = f"{cdnString}/{compiledMD5}.{ext}"
        # Full image
        full_url = data.get("large_file_url") or data.get("file_url")
        if full_url and full_url.startswith("/"):
          full_url = "https://danbooru.donmai.us" + full_url

        related_url = data.get("source") if data.get("source", "").startswith("https://i.pximg.net") else full_url

        characters = data.get("tag_string_character", "")
        artist = data.get("tag_string_artist", "")
        characterExist = bool(characters.strip())
        prefixTitle = characters if characterExist else f"Post {post_id}"
        title = f"{prefixTitle} drawn by {artist}".strip()
        if characterExist:
          title += f" - ID {post_id}"
        created_at = data.get("created_at", "2025-01-01T00:00:00Z")
        created_dt = datetime.fromisoformat(created_at.rstrip("Z")).replace(tzinfo=timezone.utc)
        # updated = datetime.fromisoformat(created_at.rstrip("Z")).isoformat() + 'Z'
        updated = created_dt.isoformat().replace('+00:00', 'Z')
        print(f'Creating post of {post_id}')

        extra_image = ''
        custom_images = get_custom_image_urls(url)
        if custom_images:
            indent2 = ' ' * (indent_spaces + 2)
            image_tags = [
              f'{indent}<a href="{full}">\n{indent2}<img src="{thumb}"/>\n{indent}</a>'
              for thumb, full in custom_images
            ]
            extra_image = '\n' + '\n'.join(image_tags)
        feed += f'''
  <entry>
    <title>{escape(title)}</title>
    <link href="{url}" rel="alternate"/>
    <link href="{related_url}" rel="related"/>
    <link href="{thumb_url}" rel="preview"/>
    <id>{url}</id>
    <updated>{updated}</updated>
    <content type="xhtml">
      <div xmlns="http://www.w3.org/1999/xhtml">
        <a href="{img_url}">
          <img src="{thumb_url}"/>
        </a>{extra_image}
      </div>
    </content>
    <author>
      <name>Ace2k1</name>
    </author>
  </entry>
'''
    except Exception as e:
        print(f"Error on post {post_id}: {e}")
feed += "</feed>"
with open("danbooru_ref_official.xml", "w", encoding="utf-8") as f:
  f.write(feed)
print("RSS feed written to danbooru_ref_official.xml")