import tweepy  # Python'un Twitter ile konuşmasını sağlayan kütüphanemiz.biz python yazıyoruz, o bunu twitter'ın anlayacağı api diline çeviriyor.
import pandas as pd
import config # api anahtarlarını sakladığımız dosya


import feedparser           # RSS okumak için
import requests             # Web isteği göndermek için



from googleapiclient.discovery import build #Bu satır, Google’ın resmi Python API istemcisinden (google-api-python-client) build fonksiyonunu içeri aktarır.build youtube api bağlantısı kurar, api isteklerini yapmanı sağlar
# build Nedir? build Google api’lerine bağlanmak için kullanılan bir istek oluşturucu (service builder) fonksiyonudur.
# Bu fonksiyon: YouTube API’ye bağlanmanı API anahtarını kullanmanı videos(), commentThreads(), search() gibi endpoint’lere erişmeni API istekleri yapmanı sağlar.
# mesela biz aşağıda oluşturduk , bu kod: youtube isminde bir servis nesnesi oluşturur bu nesneyle youtube üzerinde istekler yapılabilir
# youtube = build("youtube", "v3", developerKey=config.YOUTUBE_API_KEY)



from googleapiclient.errors import HttpError #Google API istemcisinin hata sınıfı HttpErrorı içeri aktarır.
# HttpError Nedir ? --> youtube api isteğin başarısız olursa Google tarafından fırlatılan bir hatadır.
# Örnek hata durumları: api key yanlış --> 401  ,  Kota doldu --> 403  , Video bulunamadı --> 404  , Yorumlar kapalı --> 403  , Google sunucu hatası --> 500  Bu hataları özel olarak yakalayabiliyoruz:


import re # Regex (video id ayıklamak için), re --> “regular expressions” Bu kütüphane: metin arama , metin ayıklama (extract) , desen eşleme (pattern matching) , işleri yapmak için kullanılır. youtube URL’den video id çekmek için kullandık.



# --- Tweepy Client ---
try:
    client = tweepy.Client(bearer_token=config.TWITTER_BEARER_TOKEN) # client değişkeni ile twitter'ın kapısını çalıyoruz.client aslında bizim nesnemiz
    # bearer_token: kapıyı açmak için kullandığımız "giriş kartımız". bu kart, sadece halka açık verileri (hashtag arama gibi) okumamıza izin veriyor.
    print("✅ Tweepy Client (Bearer Token ile) başarıyla başlatıldı.")


except Exception as e:
    print(f"❌ Tweepy Client başlatılırken HATA: {e}")
    client = None
# try...except: burası bir kontroldür,önlemidir. eğer config.py dosyamızda anahtar eksikse veya internet yoksa programın tamamen çökmesini engelliyor. hata varsa client değişkenini None (boş) yapar.




# --- Tweet Çekme Fonksiyonlarımız ---



# Girilen Twitter kullanıcı adına ait tweetleri çeker.
def _fetch_tweets_by_user(username, count=config.TWITTER_MAX_RESULTS):
    # burada username hangi kullanıcının tweetleri çekilecek.
    # count kaç tweet çekilecek (varsayılan değerimiz ---> config.TWITTER_MAX_RESULTS config dosyasındaki değer).


    # client nesnesi yok ise,twitter api client'ı yoksa, yani twitter’a bağlanamıyorsak — fonksiyon boş sonuç döndürür . döndürdüğümüz DataFrame'in iki sütunu vardır: text ve link.
    if not client: return pd.DataFrame(columns=['text', 'link'])

    # if client is None:
        # return pd.DataFrame(columns=['text', 'link'])


    # burası kullanıcı aranmasının – try/except yapısı
    user_response = None
    try:

        print(f"Kullanıcı aranıyor: {username}")
        # kullanıcıyı bul (ID'sini almak için) , çünkü tweet çekebilmek için önce user_id gerekir.
        user_response = client.get_user(username=username)  # client.get_user() ---> twitter kullanıcı bilgilerini döndürür.


    # rate limit hatası yakalama ---> twitter api aynı anda çok fazla istek yapılırsa 429 TooManyRequests döndürür.
    except tweepy.errors.TooManyRequests:


        print("❌ Rate limit (Kullanıcı Arama).")
        return pd.DataFrame(columns=['text', 'link']) # Fonksiyon boş bir DataFrame döndürür. sütunları text ve link dir

    # burasıda diğer tüm hataları yakalamak için ---> api bağlantı hatası, internet kopması, yanlış kullanıcı adı gibi türevleri hatalar için
    except Exception as e:
        print(f"❌ Kullanıcı aranırken HATA: {e}")
        return pd.DataFrame(columns=['text', 'link']) # # Fonksiyon boş bir DataFrame döndürür.sütunları text ve link dir


    # Kullanıcı bulunamadı ise bunun kontrolünü yapıyoruz
    if not user_response or not user_response.data: # twitter api’ye kullanıcı adıyla sorgu gönderir , karşılık olarak bir "response" (yanıt) objesi döner --> bu dönen obje user_response içine kaydedilir.

