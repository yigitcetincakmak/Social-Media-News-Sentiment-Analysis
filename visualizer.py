# import matplotlib.pyplot as plt  ---> matplotlip ile de pasta grafiği çizebilirdik ancak plotly ile daha ayrıntılı bir pasta grafiği oluşturabiliyoruz.daha etkileşimi olur.

import pandas as pd
import plotly.express as px


# burada fonksiyonumuz tek bir parametre alıyor(analysis_results) buda ---> sentiment_analyzer.py dosyamızdan gelen duygu sayımlarının adetlerini içeren tutan sözlüğümüzdü.
def create_sentiment_pie_chart(analysis_results):


    # bu şekilde tek satır şeklinde ki yazıma "dictionary comprehension" deniyor
    filtered_data = {k.capitalize(): v for k, v in analysis_results.items() if v > 0}
    # burada yapılan parametremizden , sözlüğümüzden gelen her bir anahtar mesela positive gibi ve değer mesela 10 çifti için döngü başlatıyor.("positive":10)
    # if v > 0 eğer değerimiz(v) sıfırdan büyükse (yani o duygudan en az 1 adet varsa ---> k.capitalize ---> anahtarın ilk harfini büyütüyor (positive ---> Positive) ve bu anahtarıda onun değeri ile birlikte "filtered data" adındaki yeni sözlüğümüze ekliyor
    # amaç burada sıfır adet olan pasta dilimlerini grafikte göstermemek ve görünüş açısından daha uygun olsun diye duygu durumların(etiketler) ilk harfini büyük yaptık

# bu satırın yaptığı aslında bu aşağıdaki yazmış olduğumuz işlemdir.


#             filtered_data = {}                           diye başlangıçta boş olan bir sözlüğümüz var
#             for k, v in analysis_results.items():            for ile aldığımız parametre sözlük içinde dolaşıyoruz ve anahtar(k) değer(v) ikilisini tek tek alıyoruz
#                 if v > 0:                o duygu durumundan en az 1 adet varsa
#                       yeni_anahtar = k.capitalize()                duygu durumunun(anahtar) ilk harfini büyük yap
#                       filtered_data[yeni_anahtar] = v                    ilk harfini büyük yaptıktan sonra o anahtarı değerinide ona atayarak yeni boş sözlüğümüze ekle


# bu döngü bittiğinde mesela şu şekilde birşey tutacak bu değişkenimiz --->  {"Positive": 10, "Negative":8 ,"Neutral": 2} gibi.


    # Eğer sözlüğümüz boş ise yani duygu durumlarının hepsi sıfır adet olarak gelmiş ise,analiz edilecek veri yok ise grfaik çizebileceğimiz bir veri yok ise bış değer --> none döndürsün
    if not filtered_data:
        return None

    # burada filtered_data sözlüğümüzü dataframe şekline dönüştürüyoruz , burada
    # list(filtered_data.keys()) ---> ile sözlüğümüzün anahtarlarını listeye çeviriyor ve bunu Duygu adında bir sütun haline getiriyor
    # list(filtered_data.values()) ---> burada da değerlerimizi listeye çeviriyor bunu da Sayı adında bir sütun yapıyor
    # ---> sonuç olarak df değişkenimiz iki sütunlu bir tablo bir dataframe halini almış oluyor ---> plotly grafiğini çizmek için de uygun bir halde olmuş olur.
    df = pd.DataFrame({
        "Duygu": list(filtered_data.keys()),
        "Sayı": list(filtered_data.values())
    })


    # burada renklerimizi belirliyoruz her bir duygu anahtarı için .
    # bu sözlükte anahtarlar dataframe de Duygu sütunundaki değerler ile eşleşir
    # buradaki değerlerimiz is hexedecimal renk kodlarımızdır
    color_map = {
        'Positive': '#4CAF50', # Yeşil
        'Negative': '#F44336', # Kırmızı
        'Neutral': '#FFC107'   # Sarı-Turuncu
    }

    # grafiğimiz için bir figür oluşturuyoruz
    fig = px.pie(
        df,         # kullancağımız verilerimiz
        values='Sayı',  # burada pasta dilimlerin büyüklüğünün df deki Sayı sütununa göre belirlensin diyoruz
        names='Duygu',  # pasta dilimlerinin isimleri Duygu sütunundan gelecek
        title="Duygu Analizi Sonuç Dağılımı",  # grafik başlığımız
        color='Duygu',  # pasta dilimlerinin renklerini Duygu sütunundaki değerlere göre renklendir diyoruz.
        color_discrete_map=color_map  # sözlükte belirlediğimiz renk haritasını kullanıyoruz
    )

    # burada oluşturduğumuz grafiğin görünümünü özelleştiriyoruz
    # .uptade_traces ---> traces burada grafikte çizilen elemanlardır yani bizde pasta dilimleri
    fig.update_traces(
        textposition='inside', # burada dilim üzerinde bulunan yazıların (yüzdesi ve etiketi) dilimin içnde gösterilmesini sağilıyor
        textinfo='percent+label',  # burada dilim içinde hem yüzde oranını hem etiket adı görünsün ---> mesela %50 Positive gibi
        hole=.3,  # pastanı ortasını bir boşluk delik oluşuruyor %30 luk
        pull=[0.05 if v == df['Sayı'].max() else 0 for v in df['Sayı']]  # burada hangi dilimin merkezden ne kadar dışarı itileceğini belirliyoruz , burada dataframe deki Sayı sütunundaki en buyuk değere sahip dilimi 0.05 birim dışarı itiyor.
    )
# yukarıda bulunan pull paramtresinin açık hali bu şekilde

#           en_buyuk_sayi = df['Sayı'].max()  ---> en buyuk sayıyı buluyoruz bunu değişkende tutuyoruz
#           pull = []                     ---> bos bir pull listsi oluşturduk
#           for v in df['Sayı']:         ---> listede bulunan her v değeri için --- tek tek alıyoruz
#                   if v == en_buyuk_sayi:    ---> v - en buyuk sayıya eşit ise pull listesine 0.05 ekle
#                          pull.append(0.05)
#                   else:                       ---> değise listeye 0 sayısını ekle
#                          pull.append(0)

#               ---> en sonunda [0.05, 0 , 0 ]  gibi ve benzerleri bir liste oluşacak mesela sadece 20 positiv değer olsa ---> [0.05] olur



    # .uptade_layout ---> grafiğin genel yerleşimi ve stilini ayarlıyor
    fig.update_layout(
        showlegend=True,  # oluştırduğumuz pasta grafiğinin yanında (sağında) dikey şeklinde bulunan hangi rengin hangi duyguya karşılık geldiğini gösteren açıklama kutsusunun(legend) görünür olmasını sağlıyor
        font=dict(size=16)  # grafikteki tüm yazıların mesela başlıklar , etiketler ,legend ---> yazı boyutu 16 piksel olark ayarlaıyor
    )

    return fig # en sonunda oluşturduğumuz figür döndürülür , farklı dosyalardan da çağrılıp kullanmak için döndürülebilir




