# Huggin face üzerinde indireceğimiz , kullanacağımız duygu analizi modelimizin adı
MODEL_NAME = "savasy/bert-base-turkish-sentiment-cased"


# veri limitimiz
TWITTER_MAX_RESULTS = 10
NEWS_MAX_RESULTS = 20
YOUTUBE_MAX_RESULTS = 30


# twitter developer platform dan aldığımız anahtarlarımız
# Bu değişkenler twitter api ye bağlanmamız için gerekli kimlik bilgilerini saklayan değişkenlerdir.twitter api’ye bağlanmak için 5 farklı anahtar/token gerekiyor.

TWITTER_API_KEY = "..."                 # uygulama kimliği  --->  “uygulama benim”
TWITTER_API_SECRET_KEY = "..."          # uygulama gizli anahtarı  --->  “ben bu uygulamanın sahibiyim”
TWITTER_ACCESS_TOKEN = "..."            # kullanıcı yetkisi  --->  “kullanıcının hesabını kullanıyorum”
TWITTER_ACCESS_TOKEN_SECRET = "..."     # kullanıcı gizli anahtarı  --->  “bu kullanıcı gerçekten benim”
TWITTER_BEARER_TOKEN = "..."            # okuma izni  --->  “tweetleri okuyabilirim”


# --- YOUTUBE API AYARI ---
YOUTUBE_API_KEY = ""





# --- HABER SİTELERİ VE KATEGORİLERİ ---

# bu kodda bildiğimiz haber sitelerini tek bir değişkende toplar , her siteye ait kategorileri (Gündem, Spor, Dünya...) içerir , her kategori için ilgili RSS beslemesi (haber akışı) linkini saklar.
# Bu sözlük iç içe bir yapıda  dış sözlük --> siteler , iç sözlük --> kategoriler , en iç --> RSS linki var
# NEWS_SITES, haber sitelerini barındıran büyük bir sözlüktür mesela "Sözcü" , Sözcü gazetesi için bir alt sözlük demektir , NEW_SITES içinde bu bir anahtardır. bu alt sözlük içinde Anahtar "Gündem" , Değer ise RSS adresi linkidir   ---  "Sözcü" --> { Gündem --> link } mantığında , her kategori bir RSS linki tutar.

# ----  RSS Linkleri Nedir  ----
# sitelerin haberlerini makineler için düzenli formatta sunma şeklidir.
# haber başlıkları, linkler, tarih bilgileri içerir.
# bu linkleri feedparser ile okuyup haber başlıklarını çekiyoruz.
# https://www.ntv.com.tr/gundem.rss  -->  mesela bu linke gidersek son dakika haberlerini XML formatında görürüz işte Python bu veriyi otomatik alıyor.

# mesela kullanıcı site seçtiğinde site_key = "Sözcü"  , kullanıcı kategori seçtiğinde category_key = "Spor" böylece RSS linki kolayca çekilir --> rss_url = NEWS_SITES[site_key][category_key]  bu,pratik bir kullanım sağlar.




NEWS_SITES = {

     "Sözcü": {
         "Gündem": "https://www.sozcu.com.tr/feeds-rss-category-gundem",
         "Spor": "https://www.sozcu.com.tr/feeds-rss-category-spor",
         "Dünya": "https://www.sozcu.com.tr/feeds-rss-category-dunya",
         "Teknoloji": "https://www.sozcu.com.tr/feeds-rss-category-bilim-teknoloji"
     },
    "Habertürk": {
        "Gündem": "https://www.haberturk.com/rss/gundem.xml",
        "Spor": "https://www.haberturk.com/rss/spor.xml",
        "Dünya": "https://www.haberturk.com/rss/dunya.xml",
        "Teknoloji": "https://www.haberturk.com/rss/teknoloji.xml"
    },
    "NTV": {
        "Gündem": "https://www.ntv.com.tr/gundem.rss",
        "Spor": "https://www.ntv.com.tr/spor.rss",
        "Dünya": "https://www.ntv.com.tr/dunya.rss",
        "Teknoloji": "https://www.ntv.com.tr/teknoloji.rss"
    },
    "Cumhuriyet": {
        "Gündem": "https://www.cumhuriyet.com.tr/rss/1.xml",
        "Spor": "https://www.cumhuriyet.com.tr/rss/8.xml",
        "Dünya": "https://www.cumhuriyet.com.tr/rss/4.xml",
        "Teknoloji": "https://www.cumhuriyet.com.tr/rss/10.xml"
    },
    "TRT Haber": {
        "Gündem": "https://www.trthaber.com/gundem_articles.rss",
        "Spor": "https://www.trthaber.com/spor_articles.rss",
        "Dünya": "https://www.trthaber.com/dunya_articles.rss",
        "Bilim-Teknoloji": "https://www.trthaber.com/bilim_teknoloji_articles.rss"
    },
    "CNN Türk": {
        "Gündem": "https://www.cnnturk.com/feed/rss/all/news",
        "Spor":   "https://www.cnnturk.com/feed/rss/spor/news",
        "Dünya":  "https://www.cnnturk.com/feed/rss/dunya/news",
        "Teknoloji": "https://www.cnnturk.com/feed/rss/teknoloji/news"
    },
    "AnadoluAjansi" : {
        "Gündem": "https://www.aa.com.tr/tr/rss/default?cat=guncel",
        "Spor": "https://www.aa.com.tr/tr/rss/default?cat=spor",
        "Dünya": "https://www.aa.com.tr/tr/rss/default?cat=dunya",
        "Ekonomi": "https://www.aa.com.tr/tr/rss/default?cat=ekonomi",
        "Bilim-Teknoloji": "https://www.aa.com.tr/tr/rss/default?cat=bilim-teknoloji"
    },
    "BBC Türkçe": {
        "Ana Sayfa": "https://feeds.bbci.co.uk/turkce/rss.xml",
    }
}


