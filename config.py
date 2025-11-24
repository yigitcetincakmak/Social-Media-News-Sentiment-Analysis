# Huggin face üzerinde indireceğimiz , kullanacağımız duygu analizi modelimizin adı
MODEL_NAME = "savasy/bert-base-turkish-sentiment-cased"


# veri limitimiz
TWITTER_MAX_RESULTS = 10

# twitter developer platform dan aldığımız anahtarlarımız

# Bu değişkenler twitter api ye bağlanmamız için gerekli kimlik bilgilerini saklayan değişkenlerdir.twitter api’ye bağlanmak için 5 farklı anahtar/token gerekiyor.

TWITTER_API_KEY = "..."                 # uygulama kimliği  --->  “uygulama benim”
TWITTER_API_SECRET_KEY = "..."          # uygulama gizli anahtarı  --->  “ben bu uygulamanın sahibiyim”
TWITTER_ACCESS_TOKEN = "..."            # kullanıcı yetkisi  --->  “kullanıcının hesabını kullanıyorum”
TWITTER_ACCESS_TOKEN_SECRET = "..."     # kullanıcı gizli anahtarı  --->  “bu kullanıcı gerçekten benim”
TWITTER_BEARER_TOKEN = "..."            # okuma izni  --->  “tweetleri okuyabilirim”