# user_response genelde şöyle bir yapıdadır yani içinde data --> kullanıcı bilgileri (ID, isim, kullanıcı adı…) , errors ---> kullanıcı bulunamadıysa vb. , meta → ek bilgiler

    #    user_response = {
    #        data: {...Kullanıcı bilgileri...},
    #        errors: [...hatalar...],
    #        meta: {...ek bilgiler...}
    #    }

# peki user_response.data nedir , burası kullanıcının gerçek bilgilerini taşır. ---> user_response.data.id , user_response.data.name , user_response.data.username ---- eğer kullanıcı bulunamazsa user_response.data = None olur.
# işte bu yüzden not user_response ---> api çağrısı başarısız olduysa ve not user_response.data kullanıcı bulunmadıysa (data = None gelir).

        print(f"❌ Kullanıcı '{username}' bulunamadı.")
        return pd.DataFrame(columns=['text', 'link']) # fonksiyon boş DataFrame döndürür.

    user_id = user_response.data.id # işte burada kullanıcının id değeri alınır. tweet çekerken id kullanılır (username değil).
    username_for_link = username # username_for_link tweet linki oluşturabilmek için saklıyoruz değişkende tutuyoruz.
    print(f"✅ Kullanıcı bulundu: ID={user_id}, Ad={username_for_link}. Tweetler çekiliyor...")

   # burası tweetleri çekme aşaması
    try:
        # Kullanıcının tweetlerini çekme işlemi ---> bu fonksiyon kullanıcının tweetlerini alır.
        # Parametreler:  id=user_id --> tweetleri hangi kullanıcıdan çekeceğiz , max_results=count → kaç adet tweet istiyoruz , exclude=['retweets','replies'] --> sadece orijinal tweetler , tweet_fields=['id','text'] --> tweet id ve metni gelsin

        response = client.get_users_tweets(
            id=user_id,
            max_results=count,
            exclude=['retweets', 'replies'],  # retweet ve yanıtları(replies) hariç tut diyoruz
            tweet_fields=['id', 'text']
        )

        # tweet listesine dönüştürme
        data = []
        if response and response.data: # eğer tweet varsa:
            print(f"✅ {len(response.data)} adet tweet verisi bulundu.")
            for t in response.data: # her tweet için , tweet metnini (t.text) , tweet linkini (https://twitter.com/username/status/id) ---> bu iki değeri bir dictionary içine koyar.
                # link oluşturma
                link = f"https://twitter.com/{username_for_link}/status/{t.id}"
                data.append({'text': t.text, 'link': link})

        else:
            print("❌ Kullanıcı tweet yanıtı 'data' içermiyor veya boş.")

        return pd.DataFrame(data, columns=['text', 'link']) # DataFrame döndürme ,Tweet metinleri --> text , tweet url'leri --> link , bu yapı Streamlit’te tablo şeklinde gösterilebilir.

    except tweepy.errors.TooManyRequests: # tweet çekerken rate limit hatası --> tweet çekme sırasında limit aşılırsa


        print("❌ Rate limit (Tweet Çekme).")
        return pd.DataFrame(columns=['text', 'link'])

    # ve tüm diğer hatalar için
    except Exception as e:

        print(f"❌ Kullanıcı tweetleri çekilirken HATA: {e}")
        return pd.DataFrame(columns=['text', 'link'])

# özet ile bu yazdığımız fonksiyon ile ne yaptık
# 1-kullanıcıyı api ile arar , 2-kullanıcı id’sini alır , 3-rate limit ve api hatalarını yakalar , 4-kullanıcının tweetlerini çeker
# 5-retweet ve reply’ları hariç tutar , 6-tweet metinlerini ve linklerini bir listeye kaydeder , 7-listeyi DataFrame olarak döner








