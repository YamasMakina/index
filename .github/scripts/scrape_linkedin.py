import os
import json
import re
import requests
import xml.etree.ElementTree as ET

RSS_URL = "https://rsshub.app/linkedin/company/yamas-ya%C5%9Far-makina-ltd-%C5%9Fti-/posts"
os.makedirs("index", exist_ok=True)

print("🌐 RSSHub'tan LinkedIn gönderileri alınıyor...")

try:
    r = requests.get(RSS_URL, timeout=20)
    r.raise_for_status()
    xml_text = r.text

    root = ET.fromstring(xml_text)
    items = root.findall(".//item")

    posts = []
    for item in items[:6]:
        title = item.findtext("title", "").strip()
        desc = re.sub(r"<.*?>", "", item.findtext("description", "").strip())
        link = item.findtext("link", "").strip()
        pub = item.findtext("pubDate", "").strip()
        text = desc or title
        if len(text) > 350:
            text = text[:347] + "..."
        posts.append({
            "date": pub,
            "text": text,
            "link": link,
            "image": "https://yamasmakina.github.io/index/default.jpg"
        })

    if not posts:
        posts.append({
            "date": "",
            "text": "RSSHub gönderileri boş döndü.",
            "link": RSS_URL,
            "image": "https://yamasmakina.github.io/index/default.jpg"
        })

    with open("index/social.json", "w", encoding="utf-8") as f:
        json.dump(posts, f, ensure_ascii=False, indent=2)

    print(f"✅ {len(posts)} gönderi kaydedildi.")
except Exception as e:
    print("⚠️ Hata:", e)
    with open("index/social.json", "w", encoding="utf-8") as f:
        json.dump([{
            "date": "",
            "text": f"Hata: {e}",
            "link": RSS_URL,
            "image": ""
        }], f, ensure_ascii=False, indent=2)
