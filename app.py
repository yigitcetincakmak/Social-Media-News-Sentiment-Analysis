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


# --- Hafıza Temizleme Fonksiyonu ---
# bu fonksiyon uygulamamızda daha önce bellekte tutulan verileri silerek hafızayı (session_state) temizler.çünkü streamlit her işlem arasında değişkenleri korur.
def clear_results():
    keys_to_delete = ["processed_df", "analysis_counts", "search_term"] # burada silinmesini istediğimiz anahtarları bir liste içinde topladık.
    # burada processed_df --> işlenmiş veri çerçevesi (DataFrame) , analysis_counts --> analiz içinde hesaplanmış sayılar / kelime sayıları vb. , search_term --> Kullanıcının arama yaptığı kelime , bunlar Streamlit session_state içinde saklanan verilerdir.
    for key in keys_to_delete: # bu for döngüsü listeyi sırayla döner
        if key in st.session_state: del st.session_state[key] # bu satır şunu kontrol ediyor --> if key in st.session_state --> bu anahtar streamlit’in session_state'inde var mı ---- del st.session_state[key] --> session state’teki o anahtarı tamamen siler artık bellekte yer kaplamaz.bir sonraki işlemde eski veri karışıklık yapmaz.del ile silerek RAM’i temizliyorsun
                                                                # eski verileri siler , RAM kullanımını azaltır



# --- Arayüz Başlığımız ---
st.title("📊 Sosyal Medya ve Haberler için Duygu Analizi")
st.markdown("Bu uygulama, Twitter ve Haber Siteleri üzerinden alınan verileri analiz eder.")

# burada title Ana Başlığımız  ,  markdown ile başlık altına bir açıklama metni ekliyoruz



# --- Kenar Çubuğu ---