def _fetch_tweets_by_hashtag(hashtag_or_query, count=config.TWITTER_MAX_RESULTS): # Parametrelerimiz hashtag_or_query (kullanıcının yazdığı kelime) ve count (kaç tweet çekileceği).
    if not client: return pd.DataFrame(columns=['text', 'link'])

    # if not client:
    #   return pd.DataFrame(columns=['text', 'link'])


    query_text = ""

    if " " in hashtag_or_query:  # Eğer kullanıcı  mesela "duygu analizi" gibi boşluklu bir şey yazdıysa, twitter bunu tek bir kalıp olarak arasın diye tırnak içine alıyoruz ("duygu analizi").
        query_text = f'"{hashtag_or_query}" -is:retweet lang:tr'  # -is:retweet: bu kısım çok önemli . "bana sadece orijinal yazıları getir, RT (Retweet) edilmiş kopyaları getirme" komutudur. ve "lang:tr" ise Sadece Türkçe tweetleri getir.


    elif hashtag_or_query.startswith('#'): # eğer kullanıcı zaten #teknofest yazdıysa, fazladan # ekleyip ##teknofest yapmamak için önce temizliyoruz, sonra tek # ekliyoruz.
        clean_hashtag = hashtag_or_query.lstrip('#')
        query_text = f"#{clean_hashtag} -is:retweet lang:tr"


    else: # eğer kullanıcı düz teknofest yazdıysa, başına # ekliyoruz.
        query_text = f"#{hashtag_or_query} -is:retweet lang:tr"  # "-is:retweet ---> Bana sadece orijinal yazıları getir, RT (Retweet) edilmiş kopyaları getirme"  -- lang:tr Sadece Türkçe tweetleri getir.

    print(f"Hashtag/Kelime aranıyor: {query_text}")



    try:
        # twitter'a soru sorma (API İsteğimiz)
        response = client.search_recent_tweets(  # burada client twitter api ile bağlantıyı sağlayan nesne. search_recent_tweets() Son atılmış tweetleri arayan fonksiyon. dönen değer response(cevap,sonuç anlamında) değişkenine kaydedilir.
            query=query_text, # burada twitter’da ne aramak istiyorsak onu yazarız. örneğin "duygu analizi" ---> bu durumda api "duygu analizi" içeren tweetleri arar.
            max_results=count, # en fazla kaç tweet çekilecek
            expansions='author_id', # tweeti atan kullanıcının kimliğini (user id) de getir anlamına gelir.normalde tweet objesinde kullanıcı bilgisi olmaz.author_id kullanılırsa api ayrıca kullanıcı bilgilerini de gönderir.
            user_fields='username', # twitter api tweet içinde normalde kullanıcı bilgisi göndermez.biz ekstra olarak “şu kullanıcı alanlarını da gönder” diyoruz.
            tweet_fields=['id', 'text'] # tweet'in sadece ID'sini ve metnini ver biz bu alanları istiyoruz, gerisi gerekli değil.mesela konum vb.gibi.
        )

        # veriyi birleştirme kısmı
        users_lookup = {} # users_lookup , kullanıcı araması boş bir sözlük ve bu içinde kullanıcıID → kullanıcıAdı  şeklinde veri tutacak. "12345": "ronaldo" gibi
        if response.includes and 'users' in response.includes: # includes içermek demek response.includes --> varsa gibi bir anlamı var. response.includes varsa → yani api ek bir bilgi göndermişse. users anahtarı varsa → yani api tweeti yazan kullanıcı bilgilerini gerçekten göndermiş ise.
            users_lookup = {u.id: u.username for u in response.includes['users']} # bu satır bir “dictionary comprehension” yani kısa sözlük üretme yöntemidir  .  response.includes['users'] → api’nin döndürdüğü kullanıcı listesi
            # Her kullanıcı (u) için:
            # u.id → kullanıcının benzersiz id’si (örn: "44196397")
            # u.username → kullanıcı adı (örn: "ronaldo")

            # boyle bir sozluk elde edilir
            #   {
            #       "44196397": "ronaldo",
            #       "12": "alex"
            #   }
       # Bu sözlük sayesinde tweeti atan kişinin adını bulabiliriz.


# ---> users_lookup = {u.id: u.username for u in response.includes['users']} bu satırın normal,kısaltma olmayan açık yazılmış hali bu şekildedir

        #           users_lookup = {}  # Boş bir sözlük oluştur

        #           for u in response.includes['users']:      api'nin gönderdiği her kullanıcı için döngüye gir
        #                user_id = u.id                       kullanıcının ID'sini al
        #                username = u.username                kullanıcının kullanıcı adını al

        #                users_lookup[user_id] = username     sözlüğe ekle (ID → username)



        data = [] # boş bir liste oluşturuyoruz her tweet için {text, link} şeklinde sözlük ekleyeceğiz.
        if response and response.data: # burada response varsa (None değilse) , response.data boş değilse , bu iki koşul sağlanırsa tweetler vardır.

            print(f"✅ {len(response.data)} adet tweet verisi bulundu.") # Kaç tane tweet bulunduğunu yazdırır
            for t in response.data:# her bir tweet için döngüye giriyoruz t → tek bir tweet objesi.
                username = users_lookup.get(t.author_id, 'bilinmeyen') # tweeti atan kişinin adını buluyoruz , t.author_id → tweetin yazarı kim --- users_lookup sözlüğünden ID ile username alıyoruz. eğer kullanıcı bulunamazsa 'bilinmeyen' yazıyoruz (hata olmaması için).
                link = f"https://twitter.com/{username}/status/{t.id}" # tweet linkini oluşturuyoruz . Twitter link formatı böyle --> https://twitter.com/<kullanıcı>/status/<tweetID> ---> mesela bizde https://twitter.com/ronaldo/status/1234567890
                data.append({'text': t.text, 'link': link}) # listeye tweet metni ve linkini ekliyoruz. şu şekil ---> {'text': 'tweetin metni', 'link': 'https://twitter...'}  ---> bu listemiz DataFrame’e dönüşecek.

        else:
            print("❌ Hashtag yanıtı 'data' içermiyor veya boş.") # response.data yoksa uyarı veriyoruz.

        return pd.DataFrame(data, columns=['text', 'link']) # sonuç olarak iki sütunlu bir DataFrame döner bir sütun "text" diğer sütun yanında "link"


    # --- BURASI HATA YAKALAMA BLOKLARIMIZ ---

    except tweepy.errors.TooManyRequests: # twitter bizi engellediyse (çok istek attıysak) --- rate limit'e takılınca buraya düşer.


        print("❌ Rate limit (Hashtag Arama).") # konsola uyarı mesajı yazdırır.
        return pd.DataFrame(columns=['text', 'link']) # Boş DataFrame gönderir.

    # Genel Hatalarımız , işte internet yoksa veya client bozuksa yada response yapısı değiştiyse ---> Hatanın detayını yazdırıp boş DataFrame döner.
    except Exception as e:
        print(f"❌ Hashtag tweetleri çekilirken HATA: {e}") # Hatanın detayı
        return pd.DataFrame(columns=['text', 'link']) # boş DataFrame döner


