import requests, re, json
from bs4 import BeautifulSoup

URL = "https://www.linkedin.com/company/yamas-ya%C5%9Far-makina-ltd-%C5%9Fti-/posts/"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Accept-Language": "tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7"
}

html = requests.get(URL, headers=headers).text
soup = BeautifulSoup(html, "html.parser")

posts = []
for tag in soup.find_all("meta"):
    prop = tag.get("property", "")
    content = tag.get("content", "")
    if prop == "og:title" and content.strip():
        title = content.strip()
        posts.append({"text": title, "link": URL})
    elif prop == "og:image" and posts:
        posts[-1]["image"] = content

# Basit tarih ekleme
for p in posts:
    p["date"] = ""
    if "image" not in p:
        p["image"] = "https://yamasmakina.github.io/index/default.jpg"

# İlk 8 gönderiyle sınırla
posts = posts[:8]

# JSON'a yaz
with open("index/social.json", "w", encoding="utf-8") as f:
    json.dump(posts, f, ensure_ascii=False, indent=2)