# burada kullandığımız sidebar yani kenar çubuğumuz (yan panelimiz) --- > with bloğu içindeki işlemleri yazılan her şey , streamlit elemanlarını(st.selectbox,st.header) sayfamızın sol tarafındaki kenar çubuğumuza koyar.
with st.sidebar:
    st.header("⚙️ Analiz Ayarları")

    # Veri Kaynağı Seçimi (Şimdilik Sadece Twitter ve Manuel Var)
    source_option = st.selectbox(
        "Veri Kaynağını Seçin:",
        ("Twitter", "Haber Siteleri", "Manuel Test"),# veri kaynağı seçimine haber siteleri eklendi
        key="source_option", # burada streamlit bileşenleri için benzersiz kimlik (unique key) verir.neden kullanırız session state içinde bu selectbox’ın değerini saklayabilmek için.
                            # eğer key vermezsek aynı sayfada birden fazla selectbox varsa streamlit hata verebilir , değer session_state’te tutulmaz.
        on_change=clear_results # bu parametre kullanıcı bu seçimi değiştirdiğinde hangi fonksiyon çalıştırılsın sorusunun cevabıdır ,
                        # burada clear_results fonksiyonu çağrılır , yani kullanıcı Twitter --> Haber Siteleri diye seçimi değiştirdiğinde --> hafıza temizlenir , önceki arama / analiz sonuçları silinir , yeni seçime göre taze bir başlangıç yapılır.
    )
    st.markdown("---")




    query = ""   # query sorgu demek başlangıçta boş , kullanıcının gireceği arama metnini tutar.
    site_key = ""  # kullanıcının seçtiği haber sitesinin adını tutar
    category_key = ""  # seçilen sitenin hangi kategorisinin seçildiğini tutar.

    # bu değişkenler başta boş string olarak başlatılır ki aşağıdaki seçeneklerde doldurulabilsin.



    if source_option == "Twitter": # eğer kullanıcı twitter seçtiyse aşağıdaki kodlar çalışacak.
        st.subheader("Twitter Ayarları") # eğer kullanıcı twitter seçti ise alt başlık yazılır:

        # --- YENİ: Arama Tipi Seçimi ---
        search_type_display = st.selectbox(
            "Arama Tipini Seçin:",
            ("Anahtar Kelime / Hashtag", "Kullanıcı Adı"),key='search_type', on_change=clear_results
        )#


        # etiketi seçime göre değiştir , eğer kullanıcı "Hashtag / Anahtar kelime" seçtiyse label --> "Aranacak Metin (#teknofest gibi)" , eğer "Kullanıcı Adı" seçtiyse label --> "Aranacak Metin (@ olmadan)" , bu dinamik bir etiket. kullanıcı ne seçerse ona uygun açıklama gösteriliyor.
        label_text = f"Aranacak Metin {'(#teknofest gibi)' if search_type_display == 'Anahtar Kelime / Hashtag' else '(@ olmadan)'}"



        # burası arama metni girişi , kullanıcının yazdığı değer query değişkenine aktarılır.
        query = st.text_input(  # kullanıcıdan hashtag/kelime girmesi istenir ve sonuç query değişkenine aktarılır.
            label_text,
            placeholder="Örn: teknofest",
            key="query",
            on_change=clear_results
        )

        # API'ye gönderilecek tipi belirle , kullanıcı “Kullanıcı Adı” seçtiyse --> API’ye "username" gönderilir , diğer durumda --> "hashtag" gönderilir.
        search_type_api = 'username' if search_type_display == 'Kullanıcı Adı' else 'hashtag'         # yani bu satır kullanıcı seçimlerini API’nin anlayacağı dile çevirir.


    # Kullanıcı “Haber Siteleri” seçerse bu blok çalışır.
    elif source_option == "Haber Siteleri":
        st.subheader("Haber Sitesi Ayarları")

        # 1. site seçimi , site seçme kutusu
        site_key = st.selectbox(
            "Haber Kaynağını Seçin:",
            list(config.NEWS_SITES.keys()),  # config'deki site isimlerini getir , config.NEWS_SITES --> Python sözlüğümüzdü (dict) , .keys() --> sözlükteki site adlarını verir , "Sözcü", "Habertürk", "NTV" gibi ,kullanıcı seçim yapınca değer site_key değişkenine yazılır.
            key="site_key",
            on_change=clear_results
        )

        # 2. kategori seçimi (seçilen siteye göre değişir) burada seçilen siteye Göre kategori seçiyoruz Önemli bir yapı
        if site_key:
            category_key = st.selectbox(
                "Kategori Seçin:",
                list(config.NEWS_SITES[site_key].keys()),  # config.NEWS_SITES[site_key] --> seçilen sitenin kategorilerini verir , .keys() --> “Gündem”, “Spor”, “Dünya”, “Teknoloji” gibi kategorileri listeler. kısacası yani site_key = “NTV” seçilirse --> o sitenin kategorileri gösterilir.değer category_key değişkenine yazılır.
                key="category_key", # streamlit tüm bileşenleri tanımak için bir şeye ihtiyaç duyar her widget'ın benzersiz (unique) bir adı olmalı.key = widget'a verilen benzersiz kimliktir
               # key olmazsa ne olur aynı sayfada birden fazla selectbox varsa karışır streamlit hangi selectbox’ın hangi değer olduğunu çözemeyebilir Streamlit şöyle diyecektir --> “Hangisi hangisi? Bu iki widget birbirine benziyor, ayırt edemiyorum.”

                on_change=clear_results # burada on_change nedir , streamlit’te her kullanıcı etkileşimi (selectbox seçimi, text_input yazımı, radio değişimi…) bir olaydır.kullanıcı o widget’ın değerini değiştirdiği anda verilen fonksiyonu çalıştırır.yani kullanıcı seçim değiştirir --> streamlit otomatik olarak bir fonksiyon çağırır.
            )



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
            df = data_collector.fetch_tweets(query, search_type=search_type_api, count=config.TWITTER_MAX_RESULTS)

            # sonucunda df artık tweet metinleri + linkler içeren bir DataFrame olur.


    # kullanıcı veri kaynağı olarak kullanıcı "Haber Siteleri" seçtiğinde bu blok çalışır.
    elif source_option == "Haber Siteleri":
        if not category_key: # Kullanıcı kategori seçti mi seçmedi mi bunu kontrol eder , category_key = kullanıcının seçtiği kategori --> "Gündem", "Spor", "Dünya" gibi ---> streamlit’te kategori seçim kutusunu doldurduğumuzda streamlit değeri st.session_state['category_key'] içine koyar.
            st.warning("Lütfen bir kategori seçin.")
            st.stop()
        with st.spinner(f"{site_key} ({category_key}) haberleri çekiliyor..."): # bu satırda spinner bekleme animasyonu (loading spinner) açılır yani Yani kullanıcı şunu görür  meesela “NTV (Spor) haberleri çekiliyor…” , “Sözcü (Gündem) haberleri çekiliyor…” gibi , bu kullanıcıya programın donmadığını, arka planda veri çekildiğini ,işlemin sürdüğünü gösterir
            # Haber çekme fonksiyonunu çağırıyoruz
            df = data_collector.fetch_news_headlines(site_key, category_key, count=config.NEWS_MAX_RESULTS) # haber çeken fonksiyonu çağırıyoruz. bu fonksiyon RSS linkine gidip haber başlıklarını okuyor.sonuçları bir DataFrame olarak döndürüyor.
            # burada parametrelerimiz site_key kullanıcının seçtiği site adı. mesela "NTV" , category_key seçtiği kategori. mesela "Dünya" , count maximum kaç haber alınsın mesela 20


    # Manuel Test seçilirse
    elif source_option == "Manuel Test":

        df = pd.DataFrame({'text': [user_input]}) # kullanıcının yazdığı tek bir cümleyi tek satırlık DataFrame’e çeviriyoruz , çünkü analiz sistemi DataFrame formatında çalışıyor.



    # Arayüzde gösterilecek başlığı belirliyoruz , bu kısım sadece arayüzde kullanıcıya gösterilecek başlığı belirlemek için.
    if source_option == "Twitter":
            search_term = query # mesela twitter seçilirse kullanıcı "deprem" yazarsa , bunun gibi bir arama yaparsa   ekranda şöyle gösterilir Arama Terimi: deprem

    elif source_option == "Haber Siteleri":
            search_term = f"{site_key} - {category_key}" # haber siteleri seçilirse Bu iki değeri birleştirir site_key = "NTV" , category_key = "Spor" sonuç olarak ---> Arama Terimi: NTV - Spor

    else:
            search_term = "Manuel Metin" # Manuel Test seçilirse , yani kullanıcı kendi cümlesini yazıyorsa sabit bir başlık gösterilir , Arama Terimi: Manuel Metin

    # 4 adımda görselleştirmede "search_term" değişkenini header olarak kullanıyoruz




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
          st.header(f"📈 Analiz Sonuçları: {search_term}")
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
                st.metric("Pozitif", analysis_counts.get('positive', 0),delta=analysis_counts.get('positive', 0), delta_color="normal")
                st.metric("Negatif", analysis_counts.get('negative', 0),delta=-1*analysis_counts.get('negative', 0), delta_color="normal")
                st.metric("Nötr", analysis_counts.get('neutral', 0),delta=0, delta_color="off")


