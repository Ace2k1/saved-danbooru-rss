import requests
from datetime import datetime, timezone
from html import escape
urls = list(
  ['https://danbooru.donmai.us/posts/2734994']
)
image_info = {
  "https://danbooru.donmai.us/posts/2734994":[("1fd53ea812fdcc40a9cbe9c1c1c6b5d0","jpg"), ("969ebe5a042caa6d5a0a3f7512a766e0","jpg"), ("a0ed6a9d4ba0ffd321eb05f786afc841","jpg"), ("7299e17a82dead32176e632ee2022f14","jpg")],
  "https://danbooru.donmai.us/posts/588747" : ('https://raw.githubusercontent.com/Ace2k1/saved-danbooru-rss/main/images/ouji_misao.png','link')
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
    if ext =='link':
      result.append((md5, md5))
    else:
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
with open("danbooru_ref_vn.xml", "w", encoding="utf-8") as f:
  f.write(feed)
print("RSS feed written to danbooru_ref_vn.xml")