import pandas as pd
import psycopg2
import config



# bu fonksiyonumuz çağrıldığında veritabanı bağlantısı oluşturmaya çalışacak.
def get_db_connection():

    try:# hata (exception) çıkma ihtimaline karşı koruma bloğumuz.

        conn = psycopg2.connect(    # .connect PostgreSQL sunucusuna TCP/IP veya yerel soket üzerinden bağlanmanızı sağlayan fonksiyon bu fonksiyonumuz başarılı olursa conn (connection) adında bir nesne döndürür;
         # Parametrelerimiz (her biri bir bağlantı parametresidir):
            host=config.DB_HOST,  # veritabanı sunucumuzun adresi. örneğin "localhost"
            database=config.DB_NAME, # bağlanılacak veritabanının adı
            user=config.DB_USER, # veritabanı kullanıcı adı örneğin "postgres"
            password=config.DB_PASSWORD, # parolamız
            port=config.DB_PORT # PostgreSQL’in dinlediği TCP portu (varsayılan 5432). eğer sunucu farklı bir portta çalışıyorsa onu yazarız.
        )
        # conn nesnesi bir bağlantı” nesnesidir: üzerinde .cursor(), .commit(), .rollback(), .close() gibi metodlar vardır.

        print("✅ Veritabanı bağlantısı başarılı.")
        return conn  # fonksiyon, bağlantı nesnemizi döndürür. dönen conn ile sorgu çalıştırılır.


    except psycopg2.OperationalError as e: # try bloğunda psycopg2.OperationalError türünde bir hata oluşursa burası çalışır.OperationalError genellikle bağlantı aşamasındaki hataları ifade eder: sunucu çalışmıyor, host yanlış, port kapalı, kimlik doğrulama başarısız, ağ problemi vb. , as e kısmı hatayı e değişkenine atar; bu değişkenin içinden hata mesajı alınabilir.
        print(f"❌ Veritabanına bağlanılamadı: {e}")
        return None # bağlantı kurulamadığını belirtmek için None döndürüyoruz. Kodun diğer yerleri --> if not conn: kontrolü ile bu durumu yakalayabiliriz.


# sql komutu; IF NOT EXISTS eklendiğinde tablo zaten varsa yeni tablo oluşturmaya çalışmaz, hata fırlatmaz. Bu sayede uygulama her çalıştırıldığında tabloyu oluşturma denemesi yapabilir ve uygulama hata almaz.
# conn parametresi: önceki fonksiyonumuzdan dönen bağlantı nesnesimiz . conn bir psycopg2 bağlantı nesnesidir.
def create_table_if_not_exists(conn):
    # burada  analiz_gecmisi tablosunu yoksa oluşturur diyrouz.

    if not conn: return False # eğer conn None veya False benzeri bir şeyse (yani bağlantı yoksa), fonksiyon çalışmayı durdurur ve False döndürür. Böylece tablo oluşturma denemesi yapılmaz.

    create_table_query = """
    CREATE TABLE IF NOT EXISTS analiz_gecmisi (
        id SERIAL PRIMARY KEY,
        analiz_zamani TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        kaynak_tipi VARCHAR(50) NOT NULL,
        kaynak_detay VARCHAR(255) NOT NULL,
        kategori VARCHAR(100),
        toplam_metin INTEGER NOT NULL,
        pozitif_sayisi INTEGER DEFAULT 0,
        negatif_sayisi INTEGER DEFAULT 0,
        notr_sayisi INTEGER DEFAULT 0
    );
    """

# CREATE TABLE IF NOT EXISTS analiz_gecmisi (   -- CREATE TABLE — yeni bir tablo oluşturma komutu . IF NOT EXISTS — tablo zaten varsa hata vermez ; yalnızca yoksa oluşturur. Bu, tekrar tekrar uygulama başlatıldığında aynı tabloyu yeniden oluşturmaya çalıştığında hata oluşmasını engeller.
# id SERIAL PRIMARY KEY,       -- burada SERIAL — PostgreSQL’de otomatik artan tam sayı (integer) sütunu oluşturur. her yeni satır için otomatik artan bir değer üretir.
# analiz_zamani TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,    -- TIMESTAMP WITH TIME ZONE — tarih-saat bilgisini ve zaman dilimini saklar (örn. 2025-12-06 11:00:00+03). DEFAULT CURRENT_TIMESTAMP — eğer ekleme sırasında bu alan belirtilmezse otomatik olarak satırın eklenme zamanı girilir.
# kaynak_tipi VARCHAR(50) NOT NULL,  -- VARCHAR(50) — maksimum 50 karakter uzunluğunda metin.  NOT NULL — bu sütun boş bırakılamaz, zorunlu alan.
# Pozitif/negatif/notr sayıları için varsayılan değer 0. Yani ekleme sırasında belirtilmezse 0 olur.






    try:# buradaki sql aşamaları sırasında hata çıkma ihtimaline karşı blok başlatıldı.
