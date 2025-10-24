import requests, re, json
from bs4 import BeautifulSoup

URL = "https://www.linkedin.com/company/yamas-ya%C5%9Far-makina-ltd-%C5%9Fti-/posts/"
headers = {"User-Agent": "Mozilla/5.0", "Accept-Language": "tr-TR,tr;q=0.9"}

html = requests.get(URL, headers=headers).text
soup = BeautifulSoup(html, "html.parser")

posts = []
for tag in soup.find_all("meta", {"property": "og:title"}):
    posts.append({
        "text": tag.get("content", "")[:220],
        "link": URL,
        "image": "",
        "date": ""
    })

if not posts:
    posts.append({
        "text": "Henüz gönderi bulunamadı.",
        "link": URL,
        "image": "",
        "date": ""
    })

with open("index/social.json", "w", encoding="utf-8") as f:
    json.dump(posts, f, ensure_ascii=False, indent=2)
