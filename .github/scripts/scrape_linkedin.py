import json, feedparser, os

# RSSHub feed URL'in
RSS_URL = "https://rsshub.app/linkedin/company/yamas-ya%C5%9Far-makina-ltd-%C5%9Fti-/posts"
os.makedirs("index", exist_ok=True)

print("🌐 RSSHub'tan gönderiler çekiliyor...")

feed = feedparser.parse(RSS_URL)
posts = []

for entry in feed.entries[:6]:  # son 6 gönderi
    title = entry.title
    link = entry.link
    image = ""
    # Bazı RSSHub feed'lerinde görsel HTML içindedir
    if "media_content" in entry:
        image = entry.media_content[0]["url"]
    elif "summary" in entry:
        import re
        m = re.search(r'src="([^"]+)"', entry.summary)
        if m:
            image = m.group(1)
    posts.append({
        "date": entry.get("published", ""),
        "text": title,
        "link": link,
        "image": image or "https://yamasmakina.github.io/index/default.jpg"
    })

if not posts:
    posts.append({
        "date": "",
        "text": "RSSHub gönderileri çekilemedi.",
        "link": RSS_URL,
        "image": "https://yamasmakina.github.io/index/default.jpg"
    })

with open("index/social.json", "w", encoding="utf-8") as f:
    json.dump(posts, f, ensure_ascii=False, indent=2)

print(f"✅ {len(posts)} gönderi kaydedildi.")
