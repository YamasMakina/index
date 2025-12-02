#!/usr/bin/env python3
import os, sys, json, time, re
import requests
import feedparser
from pathlib import Path

RSS_URL = os.environ.get("RSS_URL", "").strip() or \
    "https://rsshub.app/linkedin/company/yamas-ya%C5%9Far-makina-ltd-%C5%9Fti-/posts"
OUTPUT_PATH = os.environ.get("OUTPUT_PATH", "index/social.json")

OUT = Path(OUTPUT_PATH)
OUT.parent.mkdir(parents=True, exist_ok=True)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; YAMAS-Scraper/1.0; +github-actions)"
}

def fetch_rss_with_retry(url: str, tries=4, base_delay=6, timeout=90):
    last_err = None
    for i in range(1, tries + 1):
        try:
            print(f"🔎 [{i}/{tries}] RSS çekiliyor: {url} (timeout={timeout}s)")
            r = requests.get(url, headers=HEADERS, timeout=timeout)
            r.raise_for_status()
            return r.text
        except Exception as e:
            last_err = e
            wait = base_delay * i
            print(f"⚠️ Deneme {i} hata: {e} — {wait}s bekleniyor...")
            time.sleep(wait)
    raise last_err

def strip_html(s: str) -> str:
    return re.sub(r"<.*?>", "", s or "").strip()

def load_previous_json() -> list:
    try:
        if OUT.exists():
            return json.loads(OUT.read_text(encoding="utf-8"))
    except Exception:
        pass
    return []

def safe_write(posts: list):
    try:
        OUT.write_text(json.dumps(posts, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"✅ Yazıldı: {OUT} ({len(posts)} kayıt)")
    except Exception as e:
        print(f"❌ Yazma hatası: {e}")

def main():
    print("🌐 RSSHub => LinkedIn scrape başlıyor...")
    prev = load_previous_json()

    try:
        xml_text = fetch_rss_with_retry(RSS_URL, tries=4, base_delay=7, timeout=90)
        feed = feedparser.parse(xml_text)

        if feed.bozo:
            print(f"⚠️ feedparser bozo: {feed.bozo_exception}")

        items = feed.entries or []
        if not items:
            raise RuntimeError("RSS boş döndü.")

        posts = []
        for it in items[:8]:
            title = strip_html(getattr(it, "title", "")) or "Başlıksız Gönderi"
            desc = strip_html(getattr(it, "summary", "")) or ""
            link = getattr(it, "link", "").strip() or "#"
            pub = getattr(it, "published", "").strip()

            text = desc or title
            if len(text) > 350:
                text = text[:347] + "..."

            posts.append({
                "date": pub,
                "text": text,
                "link": link,
                "image": "https://yamasmakina.github.io/index/default.jpg"
            })

        safe_write(posts)
        print("🏁 Bitti (başarılı).")
        return 0

    except Exception as e:
        print(f"❗ Scrape hatası: {e}")

        # 1) Önce eski dosyayı KORU (varsa) ve onu tekrar yaz (format sağlam kalsın)
        if prev:
            print("↩️ Eski sosyal.json korunuyor (RSS arızalı).")
            safe_write(prev)
            return 0

        # 2) Hiç yoksa bilgilendirici tek kart yaz
        fallback = [{
            "date": "",
            "text": f"Hata: {e}\nRSSHub şu an erişilemiyor veya çok yavaş. Sistem kısa süre içinde tekrar deneyecek.",
            "link": RSS_URL,
            "image": "https://yamasmakina.github.io/index/default.jpg"
        }]
        safe_write(fallback)
        return 0

if __name__ == "__main__":
    # Asla nonzero çıkma — workflow'un kırılmasını istemiyoruz
    try:
        sys.exit(main() or 0)
    except SystemExit as se:
        # Her ihtimale karşı
        code = int(se.code) if isinstance(se.code, int) else 0
        sys.exit(0 if code != 0 else 0)
    except Exception:
        sys.exit(0)
