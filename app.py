import os
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"  # ileride ekleyeceğimiz kütüphaneler (PyTorch ve NumPy arasında olan yaygın teknik çakışmayı engellemek veya
# özellikle pyTorch kütüphanesinin birden fazla versiyonun çakışmasından kaynaklanan ve analizin donmasına neden olan hatayı(OMP:Error #15) engellemek
# için çünkü bu çakışma programı çökerten bir çakışma bizde --> (Duplicate Library OK = TRUE --> yani Tekrarlanan Kütüphane Tamam). ile çökme veya kilitlenme, programın çalışmasına izin ver demiş bulunuyoruz.
# ve bunu programın en başına koyduk ilk olarak çalışması ve ileride bu dosyada birçok işlem yapacağız , analiz sonuçlarını göstereceğiz problem çıkartmaması için şu anlık bunu ekledik. )



import streamlit as st          # Arayüz kütüphanemiz
import pandas as pd             # Dataframe işlemlerimiz için
import data_collector           # Twitter verisi için
import config                   # Ayarlarımızı okumak için
import text_processor           # Metin temizleme fonksiyonları için
import sentiment_analyzer       # Duygu analizi fonksiyonları için
import visualizer               # Grafik çizme fonksiyonları için



# --- Sayfa Ayarlarımız ---
st.set_page_config(page_title="Duygu Analizi Projesi", page_icon="📊", layout="wide")

# st.set_page_config streamlit uygulamamızın sayfasının genel ayarlarını yapar
# burada page_title tarayıcı sekmesinde görünecek olan başlığımız
# page_icon tarayıcı sekmesinde görünecek ikonumuz,emojimiz
# burada layout ise sayfamızda bulunan içeriğimizin tüm ekrana sığmasını , yani tüm ekranın genişliğini kullanmasını sağlar


# --- Model Yükleme ---

# Modeli önbelleğe alarak yüklüyoruz
# sentiment_analyzer dosyamızdaki load_model fonksiyonunu çağırıyoruz
# bu fonksiyonumuz  @st.cache_resource ile etiketlendiği , işaretlendiği için model sadece ilk çalıştırmada yüklenir.
# bu isaretleme işlemi sadece bir kez yapılıyor ve yüklenmiş modelimiz "model" değişkeninde saklanıyor , yani bu bize analizin daha hızlı olmasını sağlıyor
with st.spinner("Duygu analizi modeli yükleniyor..."):
    model = sentiment_analyzer.load_model()






# --- Arayüz Başlığımız ---
st.title("📊 Sosyal Medya ve Haberler için Duygu Analizi")
st.markdown("Bu uygulama, Twitter üzerinden alınan verileri analiz eder.")

# burada title Ana Başlığımız  ,  markdown ile başlık altına bir açıklama metni ekliyoruz



# --- Kenar Çubuğu ---

# burada kullandığımız sidebar yani kenar çubuğumuz (yan panelimiz) --- > with bloğu içindeki işlemleri yazılan her şey , streamlit elemanlarını(st.selectbox,st.header) sayfamızın sol tarafındaki kenar çubuğumuza koyar.
with st.sidebar:
    st.header("⚙️ Analiz Ayarları")

    # Veri Kaynağı Seçimi (Şimdilik Sadece Twitter ve Manuel Var)
    source_option = st.selectbox(
        "Veri Kaynağını Seçin:",
        ("Twitter", "Manuel Test")
    )

    query = "" # query sorgu demek başlangıçta boş

    if source_option == "Twitter":
        st.subheader("Twitter Ayarları") # eğer kullanıcı twitter seçti ise alt başlık yazılır:

        query = st.text_input(  # kullanıcıdan hashtag/kelime girmesi istenir ve sonuç query değişkenine aktarılır.
            "Aranacak Hashtag / Kelime:",
            placeholder="Örn: teknofest"
        )
        st.caption("Not: Sadece Hashtag araması aktiftir.") # küçük açıklama notu,soluk renkte bu açıklama görünür

    elif source_option == "Manuel Test": # eğer kullanıcı "Manuel Test" seçerse bu blok çalışır.
         # Test için metin girişi
         user_input = st.text_area( # kullanıcı kendi cümlesini elle yazar ve sonuç user_input değişkenine gelir
                "Analiz edilecek metni girin:",
                 height=150 # metin alanının yükseliği
    )

    analyze_button = st.button("🚀 Analizi Başlat", type="primary")