# cursor nedir:
# Cursor veritabanına sorgu göndermek ve sonuçları almak için kullanılan nesnedir. cur.execute(sql) ile SQL çalıştırırsınız. cur.fetchone(), cur.fetchall() ile sonuçları alabilirsiniz. Cursor ayrıca parametreli sorgularda placeholder kullanmaya yarar.

# with bloğu içinde bir resource (burada cursor) kullanılır; with bloğu bitince resource otomatik kapatılır (cur.close() çağrılır).
# as cur ile with bloğu içinde cursor nesnesine cur ismiyle erişirsiniz.
# peki cur.execute(...) ne yapar --> verilen sql komutunu çalıştırır. Örnek: tablo oluşturma, INSERT, SELECT, UPDATE, DELETE vb. parametreli sorgularda cur.execute(sql, (param1, param2)) şeklinde kullanılır;
# peki conn.commit() ne yapar --> O anki transaction içindeki tüm değişiklikleri veritabanına kalıcı olarak yazar. INSERT, UPDATE, DELETE veya CREATE TABLE gibi işlemler commit() çağrılana kadar diğer bağlantılardan görünmeyebilir. commit() çağrılmazsa işlem rollback yapılabilir.
# O anki transaction içindeki henüz commit edilmemiş değişiklikleri iptal eder ve veritabanını değişikliklerden önceki tutarlı haline geri döndürür. Hata durumlarında veri bütünlüğünü korumak için kullanılır.

        with conn.cursor() as cur:
            cur.execute(create_table_query)
        conn.commit()  # veritabanına yapılan değişiklikleri (DDL veya DML) kalıcı hale getirir. PostgreSQL bağlantıları otomatik commit modunda değildir genelde; bu yüzden commit() çağrılmazsa değişiklikler geri alınır (connection kapandığında rollback yapılabilir).burada tablo oluşturma (DDL) commit edildi.


        print("✅ 'analiz_gecmisi' tablosu kontrol edildi/oluşturuldu.")
        return True # başarı durumunu belirtir.


    except Exception as e:
        print(f"❌ Tablo oluşturulurken/kontrol edilirken hata: {e}")

        conn.rollback()  # Hata olursa işlemi geri al , O anki transaction içindeki henüz commit edilmemiş değişiklikleri iptal eder ve veritabanını değişikliklerden önceki tutarlı haline geri döndürür. Hata durumlarında veri bütünlüğünü korumak için kullanılır.

        return False # fonksiyonun başarısız olduğunu belirtir.

#                         kısaca sonuç olarak
# psycopg2.connect(...) --> veritabanı bağlantısı açar --> dönen conn ile işlem yaparız.
# conn.cursor() --> SQL çalıştırmak için cursor alınır.
# with conn.cursor() as cur: --> cursor yönetimi otomatik (kapanır).
# cur.execute(sql) --> SQL çalıştırır.
# conn.commit() --> değişiklikleri kaydeder.
# conn.rollback() --> hata durumunda değişiklikleri geri alır.
# CREATE TABLE IF NOT EXISTS ... --> tablo yoksa oluşturur, varsa hata vermez.
# OperationalError --> bağlantı/ağ/kimlik doğrulama gibi operasyonel bağlantı hataları.









# conn PostgreSQL bağlantı nesnemiz (psycopg2.connect ile oluşturulur). veritabanına komut göndermek için gerekir.
# kaynak_tipi Metinlerin nereden geldiği: (Twitter, Haber Siteleri, Reddit, YouTube...).
# kaynak_detay Detay bilgi: – Twitter’da kullanıcı adı, – YouTube’da video ID,  – Haber sitesinde site adı gibi.
# kategori Sadece haber sitelerinde kategori tutulur (spor, ekonomi...).  Diğerlerde None olur.
# bir diğer parametre counts Python sözlüğü (dict) şeklindedir: {"positive": 5, "negative": 3, "neutral": 2}

