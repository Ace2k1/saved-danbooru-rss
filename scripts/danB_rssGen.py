import requests
from datetime import datetime
from email.utils import format_datetime
from html import escape
urls = list(reversed([
    "https://danbooru.donmai.us/posts/4159319",
    "https://danbooru.donmai.us/posts/4221211",
    "https://danbooru.donmai.us/posts/4497641",
    "https://danbooru.donmai.us/posts/5165670",
    "https://danbooru.donmai.us/posts/5489217",
    "https://danbooru.donmai.us/posts/5489218",
    "https://danbooru.donmai.us/posts/6196127",
    "https://danbooru.donmai.us/posts/6196143",
    "https://danbooru.donmai.us/posts/6196171",
    "https://danbooru.donmai.us/posts/6196277",
    "https://danbooru.donmai.us/posts/6545834",
    "https://danbooru.donmai.us/posts/6880331",
    "https://danbooru.donmai.us/posts/7129231",
    "https://danbooru.donmai.us/posts/7134112",
    "https://danbooru.donmai.us/posts/7307173",
    "https://danbooru.donmai.us/posts/7317742",
    "https://danbooru.donmai.us/posts/7553328",
    "https://danbooru.donmai.us/posts/7618118",
    "https://danbooru.donmai.us/posts/7747356",
    "https://danbooru.donmai.us/posts/7868140",
    "https://danbooru.donmai.us/posts/7945409",
    "https://danbooru.donmai.us/posts/8044616",
    "https://danbooru.donmai.us/posts/8114443",
    "https://danbooru.donmai.us/posts/8225477",
    "https://danbooru.donmai.us/posts/8365912",
    "https://danbooru.donmai.us/posts/8507085",
    "https://danbooru.donmai.us/posts/8541491",
    "https://danbooru.donmai.us/posts/8566867",
    "https://danbooru.donmai.us/posts/8647146",
    "https://danbooru.donmai.us/posts/8750614",
    "https://danbooru.donmai.us/posts/8838343",
    "https://danbooru.donmai.us/posts/9052339",
    "https://danbooru.donmai.us/posts/9058666",
    "https://danbooru.donmai.us/posts/9095537",
    "https://danbooru.donmai.us/posts/9139251",
    "https://danbooru.donmai.us/posts/9146168",
    "https://danbooru.donmai.us/posts/9169844",
    "https://danbooru.donmai.us/posts/9183678",
    "https://danbooru.donmai.us/posts/9183749",
    "https://danbooru.donmai.us/posts/9223184",
    "https://danbooru.donmai.us/posts/9281207",
    "https://danbooru.donmai.us/posts/9304597",
    "https://danbooru.donmai.us/posts/9309263"
]))


feed = '''<?xml version="1.0" encoding="utf-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">
  <title>Ace's Danbooru Feed</title>
  <link href="https://danbooru.donmai.us"/>
  <updated>{}</updated>
  <id>tag:danbooru.donmai.us,2025:/feed</id>
'''.format(datetime.utcnow().isoformat() + 'Z')

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
        updated = datetime.fromisoformat(created_at.rstrip("Z")).isoformat() + 'Z'
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

with open("danbooru_fav.xml", "w", encoding="utf-8") as f:
    f.write(feed)

print("RSS feed written to danbooru_feed.xml")