# burada text area ile çok satırlı bir metin alanı text area oluşturduk.
# butonumuz  True → kullanıcı o anda butona bastığında  ,  False → basılmadığında  şeklinde bir dönüş değeri döndürüyor.
# burada butonumuz içinde bulunan type parametresinin değeri "primary" şeklinde buton rengi ana temeya göre kırmızı-turuncu vb rengini aldı , varsayılan type "secondary" de ise buton içi boş ve gri-beyazdır.







# --- Ana Akış ---

# Kullanıcı 'Analizi Başlat' butonuna bastıysa (yani True dönerse) VE metin kutusu boş değilse (buda True dönerse) içeri gir.
if analyze_button:
    # 1.adım burada verimizi hazırlıyoruz aslında formatlıyoruz  çünkü bizim 'text_processor' ve 'sentiment_analyzer' dosyalarımızı,
    # tek bir string (metin) ile değil, dataframe(tablo) ile çalışacak şekilde oluşturduk.
    # Bu yüzden elimizdeki tek cümleyi kullanıcının girdiği texti, tek satırlık bir tabloya dönüştürüyoruz.

    # 1.adım veri toplama
    df = pd.DataFrame() # veri toplamak için boş DataFrame oluşturuyoruz , elimizde bir tablo yok,boş tablo oluşturuyoruz.

    if source_option == "Twitter":
        if not query:  # kullanıcı hashtag yazmadıysa , uyarı ver ve işlemi durdur.
            st.warning("Lütfen bir arama terimi girin.")
            st.stop()

        with st.spinner("Twitter'dan veriler çekiliyor..."):  # kullanıcı beklemesin diye animasyonlu “yükleniyor” göstergesi açılıyor.
            # data_collector modülünü çağırıyoruz , twitter’dan tweetleri çeken fonksiyonu çağırıyoruz
            df = data_collector.fetch_tweets(query, search_type='hashtag', count=config.TWITTER_MAX_RESULTS)

            # sonucunda df artık tweet metinleri + linkler içeren bir DataFrame olur.

    # Manuel Test seçilirse
    elif source_option == "Manuel Test":

        df = pd.DataFrame({'text': [user_input]}) # kullanıcının yazdığı tek bir cümleyi tek satırlık DataFrame’e çeviriyoruz , çünkü analiz sistemi DataFrame formatında çalışıyor.



    # 2.adım veri kontrolü
    if df.empty: # eğer tablo boş ise hata mesajı
          st.error("Hiçbir sonuç bulunamadı.")

    else:  # değilse kaç satır veri bulunduğunu yaz
          st.success(f"Başarıyla {len(df)} adet veri bulundu!")


    # 3.adım metin temizle(pre-processing) ve duygu analizi
          with st.spinner("Analiz yapılıyor..."):# bu satırda işlem devam ederken kullancıya belirtme yapıyoruz
                 processed_df = text_processor.process_dataframe(df)
                 # oluşturduğumuz tabloyu(df) temizleyen bu işi yapan modüle gönderiyoruz.
                 # oda geriye cleaned_text sütunu eklenmiş temiz bir şekilde tabloyu dönüyor(processed_df)

                 processed_df, analysis_counts = sentiment_analyzer.analyze_dataframe(processed_df, model)
                 # burada temizlenmiş olan df mizi yani tablomuzu analize gönderiyoruz
                 # burada bize 2 şey veriyor geriye
                 # 1. si  processed_df içinde artık "Duygu Durumu" sütunu da var.
                 # 2. si analysis_counts, yani analiz sayımlarının toplam sonuçları (Örneğin: {'positive': 1, 'negative': 0...})




    # 4.adım sonuçları gösterme , görselleştirme(Visualization)
    col1, col2 = st.columns([2, 1])
    # Ekranı ikiye bölüyoruz. sol kısım daha geniş (grafik için) , sağ kısım daha dar (sayılar için)
    # [2, 1] oranı şunu demek: Sol sütun "col1" ekranın 2/3'ünü, Sağ sütun "col2" 1/3'ünü kaplasın.
    # Grafiğe daha fazla yer ayırmak için bunu yaptık.

    # Sol sütun grafik alanı için
    with col1:
        st.write("#### Duygu Dağılımı")
        # visualizer modülümüzdeki fonksiyonla pasta grafiğini (fig) oluşturuyoruz.
        fig = visualizer.create_sentiment_pie_chart(analysis_counts)

        if fig:   # Eğer grafik başarıyla oluştuysa ekrana ver.
            st.plotly_chart(fig, use_container_width=True)
            # burada --> use_container_width=True: Grafiği sütunun genişliğine tam sığdır.

        else: # Eğer veri yoksa (hepsi 0 ise) bilgi verir.
            st.info("Veri yok.")

    # Sağ sütun sayısal sonuçlarımızın alanı
    with col2:
        # Sayıları Gösterme

        # Metrikleri (Kutucuk içindeki büyük sayılar) gösteriyoruz.
        # .get('positive', 0) -> Eğer 'positive' anahtarı yoksa hata verme, 0 yaz. --- .get ---> eğer anahtar yoksa 0 yaz.

        # st.metric() streamlit’te sayısal özet kutusu göstermeye yarayan bir fonksiyon."Toplam" Metric kutusunun başlığı.Yani kutuda üstte “Toplam” yazacak.
        # analysis_counts sözlük yapısıdır

       #        analysis_counts = {
       #               'positive': 4,
       #               'negative': 1,
       #               'neutral': 3
       #        }

        # analysis_counts.values() ---> [4, 1, 3] değerlerini döndürür. Tüm değerleri toplar ---> 4 + 1 + 3 = 8 --- başlık Toplam olur analiz edilen toplam metin sayısıdır

        st.write("#### Özet")
        st.metric("Toplam", sum(analysis_counts.values()))
        st.metric("Pozitif", analysis_counts.get('positive', 0))
        st.metric("Negatif", analysis_counts.get('negative', 0))
        st.metric("Nötr", analysis_counts.get('neutral', 0))

    # 5.adım Detaylı veri gösterimi
    st.markdown("---") # Araya bir ayırıcı çizgi çekiyoruz
    with st.expander("📝 Detaylı Veriyi Gör"): # st.expander: Açılıp Kapanabilen bir kutu oluşturuyoruz.Sayfayı kalabalık göstermemek için tabloyu varsayılan olarak gizli tutuyoruz.Kullanıcı isterse tıklayıp detayları görebilir.
        st.dataframe(processed_df) # # İşlenmiş ve analiz edilmiş son tabloyu göster.






# Burada aslında sıralı bir işlem gerçekleştiriyoruz:

# Kullanıcının girdiği metni alıyoruz.
# Metni bir DataFrame koyuyoruz.
# text_processor ile temizliyoruz.
# sentiment_analyzer ile , Yapay Zeka ile duygu analizi gerçekleştiriyoruz.
# Sonuçları visualizer ile grafiğe döküyoruz ve kullanıcıya sunuyoruz.
# Bu yapı sayesinde, ileride yeni bir veri kaynağı eklediğimizde de sadece değiştirmemiz yetecek; geri kalan (temizleme, analiz, görselleştirme) her şey aynı şekilde çalışmaya devam edecek. buradanda aslında modülerliğin modüler yapının uygunluğunu düzenli yapısını görüyoruz.











