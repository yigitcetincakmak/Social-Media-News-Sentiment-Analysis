import tweepy  # Python'un Twitter ile konuşmasını sağlayan kütüphanemiz.biz python yazıyoruz, o bunu twitter'ın anlayacağı api diline çeviriyor.
import pandas as pd
import config # api anahtarlarını sakladığımız dosya
import streamlit as st



# --- Tweepy Client ---
try:
    client = tweepy.Client(bearer_token=config.TWITTER_BEARER_TOKEN) # client değişkeni ile twitter'ın kapısını çalıyoruz.
    # bearer_token: kapıyı açmak için kullandığımız "giriş kartımız". bu kart, sadece halka açık verileri (hashtag arama gibi) okumamıza izin veriyor.
    print("✅ Tweepy Client (Bearer Token ile) başarıyla başlatıldı.")


except Exception as e:
    print(f"❌ Tweepy Client başlatılırken HATA: {e}")
    client = None
# try...except: burası bir kontroldür,önlemidir. eğer config.py dosyamızda anahtar eksikse veya internet yoksa programın tamamen çökmesini engelliyor. hata varsa client değişkenini None (boş) yapar.




# --- Tweet Çekme Fonksiyonlarımız ---

def _fetch_tweets_by_hashtag(hashtag_or_query, count=config.TWITTER_MAX_RESULTS): # Parametrelerimiz hashtag_or_query (kullanıcının yazdığı kelime) ve count (kaç tweet çekileceği).
    if not client: return pd.DataFrame(columns=['text', 'link'])

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

        st.error("⏳ Twitter API kullanım limitine takıldınız (Hashtag Arama). Lütfen ~15 dakika sonra tekrar deneyin.") # kullanıcıya streamlit içinden uyarı verir.
        print("❌ Rate limit (Hashtag Arama).") # konsola uyarı mesajı yazdırır.
        return pd.DataFrame(columns=['text', 'link']) # Boş DataFrame gönderir.

    # Genel Hatalarımız , işte internet yoksa veya client bozuksa yada response yapısı değiştiyse ---> Hatanın detayını yazdırıp boş DataFrame döner.
    except Exception as e:
        print(f"❌ Hashtag tweetleri çekilirken HATA: {e}") # Hatanın detayı
        return pd.DataFrame(columns=['text', 'link']) # boş DataFrame döner


# --- Ana Çağrı Fonksiyonumuz ---

# Bu fonksiyon twitter’dan tweet çekmek için ortak bir kapımız (ana fonksiyonumuz).
def fetch_tweets(query, search_type='hashtag', count=config.TWITTER_MAX_RESULTS): # query → aranan metin veya hashtag (#python gibi) , search_type='hashtag' → varsayılan olarak hashtag araması çalışıyor  , count=config.TWITTER_MAX_RESULTS → çekilecek tweet sayısı
    print(f"--- Twitter API İsteği Başlatılıyor ---")
    df = pd.DataFrame(columns=['text', 'link']) # boş bir DataFrame oluşturuyor -- eğer ileride bir hata olursa en azından boş bir DataFrame döndürücek bize. sütunlarımız text ---> tweet metni , link ---> tweet linki

    if search_type == 'hashtag': # arama türü hashtag mi kontrol ediyor , eğer arama tipi hashtag ise, hashtag arama fonksiyonunu çağırır(_fetch_tweets_by_hashtag)
        df = _fetch_tweets_by_hashtag(hashtag_or_query=query, count=count)

            # bu fonksiyon:

                    # twitter’a api isteği gönderir
                    # tweetleri toplar
                    # kullanıcı isimlerini çıkarır
                    # linkleri oluşturur
                    # DataFrame döndürür

            # Sonuç olarak df artık gerçek tweetlerle dolmuş olur.


    else: # Eğer search_type hashtag değil ise uyarı verir

        print(f"⚠️ Arama tipi '{search_type}' henüz aktif değil.")

    print(f"--- İstek Tamamlandı ---")
    return df # ister tweet listesi dolu olsun, ister boş — fonksiyon her zaman bir DataFrame döndürür.