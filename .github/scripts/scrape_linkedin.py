import os
import json
import re
import time
import requests
import xml.etree.ElementTree as ET

RSS_URL = "https://rsshub.app/linkedin/company/yamas-ya%C5%9Far-makina-ltd-%C5%9Fti-/posts"
OUTPUT_FILE = "index/social.json"
os.makedirs("index", exist_ok=True)

print("🌐 RSSHub'tan LinkedIn gönderileri alınıyor...")

def fetch_rss():
    """RSSHub'tan XML çekme işlemi (retry dahil)"""
    for attempt in range(3):
        try:
            r = requests.get(RSS_URL, timeout=20)
            r.raise_for_status()
            return r.text
        except Exception as e:
            print(f"⚠️ Deneme {attempt+1}/3 başarısız: {e}")
            time.sleep(5)
    raise Exception("RSSHub 3 denemede de yanıt vermedi.")

try:
    xml_text = fetch_rss()
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
        print("⚠️ RSSHub boş döndü, eski veriyi koruyorum.")
        raise Exception("RSSHub boş yanıt verdi.")

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(posts, f, ensure_ascii=False, indent=2)

    print(f"✅ {len(posts)} gönderi kaydedildi.")

except Exception as e:
    print(f"🚫 Hata: {e}")
    # Eğer eski social.json varsa, onu koru
    if os.path.exists(OUTPUT_FILE):
        print("📦 Eski social.json korunuyor (üzerine yazılmadı).")
    else:
        print("⚠️ Eski dosya yok, hata kaydediliyor.")
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            json.dump([{
                "date": "",
                "text": f"Hata: {e}",
                "link": RSS_URL,
                "image": ""
            }], f, ensure_ascii=False, indent=2)
