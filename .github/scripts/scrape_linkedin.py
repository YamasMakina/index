import json, feedparser, os, re

RSS_URL = "https://rsshub.app/linkedin/company/yamas-ya%C5%9Far-makina-ltd-%C5%9Fti-/posts"
os.makedirs("index", exist_ok=True)

print("🌐 RSSHub'tan gönderiler çekiliyor...")

feed = feedparser.parse(RSS_URL)
posts = []

for entry in feed.entries[:6]:
    title = entry.title.strip()
    link = entry.link
    desc = re.sub(r"<.*?>", "", entry.get("description", ""))  # HTML etiketlerini temizle
    text = desc or title
    if len(text) > 300:
        text = text[:297] + "..."
    posts.append({
        "date": entry.get("published", ""),
        "text": text,
        "link": link,
        "image": "https://yamasmakina.github.io/index/default.jpg"
    })

if not posts:
    posts.append({
        "date": "",
        "text": "Gönderi bulunamadı veya RSSHub'tan veri alınamadı.",
        "link": RSS_URL,
        "image": "https://yamasmakina.github.io/index/default.jpg"
    })

with open("index/social.json", "w", encoding="utf-8") as f:
    json.dump(posts, f, ensure_ascii=False, indent=2)

print(f"✅ {len(posts)} gönderi kaydedildi.")
