import requests
from datetime import datetime, timezone
from html import escape
urls = list(reversed([
    "https://danbooru.donmai.us/posts/6993529",
    "https://danbooru.donmai.us/posts/8114443",
    "https://danbooru.donmai.us/posts/6021128",
    "https://danbooru.donmai.us/posts/5786630",
    "https://danbooru.donmai.us/posts/8566867",
    "https://danbooru.donmai.us/posts/8225477",
    "https://danbooru.donmai.us/posts/8895250",
    "https://danbooru.donmai.us/posts/8320180",
]))


feed = '''<?xml version="1.0" encoding="utf-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">
  <title>Ace's Danbooru Feed Reference</title>
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
        thumb_url = f"https://cdn.donmai.us/360x360/{md5[0:2]}/{md5[2:4]}/{md5}.{ext}"
        thumb_response = requests.head(thumb_url)
        if thumb_response.status_code != 200 and ext != "jpg":
            # Try fallback to jpg
            thumb_ext = "jpg"
            thumb_url = f"https://cdn.donmai.us/360x360/{md5[0:2]}/{md5[2:4]}/{md5}.{thumb_ext}"
        # Full image
        full_url = data.get("large_file_url") or data.get("file_url")
        if full_url and full_url.startswith("/"):
            full_url = "https://danbooru.donmai.us" + full_url

        related_url = data.get("source") if data.get("source", "").startswith("https://i.pximg.net") else full_url

        characters = data.get("tag_string_character", "")
        artist = data.get("tag_string_artist", "")
        title = f"{characters} drawn by {artist}".strip() or f"Post {post_id}"

        created_at = data.get("created_at", "2025-01-01T00:00:00Z")
        created_dt = datetime.fromisoformat(created_at.rstrip("Z")).replace(tzinfo=timezone.utc)
        # updated = datetime.fromisoformat(created_at.rstrip("Z")).isoformat() + 'Z'
        updated = created_dt.isoformat().replace('+00:00', 'Z')
        print(f'Creating post of {post_id}')
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
        <a href="{url}">
            <img src="{thumb_url}" />
        </a>
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

with open("danbooru_ref_fav.xml", "w", encoding="utf-8") as f:
    f.write(feed)

print("RSS feed written to danbooru_ref_fav.xml")