# delta = önceki değere göre değişim pozitif(+) bir değer verirsem yeşil ok negatif(-) bir değer verirsem kırmızı ok 0 verirsem ok olmaz
# streamlit’in st.metric() bileşeni ile metrik kutuları (istatistik kartları) oluşturuyor.
# burada mesela ilk metrikte label: "Toplam"  ve  value: tüm sentiment sayılarını topluyor
# mesela pozitif tweet sayısı 2.metrikte  value: pozitif tweet sayısı , delta: pozitif tweet sayısını tekrar veriyor --> yani değişim + değer kadar gösterilir , delta_color="normal" ise pozitif delta --> yeşil ok ve negatif delta --> kırmızı ok
# negatif tweet için delta negatif sayı çünkü -1 ile çapılıyor,delta hep negatif olur bu da kırmızı ok gösterir -- negatif değerlendirme sayıları kötü sonuç gibi gösterilmek istendiği için
# mesela nötr tweet delta 0 --> değişim yok delta color = off ok simgesi gizleniyor

    # 5.adım Detaylı veri gösterimi
          st.markdown("---") # Araya bir ayırıcı çizgi çekiyoruz
          with st.expander("📝 Detaylı Veriyi Gör"): # st.expander: Açılıp Kapanabilen bir kutu oluşturuyoruz.Sayfayı kalabalık göstermemek için tabloyu varsayılan olarak gizli tutuyoruz.Kullanıcı isterse tıklayıp detayları görebilir.
              # Link sütunu varsa göster, yoksa gösterme
              if 'link' in processed_df.columns: # 'link' sütunu var mı diye kontrol ediyoruz Eğer processed_df içinde bir link sütunu varsa, tabloyu 3 sütun ile göster ---> text, Duygu Durumu, link , ama link sütunu yoksa else blogunda verdiğimiz
                  st.dataframe(
                      processed_df[['text', 'Duygu Durumu', 'link']], # tabloyu sadece istediğin sütunlarla gösteriyoruz , yani dataframe’in içindeki tüm sütunları istemiyorum , tabloyu sadeleştirmiş oluyoruz

                      column_config={
                          "link": st.column_config.LinkColumn("Haber Linki")  # burada column_config kullanmışız ne işe yarıyor , streamlit’te tabloyu gösterirken belirli sütunlara özel davranış tanımlamayı sağlar.tabloyu gösterirken bir sütunu link, image, number, progress bar gibi özel formatta gösterebilirsin.
                            # st.column_config.LinkColumn  ise ---> Bu sütundaki değerleri tıklanabilir link yapar. ---> normalde bu link sadece düz metin olurdu. ama LinkColumn sayesinde tıklanabilir hale geliyor.
                            # biz burada column_config={} yapısnda kullanmışız , tablo gösterilirken "link" sütunu Haber Linki başlığıyla gözüksün.ve içindeki URL’ler tıklanabilir link olsun.
                      }
                  )

              else:
                st.dataframe(processed_df) # İşlenmiş ve analiz edilmiş son tabloyu göster.






# Burada aslında sıralı bir işlem gerçekleştiriyoruz:

# Kullanıcının girdiği metni alıyoruz.
# Metni bir DataFrame koyuyoruz.
# text_processor ile temizliyoruz.
# sentiment_analyzer ile , Yapay Zeka ile duygu analizi gerçekleştiriyoruz.
# Sonuçları visualizer ile grafiğe döküyoruz ve kullanıcıya sunuyoruz.
# Bu yapı sayesinde, ileride yeni bir veri kaynağı eklediğimizde de sadece değiştirmemiz yetecek; geri kalan (temizleme, analiz, görselleştirme) her şey aynı şekilde çalışmaya devam edecek. buradanda aslında modülerliğin modüler yapının uygunluğunu düzenli yapısını görüyoruz.











