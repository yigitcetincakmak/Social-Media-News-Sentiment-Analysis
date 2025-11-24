import pandas as pd
import streamlit as st
from transformers import pipeline

import config

'''
@st.cache_resource ---> streamlit'in bir dekoratörüdür yani fonksiyonu süsleyen bir direktif bunu kullanma amacımız
fonksiyon ilk kez çağrıldığında sonucumuzu yani return ettiğimizi burada modelimiz return ediyoruz bunu streamlit'in hafızasında yani cache'de tutması kaydetmesidir
çünkü ilerde fonksiyon çağrıları yaptığımızda bu fonksiyonu tekrar çalıştırmak yerine , hafızadaki o değeri , sonucu bize direkt geri döner.
dil modelleri boyutları genelde yüksektir her analizde diskten okuma yapıp belleğe yazma işlemi işlemlerimizi yavaşlatmasın diye bu işlemi gerçekleştirdik.

'''
@st.cache_resource
def load_model():

    try:
        print("Duygu analiz modeli yükleniyor...")

        # modelimizin yüklendiği kısmımızdır transformers kütüphanesinden pipeline fonksiyonunu çağırıyoruz
        model = pipeline("sentiment-analysis",model=config.MODEL_NAME,tokenizer=config.MODEL_NAME)
        # burada  sentiment-analysis yapmak istediğimzi işlemin adıdır Hugging Face bu göreve uygun bir yapı oluşturuyor . model --> kullanmak istediğimiz modeli belirtiyoruz.

        print("Model başarıyla yüklendi.")
        return model # işlemler başarılı bir şekilde gerçekleşirse modelimiz yüklenirse yani , bir pipeline nesnesi oluşuyor

        '''
        "pipeline"  verinin bir işlem hattından geçmesi anlamındadır.yani bir işlem, diğerine bağlı şekilde sıralanıyor
         mesela   Tokenizer’ı yükle - sonra Modeli yükle - sonra Metni token’lara çevir ve Modeli çalıştır ---> bu bir işlem hattıdır her işlemi satır satır kod yazarak gerçekleştiririz
         pipeline bunların hepsini arka planda otomatik yapar.
        
        '''

    except Exception as e :
        print(f"Model yüklenirken hata oluştu: {e}")
        st.error(f"Model yüklenemdi: {e}")
        return None


