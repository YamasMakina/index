import os, re, json
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import chromedriver_autoinstaller
import time

URL = "https://www.linkedin.com/company/yamas-ya%C5%9Far-makina-ltd-%C5%9Fti-/posts/"
os.makedirs("index", exist_ok=True)

print("🌐 LinkedIn sayfası yükleniyor...")

# Chrome ayarları
chromedriver_autoinstaller.install()
chrome_options = Options()
chrome_options.add_argument("--headless=new")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--window-size=1920,1080")

driver = webdriver.Chrome(options=chrome_options)

try:
    driver.get(URL)

    # Sayfanın tamamen yüklenmesini bekle
    try:
        WebDriverWait(driver, 25).until(
            EC.presence_of_element_located((By.CLASS_NAME, "feed-shared-update-v2"))
        )
        print("🟢 Gönderiler yüklendi, veri çekiliyor...")
    except:
        print("⚠️ Gönderiler zamanında yüklenmedi, mevcut içerik çekilecek...")

    time.sleep(2)
    html = driver.page_source
    soup = BeautifulSoup(html, "html.parser")

    posts = []
    for post in soup.find_all("div", class_=re.compile("feed-shared-update-v2")):
        text_el = post.find("span", {"dir": "ltr"})
        img_el = post.find("img", class_=re.compile("feed-shared-image__image"))
        if text_el:
            text = text_el.get_text(" ", strip=True)
            if len(text) > 220:
                text = text[:217] + "..."
            image_url = (
                img_el["src"]
                if img_el and img_el.get("src")
                else "https://yamasmakina.github.io/index/default.jpg"
            )
            posts.append({
                "date": "",
                "text": text,
                "link": URL,
                "image": image_url
            })

    if not posts:
        posts.append({
            "date": "",
            "text": "Gönderi bulunamadı veya içerik dinamik olarak yüklenemedi.",
            "link": URL,
            "image": "https://yamasmakina.github.io/index/default.jpg"
        })

    # Sadece son 5 gönderiyi kaydet
    posts = posts[:5]

    # JSON kaydet
    with open("index/social.json", "w", encoding="utf-8") as f:
        json.dump(posts, f, ensure_ascii=False, indent=2)

    print(f"✅ {len(posts)} gönderi kaydedildi.")
except Exception as e:
    print("⚠️ Hata:", e)
    with open("index/social.json", "w", encoding="utf-8") as f:
        json.dump(
            [{"text": f"Hata: {e}", "image": "", "link": URL, "date": ""}],
            f, ensure_ascii=False, indent=2
        )
finally:
    driver.quit()