# --- Ana Çağrı Fonksiyonumuz ---

# Bu fonksiyon twitter’dan tweet çekmek için ortak bir kapımız (ana fonksiyonumuz).arama tipine göre (hashtag veya username) doğru fonksiyonu çağırır.
def fetch_tweets(query, search_type='hashtag', count=config.TWITTER_MAX_RESULTS): # query ---> aranan metin veya hashtag (#python gibi) , search_type="hashtag" veya "username" , count=config.TWITTER_MAX_RESULTS → çekilecek maksimum tweet sayısı
    print(f"--- Twitter API İsteği Başlatılıyor ---")
    # df = pd.DataFrame(columns=['text', 'link']) # boş bir DataFrame oluşturuyor -- eğer ileride bir hata olursa en azından boş bir DataFrame döndürücek bize. sütunlarımız text ---> tweet metni , link ---> tweet linki

    if search_type == 'hashtag': # arama türü hashtag mi kontrol ediyor , eğer arama tipi hashtag ise, hashtag arama fonksiyonunu çağırır(_fetch_tweets_by_hashtag)
        return _fetch_tweets_by_hashtag(query, count)

    elif search_type == 'username': # arama türü username mi kontrol ediyor , eğer arama tipi username ise, username arama fonksiyonunu çağırır(_fetch_tweets_by_user)
        return _fetch_tweets_by_user(query, count)

    else: # Eğer search_type geçerli değil ise uyarı verir
        print(f"⚠️ Geçersiz arama tipi: {search_type}")
        return pd.DataFrame(columns=['text', 'link'])



            # bu fonksiyon(_fetch_tweets_by_hashtag):

                    # twitter’a api isteği gönderir
                    # tweetleri toplar
                    # kullanıcı isimlerini çıkarır
                    # linkleri oluşturur
                    # DataFrame döndürür

            # Sonuç olarak df artık gerçek tweetlerle dolmuş olur.








# ==========================================
# BÖLÜM 2: HABER SİTELERİ (RSS) FONKSİYONLARI
# ==========================================



# web siteleri, dışarıdan gelen isteklere bakar , eğer isteği bir bot yaptıysa çoğu site engeller.
# header tarayıcı gibi görünmek ne demektarayıcı gibi görünmek için gerekli başlıklarımız , bunlar tarayıcı gibi görünmek için HTTP header’ları (çünkü bazı siteler botları engeller)
# bazı siteler botlardan gelen istekleri engeller.biz de kendimizi gerçek bir tarayıcıymış gibi gösteriyoruz.
# Parametrelerimiz User-Agent --> Tarayıcının kimliği , burada Chrome 118 , Windows 10 gibi görünüyor. Accept --> tarayıcının kabul ettiği içerik türleri.“HTML, XML, resim, tüm veri türleri olabilir” gibi.


BROWSER_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
}

# burada User-Agent nedir --> tarayıcının kimlik bilgisi , Chrome açtığında Chrome kendini siteye şu şekilde tanıtır  User-Agent: Mozilla/5.0 ... , biz de bu kodda kendimizi gerçek bir tarayıcıymış gibi gösteriyoruz , bu yüzden siteler bizi engellemiyor.








