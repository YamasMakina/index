import os, requests, re, json
from bs4 import BeautifulSoup

URL = "https://www.linkedin.com/company/yamas-ya%C5%9Far-makina-ltd-%C5%9Fti-/posts/"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Accept-Language": "tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7"
}

print("🔄 LinkedIn gönderileri çekiliyor...")

# 💡 Sosyal JSON dizini yoksa oluştur
os.makedirs("index", exist_ok=True)

try:
    html = requests.get(URL, headers=headers, timeout=20).text
    soup = BeautifulSoup(html, "html.parser")
    posts = []
    current = {}

    for tag in soup.find_all("meta"):
        prop = tag.get("property", "")
        content = tag.get("content", "")
        if not content:
            continue

        # Başlık
        if prop == "og:title":
            if current:
                posts.append(current)
            current = {"text": content.strip(), "link": URL}
        # Görsel
        elif prop == "og:image" and current:
            img = content.strip()
            if "media.licdn" in img:
                img = img.replace("feedshare-shrink_800", "feedshare-shrink_600")  # optimize
            current["image"] = img

    if current:
        posts.append(current)

    # Filtrele, sınırla
    clean_posts = []
    for p in posts:
        if not p.get("text"):
            continue
        text = re.sub(r"\s+", " ", p["text"]).strip()
        if len(text) > 180:
            text = text[:177] + "..."
        img = p.get("image", "https://yamasmakina.github.io/index/default.jpg")
        clean_posts.append({
            "date": "",
            "text": text,
            "link": p.get("link", URL),
            "image": img
        })

    clean_posts = clean_posts[:5]  # sadece son 5 gönderi

    with open("index/social.json", "w", encoding="utf-8") as f:
        json.dump(clean_posts, f, ensure_ascii=False, indent=2)

    print(f"✅ {len(clean_posts)} gönderi kaydedildi.")
except Exception as e:
    print("⚠️ Hata:", e)
    os.makedirs("index", exist_ok=True)
    with open("index/social.json", "w", encoding="utf-8") as f:
        json.dump(
            [{"text": f"Veri alınamadı ({e})", "image": "", "link": URL, "date": ""}],
            f, ensure_ascii=False, indent=2
        )
