import feedparser
import requests
import time
import re

# --- AYARLARIN ---
BOT_TOKEN = "BURAYA_BOT_TOKEN_YAZ"
CHANNEL_ID = "@CryptoELlTES"
TWITTER_USERNAME = "CryptooELITES"
CHECK_INTERVAL = 120 # 2 dakikada bir kontrol eder

last_link = ""

def send_to_telegram(message, image_url=None):
    if image_url:
        # Görsel varsa: Fotoğraf + Metin olarak gönderir
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"
        payload = {
            "chat_id": CHANNEL_ID,
            "photo": image_url,
            "caption": message,
            "parse_mode": "HTML"
        }
    else:
        # Görsel yoksa: Sadece Metin gönderir
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        payload = {
            "chat_id": CHANNEL_ID,
            "text": message,
            "parse_mode": "HTML"
        }
    requests.post(url, data=payload)

print("Bot baslatildi...")

while True:
    try:
        feed = feedparser.parse(f"https://rsshub.app/twitter/user/{TWITTER_USERNAME}")
        
        if feed.entries:
            tweet = feed.entries[0]
            link = tweet.link
            
            # Eğer yeni bir tweet ise ve Retweet degilse (RT filtresi)
            if link != last_link and not tweet.title.startswith("RT @"):
                
                # Metni temizle (HTML etiketlerinden arindir)
                clean_text = re.sub(r'<[^>]+>', '', tweet.summary)
                full_message = f"{clean_text}\n\n🔗 <a href='{link}'>Tweet Linki</a>"
                
                # Görsel bulma (RSS içindeki resim linkini yakalar)
                img_url = None
                if 'media_content' in tweet:
                    img_url = tweet.media_content[0]['url']
                elif 'links' in tweet:
                    for l in tweet.links:
                        if 'image' in l.get('type', ''):
                            img_url = l.get('href')

                send_to_telegram(full_message, img_url)
                last_link = link
                print(f"Paylasildi: {link}")
                
    except Exception as e:
        print(f"Bir hata oldu ama devam ediyorum: {e}")
        
    time.sleep(CHECK_INTERVAL)
