import feedparser
import requests
import time
import re
import os

# --- AYARLARIN (Railway'deki Variables kısmından çekilir) ---
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")
TWITTER_USERNAME = os.getenv("TWITTER_USERNAME")
CHECK_INTERVAL = 120 # 2 dakikada bir kontrol eder

last_link = ""

def send_to_telegram(message, image_url=None):
    try:
        if image_url:
            url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"
            payload = {
                "chat_id": CHANNEL_ID,
                "photo": image_url,
                "caption": message,
                "parse_mode": "HTML"
            }
        else:
            url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
            payload = {
                "chat_id": CHANNEL_ID,
                "text": message,
                "parse_mode": "HTML"
            }
        r = requests.post(url, data=payload)
        print(f"Telegram Yanıtı: {r.status_code}")
    except Exception as e:
        print(f"Mesaj gonderilirken hata olustu: {e}")

print("Bot baslatildi...")

while True:
    try:
        # RSSHub üzerinden Twitter akışını al
        feed_url = f"https://rsshub.app/twitter/user/{TWITTER_USERNAME}"
        feed = feedparser.parse(feed_url)
        
        if feed.entries:
            tweet = feed.entries[0]
            link = tweet.link
            
            # İlk çalıştırmada son tweeti kaydet ama paylaşma (kanalı korumak için)
            if not last_link:
                last_link = link
                print(f"Baslangic tweeti kaydedildi: {link}")
            
            # Eğer yeni bir tweet ise ve Retweet degilse
            elif link != last_link and not tweet.title.startswith("RT @"):
                
                # Metni temizle
                clean_text = re.sub(r'<[^>]+>', '', tweet.summary)
                full_message = f"{clean_text}\n\n🔗 <a href='{link}'>Tweet Linki</a>"
                
                # Görsel bulma
                img_url = None
                if 'media_content' in tweet:
                    img_url = tweet.media_content[0]['url']
                elif 'links' in tweet:
                    for l in tweet.links:
                        if 'image' in l.get('type', ''):
                            img_url = l.get('href')

                send_to_telegram(full_message, img_url)
                last_link = link
                print(f"Yeni tweet paylasildi: {link}")
        else:
            print("Tweet bulunamadi veya RSSHub su an yanit vermiyor.")
                
    except Exception as e:
        print(f"Döngü hatası: {e}")
        
    time.sleep(CHECK_INTERVAL)
