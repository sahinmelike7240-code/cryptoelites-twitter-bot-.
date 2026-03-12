import feedparser
import requests
import time
import re
import os

# --- AYARLAR (Railway'deki Variables kısmından çekilir) ---
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")
# RSS.app linkini buraya direkt sabitliyoruz çünkü en sağlamı bu:
feed_url = "https://rss.app/feeds/X411D152Had8CdC6.xml"
CHECK_INTERVAL = 120 # 2 dakikada bir kontrol eder

last_link = ""

def send_to_telegram(message, image_url=None):
    try:
        if image_url:
            url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"
            payload = {
                "chat_id": CHANNEL_ID,
                "photo": image_url,
                "caption": message
            }
        else:
            url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
            payload = {
                "chat_id": CHANNEL_ID,
                "text": message
            }
        
        response = requests.post(url, data=payload)
        print(f"Telegram Yanıtı: {response.status_code}")
        return response.status_code == 200
    except Exception as e:
        print(f"Mesaj gonderilirken hata olustu: {e}")

print("Bot baslatildi...")
# Botun açıldığını kanıtlamak için (İstersen sonra bu satırı silebilirsin)
send_to_telegram("Sistem Kontrol: Bot RSS.app üzerinden yayına başladı! 🚀")

while True:
    try:
        feed = feedparser.parse(feed_url)
        
        if feed.entries:
            # En son tweeti al
            tweet = feed.entries[0]
            current_link = tweet.link
            
            # Eğer bu link daha önce paylaşılanla aynı değilse PAYLAŞ
            if current_link != last_link:
                # Metni al ve temizle
                raw_text = tweet.get('summary', tweet.get('description', ''))
                clean_text = re.sub(r'<[^>]+>', '', raw_text) # HTML etiketlerini sil
                
                message = f"{clean_text}\n\n{current_link}"
                
                # Varsa görseli al
                image_url = None
                if 'media_content' in tweet:
                    image_url = tweet.media_content[0]['url']
                elif 'links' in tweet:
                    for l in tweet.links:
                        if 'image' in l.get('type', ''):
                            image_url = l.get('href')
                
                # Telegram'a gönder
                if send_to_telegram(message, image_url):
                    last_link = current_link
                    print(f"Yeni tweet paylasildi: {current_link}")
        
        else:
            print("RSS feed bos veya ulasilamiyor.")

    except Exception as e:
        print(f"Bir hata olustu: {e}")
    
    time.sleep(CHECK_INTERVAL)
