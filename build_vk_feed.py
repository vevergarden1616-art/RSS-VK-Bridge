# build_vk_feed.py
import os, sys, time, html, re
from datetime import datetime, timezone
import requests
from feedgen.feed import FeedGenerator

API_URL = "https://api.vk.com/method/wall.get"
API_VERSION = os.environ.get("VK_API_VERSION", "5.199")

VK_TOKEN    = os.environ.get("VK_TOKEN", "").strip()
VK_DOMAIN   = os.environ.get("VK_DOMAIN", "").strip()
VK_OWNER_ID = os.environ.get("VK_OWNER_ID", "").strip()
COUNT       = int(os.environ.get("VK_COUNT", "50"))
FILTER      = os.environ.get("VK_FILTER", "all")

if not VK_TOKEN:
    print("ERROR: Brak VK_TOKEN (GitHub Secret).")
    sys.exit(1)

if not VK_DOMAIN and not VK_OWNER_ID:
    print("ERROR: Ustaw VK_DOMAIN albo VK_OWNER_ID.")
    sys.exit(1)

params = {
    "access_token": VK_TOKEN,
    "v": API_VERSION,
    "count": min(max(COUNT, 1), 100),
    "filter": FILTER,
    "extended": 1
}
if VK_DOMAIN:
    params["domain"] = VK_DOMAIN
else:
    params["owner_id"] = VK_OWNER_ID

resp = requests.get(API_URL, params=params, timeout=30)
data = resp.json()
if "error" in data:
    print("VK API ERROR:", data["error"])
    sys.exit(1)

response = data.get("response", {})
items = response.get("items", [])

def fmt_dt(ts):
    return datetime.utcfromtimestamp(int(ts)).replace(tzinfo=timezone.utc)

def escape(s): return html.escape(s or "")

def biggest_photo_url(photo):
    sizes = photo.get("sizes", [])
    if not sizes: return None
    sizes = sorted(sizes, key=lambda x: (x.get("width", 0), x.get("height", 0)), reverse=True)
    return sizes[0].get("url")

def render_attachments(atts):
    parts = []
    for a in atts or []:
        t = a.get("type")
        obj = a.get(t) or {}
        if t == "photo":
            img = biggest_photo_url(obj) or obj.get("url")
            if img: parts.append(f'<p><a href="{img}">[photo]</a></p>')
        elif t == "video":
            owner = obj.get("owner_id")
            vid = obj.get("id")
            ak = obj.get("access_key")
            if owner is not None and vid is not None:
                link = f"https://vk.com/video{owner}_{vid}"
                if ak: link += f"?access_key={ak}"
                parts.append(f'<p><a href="{link}">[video]</a></p>')
        elif t == "link":
            url = obj.get("url")
            title = escape(obj.get("title") or url or "[link]")
            if url: parts.append(f'<p><a href="{url}">{title}</a></p>')
        elif t == "doc":
            url = obj.get("url")
            title = escape(obj.get("title") or "[document]")
            if url: parts.append(f'<p><a href="{url}">{title}</a></p>')
        elif t == "audio":
            artist = escape(obj.get("artist", ""))
            title = escape(obj.get("title", ""))
            label = (artist + " – " + title).strip(" –")
            parts.append(f'<p>[audio] {label}</p>')
        else:
            parts.append(f"<p>[{escape(t)}]</p>")
    return "\n".join(parts)

def render_copy_history(ch):
    if not ch: return ""
    parts = []
    for post in ch:
        t = escape(post.get("text", ""))
        parts.append("<hr><p><i>Repost (oryginał):</i></p>")
        if t: parts.append(f"<blockquote>{t}</blockquote>")
        parts.append(render_attachments(post.get("attachments")))
    return "\n".join([p for p in parts if p])

feed_title = "VK feed"
feed_link = "https://vk.com"
if VK_DOMAIN:
    feed_title = f"VK – {VK_DOMAIN}"
    feed_link = f"https://vk.com/{VK_DOMAIN}"
elif VK_OWNER_ID:
    feed_title = f"VK – wall{VK_OWNER_ID}"
    feed_link = f"https://vk.com/wall{VK_OWNER_ID}"

fg = FeedGenerator()
fg.title(feed_title)
fg.link(href=feed_link, rel='alternate')
fg.link(href=feed_link, rel='self')
fg.description(f"Publiczne posty z VK ({feed_title}) – GitHub Actions.")

for it in items:
    post_id = it.get("id")
    owner_id = it.get("owner_id")
    url = f"https://vk.com/wall{owner_id}_{post_id}"
    txt = it.get("text") or ""
    title = re.sub(r"\s+", " ", txt.strip())[:140] or f"Post {post_id}"
    pub = fmt_dt(it.get("date", time.time()))

    parts = []
    if txt: parts.append(f"<p>{escape(txt)}</p>")
    parts.append(render_attachments(it.get("attachments")))
    parts.append(render_copy_history(it.get("copy_history")))
    content = "\n".join([p for p in parts if p]) or "(brak treści)"

    fe = fg.add_entry()
    fe.id(url)
    fe.title(title)
    fe.link(href=url)
    fe.published(pub)
    fe.content(content, type='html')

rss = fg.rss_str(pretty=True)
os.makedirs("docs", exist_ok=True)
open("docs/feed.xml", "wb").write(rss)
print(f"OK: zapisano docs/feed.xml z {len(items)} wpisami.")
