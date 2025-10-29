import re
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import pandas as pd

# nltk paketlerinin indirilip , indirilmediğini kontrol ediyoruz eğer indirilmemiş ise unutulmuş ise otomatik indiriyoruz nltk.download() komutu ile.

try:

    stopwords.words("turkish")

except LookupError:

    nltk.download("stopwords")

#------------------------------------------

try:

    nltk.data.find("tokenizers/punkt") # tokenizers alt klasöründe punkt modeli varmı , gerekli dosyaları var mı bunu buluyoruz

except LookupError:

    nltk.download("punkt")


def clean_text(text):

        if not isinstance(text , str):
            return ""

        # 1. adım textimizi  küçük harflere çeviriyoruz
        text = text.lower()
#--------------------------------------------------------------------------------

        # 2. adımımız URL , mention ve hastag'leri kaldırıyoruz

        text = re.sub(r"http\S+|www\S+|https\S+",text,flags=re.MULTILINE)

        '''
        
         URL'leri yani http, https veya www ile başlayıp boşluğa kadar giden kısımları bulup ve silme işlemini yapıyoruz.
        
        text = re.sub(
            r'http\S+|www\S+|https\S+',   ---> Aranacak olan URL kalıbı: (httpS+ VEYA wwwS+ VEYA httpsS+)
            '',        ---> sildikten sonra Yerine boş string koyuyoruz (sil)
            text,    ---> bu işlemleri yapıcağımız metin
            flags=re.MULTILINE  # birden çok satırı olan metinler içinde bu desteği alıyoruz
        )
        
        '''

        text = re.sub(r'\@\w+|\#', '', text)

        '''
            r'...': bunun bir "raw string" olduğunu belirtiyoruz .yani burada r harfi başına eklendi ve python artık \n’i özel karakter olarak değil, metin olarak görür mesela r"Merhaba\nDünya" çıktısı Merhaba\nDünya olur.
            
            burada  |: "VEYA" anlamına gelir.
            
            Mention'ları (@kullaniciadi gibi) ve hashtag sembolünü (#) buluyoruz ve siliyoruz.
            mention ---> @ sembolü mesela @google boşluk olmadan , bir kullanıcıdan doğrudan bahsetmek gibi.
            
            text = re.sub(
            
            r'\@\w+|\#',  --->  Arayacağımız kalıp şu şekilde (@ ile başlayıp  harf/rakam/alt  çizgi ile devam eden
             (burada w+ ---> @ sembolünden sonra gelen bir yada birden fazla(+) alfanümerik karakteri (\w, yani harfler, rakamlar ve alt çizgi _) bulur.
              Alfanümerik karakterlere örnek olarak "abc123", "A1B2C3" veya "password1" gibi harf ve rakamların herhangi bir karışımı verilebilir.) veya # işareti ile
                                    )
           
            '',      ---> bu bulduklarımızın yerine boş string koyuyoruz yani siliyoruz
            text     ---> bu işlemleri gerçekleştireceğimiz metnimiz
            
            )
        
        '''
#------------------------------------------------------------------------------------------

        # 3. adımımız sayıları ve noktalama işaretlerini kaldırıyoruz ve en son olarak metnimizde sadece küçük harfler ve boşluklar kalıyor
        # burası artık metnimizi duygu analizi için en saf haline , temiz haline getirmeye çalıştığımız kısımdan biridir.

        text = re.sub(r'[^a-zğüşıöç\s]', '', text)

        '''
          
           r'...': bunun bir "raw string" olduğunu belirtiyoruz .yani burada r harfi başına eklendi ve python artık \n’i özel karakter olarak değil, metin olarak görür mesela r"Merhaba\nDünya" çıktısı Merhaba\nDünya olur.     
           burada [^a-zğüşıöç\s] --->  Bir karakter setini tanımlıyor
            
            "^"  işareti bu karakter setimizin hemen başında kullanıldığında ---> "bu setin içindeki karakterler HARİÇ herhangi bir karakteri eşleştir" anlamına geliyor.
            a-z: ---> a'dan z'ye kadar tüm küçük ingilizce harflerini kapsıyor.
            
            ğüşıöç: --->  bunlara ek olarak türkçe'ye özel olan küçük harfleri tek tek ekliyoruz.
            
            \s: ---> herhangi bir boşluk karakterini ifade ediyor mesela ---> "normal boşluk" ,  "tab \t"  , "yeni satır \n"   vb. ifade eder.
            
            '', ---> yerine boş string koy yani siliyoruz 
            text --->  bu işlemleri yapıcağımız metin
        '''

#-----------------------------------------------------------------------------------------------

        # 4. adımımız stopwords yani durdurma , duraklama ,etkisiz kelimeleri kaldırma
        # ve metnimizi token'larına ayırma yani kelime kelime ayırma işlemlerini gerçekleştireceğiz

        # metni token'larına ayırma
        tokens = word_tokenize(text , language = "turkish")

        # nltk ' nın  stopwords modülünde türkçe için tanımlanmış etkisiz kelimeler listesini alıyoruz mesela ---> (["acaba","ama",....,"belki"])
        # bu listeyi bir kümeye(set) çeviriyoruz , kümelerde bir elemanın olup olmadığını kontrol etmek listelere göre daha hızlıdır.
        turkish_stop_words = set(stopwords.words("turkish"))


        filtered_tokens = [word for word in tokens if word not in turkish_stop_words]

        '''
        yukarıdaki kullanım  "list comprehension" aynı işi tek satırda yapabiliyoruz
        
        bu satırda tokens listemizdeki her bir word yani kelime için for döngüsü başlatıyoruz
        eğer o kelime yani word bizim turkish_stop_words kümemizin içinde değilse(yani etkisiz bir kelime değilse)
        bu kelimeyi yeni oluşturduğumuz filtered_tokens listesine ekliyoruz
        
        burada sonuç olarak yani tokens listesinin sadece etkisiz kelimelerden temizlenmiş , ayıklanmış halini filtered_tokens listesinde topluyoruz 
        
        
        filtered_tokens = []
        for word in tokens:
                if word not in turkish_stop_words:
                    filtered_tokens.append(word)
        
        '''
        # filtered_tokens listesindeki kelimeleri alıyoruz ve aralarına bir boşluk koyarak yeniden bir metin , string haline getiriyoruz ve son olarak bunu bu son haliyle döndürüyoruz
        # mesela (["kırmız" , "bina"]) ----> ("kırmızı bina")
        return " ".join(filtered_tokens)


def process_dataframe(df):

    # parametre olarak gelen dataframe'in sütunları arasında text adında bir kolonun ,sütunun olup olmadığını kontrol ediyoruz
    if "text" not in df.columns:

        # Eğer text sütunu yok ise hata mesajıyla program durdurulur
        raise ValueError("DataFrame'de text sütunu bulunmalıdır.")


    df["cleaned_text"] = df["text"].dropna().apply(clean_text)
    '''
    "text" sütunundaki her bir metin için clean_text fonksiyonunu uyguluyoruz(pandasın apply metodu ile seçilen sütunun her bir satırına parantez içindeki fonksiyonu uyguluyoruz) 
     ve dropna() ile nan olan boş satırları temizliyoruz,böylece clean_text fonksiyonuna boş değer gönderilmesini engelliyoruz. 
    
    '''
    return df