def insert_analysis_result(conn, kaynak_tipi, kaynak_detay, kategori, counts):
    """ Analiz sonuçlarını veritabanına ekliyoruz. """
    if not conn: return False # conn boşsa (None ise) veritabanına bağlanılamamıştır. Bu durumda ekleme yapılamaz --> False döner.


    # Üç tırnak (""") ---> python’da çok satırlı string anlamına gelir,bu bir string dir,sql komutu içeren bir string..   a = "selam   a = """selam"""  a = '''selam'''  bunların hepsi stringdir
    insert_query = """
    INSERT INTO analiz_gecmisi 
        (kaynak_tipi, kaynak_detay, kategori, toplam_metin, pozitif_sayisi, negatif_sayisi, notr_sayisi)
    VALUES (%s, %s, %s, %s, %s, %s, %s);
    """
    # %s --> "Buraya bir değer gelecek" demektir.  %s = SQL değeri için yer tutucu  , Python bu %s’leri otomatik olarak temizler, özel karakterleri etkisiz hale getirir ve verileri güvenli şekilde ekler.
    # veritabanına şu şekilde değerleri sonradan göndeririz (kaynak, detay, kategori, toplam, pozitif, negatif, notr))


    # toplam metin sayısı hesaplama
    toplam = sum(counts.values()) # counts.values() sözlükteki sayı değerlerini verir. Ör: [5, 3, 2] , sum() bu listeyi toplar --> 5+3+2 = 10

    # Pozitif, Negatif, Nötr sayıları alma
    pozitif = counts.get('positive', 0) # .get(key, default) ---> python dict (sözlük) metodudur. Anahtar varsa ---> değerini döner  Anahtar yoksa ---> default döner , Öreğin --> counts.get("positive", 0)
    negatif = counts.get('negative', 0) # eğer "negative" yoksa hata vermez, 0 döner. bu güvenli bir yöntemdir.
    notr = counts.get('neutral', 0)

    # Sadece haber sitelerinde kategori vardır --> diğerlerinde None yazılır.
    kategori_value = kategori if kaynak_tipi == "Haber Siteleri" else None

    # Kaynak detayı (site_key, query veya video_id) , Direkt gelen değeri kullanır.
    detay_value = kaynak_detay

    # sql’e gönderilecek tuple , bu tuple %s parametreleri ile sırasıyla eşleşir.
    values = (kaynak_tipi, detay_value, kategori_value, toplam, pozitif, negatif, notr)

    # veritabanına gönderme işlemi
    try:
        # with conn.cursor() as cur: bu ne demek ---> bu şu demektir:  1.bir cursor oluştur (cur) , 2.işini yap  , 3.Otomatik kapat (kapatmayı sen düşünme) with yapısı otomatik temizleme yapar. bunu yapmazsan kapatıp kapatmadığını unutur.

        with conn.cursor() as cur: # cursor açar --> iş bitince otomatik kapatır. cursor = veritabanına komut gönderen, cevabı alan araçtır . connection üzerinden oluşturulur , sql sorgularını çalıştırır , sonuç döndürür (fetchone, fetchall) , işlem bittikten sonra kapanır.
            cur.execute(insert_query, values) # SQL komutunu çalıştırır.  cur.execute(query, values) nedir ---> bu komut: SQL komutunu çalıştırır values içindeki tuple'ı alıp %s leri sırayla doldurur.

     #    peki burası nasıl işliyor?

# INSERT INTO analiz_gecmisi
# (kaynak_tipi, kaynak_detay, kategori, toplam_metin, pozitif_sayisi, negatif_sayisi, notr_sayisi)
# VALUES (%s, %s, %s, %s, %s, %s, %s);

# Bu bir şablondur.

# Bu şablonun yerini values tuple’ı doldurur:

# values = (
#    kaynak_tipi,     # -> 1. %s
#    detay_value,     # -> 2. %s
#    kategori_value,  # -> 3. %s
#    toplam,          # -> 4. %s
#    pozitif,         # -> 5. %s
#    negatif,         # -> 6. %s
#    notr             # -> 7. %s
# )

# Sıra = sıra
# Bu eşleşmeyi psycopg2 otomatik yapar.


        conn.commit() # veritabanında yapılan değişiklikleri kalıcı olarak kaydeder.Commit olmazsa: INSERT yapılmış olur ama kaydedilmez , bağlantı kapanınca tüm değişiklikler kaybolur

        print(f"✅ Analiz sonucu veritabanına eklendi: {kaynak_tipi} - {detay_value}")
        return True

    # Hata yakalama
    except Exception as e:
        print(f"❌ Veritabanına eklerken hata: {e}")

        conn.rollback()# bir hata olduğunda O işlem sırasında yapılan tüm değişiklikler geri alınır.bu veritabanı güvenliği için çok önemlidir.

        return False


# --- ileride tarihsel veri çekmek için fonksiyonumuz ---
# bu parametre psycopg2.connect() ile oluşturduğun veritabanı bağlantısıdır.
# conn --> PostgreSQL ile açık bağlantı nesnesidir bu olmadan veritabanıyla konuşamazsın.
# limit=100 Varsayılan parametre. Yani kullanıcı bir şey göndermezse limit otomatik 100 olarak çalışır.

