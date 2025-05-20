import requests
from datetime import datetime, timezone
from html import escape
urls = list([
    "https://danbooru.donmai.us/posts/9315003",
    "https://danbooru.donmai.us/posts/9309263",
    "https://danbooru.donmai.us/posts/9281207",
    "https://danbooru.donmai.us/posts/9259171",
    "https://danbooru.donmai.us/posts/9255073",
    "https://danbooru.donmai.us/posts/9249317",
    "https://danbooru.donmai.us/posts/9223184",
    "https://danbooru.donmai.us/posts/9183678",
    "https://danbooru.donmai.us/posts/9183661",
    "https://danbooru.donmai.us/posts/9182468",
    "https://danbooru.donmai.us/posts/9179953",
    "https://danbooru.donmai.us/posts/9169844",
    "https://danbooru.donmai.us/posts/9146168",
    "https://danbooru.donmai.us/posts/9139250",
    "https://danbooru.donmai.us/posts/9095537",
    "https://danbooru.donmai.us/posts/9078272",
    "https://danbooru.donmai.us/posts/9058666",
    "https://danbooru.donmai.us/posts/9005362",
    "https://danbooru.donmai.us/posts/8974672",
    "https://danbooru.donmai.us/posts/8895250",
    "https://danbooru.donmai.us/posts/8862059",
    "https://danbooru.donmai.us/posts/8841982",
    "https://danbooru.donmai.us/posts/8810032",
    "https://danbooru.donmai.us/posts/8733499",
    "https://danbooru.donmai.us/posts/8695013",
    "https://danbooru.donmai.us/posts/8647146",
    "https://danbooru.donmai.us/posts/8614576",
    "https://danbooru.donmai.us/posts/8566867",
    "https://danbooru.donmai.us/posts/8507085",
    "https://danbooru.donmai.us/posts/8503532",
    "https://danbooru.donmai.us/posts/8501737",
    "https://danbooru.donmai.us/posts/8500372",
    "https://danbooru.donmai.us/posts/8477800",
    "https://danbooru.donmai.us/posts/8471801",
    "https://danbooru.donmai.us/posts/8320180",
    "https://danbooru.donmai.us/posts/8225477",
    "https://danbooru.donmai.us/posts/8114443",
    "https://danbooru.donmai.us/posts/8044616",
    "https://danbooru.donmai.us/posts/8017980",
    "https://danbooru.donmai.us/posts/8003928",
    "https://danbooru.donmai.us/posts/7982459",
    "https://danbooru.donmai.us/posts/7966454",
    "https://danbooru.donmai.us/posts/7945409",
    "https://danbooru.donmai.us/posts/7930867",
    "https://danbooru.donmai.us/posts/7899191",
    "https://danbooru.donmai.us/posts/7865853",
    "https://danbooru.donmai.us/posts/7682905",
    "https://danbooru.donmai.us/posts/7670183",
    "https://danbooru.donmai.us/posts/7610336",
    "https://danbooru.donmai.us/posts/7553328",
    "https://danbooru.donmai.us/posts/7370071",
    "https://danbooru.donmai.us/posts/7370022",
    "https://danbooru.donmai.us/posts/7290005",
    "https://danbooru.donmai.us/posts/7161239",
    "https://danbooru.donmai.us/posts/7157242",
    "https://danbooru.donmai.us/posts/7134112",
    "https://danbooru.donmai.us/posts/7129231",
    "https://danbooru.donmai.us/posts/7110185",
    "https://danbooru.donmai.us/posts/6993529",
    "https://danbooru.donmai.us/posts/6986700",
    "https://danbooru.donmai.us/posts/6945945",
    "https://danbooru.donmai.us/posts/6880331",
    "https://danbooru.donmai.us/posts/6787393",
    "https://danbooru.donmai.us/posts/6746224",
    "https://danbooru.donmai.us/posts/6741019",
    "https://danbooru.donmai.us/posts/6695180",
    "https://danbooru.donmai.us/posts/6611132",
    "https://danbooru.donmai.us/posts/6566350",
    "https://danbooru.donmai.us/posts/6557284",
    "https://danbooru.donmai.us/posts/6314939",
    "https://danbooru.donmai.us/posts/6307201",
    "https://danbooru.donmai.us/posts/6021128",
    "https://danbooru.donmai.us/posts/5984560",
    "https://danbooru.donmai.us/posts/5950799",
    "https://danbooru.donmai.us/posts/5869785",
    "https://danbooru.donmai.us/posts/5834380",
    "https://danbooru.donmai.us/posts/5786630",
    "https://danbooru.donmai.us/posts/5786575",
    "https://danbooru.donmai.us/posts/5748467",
    "https://danbooru.donmai.us/posts/5698872",
    "https://danbooru.donmai.us/posts/5609393",
    "https://danbooru.donmai.us/posts/5533131",
    "https://danbooru.donmai.us/posts/5371927",
    "https://danbooru.donmai.us/posts/5350149",
    "https://danbooru.donmai.us/posts/5312834",
    "https://danbooru.donmai.us/posts/5261001",
    "https://danbooru.donmai.us/posts/5251873",
    "https://danbooru.donmai.us/posts/5158945",
    "https://danbooru.donmai.us/posts/5089699",
    "https://danbooru.donmai.us/posts/5048288",
    "https://danbooru.donmai.us/posts/4681891",
    "https://danbooru.donmai.us/posts/4133712",
    "https://danbooru.donmai.us/posts/3346440",
    "https://danbooru.donmai.us/posts/3314284",
])

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
        thumb_url = f"https://cdn.donmai.us/{md5[0:2]}/{md5[2:4]}/{md5}.{ext}"
        thumb_response = requests.head(thumb_url)
        if thumb_response.status_code != 200 and ext != "jpg":
            # Try fallback to jpg
            thumb_ext = "jpg"
            thumb_url = f"https://cdn.donmai.us/{md5[0:2]}/{md5[2:4]}/{md5}.{thumb_ext}"
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

with open("danbooru_ref_fav_fullres.xml", "w", encoding="utf-8") as f:
    f.write(feed)

print("RSS feed written to danbooru_ref_fav_fullres.xml")
