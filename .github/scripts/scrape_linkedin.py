import os, time, json, re
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import chromedriver_autoinstaller

# Hedef URL
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
    time.sleep(8)  # Dinamik içeriklerin yüklenmesi için bekleme süresi

    html = driver.page_source
    soup = BeautifulSoup(html, "html.parser")

    posts = []
    divs = soup.find_all("div", class_=re.compile("feed-shared-update-v2__description"))
    images = soup.find_all("img", class_=re.compile("feed-shared-image__image"))

    print(f"🧩 {len(divs)} gönderi bulundu.")

    for i, div in enumerate(divs[:5]):  # sadece son 5 gönderi
        text = div.get_text(strip=True)
        if len(text) > 220:
            text = text[:217] + "..."
        image_url = images[i]["src"] if i < len(images) else "https://yamasmakina.github.io/index/default.jpg"
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

    # JSON kaydet
    with open("index/social.json", "w", encoding="utf-8") as f:
        json.dump(posts, f, ensure_ascii=False, indent=2)

    print(f"✅ {len(posts)} gönderi kaydedildi.")
except Exception as e:
    print("⚠️ Hata:", e)
    with open("index/social.json", "w", encoding="utf-8") as f:
        json.dump([{"text": f"Hata: {e}", "image": "", "link": URL, "date": ""}], f, ensure_ascii=False, indent=2)
finally:
    driver.quit()