def fetch_historical_data(conn, limit=100):
    """ veritabanından son analiz kayıtlarını çekiyoruz """
    if not conn: return pd.DataFrame()  # if not conn bağlantı başarısızsa (conn = None) hata çıkmasın diye kontrol eder.boş DataFrame dön
                                            # pd.DataFrame() boş DataFrame oluşturması , Boş tablo döner ---> uygulama çökmez.

    # bu sql komutu: SELECT * Tüm sütunları seç.   FROM analiz_gecmisi   Tablonun adı. ORDER BY analiz_zamani DESC  Zaman sütununa göre yeni --> eski sıralama.   DESC = descending (azalan)
    # LIMIT %s  Kaç tane kayıt istendiğini belirler. Bu %s bir SQL parametresi yeridir.
    query = "SELECT * FROM analiz_gecmisi ORDER BY analiz_zamani DESC LIMIT %s;"

    try:
        # bu en önemli kısım(pd.read_sql_query). sql sorgusu çalıştırır --> sonucu otomatik DataFrame’e dönüştürür.
        # Parametreler : query sql komutumuz (SELECT olan) , conn PostgreSQL bağlantı nesnesi psycopg2.connect() ile açmış olduğumuz.params=(limit,)
# burada parametre tuple olarak gönderilir.  %s yer tutucusu LIMIT için.  (limit,) = tek elemanlı tuple
        # Neden tuple içinde veriyoruz --> Çünkü psycopg2 parametreleri tuple/list içinde ister. Neden virgül var ---> Python’da (limit) = sadece parantez , bu şekilde ise (limit,) = tuple dır
        # mesela (5) --->  integer (sadece parantez)   ,   (5,)  ---> tuple     -  sql parametreleri tuple olmalı --> o yüzden (limit,) kullanıyoruz.
        df = pd.read_sql_query(query, conn, params=(limit,))
        print(f"✅ Veritabanından {len(df)} kayıt çekildi.")
        return df

    except Exception as e:
        print(f"❌ Veritabanından okurken hata: {e}")
        return pd.DataFrame()









# conn burada postgresql bağlantısıdır. psycopg2.connect() ile oluşturmuştuk.bu bağlantı olmadan SQL çalışmaz.
def get_overall_statistics(conn):
    """ burada tüm geçmiş analizlerin toplam sayılarını çeker. """
    if not conn: return None # Eğer conn None ya da bozuk bir nesneyse Fonksiyon hiçbir şey yapmadan None döner.

    # Cursor, PostgreSQL üzerinde komut gönderen ve sonuç alan bir ara nesnedir.Kısaca:  SQL komutunu çalıştırır   Sonuçları alır  Bağlantıyla iletişimi sağlar
    # Neden with kullanıyoruz?  İş bittikten sonra cursor otomatik kapanır.  Mem leak / açık bağlantı kalmaz.
    try:
        with conn.cursor() as cur:
            # SQL'in SUM fonksiyonu ile tüm sütunları topluyoruz bu bir çok satırlı stringdir. yorum satırı değildir.  Python """ ... """ içindekileri string kabul eder
            query = """
                SELECT 
                    SUM(toplam_metin), 
                    SUM(pozitif_sayisi), 
                    SUM(negatif_sayisi), 
                    SUM(notr_sayisi) 
                FROM analiz_gecmisi;
            """
          # SUM(toplam_metin)	Kaç metin analiz edilmiş toplam  SUM(pozitif_sayisi)	Tüm pozitif adetlerin toplamı  SUM(negatif_sayisi)	Tüm negatif adetlerin toplamı  SUM(notr_sayisi)	Tüm nötr adetlerin toplamı

            # SORGUNUN ÇALIŞTIRILMASI execute()  SQL komutunu veritabanına gönderir.  Çalıştırır. Sonuçları cursor’a yükler.
            cur.execute(query)
            result = cur.fetchone()  # (toplam, pos, neg, neu) şeklinde bir tuple döner

            #   fetchone() nedir
            #    Son SQL sonucundan 1 satır getirir.
            #   Bu satır bir tuple olarak döner.
            #   Örnek:
            #   Tabloda 10 kayıt varsa

            #    (140, 70, 40, 30)
            #    gibi bir sonuç döner.
            #    Bu tuple şu anlama gelir:

            #    result[0] = toplam_metin
            #    result[1] = pozitif
            #    result[2] = negatif
            #    result[3] = nötr
                


            # Eğer veritabanı boşsa None dönebilir, kontrol edelim
            if result[0] is None:
                return {'total': 0, 'pos': 0, 'neg': 0, 'neu': 0}
            # Eğer tablo boşsa (hiç kayıt yoksa)  sql şöyle döner: (None, None, None, None)

            # Bu durumda:  0 kayıt vardır  Total pozitif/negatif/nötr = 0 olsun diye  bunu döndürür return {'total': 0, 'pos': 0, 'neg': 0, 'neu': 0}
            # Burada tuple parçalanıp dictionary olarak döndürülür.

            return {
                'total': result[0],
                'pos': result[1],
                'neg': result[2],
                'neu': result[3]
            }


    except Exception as e:
        print(f"İstatistik çekme hatası: {e}")
        return None