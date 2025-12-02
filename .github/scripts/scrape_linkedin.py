#!/usr/bin/env python3
import os, sys, json, time, re
import requests
import feedparser
from pathlib import Path

# 1) Çoklu RSSHub aynaları (sırayla denenir)
MIRRORS = [
    "https://rsshub.app",
    "https://rsshub.moeyy.cn",
    "https://rsshub.uneasy.win",
    "https://rsshub.woodland.cafe",
]

COMPANY_SLUG = "yamas-ya%C5%9Far-makina-ltd-%C5%9Fti-"
PATH = f"/linkedin/company/{COMPANY_SLUG}/posts"

OUTPUT_PATH = os.environ.get("OUTPUT_PATH", "index/social.json")
OUT = Path(OUTPUT_PATH)
OUT.parent.mkdir(parents=True, exist_ok=True)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; YAMAS-Scraper/1.1; +github-actions)"
}

def strip_html(s: str) -> str:
    return re.sub(r"<.*?>", "", s or "").strip()

def load_previous_json():
    try:
        if OUT.exists():
            return json.loads(OUT.read_text(encoding="utf-8"))
    except Exception:
        pass
    return []

def safe_write(posts):
    OUT.write_text(json.dumps(posts, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"✅ Yazıldı: {OUT} ({len(posts)} kayıt)")

def uniq_key(item):
    # benzersizliği anlamak için link ya da text’in ilk 48 karakteri
    return (item.get("link") or "") or (item.get("text") or "")[:48]

def fetch_first_alive(tries_per_mirror=2, base_delay=6, timeout=90):
    last_err = None
    for base in MIRRORS:
        url = base + PATH
        for t in range(1, tries_per_mirror + 1):
            try:
                print(f"🔎 [{base}] deneme {t}/{tries_per_mirror} → {url} (timeout={timeout}s)")
                r = requests.get(url, headers=HEADERS, timeout=timeout)
                r.raise_for_status()
                return r.text, url
            except Exception as e:
                last_err = e
                wait = base_delay * t
                print(f"⚠️ [{base}] hata: {e} — {wait}s bekleniyor…")
                time.sleep(wait)
    raise last_err

def main():
    print("🌐 LinkedIn → RSSHub çekimi başlıyor…")
    prev = load_previous_json()

    try:
        xml_text, used_url = fetch_first_alive()
        feed = feedparser.parse(xml_text)

        if feed.bozo:
            print(f"⚠️ feedparser bozo: {feed.bozo_exception}")

        items = feed.entries or []
        if not items:
            raise RuntimeError("RSS boş döndü.")

        posts = []
        for it in items[:10]:
            title = strip_html(getattr(it, "title", "")) or "Başlıksız Gönderi"
            desc  = strip_html(getattr(it, "summary", "")) or ""
            link  = (getattr(it, "link", "") or "").strip()
            pub   = (getattr(it, "published", "") or "").strip()

            text = desc or title
            if len(text) > 350:
                text = text[:347] + "…"

            posts.append({
                "date": pub,
                "text": text,
                "link": link,
                "image": "https://yamasmakina.github.io/index/default.jpg"
            })

        # 2) Boşsa yazma
        if not posts:
            raise RuntimeError("parse sonrası boş")

        # 3) Gerçekten yeni mi? (GUID/link seti karşılaştırması)
        prev_keys = {uniq_key(p) for p in prev} if prev else set()
        new_keys  = {uniq_key(p) for p in posts}

        if new_keys and new_keys != prev_keys:
            print("🆕 Yeni içerik var → dosya güncellenecek.")
            safe_write(posts)
        else:
            print("ℹ️ İçerik değişmemiş → eski dosya korunuyor.")
            # yine de formatı sağlam tutmak için önceki varsa onu yaz
            if prev:
                safe_write(prev)
            else:
                safe_write(posts)

        print(f"🏁 Bitti. Kaynak: {used_url}")
        return 0

    except Exception as e:
        print(f"❗ Scrape hatası: {e}")
        if prev:
            print("↩️ Eski social.json korunuyor (RSS arızalı).")
            safe_write(prev)
        else:
            fallback = [{
                "date": "",
                "text": f"Hata: {e}\nRSSHub şu an erişilemiyor. Bir sonraki çalışmada tekrar denenecek.",
                "link": MIRRORS[0] + PATH,
                "image": "https://yamasmakina.github.io/index/default.jpg"
            }]
            safe_write(fallback)
        return 0

if __name__ == "__main__":
    try:
        sys.exit(main() or 0)
    except SystemExit:
        sys.exit(0)
    except Exception:
        sys.exit(0)