# burada fonksiyonumuz parametreleri --> site_key config’deki haber sitesinin anahtar adı ,sitenin adı yani  (örn: "bbc", "trthaber") , category_key --> site içerisindeki kategori (örn: "teknoloji", "spor") , count	kaç haber çekileceği (default değerimiz kullanıcıya bağlı değil --> config.NEWS_MAX_RESULTS)
def fetch_news_headlines(site_key, category_key, count=config.NEWS_MAX_RESULTS):
    """
    Belirtilen sitenin belirtilen kategorisindeki RSS beslemesini çeker.
    """
    # config kontrolümüz , girilen site config.NEWS_SITES içinde var mı kontrol edilir , site içinde kategori var mı bakılır.eğer yok ise hata verir boş DataFrame döner --> çökmez , kullanıcı yanlış site adı girerse hata verir mesela bbc --> yerine bbcc gibi
    if site_key not in config.NEWS_SITES or category_key not in config.NEWS_SITES[site_key]:

        print(f"Hata: '{site_key}' sitesinde '{category_key}' kategorisi bulunamadı.")
        return pd.DataFrame(columns=['text', 'link'])

    # RSS linkini çekme , RSS url sini alma --> RSS bir XML formatıdır.
    # rss nedir dersek , haber sitelerinin içeriklerini XML formatında yayınladığı yapıdır. örneğin <title>Haber Başlığı</title> , <link>https://....</link> --> biz bu XML’i parse edip başlıkları çekiyoruz.
    feed_url = config.NEWS_SITES[site_key][category_key] # config içerisindeki RSS URL’sine erişiyoruz.mesela https://www.bbc.com/news/rss.xml gibi
    print(f"RSS beslemesi okunuyor: {feed_url}")

    try:
        # 1. Requests ile veriyi çek (Tarayıcı taklidi yaparak)
        response = requests.get(feed_url, headers=BROWSER_HEADERS, timeout=10) # burada feed_url --> RSS linki , headers=BROWSER_HEADERS --> tarayıcı gibi görünmesini sağlar , timeout=10 --> 10 saniye içinde yanıt gelmezse hata ver
        # mesela burada request kütüphanesi Python’un internetten veri çekmek için kullanılan paketidir --> parametrelerine bakalım --> feed_url çekilecek adres , headers=BROWSER_HEADERS --> tarayıcı gibi görünmek için , timeout=10 --> 10 saniyede yanıt gelmezse iptal


        # burası HTTP Hata Kontrolü peki ne işe yarar --> 404, 500, 403 gibi hataları yakalar.
        response.raise_for_status()  # hata varsa durdur (404, 500 vs.) , HTTP hata kodu (404, 500, 403) varsa programı durdurur , böylece yanlış veri işlenmez.

        # 2. gelen veriyi feedparser ile işle , veriyi RSS formatında çözümleme
        feed = feedparser.parse(response.content)  # ne yapıyor gelen XML RSS datasını Python tarafından okunabilir hale dönüştürüyor, feed.entries haber listesi demektir.

        # burada feedparser kullanmışız feedparser RSS formatındaki XML’i okuyup Python objelerine çeviren bir kütüphane.

        # mesela:
        # feed.entries = haberlerin listesi
        # feed.entries[0].title = ilk haber başlığı
        # feed.entries[0].link = ilk haber linki
        # ----> bu sebepten feedparser kullanıyoruz. requests XML’i sadece döndürür, işlemez.


        # Hata kontrolü (Bozo bit)
        if feed.bozo:
            print(f"Uyarı: RSS okurken sorun oluştu (Bozo): {feed.bozo_exception}")

        # feed bozo --> RSS dosyası hatalıysa true olur.burada “Bozo” kelimesi "problemli RSS" anlamında feedparser geliştirenlerin verdiği bir isim.
        # örneğin eksik XML tag , hatalı karakterler ---> RSS bozuk olsa bile işlem durmaz, sadece uyarı verilir.




        # haberleri listeye ekleme
        data_list = []

        # entries[:count] --> listenin ilk count kadar elemanını al demektir.türü listedir
        # İstenilen sayı kadar haberi al , burada kullandığımız [:count] nedir bu bir slicing (dilimleme) dir.
        for entry in feed.entries[:count]: # ilk count haber alıyoruz  mesela count = 5 --> ilk 5 haber , feed.entries RSS içindeki haberlerin listesi demektir mesela RSS içinde 10 tane haber olsun --> feed.entries = [entry1,entry2,entry3,....] .entries --> çoklu haber , her bir eleman bir "entry" (haber) objesidir.
        # burada entry, RSS içindeki tek bir haber demektir , şunları içerir entry.title --> haber başlığı , entry.link --> haber linki , entry.summary --> haber özeti , entry.published --> tarih

            if 'title' in entry and 'link' in entry: # entry’nin gerçekten başlık + link içerdiğini kontrol eder. ne yapar haber başlığı ve linki varsa listeye ekler.her eleman bir sözlüktür ---> {"text": "Haber başlığı", "link": "https://...."} gibi
                data_list.append({'text': entry.title, 'link': entry.link})

        if not data_list: # eğer data_list boşsa buda şu demek ---> eğer RSS içinden bir tane bile haber çekilememiş ise
            print(f"Uyarı: Beslemeden hiç haber başlığı bulunamadı.")

        return pd.DataFrame(data_list, columns=['text', 'link']) # columns=['text', 'link'] , birinci sütun adı --> text , ikinci sütun adı --> link , burası DataFrame’e dönüştürme

    except Exception as e: # üstteki kodlarda herhangi bir hata olursa , Konsola yazar , streamlit ekranda gösterir , fonksiyon çökmez, boş tablo döndürür.
        print(f"RSS beslemesi işlenirken bir hata oluştu: {e}")

        return pd.DataFrame(columns=['text', 'link'])