def analyze_dataframe(df,model):

        '''
        alt satırda if satırı ile şunları kontrol ediyoruz model is none ---> model yüklenmiş mi , boş mu , yüklenirken bir hata olmuş mu
        "cleaned_text" not in df.columns ---> dataframe de temizlenmiş metin sütunu , kolonu var mı
        df["cleaned_text"].dropna().empty ---> temizlenmiş metin sütunu tamamen boş mu yani analiz edilecek bir metin yokmu

        ---> yani sonuç olarak bu durumlardan herhangi biri ile karşılaşılırsa yani true , doğruysa analiz yapılmaz

        '''
        if model is None or "cleaned_text" not in df.columns or df["cleaned_text"].dropna().empty:

            df["Duygu Durumu"] = "Analiz Edilemedi" # dataframe de duygu durumu adında yeni bir sütun ekler ve tüm değerlerinide "Analiz Edilmedi" diye ayarlar

            return df , {"positive":0 , "negative":0 , "neutral":0}  # son halinde bulunan dataframe'i ve analiz etmediğimiz için duygu durumlarının duygu durum sayıları da adet olarak sıfır ayarladık
                                                                    # burada analiz yapılmadı ve tüm duygu durumlarını sıfır adet olarak ayarladık ve program çökmesini engellemeye çalıştık


        valid_texts = df["cleaned_text"].dropna()  # cleaned sütunu seçiyoruz içindeki boş , nan değerleri kaldırıyoruz , ve boş olmayan ön işlemeden geçmiş metinleri "valid_texts" değişkenine atıyoruz
        text_list = valid_texts.tolist() # burada valid_texts'ten aldığımız metinleri liste içinde tutuyoruz , listeye dönüştürüyoruz ---> pipeline modeli genellikle en iyi performansı bir liste aldığında verir


        # try ile modelimizin analiz yapması denenir
        try:

            sentiments = model(text_list)
            '''
            işte bu satırda duygu analizi yapılır , yüklenmiş olan modelimiz (pipeline nesnemiz)
            ön işlemden geçmiş ve temiz bir halde bulunan "text_list" i alır ve her bir metin elemanı için analiz yapar
            '''

        except Exception as e:

            # herhangi bir hata oluşursa hem terminalde hemde arayüz ekranımızda hata olduğunu belirtiyoruz
            print(f"Metinler analiz edilirken bir hata oluştu: {e}")
            st.warning("Bazı metinler analiz edilirken bir sorun oluştu.")


            df["Duygu Durumu"] = "Hata" # dataframe deki duygu durumunu hata olarak ayarlıyoruz

            # yine aynı şekilde son halde bulunan dataframe ve duygu durumlarının sayısını her bir duygu durumunun sıfır adet olarak ayarlıyoruz ve bunları döndürüyoruz.
            return df , {"positive":0 , "negative":0 , "neutral":0}


        labels = [s['label'].lower() for s in sentiments]



        '''
        yukarıdaki kod satırında sentiments listesindeki her bir sonuç sözlüğünden sadece label i yani etiketi
        alıyoruz ---> (s["label"]) ve bunu (.lower()) ile küçük harfe çeviriyoruz ["positive","negative",....] şeklinde bir liste haline geliyor .
        sonuç olarak sadece etiket yani duygu durumunun adını içeren bir liste haline gelmiş oluyor.
        
        # yukarıdaki tek satırda pythonda "list comprehension" kullanımı ---> altta bulunan 5 satırı tek satıra indirgemiş oluyoruz
       
        labels = []
        for s in sentiments:
                etiket = s['label']
                kucuk_harfli_etiket = etiket.lower()
                labels.append(kucuk_harfli_etiket)
        
        '''



        # burada(alt satırdaki kodda) az önce oluşturduğumuz labels listesini veriyoruz ve bu listenin indexlerininde
        # bizim analiz etmek istediğimiz valid_texts in indexleri ile aynı olmasını istiyoruz
        # böylece bu yeni oluşturduğumuz series ı dataframe mize bir sütun olarak ekliyoruz
        # ---> böylece analiz sonuçları , orijinal dataframe deki doğru metin satırları ile eşleşmiş olur(boş satırları atladığımız için eşleşme olması gerekiyordu)
        df["Duygu Durumu"] = pd.Series(labels , index = valid_texts.index)

        df["Duygu Durumu"] = df["Duygu Durumu"].fillna("Analiz Edilemedi")
        # Duygu Durumu sütununda boş nan değerler varsa , bunları analiz edilemedi stringi ile dolduruyoruz

        results = df["Duygu Durumu"].value_counts().to_dict()
        # burada yeni eklediğimiz bu Duygu Durumu sütununda her değerin kaç adet olduğunu sayar ve series olarak çıktı verir
        # bu çıktıyada to_dict() ile sözlüğe çeviririz results ile bu sayım sözlüğünü tutarız
        # mesela {"positive":15 , "negative":3 , "neutral":2} ---> yani sonuçları sayıyoruz


        # bir sözlük oluşturduk duygu durumlarımız anahtar olacak şekilde ve hepsi başlangıçta sıfır adet
        final_counts = {'positive': 0, 'negative': 0, 'neutral': 0}

        for key , value in results.items():
            if key in final_counts:
                final_counts[key] += value

        return df , final_counts # dataframe mizi ve duygu durumlarının adet olark bulunduğu sözlüğümüzü döner .

        '''
        burada for ile results sözlünden gelen her bir anahtar - değer çifti için döngü yapıyoruz mesela {key="positive" , value = 15} için bir döngü başlatılır
        if key in final_counts: ---> bu kısım ile eğer results sözlüğündeki anahtar(key) bizim final counts sözlüğümüz içinde de varsa yani positive , negative , neutral ise
        final_counts[key] += value    ---> o anahtarın değerini results daki sayıyla arttır
       
        ---> burada mesela value_counts sonucunda herhangi bir duygu durumu bulunmasa dahi mesela "neutral" yok , bulunmadı diyelim
             yinede buna final_counts  sözlüğünde sıfır olarak başlangıç değeri veriyoruz ---> anahtarların kesin bir şekilde bulunmasını sağlıyoruz
             ----> bunu sebebi duygu durumlarının grafiğini çizdireceğimiz vakit hata almamaya çalışmak.
        '''









