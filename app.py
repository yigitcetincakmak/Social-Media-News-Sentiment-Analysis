import os
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"  # ileride ekleyeceğimiz kütüphaneler (PyTorch ve NumPy arasında olan yaygın teknik çakışmayı engellemek veya
# özellikle pyTorch kütüphanesinin birden fazla versiyonun çakışmasından kaynaklanan ve analizin donmasına neden olan hatayı(OMP:Error #15) engellemek
# için çünkü bu çakışma programı çökerten bir çakışma bizde --> (Duplicate Library OK = TRUE --> yani Tekrarlanan Kütüphane Tamam). ile çökme veya kilitlenme, programın çalışmasına izin ver demiş bulunuyoruz.
# ve bunu programın en başına koyduk ilk olarak çalışması ve ileride bu dosyada birçok işlem yapacağız , analiz sonuçlarını göstereceğiz problem çıkartmaması için şu anlık bunu ekledik. )



from flask import Flask, render_template, request, jsonify

import pandas as pd             # Dataframe işlemlerimiz için
import data_collector           # Twitter verisi için
import config                   # Ayarlarımızı okumak için
import text_processor           # Metin temizleme fonksiyonları için
import sentiment_analyzer       # Duygu analizi fonksiyonları için
import database




# Flask bir web uygulamasıdır.
# Tarayıcı bir istek gönderir --> Flask karşılar --> Python kodu çalışır --> cevap JSON veya HTML olarak döner.


app = Flask(__name__) # Flask sınıfından bir uygulama (web server) oluşturuyoruz. Bu uygulama: Route’ları (URL yollarını),API fonksiyonlarını,HTML sayfalarını barındırır

# Modeli sunucu başlarken yükle
print("Model yükleniyor...")
model = sentiment_analyzer.load_model() # uygulama başlarken duygu analiz modelini RAM'e yüklüyoruz.her istek için tekrar yüklenmesin diye bir kere yüklenir.
print("Model hazır.")



# route ne demek --> tarayıcıdan girilen veya fetch ile çağrılan URL’ye bağlı bir fonksiyon.
# örneğin / --> index()  ,  /api/analyze  --> analyze()


# / adresine (ana sayfa) bir istek gelince bu fonksiyon çalışır.
@app.route('/')
def index():
    return render_template("index.html") # render_template("index.html") templates klasöründeki HTML dosyasını tarayıcıya gönderir.render = “işle”  ,  template = “HTML şablonu”


# Bu ne demek?  /api/analyze adresine istek gelirse bu fonksiyon çalışır.
# methods=['POST'] --->  Bu endpoint sadece POST isteği kabul eder.
    ''' GET ve POST farkı ne?

| GET              | POST                      |
| ---------------- | ------------------------- |
| URL ile gönderir | Gövde (body) ile gönderir |
| Görünür          | Gizli                     |
| Veri almak       | Veri göndermek            |

GET nedir ?
-Sunucudan veri almak için kullanılır.
-Bir şey göndermezsin, yalnızca soru sorarsın.
-Gövde (body) kullanılmaz.
Veriler URL içinde gönderilir --> buna query parametre denir.

------------------------------------------------------------

POST nedir?
- Sunucuya veri göndermek için kullanılır.
- Form doldurmak, login olmak, kayıt oluşturmak gibi işlemlerde kullanılır.
- Veriler body (gövde) içinde gönderilir.


Gövde (body) nedir?
Şurada görünen kısım:
{
  "name": "Alperen",
  "age": 20
}
Bu JSON formatında gönderilen kullanıcı verisidir.

Yani şunu diyoruz :
“Sunucuya sana bir kişi bilgisi gönderiyorum:

adı: Alperen
yaşı: 20
Bunu işleyip kaydet.”

Flask’ta bunu böyle okuyoruz:

data = request.get_json()
name = data["name"]
age = data["age"]


Örneğin:
GET --> /products?category=phone
POST --> Gövde: { "name": "Alperen", "age": 20 }
'''