# ==========================================
# BÖLÜM 3: YOUTUBE FONKSİYONLARI
# ==========================================

# fonksiyon adında da görüldüğü gibi fonksiyon bir argüman alır -->  url . ama kullanıcının girdiği şey bir URL ya da doğrudan video ID'si olabilir.
def get_video_id_from_url(url):
    """ YouTube URL'sinden video ID'sini çıkarır. Fonksiyon tek bir işi yapacak — parametre olarak verilen değerden YouTube video ID'sini çıkarmak."""
    if not isinstance(url, str): return None # Güvenlik kontrolü girilen url string değilse (None, int, list vs.) fonksiyon None döndürür.

    '''
        burada isinstance(obj, type) ne yapar
        isinstance(url, str) ifadesi, url değişkeninin gerçekten bir string (str) olup olmadığını kontrol ediyor.
        isinstance bir Python yerleşik fonksiyonudur ve tip kontrolü için kullanılır.
        Eğer url string değilse (None, int, list, vs.), fonksiyon None döndürür.
        Neden gerekli: Regex (re.search) gibi string üzerinde çalışan işlemleri uygulamadan önce tip güvenliği sağlıyor; hataları (ör. 'NoneType' object has no attribute '...') önler.
    '''

    # Olası URL formatları
    # burada patterns regex(düzenli ifade) desenlerinin listesi , biz iki yaygın YouTube ID formatını hedefliyoruz.neden iki desen youtube URL'leri birkaç farklı formatta gelebilir
    # mesela standart --> https://www.youtube.com/watch?v=VIDEO_ID  , embed ve başka formatlar --> https://www.youtube.com/embed/VIDEO_ID  veya  https://m.youtube.com/watch?v=VIDEO_ID  , kısa link --> https://youtu.be/VIDEO_ID   şeklinde

# burada patterns desenler listemiz var . listede regex (düzenli ifade) desenleri var. Her desen farklı URL formatını yakalamaya çalışır.
# Regex (düzenli ifade) Metin içinde belirli kalıpları aramak için kullanılan güçlü bir araçtır. Python'da re modülü ile kullanılır.

    patterns = [
        r"(?:v=|\/)([0-9A-Za-z_-]{11}).*",  # Standart ve embed
        r"youtu\.be\/([0-9A-Za-z_-]{11})"  # Kısa linkler
    ]

# Örnekler (girdi --> beklenen çıktı)
    # "https://www.youtube.com/watch?v=abcDEfGhI12" → "abcDEfGhI12"
    # "https://youtu.be/abcDEfGhI12" → "abcDEfGhI12"
    # "https://www.youtube.com/embed/abcDEfGhI12?start=10" → "abcDEfGhI12"
    # "abcDEfGhI12" → "abcDEfGhI12" (doğrudan ID verilmişse)
    # "not a youtube url" → None


# Hazırlanan desenlerin her birini sırayla denemek için döngü başlatıyoruz.
# bu döngünün nedeni ne farklı url formatlarından hangisinin geçerli olduğunu bulup, ilk eşleşen desenle id'yi almak için.
# şimdi burada re.search , python'un re modülünden gelen bir fonksiyon. pattern desenini url içinde arar. eğer herhangi bir yerde desenle eşleşme varsa bir match nesnesi döndürür; yoksa none döner.
# re.search ile re.match arasındaki fark: re.match sadece stringin başından eşleştirme yapar; re.search stringin her yerinde arama yapar. Burada re.search tercih ettik çünkü parametrede v= sorgu parametresi URL sonunda veya ortasında olabilir.


    for pattern in patterns:
        match = re.search(pattern, url)
        if match: # eğer eşleşme bulunduysa (match None değilse) iç bloğa girer
            return match.group(1)  # burada match.group(n) var nedir bu group(1) ilk capturing grupun yakaladığı değeri döndürür. Bizim desenlerde ID ([0-9A-Za-z_-]{11}) ile birinci capturing grup olduğu için group(1) video ID'sini verir.Fonksiyonun amacı bu ID'yi geri döndürmek
                                    # match nesnesi .group(0) tamamını, .group(1) ilk yakalanan parça vb. verir.

    # eğer url parametresi tek başına 11 karakter uzunluğundaysa ve http ile başlamıyorsa
    # (yani muhtemelen zaten bir video id'si verilmiş) fonksiyon bu durumda url'yi id olarak kabul edip döndürür.
    # çünkü bazı kullanımlar doğrudan videoid parametresi verir — fonksiyonu daha esnek yapmak için bu durum da kontrol edildi.
    if len(url) == 11 and not url.startswith('http'):
        return url # Direkt ID olarak verilen 11 karakteri geri döndürür.

    return None # Hiçbir desen eşleşmemişse ve yukarıdaki doğrudan ID kontrolü de geçerli değilse, fonksiyon None döndürür.çünkü id bulunamadığını belirtmek için.




