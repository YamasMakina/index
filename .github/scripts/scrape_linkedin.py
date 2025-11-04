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

def normalize_link(link):
    """RSSHub bazen tr.linkedin.com veya kısmi link döndürüyor — düzeltelim"""
    if not link:
        return ""
    link = link.strip()
    link = link.replace("tr.linkedin.com", "www.linkedin.com")
    link = link.replace("linkedin.com/company/", "www.linkedin.com/company/")
    # Eğer 'activity-' veya 'feed/update' içermiyorsa, gönderi linki eksiktir
    if not ("activity-" in link or "feed/update" in link):
        # fallback: sadece şirket sayfasına yönlendir
        return "https://www.linkedin.com/company/yamas-ya%C5%9Far-makina-ltd-%C5%9Fti-/posts/"
    return link

def fetch_rss():
    for attempt in range(3):
        try:
            start = time.time()
            r = requests.get(RSS_URL, timeout=90)
            r.raise_for_status()
            elapsed = round(time.time() - start, 1)
            print(f"✅ RSSHub bağlantısı başarılı ({elapsed} sn)")
            return r.text
        except Exception as e:
            print(f"⚠️ Deneme {attempt+1}/3 başarısız: {e}")
            if attempt < 2:
                print("⏳ 8 saniye sonra yeniden denenecek...")
                time.sleep(8)
    raise Exception("RSSHub 3 denemede de yanıt vermedi (timeout veya erişim hatası).")

try:
    xml_text = fetch_rss()
    root = ET.fromstring(xml_text)
    items = root.findall(".//item")

    posts = []
    for item in items[:6]:
        title = item.findtext("title", "").strip()
        desc = re.sub(r"<.*?>", "", item.findtext("description", "").strip())
        link = normalize_link(item.findtext("link", "").strip())
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
        raise Exception("RSSHub boş yanıt verdi.")
    })

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(posts, f, ensure_ascii=False, indent=2)

    print(f"✅ {len(posts)-1} gönderi kaydedildi (toplam {len(posts)} kayıt).")

except Exception as e:
    print(f"🚫 Hata: {e}")
    if os.path.exists(OUTPUT_FILE):
        print("📦 Eski social.json korunuyor.")
    else:
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            json.dump([{
                "date": "",
                "text": f"Hata: {e}",
                "link": RSS_URL,
                "image": ""
            }], f, ensure_ascii=False, indent=2)