@app.route('/api/analyze', methods=['POST'])
def analyze():
    data = request.json # İstekten gelen JSON’u alıyoruz , Frontend POST olarak JSON gönderiyor.

   # örneğin {
   #             "source": "twitter",
   #             "input_value": "Fenerbahçe",
   #             "sub_option": "Kullanıcı Adı"
   # } Bunu Python sözlüğü (dict) haline getiriyoruz.


    # buradki 3 satır JSON içinden değer çekme yapıyoruz.data bir Python dict (JSON’dan gelmiş).
    source = data.get("source") # JSON'da "source" anahtarının değerini alır. get() kullanmak güvenlidir. Anahtar yoksa hata vermez, None döner.   source = "twitter" veya "news" veya "youtube"
    input_value = data.get("input_value")  # Query, URL veya Kategori , input_value kullanıcı adı = "ronaldo" (Twitter kullanıcı adı) veya "#python" (hashtag) veya "https://youtu.be/abc123" (YouTube URL) veya "spor" (kategori)
    sub_option = data.get("sub_option")  # Arama tipi veya Site adı ---  "Kullanıcı Adı" veya "hashtag" ya da haber sitesi adı (örn. "cnn")

    df = pd.DataFrame() # veri gelmezse içi boş DataFrame olur.

    try:
        # 1. VERİ ÇEKME
        if source == "twitter":
            # sub_option kullanıcı arayüzünden geliyor; kullanıcı “Kullanıcı Adı” seçmişse search_type="username", aksi halde hashtag.bu parametre fetch_tweets fonksiyonuna yönlendiriliyor.
            search_type = "username" if sub_option == "Kullanıcı Adı" else "hashtag"

            # fetch_tweets() fonksiyonu input_value değerine göre tweet çeker.dönen sonuç df’dir.
            # ne yapar Twitter api ile tweetleri çeker ve bir DataFrame döndürür.
            df = data_collector.fetch_tweets(input_value, search_type=search_type, count=config.TWITTER_MAX_RESULTS)
            # input_value — kullanıcı adı (örn. "ronaldo") veya hashtag (örn. "#python"). , search_type — "username" veya "hashtag" , count — kaç tane tweet çekileceği (örn. 100). Genelde


        # News için  sub_option --> site adı   input_value --> kategori  count --> çekilecek haber sayısı.
        elif source == "news":
            # sub_option: Site Adı, input_value: Kategori
            df = data_collector.fetch_news_headlines(sub_option, input_value, count=config.NEWS_MAX_RESULTS)

        # youtube linkinden video id çıkarır. input_value bir youtube URL’si veya paylaşım linki ise bu fonksiyon video id’sini ("dQw4w9WgXcQ" tarzı) çıkarır.
        elif source == "youtube":
            video_id = data_collector.get_video_id_from_url(input_value)
            if not video_id:
                return jsonify({"error": "Geçersiz YouTube Linki"}), 400  # jsonify ---> python sözlüğünü JSON yapar. 400 --> HTTP Hatalı istek (Bad Request) kodu.
            df, title = data_collector.fetch_youtube_comments(video_id)
            # YouTube başlığını frontend'e göndermek için
            data["video_title"] = title

        if df.empty:
            return jsonify({"error": "Sonuç bulunamadı veya erişim engellendi."}), 404

        # 2. ANALİZ AŞAMASI
        processed_df = text_processor.process_dataframe(df) # Görevi: ham metinleri temizlemek (HTML etiketleri kaldırma, URL temizleme, küçük harfe çevirme, noktalama temizleme, tokenization, stopword çıkarma vb.).
        processed_df, counts = sentiment_analyzer.analyze_dataframe(processed_df, model) # sentiment_analyzer.analyze_dataframe(processed_df, model) yüklenmiş model ile her metne duygu sınıfı atamak.

        # 3. VERİTABANI KAYDI
        conn = database.get_db_connection() # psycopg2 ile DB bağlantısını döndürür
        if conn:
            database.create_table_if_not_exists(conn) # tablo yoksa oluşturur.

            kaynak_detay = input_value
            if source == "news":
                kaynak_detay = sub_option
            elif source == "youtube":
                kaynak_detay = data.get("video_title", video_id)

            database.insert_analysis_result( # %s parametreli INSERT ile counts ve metadata’yı kaydeder.
                conn,
                kaynak_tipi=source,
                kaynak_detay=kaynak_detay,
                kategori=input_value if source == "news" else None,
                counts=counts
            )
            conn.close() # bağlantıyı kapatır; aksi halde açık bağlantılar sunucuda birikir.



        # 4. SONUCU JSON OLARAK DÖNDÜRME
        # DataFrame'i JSON formatına çevir (Frontend'de tablo yapmak için)

        # processed_df[["text", "Duygu Durumu", "link"]] --> sadece frontend’e gösterilecek sütunları seçer.
        # .to_dict(orient="records") → DataFrame’i [{...}, {...}] formatında listeye çevirir; JSON’a kolay dönüşür.
        table_data = processed_df[["text", "Duygu Durumu", "link"]].to_dict(orient="records")


        # jsonify(...) --> Flask util, Python objesini JSON response yapar ve Content-Type: application/json ekler.
        return jsonify({
            "counts": counts,
            "table": table_data,
            "total": sum(counts.values()) # toplam analiz edilen metin sayısı (poz+neg+neu).
        })

    except Exception as e:
        print(f"Hata: {e}")
        return jsonify({"error": str(e)}), 500