# Bu fonksiyonun amacı:
# youtube api kullanarak bir video id’den:Video başlığını almak ,yorumları almak,bunları bir DataFrame içinde döndürmek,Yani dönüş:(DataFrame, video_title) şeklinde
def fetch_youtube_comments(video_id, count=config.YOUTUBE_MAX_RESULTS):   # burada video_id hedef videonun  idsi (11 karakter veya None) , count --> kaç yorum isteniyor. config.YOUTUBE_MAX_RESULTS uygulamanın genel ayarından geliyor.
    """
    Belirtilen YouTube videosundan yorumları ve başlığı çeker.
    Dönen Değer: (DataFrame, video_basligi)
    """
    comments_list = [] # Buradaki amacımız yorumları tek tek topladıktan sonra liste hâlinde saklamak; daha sonra DataFrame’e çevirmek.
    video_title = f"Video ID: {video_id}"  # eğer api başlık getiremezse en azından kullanıcı ekranda bir şey görsün diye default başlık atanıyor.

    # hasattr(obj, 'attribute') ne demek?
    # Bir objenin (class, modul, instance fark etmez) içinde belirtilen isimde bir değişken var mı diye kontrol eder.
    # hasattr(config, 'YOUTUBE_API_KEY') --> config dosyasında YOUTUBE_API_KEY isminde şey var mı?
    if not hasattr(config, 'YOUTUBE_API_KEY') or not config.YOUTUBE_API_KEY:

        return pd.DataFrame(columns=['text', 'link']), video_title # eğer yoksa boş bir DataFrame ve video_title döndürür

    try:# asıl api işlemlerimiz try bloğumuz

        # şimdi burada build nedir? Google API Client Library’nin fonksiyonudur. Google’ın YouTube API’sine bağlanmamızı sağlar
        # Parametrelerimiz:
        # "youtube" → bağlanmak istediğimiz servis
        # "v3" → API versiyonu
        # developerKey= → Youtube API Key
        # Dönen  şey  Bir  YouTube  servis objesi -->  içinde tüm metodlar bulunur:  youtube.videos()  , youtube.commentThreads()  ,  youtube.channels() , youtube.search() vb.

        youtube = build("youtube", "v3", developerKey=config.YOUTUBE_API_KEY)

        # 1. Video Başlığını Çekme İşlemi
        try:
            # youtube.videos() nedir --> YouTube API’nin videos endpoint’i
            # Bu endpoint "video ile ilgili her şeyi" getirir.
            # Örneğin: title , description , channelTitle , tags , duration vb.

            # .list() parametreleri: part="snippet",snippet = video hakkında kısa bilgiler ,title, description, publish time, channel bilgisi bu kısımda , id=video_id , Hangi videonun alınacağı
            video_req = youtube.videos().list(part="snippet", id=video_id) # part="snippet" -->  hangi alanları istiyoruz: snippet içinde title, description, publishedAt, channelTitle gibi alanlar var
            video_res = video_req.execute()
            # .execute() nedir? Bu çok önemli! execute() = API isteğini gerçekten gönderen fonksiyon..list() sadece "isteği hazırladı" .execute() → YouTube API’ye request gönderir ve cevap döner.Dönen veri bir JSON objesidir (dict).
            '''{ örneğin 
  "items": [
    {
      "snippet": {
         "title": "Video Başlığı",
         "description": "...",
         ...
      }
    }
  ]
}
'''

            # .get() ne işe yarar? Python dictionary’deki bir anahtarı almaya yarar. Eğer anahtar yoksa hata vermez, None döner.
            if video_res.get("items"):
                video_title = video_res["items"][0]["snippet"]["title"] # Yapı: video_res["items"] → sonuçlar listesi    [0] → ilk video   ["snippet"] → video özellikleri   ["title"] → başlık   Bu şekilde video başlığı elde edilir.
                print(f"✅ Video başlığı: '{video_title}'")
        except Exception as e:
            print(f"⚠️ Başlık çekilemedi: {e}")

        # 2. Yorumları Çekme
        print(f"--> YouTube yorumları çekiliyor (ID: {video_id})...")

        request = youtube.commentThreads().list( # youtube.commentThreads() bu endpoint video yorumlarını getirir.
            # parametreler
            part="snippet", #Yorum detayları:yorum metni ,kullanıcı ,yayınlanma tarihi
            videoId=video_id, # Hangi videonun yorumları?
            maxResults=count, # Kaç yorum getirilsin?
            textFormat="plainText" # html içermesin; direkt düz metin.
        )
        response = request.execute() # Yorumları çeker.YouTube API’ye “yorum isteği” gönderir ve JSON döner. execute() = “İsteği YouTube API’ye gönder ve sonucu getir” demektir.

        items = response.get('items', []) # JSON içinden yorumlar items anahtarında gelir.get ile alınır eğer yoksada  [] döner.burada items artık API’den gelen yorumların listesi.
        print(f"✅ {len(items)} adet yorum bulundu.")

        for item in items: # api’den gelen tüm yorumları tek tek dolaşıyoruz.
            snippet = item["snippet"]["topLevelComment"]["snippet"] # burada amaç bir yorumun “esas bilgilerinin” bulunduğu yere ulaşmak.
            '''item
                 └── snippet
                         └── topLevelComment
                                     └── snippet  <-- asıl yorum bilgileri burada
            
            Bu içteki snippet şu bilgileri taşıyor:
            authorDisplayName → Yorum yapan kişi ,textDisplay → Yorumun metni (HTML'li olabilir) , publishedAt → Tarih ,
            likeCount → Beğeni sayısı  ,updatedAt → Düzenleme zamanı  , Yani yorumun tüm detaylarını veren JSON sözlüğü.
            
            '''


            text = snippet["textDisplay"] # burada amacımız yorumun metnini almak. YouTube API yorum metinlerini HTML formatlı döndürür:
            author = snippet["authorDisplayName"] # Yorumu yazan kişinin adını almak.
            cid = item["snippet"]["topLevelComment"]["id"] # Her yorumun benzersiz ID değerini almak , bu id sayesinde yoruma direkt link oluşturabiliriz.

            # yorum linki oluşturma
            #YouTube mantığı şudur: v= → video id , lc= → comment id (yorum)
            link = f"https://www.youtube.com/watch?v={video_id}&lc={cid}"
            comments_list.append({
                "text": f"{author}: {text}",
                "link": link
            }) # listeye ekleme Amaç: Her yorumu DataFrame’e uygun hale getirmek.

            ''' mesela örnek yapımız:
            {
                 "text": "Ahmet: Çok güzel olmuş!",
                 "link": "https://www.youtube.com/watch?v=xxx&lc=yyy"
            }
            '''
        # en sonda dönen değerimiz ne dönüyor DataFrame --> yorumlar , Video başlığı
        return pd.DataFrame(comments_list), video_title

    # hata yakalama bölümümüz youtube api çağrılarında iki tür hata olabilir:
   #YouTube API’nin kendi hataları (örneğin: yanlış api key, kota dolmuş, video bulunamadı, izin yok) ---> bunlar HttpError ile yakalanır
    #HttpError, Google’ın YouTube API kitaplığının hata sınıfıdır . geldiği    yer    from googleapiclient.errors import HttpError
    #api kry yanlış ,kota dolmuş ,video silinmiş ,yorumlar engellenmiş bu tip hatalar HTTP protokolü üzerinden geldiği için Google bunlara HttpError der.
    except HttpError as e:

        # e.resp.status Nedir? resp --> “response” anlamında youtube api’nin döndürdüğü HTTP cevabı.
        # status --> HTTP durum kodu (status code)Örnek değerler: 400: Bad Request (yanlış istek) ,401: Unauthorized (API key yanlış) ,403: Forbidden (kota doldu/erişim yok) ,404: Not Found (video yok) , 500: Internal Server Error (YouTube problemi)
        # yani e.resp.status --> api’nin döndürdüğü hata kodunu verir.
        # ------------------------------------------------------------------
        # e._get_reason() Nedir --> bu fonksiyon, youtube api hata mesajının metinsel açıklamasını döndürür.örneğin "Quota exceeded" (kota doldu) Bu metin, YouTube API’nin gönderdiği insan tarafından okunabilir açıklamadır.
        '''
        Yani bu iki satır şöyle okunabilir:
                 Hata Kodu: 403
                 Hata Sebebi: Quota Exceeded (kota doldu)
        '''

        print(f"❌ YouTube API Hatası: {e}")
        return pd.DataFrame(columns=['text', 'link']), video_title

    # Programdaki diğer hatalar (sıfıra bölme, JSON bozulması, internet kesilmesi, başka programlama hataları) -->  bunlar Exception ile yakalanır. Bu bölüm bunları ayırmak için yazılmıştır.
    # Exception sınıfı Python’daki tüm hata türlerinin atasıdır.Örnek yakalayacağı hatalar: KeyError ,TypeError ,ValueError  ,IndexError  Yani: eğer api hatası --> HttpError , diğer tüm hatalar --> Exception
    except Exception as e:

        print(f"❌ YouTube hatası: {e}")
        return pd.DataFrame(columns=['text', 'link']), video_title  # Hata olsa bile fonksiyon:boş bir DataFrame video başlığı (default)döndürür.bu sayede uygulama çökmemiş olur.