# Flask’a “/api/history URL’sine bir GET isteği gelirse aşağıdaki fonksiyonu çalıştır” der.
@app.route("/api/history")
def history(): # bu URL’ye gelen isteği işleyen fonksiyon. fonksiyonun döndürdüğü değer Flask tarafından HTTP cevabına çevrilir.
    conn = database.get_db_connection() # psycopg2 bağlantı fonksiyonu.

    if conn:  # Bağlantı varsa devam et, yoksa alt return çalışır. Bu kontrol programın çökmemesini sağlar.

            # fetch_historical_data fonksiyonu veritabanından son kayıtları çeker ve pandas DataFrame döndürür. Parametreler:   conn: veritabanı bağlantısı. limit=20: en son 20 kaydı çek diyoruz. (SQL içinde LIMIT %s olarak kullanılır.)
        df = database.fetch_historical_data(conn, limit=20)
        conn.close() # açılan veritabanı bağlantısını kapatı
        # Tarih formatını düzelt (string'e çevir)
        df["analiz_zamani"] = df["analiz_zamani"].astype(str) # dataFrame’deki analiz_zamani sütununu Python string tipine çeviriyor.

        return jsonify(df.to_dict(orient="records"))
    # df.to_dict(orient="records") --> DataFrame'i liste halinde sözlüklere dönüştürür:
    # orient="records": her satır bir dict olacak şekilde (frontend için en kullanışlı form).
    # jsonify(...) --> Flask util: Python veri yapısını JSON HTTP cevabı haline getirir ve Content-Type: application/json header'ını ekler.

    return jsonify([]) # Bağlantı alınamazsa boş liste JSON olarak dönülür:



# app.py dosyasına ekle (history fonksiyonunun altına):


# Flask’a şunu söyler: HTTP GET (varsayılan) ile sunucuya /api/history/stats yolundan bir istek gelirse, hemen altındaki history_stats() fonksiyonunu çalıştır.
# burada methods parametresi belirtilmediği için, dolayısıyla sadece GET istekleri kabul edilir.
@app.route("/api/history/stats")
def history_stats(): # Route tarafından çağrılan Python fonksiyonumuz.Flask, bu fonksiyonun döndürdüğü değeri HTTP cevabına çevirir (ör. jsonify(...), render_template(...), string, tuple (body, status_code), vs).

    conn = database.get_db_connection() # database modülündeki get_db_connection() fonksiyonunu çağırıp PostgreSQL bağlantı nesnesini (conn) alır. başarılıysa psycopg2 connection nesnesi döner

    if conn:
        stats = database.get_overall_statistics(conn) # database.py dosyamızdaki get_overall_statistics() fonksiyonu  veritabanındaki tüm analizlerin istatistiklerini toplar ve geri döndürür., conn parametresi ile çağrılıyor.Veritabanındaki analiz_gecmisi tablosuna SELECT SUM(...) gibi sorgular gönderir ve toplam metin, pozitif, negatif, nötr sayılarını hesaplar.
        # ne döndürü bir Python dict, örn: {'total': 1200, 'pos': 700, 'neg': 300, 'neu': 200}.
        conn.close() # açık veritabanı bağlantısını kapatır. kapatılmazsa bağlantılar birikir (connection leak) --> DB server limitine ulaşılabilir --> yeni bağlantılar reddedilir.
        return jsonify(stats)

    return jsonify({"total": 0, "pos": 0, "neg": 0, "neu": 0}) # stats Python objesini (sözlük) JSON cevap haline getirir ve HTTP cevabı olarak döndürür.if conn bloğuna girilmediğinde (yani conn yoksa , db bağlantısı alınamadığı durumda) burası çalışır.

# JSON formatında cevap döndüren Flask fonksiyonudur.Python sözlüğünü, listeleri, sayıları otomatik olarak ---> 1-JSON formatına dönüştürür , 2-HTTP cevabı haline getirir , 3-Content-Type header’ını otomatik ayarlar:
# jsonify Flask’ın içinde gelen bir fonksiyondur ve amacı Python verilerini (dict, liste vb.) otomatik olarak JSON formatına çevirip HTTP cevabı olarak göndermektir.


if __name__ == "__main__":
    app.run(debug=True, port=5000)


# debug = True flask debug modunu açar . kod değiştiğinde otomatik yeniden yükleyici
# host 127.0.0.1
