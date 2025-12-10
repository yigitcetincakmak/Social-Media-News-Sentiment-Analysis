const newsSites = {
    "Sözcü": ["Gündem", "Spor", "Dünya", "Teknoloji"],
    "Habertürk": ["Gündem", "Spor", "Dünya", "Teknoloji"],
    "NTV": ["Gündem", "Spor", "Dünya", "Teknoloji"],
    "Cumhuriyet": ["Gündem", "Spor", "Dünya", "Teknoloji"],
    "TRT Haber": ["Gündem", "Spor", "Dünya", "Bilim-Teknoloji"],
    "CNN Türk": ["Gündem", "Spor", "Dünya", "Teknoloji"],
    "BBC Türkçe": ["Ana Sayfa", "Ekonomi", "Sağlık", "Bilim", "Teknoloji"]
};

/*
newsSites bir JavaScript nesnesi (object)
Amaç: Her haber sitesinin sahip olduğu kategorileri bir listede toplamak.
Soldakiler --> Haber siteleri (key)
Sağdakiler --> Bu sitenin kategorileri (value / değer)*/



// const Sabit (constant) bir değişken tanımlar: Değişkenin kendisini yeniden atayamazsın (ör. newsSites = {} hata verir).Ancak const ile tanımlanan bir objenin içeriğini değiştirebilirsin. (Örn. newsSites['Yeni'] = [...] olur.)
//Kullanım amacı: değerin başka bir değere atanmaması gerektiğinde (sabit referans).


//let Blok-scope (sadece {} bloğu içinde geçerli) değişken tanımlar.Blok-scope (sadece {} bloğu içinde geçerli) değişken tanımlar.Değerini sonradan değiştirebilirsin: let currentSource = 'twitter'; currentSource = 'news';

/*Kısa özet:

const = referans değişmez (ama içini değiştirebilirsin).

let = tekrar atanabilir, blok içinde geçerli.*/


let currentSource = 'twitter';/*Uygulama şu anda Twitter’dan analiz yapacak demek.İleride kullanıcı başka kaynak seçebilir --> bu değişken güncellenir.*/
let sentimentChart = null; /*null başlangıçta bir şey yok demektir (boş gösterge). Başlangıçta grafik yok demek. Grafik sonradan oluşturulacak --> değişkene atanacak.*/


/*Sayfa tamamen yüklendiğinde çalışan kod. DOMContentLoaded nedir --> “Sayfa tamamen yüklendiğinde şu kodları çalıştır” demektir.
HTML --> tamamen yüklensin
CSS --> tamamen yüklensin
JavaScript --> çalışsın

Tam açıklama:
Tarayıcı HTML’i okumayı bitirdiği anda devreye giren olaydır (event).*/



//document.addEventListener('DOMContentLoaded', () => { ... })  Ne zaman çalışır --> Tarayıcı sayfanın HTML yapısını tamamen oluşturduğunda (DOM hazır olduğunda) bu fonksiyon çalışır.Amaç: HTML elementlerini (select, input, div vs.) güvenle JS ile seçip değiştirebilmek.
/*Neden DOMContentLoaded kullanılır? Eğer JS <head> içinde çalışıyorsa, HTML elementleri henüz oluşmamış olabilir. Bu event, “artık HTML hazır, DOM kullan” demek.*/

document.addEventListener('DOMContentLoaded', () => {
    const siteSelect = document.getElementById('news-site');/*Şimdi bu olay içine giren kodları tek tek açıklayalım: Haber sitesi seçim menüsünü doldurmak HTML’de id="news-site" olan elementi bulup döndürür.Eğer bulunamazsa null döner (o yüzden DOMContentLoaded sonrası kullanmak güvenlidir).
    Bu ne yapar? HTML’deki: <select id="news-site"></select> etiketini JavaScript’e getirir.--> Yani artık siteSelect, select kutusunun kendisidir.*/
    for (const site in newsSites) {/*Burası çok önemli Bu döngü şunu yapar:newsSites objesinin içindeki her sitenin adını tek tek alır.Yani sırayla:"Sözcü","Habertürk","NTV"...*/
        const opt = document.createElement('option');//Yeni bir <option> etiketi oluşturur.HTML karşılığı:<option></option>  ,  Yeni bir HTML elementi oluşturur Ancak oluşturulan element şu an DOM’un içinde değil, yalnızca bellekte Sonra özellikleri ayarlanır (opt.value = ..., opt.innerText = ...) ve DOM’a eklenir..
        opt.value = site; // Seçeneğin değeri site adı olur. örn: <option value="Sözcü">
        opt.innerText = site; // Kullanıcının göreceği yazı belirlenir. örneğin <select> <option value="Sözcü">Sözcü</option>   , <option> Sözcü </option> gibi
        siteSelect.appendChild(opt);//Oluşturduğumuz <option>, select kutusuna eklenir.  bunu <select> içine ekle.
        //Sonuç: Seçim menüsü otomatik olarak tüm haber siteleri ile doldurulur.
    }
    updateCategories();// Kullanıcının seçtiği haber sitesine göre kategori menüsünü günceller./*Yani: Sözcü seçiliyse --> Gündem/Spor/Dünya/Teknoloji BBC Türkçe seçiliyse --> Ana Sayfa/Ekonomi/Sağlık/Bilim/Teknoloji Kod burada yok ama mantığı budur.*/
    loadHistory();//Bu büyük ihtimalle: Kullanıcının daha önce yaptığı analizleri yükler.Örn: localStorage’dan geçmiş tweet analizlerini getirme.
    checkTheme();//Bu da uygulamanın: Açık / Koyu tema ayarını kontrol eder.Muhtemelen localStorage’da theme=dark varsa gece modunu açıyordur.
});

/*for..in içinde const opt = document.createElement('option'); neden const?

const opt ile o döngü adımı için sabit bir referans oluşturuyorsun. Döngü sonraki iterasyona geçince opt tekrar yeni element olur (blok scope).

const burada güvenlidir çünkü opt o blok içinde yeniden atanmaz; her döngü turunda yeni bir opt tanımlanır.*/









/*.value ve .innerText / .textContent farkı

.value:
Form elementlerinin (input, select, option) değerini (value attribute) verir veya ayarlar.
<option value="Sözcü">Sözcü</option> — opt.value = "Sözcü".

.innerText:
Bir elementin görünen metnini verir/ayarlar (render edilen metin).
Tarayıcı metni nasıl gösteriyorsa onu alır (CSS, hidden vs. etkilenebilir).

.textContent ile fark:
textContent ham metin içeriğini verir, innerText ise stil ve layout’a göre hesaplanan görünür metni döner.
Genelde textContent daha hızlı ve güvenilirdir; ama çoğu durumda innerText da işe yarar.*/


/*appendChild ne yapar?

Bir DOM node’unun içine bir çocuk (child) elementi ekler.
siteSelect.appendChild(opt) → <select> içine yeni <option> eklenir.
alternatif yöntem siteSelect.append(opt); // appendChild yerine kullanılabilir (hem text hem node alır)*/










/*function --> JavaScript’te fonksiyon tanımlama kelimesi.Fonksiyon, tekrar tekrar çalıştırabileceğin kod bloğudur.switchTab → fonksiyonun adı. (Bununla çağırırsın.)*/
/*(source) --> fonksiyona gelen parametre. Buraya örneğin 'twitter', 'news' veya 'youtube' gibi string gönderiliyordu. source içeriği fonksiyon içinde kullanılır.*/


function switchTab(source) {
    currentSource = source;//currentSource global (daha önce let currentSource = 'twitter' ile tanımlanmış) değişkene source değerini atıyor.
    document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));/*document --> tarayıcıdaki HTML sayfasının tamamını temsil eden obje..querySelectorAll('.tab-btn') --> CSS seçici kullanarak sayfadaki tüm .tab-btn sınıfına sahip elementleri seçer. Dönen şey bir NodeList (liste benzeri) objesidir.
    querySelectorAll CSS seçici sözdizimini destekler (class için .class, id için #id, etiket için div gibi)..forEach(...) --> NodeList içindeki her bir elemana sırayla işlem uygulamak için kullanılır.
    btn => btn.classList.remove('active') --> arrow function (ok fonksiyonu). Her btn için btn.classList.remove('active') çalışır.
    classList.remove('active') --> o elementin sınıf listesinden active sınıfını siler (CSS ile aktif görünüm kaldırılır). Kısaca: bütün sekme butonlarının active sınıfını temizliyor (hepsini pasif yapıyor).*/
    event.currentTarget.classList.add('active');/*Amaç: tıklanan butona active sınıfını eklemek (o butonu aktif göstermek).
    event.currentTarget nedir? event --> gerçekleşen olay (click event objesi).currentTarget → olay dinleyicisini eklediğin element (genelde tıklanan buton).event.currentTarget.classList.add('active') --> tıklanan butona active sınıfını ekler.Kısaca: bu satır tıklanan butonu aktif yapar,*/
    document.querySelectorAll('.input-group').forEach(el => el.classList.add('hidden'));
    /*querySelectorAll('.input-group') --> .input-group sınıfına sahip tüm input gruplarını seçer (Twitter inputs, news inputs, youtube inputs).
    .forEach(el => el.classList.add('hidden')) --> her birine hidden sınıfını ekler. Yani tüm input alanlarını gizler.
    el burada forEach döngüsündeki geçici isimdir (her iterasyonda sıradaki elementi temsil eder). İsim olarak el, item, node vs. olabilir; işlev değişmez.*/
    document.getElementById(`${source}-inputs`).classList.remove('hidden');
    /*`${source}-inputs` --> bu template literal (şablon string) kullanımı. Backtick ` ile yazılır; ${...} içine JS ifadesi konur. Eğer source == 'twitter' ise bu ifade 'twitter-inputs' olur.
    document.getElementById('twitter-inputs') --> id'si twitter-inputs olan HTML elementini bulur.
    .classList.remove('hidden') --> o elementten hidden sınıfını kaldırır, böylece görünür olur.
    Kısaca: önce tüm inputları gizle, sonra seçilen sourcee ait input grubunu göster.*/
}





function updateCategories() {
    const site = document.getElementById('news-site').value;/*document.getElementById('news-site') --> <select id="news-site"> elementini bulur..value --> seçicide şu an seçili olan option'un value'sunu verir (ör. "Sözcü").const site = ...; --> bu değeri site adlı değişkene atar.*/
    const catSelect = document.getElementById('news-category');//kategori seçimi yapılacak <select id="news-category"> elementinin referansı (DOM öğesi).Bu öğeyi boşaltıp yeni <option>lar ekleyeceğiz.
    catSelect.innerHTML = ''; //innerHTML --> bir elementin içindeki HTML içeriğini temsil eder.
    newsSites[site].forEach(cat => { /*siteye karşılık gelen kategori dizisi (ör. ["Gündem","Spor",...])..forEach(cat => { ... }) --> dizinin her elemanı (her kategori cat) için iç blok çalışır.cat burada geçici değişken; her iterasyonda sıradaki kategori string'i tutar.*/
        const opt = document.createElement('option');//yeni <option> elementi oluşturur.
        opt.value = cat; //option'un value attribute'unu ayarlar.
        opt.innerText = cat;//kullanıcıya gösterilecek yazı.
        catSelect.appendChild(opt);//option'u kategori <select> ine ekler.

     // Kısaca: seçilen siteye ait kategorilerin <select id="news-category"> içine yazılmasını sağlar.
    });
}




/*async bir fonksiyonun Promise döndüreceğini belirtir. İçinde await kullanmana izin verir. async fonksiyon çağrıldığında otomatik olarak bir Promise döner; fonksiyon içinde return ile dönen değer Promise.resolve(...) haline gelir.await ancak async içinde kullanılabilir.*/
/*örnek
async function foo() { return 5; }

   foo() döndürdüğü şey Promise.resolve(5)
*/






async function startAnalysis() {
    document.getElementById('results-area').classList.add('hidden');/*DOM erişimleri: document.getElementById(...) ve classList.add/remove*/
 /*document.getElementById('results-area'): HTML sayfasında id="results-area" olan elementi bulur. Eğer yoksa null döner.
 .classList DOMTokenList döndürür. add('hidden') veya remove('hidden') CSS sınıflarını ekler/çıkarır.*/

    document.getElementById('loader').classList.remove('hidden');

    let inputVal = '', subOpt = ''; //Boş string ile başlatılmış

    //Koşullara göre hangi input alanından değer okunacağı belirleniyor:
    //Twitter ise twitter-query inputu alınır.News ise news-category ve news-site.Diğer durumda (ör. youtube) youtube-url.
    if (currentSource === 'twitter') { //=== kesin eşitlik kontrolü (tip dönüşümü yapmaz). == yerine === tercih edilir.
        inputVal = document.getElementById('twitter-query').value;
        subOpt = document.getElementById('twitter-type').value === 'username' ? 'Kullanıcı Adı' : 'Hashtag';/*Ternary operatörü: condition ? valueIfTrue : valueIfFalse şeklinde kısa if-else.Yani twitter-type inputunun değeri 'username' ise subOpt = 'Kullanıcı Adı', değilse 'Hashtag'.*/
    } else if (currentSource === 'news') {
        inputVal = document.getElementById('news-category').value;
        subOpt = document.getElementById('news-site').value;
    } else {
        inputVal = document.getElementById('youtube-url').value;
    }

    if(!inputVal) {//! mantıksal NOT operatörü. !inputVal ifadesi inputVal falsey ise true olur. Yani bu if bloğu şunu kontrol eder: inputVal dolu değilse (yani kullanıcı gerekli alanı doldurmamışsa).İçeride showToast(...) ile kullanıcıya hata bildirimi gösterilip loader gizleniyor ve return; ile fonksiyon sonlandırılıyor..
        showToast("Lütfen gerekli alanları doldurun.", "error");//showToast muhtemelen uygulamada tanımlı bir yardımcı fonksiyon; kısa bildirim (toast) gösterir. Burada bir mesaj ve tip ("error") veriliyor.
        document.getElementById('loader').classList.add('hidden');
        return;
    }

    try {//try: içeride hata (exception) oluşabilecek kodu koyarsın.
        const res = await fetch('/api/analyze', { // fetch ve await detayı fetch(url, options) modern tarayıcıların sunduğu web API'si; ağ isteği yapar ve Promise<Response> döner.
/*await
await fetch(...) ile fetch tamamlanana kadar (Promise resolve olana kadar) beklenir ve res Response nesnesi olur.
await burada async fonksiyonun içerisinde olduğundan kullanılabilir.
Not: await tarayıcıdaki main thread'i bloklamaz — sadece fonksiyonun yürütmesini bekletir; event loop ve UI çalışmaya devam eder.*/

           /*options içinde:
method: 'POST' — HTTP yöntemi (GET, POST, PUT, DELETE vb).
headers: {'Content-Type': 'application/json'} — sunucuya gönderilen verinin JSON olduğunu belirtir.
body: JSON.stringify(...) — istek gövdesi; JSON olarak gönderiliyor (string halinde).*/

            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ source: currentSource, input_value: inputVal, sub_option: subOpt }) //JSON.stringify(obj) nesneyi JSON formatında string'e çevirir. HTTP isteğinde body ancak string/Blob/FormData vs. olabilir; bu yüzden JSON string gönderiliyor.
            //Gönderilen veri örneği (string halinde): {"source":"twitter","input_value":"somequery","sub_option":"Kullanıcı Adı"} Sunucu /api/analyze endpoint'i gövdeyi (body) JSON olarak alıp Content-Type: application/json başlığı ile parse edebilir.

        });
        const data = await res.json(); // res.json() Response üzerinde bulunan bir metottur; Promise döner ve HTTP yanıtının gövdesini JSON olarak parse eder (otomatik olarak JSON.parse gibi).
        //Önemli: res.json() da asenkron olduğu için await ile beklenir.Eğer sunucu JSON dönmezse res.json() hata atabilir (ör. parse error).

        if(res.ok) renderResults(data, inputVal);//res.ok boolean: HTTP durumu 200–299 aralığındaysa true. Yani "başarılı" HTTP cevap olup olmadığını kolay kontrol etmeye yarar.renderResults(data, inputVal) muhtemelen UI'ı dolduran fonksiyon — sunucudan gelen data'yı kullanarak results-area'yı günceller.
        else showToast('Hata: ' + data.error, "error");//else durumda showToast ile sunucunun döndürdüğü data.error mesajı gösteriliyor.

    } catch (e) {//catch (e): try içinde atılan exception'ı yakalar; e hatanın nesnesi (Error objesi).
        showToast('Sunucu ile bağlantı kurulamadı!', "error");
    } finally { //finally: hem try başarılı olsa hem hata olsa kesinlikle çalışır. Genelde temizleme işlemleri (loader kapama, resource serbest bırakma) için kullanılır.
    //Örnekte: ağ isteği yapılırken hata olursa kullanıcıya "Sunucu ile bağlantı kurulamadı!" gösteriliyor; loader her durumda gizleniyor ve loadHistory() çağrılıyor.
        document.getElementById('loader').classList.add('hidden');//finally sunucudan yanıt alsak da alamasak da çalışır: loader gizlenir ve loadHistory() çağrılır.
        loadHistory();
    }
}

/* 14) res, res.status, res.headers, res.ok — Response nesnesi

res.status: HTTP durum kodu (ör. 200, 404, 500).

res.statusText: durum metni (ör. "OK", "Not Found").

res.headers: HeadersCollection; res.headers.get('Content-Type') gibi çağrılabilir.

res.ok: boolean, status 200–299 aralığındaysa true.*/





//document nedir? Web sayfasındaki tüm içeriği temsil eden global nesne. Sayfadaki HTML elementlerine erişmemizi sağlar.
//renderResults adında bir fonksiyon tanımlar
function renderResults(data, title) {
    //getElementById('results-area') --> belirtilen id'ye (id="results-area") sahip olan HTML elementini döndürür
    // .classList nedir ---> O elementin HTML class listesini yönetmek için kullanılan nesne. İçinde add, remove, toggle, contains gibi metotlar bulunur.
    //Elementin class listesinden 'hidden' sınıfını çıkarır. 'hidden' CSS ile display: none veya visibility: hidden yapar; kaldırınca görünür olur. bu satır, sonuç alanını görünür hâle getirir.
    document.getElementById('results-area').classList.remove('hidden');

    //getElementById('result-title'): id="result-title" olan elementi bulur.
    //.innerText nedir --> Elementin içerisindeki görünür metni ayarlar veya okur. (HTML etiketleri değil; sadece düz metin.)
    document.getElementById('result-title').innerText = `Analiz Sonucu: ${title}`;
    //title = "Twitter" ise sonuç: "Analiz Sonucu: Twitter".

    animateValue("total-badge", 0, data.total, 2000, " Metin");
    animateValue("res-pos", 0, data.counts.positive || 0, 2000);
    animateValue("res-neg", 0, data.counts.negative || 0, 2000);
    animateValue("res-neu", 0, data.counts.neutral || 0, 2000);

    setTimeout(triggerConfetti, 500); //JavaScript'in bir fonksiyonu gecikmeli çalıştırmasını sağlar.
    // İlk parametre: çalıştırılacak fonksiyon (burada triggerConfetti — fonksiyonun adı).İkinci parametre: gecikme süresi milisaniye cinsinden (burada 500 ms = 0.5 saniye).
    //0.5 saniye sonra triggerConfetti() fonksiyonu çağrılır.ekranda konfeti animasyonu gösterir.



    //CSS seçici kullanarak sayfadaki ilk eşleşen elementi döndürür.'#result-table tbody' demek: id="result-table" olan elementin altındaki <tbody> elementini seç.
    //querySelector ile hem id hem sınıf hem etiket kombinasyonları seçebiliriz,seçilen elementi tbody değişkenine atandı
    const tbody = document.querySelector('#result-table tbody');
    tbody.innerHTML = '';
    //innerHTML, bir elementin içindeki HTML'i (etiketlerle beraber) okur/yazar , ='' ile içi boşaltılır — yani mevcut tablo satırları temizlenir.
//innerText ile innerHTML arasındaki fark: innerText sadece metin; innerHTML HTML etiketlerini de içerir ve render edilir.



    //data objesinin içinde bir dizi (array). Her eleman row olarak adlandırıl.. Örneğin: data.table = [ { 'Duygu Durumu': 'positive', text: '...', link: '...' }, ... ]
    //row => { ... } (arrow function) ES6 arrow function (ok fonksiyonu). function(row) { ... } ile aynı işi yapar . tablodaki her satır için içteki işlemleri yapacak.
    //.forEach(...) dizi üzerinde döner ve içindeki her eleman için verilen fonksiyonu çağırır.
    //row['Duygu Durumu'] row bir obje; içinden 'Duygu Durumu' adındaki alanı alıyoruz(Alternatif--> row.DuyguDurumu)
    //=== operatörü Sıkı eşitlik: hem değer hem tür aynı mı diye kontrol eder. === 'positive' demek değerin  string olarak 'positive' olup olmadığını kesin kontrol eder.

    // ? : (ternary operator) nedir --> condition(durum) ? valueIfTrue : valueIfFalse — kısa if/else. Burada iç içe ternary(üçlü) kullanılmış: Eğer 'positive' ise '#00b894'.
    // Değilse eğer 'negative' ise '#d63031'. Yoksa '#fdcb6e' (nötr için). Sonuç: statusColor değişkeni, duyguya göre satır rengini tutar.

    //  => (arrow function) kısa fonksiyon yazımı: (a) => a * 2

    data.table.forEach(row => {
        let statusColor = row['Duygu Durumu'] === 'positive' ? '#00b894' : (row['Duygu Durumu'] === 'negative' ? '#d63031' : '#fdcb6e');
       // bir string değişken (rowHTML). İçinde HTML satırı <tr>...</tr> tutuyor.
       // ${...} ile row objesinden değer yerleştiriliyor

        let rowHTML = `
            <tr>
                <td style="color:${statusColor}; font-weight:bold;">${row['Duygu Durumu'].toUpperCase()}</td> // toUpperCase() String metodudur; tüm harfleri büyük yapar. Örnek: 'hello'.toUpperCase() --> 'HELLO'.
                <td>${row.text.substring(0, 80)}...</td> // metinden ilk 80 karakter alınıp metin sonuna üç nokta ekleniyor . substring(start, end) String'in bir parçasını döndürür. start dahil, end hariç. Örnek: 'abcde'.substring(0,3) ---> 'abc'.
                <td><a href="${row.link}" target="_blank">Git <i class="fas fa-external-link-alt"></i></a></td> // <a href="${row.link}" target="_blank"> — link ekleniyor; target="_blank" yeni pencerede/sekmede aç demek.
            </tr>
        `;
        tbody.innerHTML += rowHTML; //Mevcut innerHTML'in sonuna rowHTML string'ini ekler. Yani sıfırlanıp sonradan her row için satır eklenir.
    });

    //Burada sentimentChart değişkeninin varlığını kontrol ediyoruz.     .destroy() ---> ne yapar Bu, Chart.js kütüphanesinin bir metodu. Var olan grafiği DOM'dan temizler ve belleği boşaltır; aynı canvas üzerinde yeniden chart oluşturmak için önceki grafiği yok eder.
    //Neden gerekli? Aynı canvas üzerinde üst üste grafik yaratmamak ve hafızada sızıntı olmaması için önceki grafiği yok etmek gerekir.
    if(sentimentChart) sentimentChart.destroy();
    const ctx = document.getElementById('sentimentChart').getContext('2d');//getElementById('sentimentChart') <canvas id="sentimentChart"></canvas>  canvas elementi seçer.   getContext('2d') nedir --> Canvas'ın 2D çizim bağlamını (context) döndürür. Chart.js bu ctx'yi kullanarak grafiği çizer.  ctx: artından new Chart(ctx, {...}) ile kullanılacak nesne.
    sentimentChart = new Chart(ctx, {
        type: 'doughnut', //Grafik tipi halka (doughnut — pasta grafiğe benzer orta boşluklu).
        data: { // data.labels Grafikte gösterilen etiketler (legendda ve hover metinlerinde kullanılır).
            labels: ['Pozitif', 'Negatif', 'Nötr'],
            datasets: [{ //datasets[0].data Grafik için veriler: pozitif, negatif, nötr sayıları.
                data: [data.counts.positive, data.counts.negative, data.counts.neutral],
                backgroundColor: ['#00b894', '#d63031', '#fdcb6e'], // backgroundColor Her dilim için arka plan rengi (burada hex renk kodları).
                borderWidth: 0 // dilimler arasındaki kenar çizgi kalınlığı; 0 = yok.
            }]
        },
        options: {//options Grafik davranışı ayarları:
            responsive: true, // canvas boyutunu ekran boyutuna göre uyarlama.
            maintainAspectRatio: false, // orantıyı korumama (kutunun boyutuna uyma).
            animation: { animateScale: true, animateRotate: true } // animation — grafiğin büyürken veya dönerken nasıl animasyon yapacağı. Döngüsel (doughnut) grafik çizilir ve sentimentChart değişkenine atanır.
        }
    });
    // scrollIntoView(...) nedir --> Seçilen elementi görüntülemek için sayfayı kaydırır (scroll).
    document.getElementById('results-area').scrollIntoView({ behavior: 'smooth', block: 'start' });
}  //Parametre olarak verilen objemiz { behavior: 'smooth', block: 'start' }
// burada ehavior: 'smooth' — kaydırmanın yumuşak (animasyonlu) olmasını ister; instant ya da default olabilirdi.
//block: 'start' — elementi görünümün üstüne hizala (başlangıç). Başka seçenekler vardır (center, end, nearest).







// async ne demek --> bu fonksiyonun içinde await kullanabileceğimizi belirtir. async ile tanımlanan fonksiyonlar her zaman bir Promise döner (arka planda).
//kullanım amacı: asenkron (zaman alabilecek) işlemleri (fetch, veritabanı çağrısı vb.) daha okunaklı await sözdizimiyle yazmak.Ne beklenir --> Fonksiyon çağrıldığında, içerideki await ifadeleri tamamlanana kadar beklenir (ama tarayıcı bloke olmaz — diğer işler çalışmaya devam eder).
async function loadHistory() {
    // 1. Tabloyu Doldurma

    // fetch(url) nedir --> Web API: belirtilen url'e HTTP isteği yapar ve Promise döner. Başarılıysa Response nesnesi elde edilir.
   // peki await burada ne yapıyor --> fetch tamamlanana kadar (sunucudan yanıt gelene kadar) bekler ve res değişkenine Response nesnesini atar. Kod bu satırda "bekler", ama tarayıcı bloke olmaz.
    const res = await fetch('/api/history'); //res artık Response tipinde bir nesne. İçinde status, ok, json() gibi metotlar var.
    const data = await res.json(); // res.json() Response nesnesinin bir metodu.Sunucudan gelen metni (response body) JSON olarak ayrıştırır (parse eder) ve Promise döner. Promise tamamlandığında JS objesi (veya dizi) elde edilir.
    // await burada ne yapıyor JSON ayrıştırma tamamlanana kadar bekler ve data içine gerçek JS objesini koyar.
    const tbody = document.querySelector('#history-table tbody'); // document.querySelector(selector) CSS seçici (selector) --> kullanarak sayfadaki ilk eşleşen elementi döndürür.
    //'#history-table tbody' seçici ne demek , id="history-table" olan elementin içindeki <tbody> elementini seçer. Yani <table id="history-table"><tbody>...</tbody></table> içindeki tbody.const tbody Seçilen DOM elementi tbody değişkenine atanır. Bu değişken ile tabloya satır ekleyebiliriz.


    tbody.innerHTML = ''; // innerHTML nedir -->  bir elementin HTML içeriğini (etiketlerle birlikte) temsil eder. Atama yaparsanız içeriği değiştirirsiniz. ='' --> Tablonun önceki satırlarını temizler — yani boş bırakır. Neden --> yeniden yüklerken eskileri silip yeni veriyi baştan eklemek daha güvenli.
    data.forEach(row => { // data dizisinin her elemanı için , row => { ... } Arrow function (kısa fonksiyon tanımı). function(row) { ... } ile aynı.
       // burad amaç her row için tabloya bir <tr> eklemek.
        const dateStr = row.analiz_zamani.split(' ')[0]; // row.analiz_zamani --> row objesindeki analiz_zamani alanı. Örneğin "2025-12-06 11:00:00". .split(' ') nedir --> string metodudur. belirtilen karaktere göre (burada boşluk ' ') string'i parçalara böler ve bir dizi döner.   [0] ne yapıyor --> oluşan dizinin ilk elemanını alır. yani sadece tarih kısmı "2025-12-06".
        //Tabloya satır ekleme
        tbody.innerHTML += ` // Mevcut HTML içeriğinin sonuna yeni string ekler. Yani her row için bir <tr> eklenir.      '...' --> çok satırlı string yazmayı sağlar ve ${...} ile JS ifadelerini içine gömmeyi mümkün kılar.
            <tr> //her row için bir <tr> eklenir.

                <td>${dateStr}</td>
                <td>${row.kaynak_tipi}</td> //veri kaynağı tipi (ör. "twitter").
                <td>${row.kaynak_detay}</td> // detay (kullanıcı adı, arama terimi vb.).
                <td>${row.pozitif_sayisi}</td>
                <td>${row.negatif_sayisi}</td> //sayı değerleri.
                <td>${row.notr_sayisi}</td>

            </tr>
        `;
    });

    // 2. Toplam İstatistikleri Çek, Hesapla ve Animate Et
    try {
        const statsRes = await fetch('/api/history/stats'); // /api/history/stats endpoint'ine GET isteği yapar. await ile bekler. statsRes bir Response nesnesi olur.
        const stats = await statsRes.json();

        // Yüzdeleri Hesapla
        const total = stats.total; // stats.total değerini total değişkenine atar. Bu toplam kayıt sayısıdır.
        // Eğer toplam 0 ise 0, değilse yüzdeyi hesapla ve tek ondalık basamak al (toFixed(1))

        const posPct = total > 0 ? ((stats.pos / total) * 100).toFixed(1) : 0; // Pozitiflerin yüzdesini hesaplamak; toFixed(1) ile tek ondalık basamağa yuvarlamak.total > 0 ? ... : 0 — ternary operator: Eğer total sıfırdan büyükse yüzdeyi hesapla, değilse 0 ata. Böylece total = 0 durumunda 0/0 hatası önlenir.
        //(stats.pos / total) * 100 — pozitif sayısını toplam sayıya bölüp 100 ile çarpar (yüzde)..toFixed(1) — sayıyı stringe çevirir ve 1 ondalık basamak gösterir. Örneğin: 12.345.toFixed(1) --> "12.3".           .toFixed(1) string döndürür (ör. "12.3"). Eğer sayısal işlemler yapacaksak parseFloat(... ) kullanmamız gerekecek.
        const negPct = total > 0 ? ((stats.neg / total) * 100).toFixed(1) : 0;
        const neuPct = total > 0 ? ((stats.neu / total) * 100).toFixed(1) : 0;

        // animateValue'ya HTML formatında suffix (son ek) gönderiyoruz
        // <small> etiketi ve 'pct-text' sınıfı ile CSS'de küçülteceğiz


        // animateValue çağrısı — toplam sayı
        animateValue("hist-total", 0, stats.total, 2500); // // peki animateValue burada nasıl çağrıldı , parametreler  "hist-total" — hedef elementin id (örn. <span id="hist-total">0</span>).  0 — başlangıç değeri.   stats.total — bitiş değeri (hedef).   2500 — süre milisaniye cinsinden (2500 ms = 2.5 saniye).
           // 0'dan stats.total'a doğru sayıyı animasyonla arttırır.

        // animateValue çağrısı — pozitif ile yüzde ekleme
        //Burada parametre olarak bir HTML string gönderiliyor: ` <small class="pct-text">(%${posPct})</small>` Bu , sayı değerinin yanına eklenecek metindir. Örneğin sonuç: 40 <small class="pct-text">(%40.0)</small>
// bunun dışında "hist-pos" — hedef element id'si.  0 — başlangıç.    stats.pos — hedef sayı.   2500 — süre.
        animateValue("hist-pos", 0, stats.pos, 2500, ` <small class="pct-text">(%${posPct})</small>`);
        animateValue("hist-neg", 0, stats.neg, 2500, ` <small class="pct-text">(%${negPct})</small>`);
        animateValue("hist-neu", 0, stats.neu, 2500, ` <small class="pct-text">(%${neuPct})</small>`);

    } catch (error) {
        console.error("İstatistikler yüklenemedi:", error);
    }
}








// --- YARDIMCI FONKSİYONLAR ---

// animateValue bir fonksiyon tanımlaması. Bu fonksiyon çağrıldığında bir sayıyı animasyonla start değerinden end değerine getirir ve sonucu sayfada gösterir.
// Parametreler (girdi):   objId (string): Değiştirilecek HTML elementinin id değeridir. Örnek: "hist-pos".     start (number): Animasyonun başlangıç sayısı (ör. 0).     end (number): Animasyonun hedef/bitiş sayısı (ör. 120).     duration (number): Animasyonun süresi milisaniye cinsinden (ör. 2500 = 2.5 saniye).      suffix (string, opsiyonel, default ""): Sayının sonuna eklenecek metin veya HTML. Örn. " <small>(%40.0)</small>". = ""  burada "varsayılan değer" atar; çağırırken bu parametre verilmezse boş string kullanılır.

function animateValue(objId, start, end, duration, suffix = "") {

    // Elementi DOM'dan alma işlemi
    const obj = document.getElementById(objId); // Sayfadaki HTML içinde id="..." olan elementi bulur ve döndürür
    let startTimestamp = null; // Başlangıç zamanını tutmak için değişken tanımlaması  null ile başlatılması, "henüz başlama zamanı yok" demektir.  let ile tanımlandığı için fonksiyon içinde bu değişkenin değeri değiştirilecektir (ilk çağrıda timestamp ile doldurulur).
    const step = (timestamp) => {
        if (!startTimestamp) startTimestamp = timestamp; // Başlangıç zamanını ayarlama --> Eğer startTimestamp hâlâ null ise (yani ilk frame) startTimestamp'ı şu anki timestamp ile doldurur. Böylece animasyonun başlangıç zamanı belirlenir. timestamp her frame için değişir; başlangıç referansını alıp daha sonra geçen süreyi (timestamp - startTimestamp) şeklinde hesaplamak için.
        const progress = Math.min((timestamp - startTimestamp) / duration, 1); // (timestamp - startTimestamp): Animasyonun başladığı andan beri geçen süredir (ms). ... / duration --> Bu, geçen sürenin toplam süreye oranını verir; örn. 500ms geçen ve duration 2500ms ise sonuç 0.2 olur.  Math.min(..., 1): Oranı 1'den büyük olmasını engeller. Yani progress en fazla 1 olur. (1 = animasyon tamamlandı)
                                                                // progress anlamı: 0 ile 1 arasında bir değer; 0 = hiç ilerleme yok, 1 = tamamlandı. Bu oranı kullanarak aradaki değeri hesaplarız.
        // innerText yerine innerHTML kullanıyoruz ki <span> veya <small> etiketleri çalışsın
        obj.innerHTML = Math.floor(progress * (end - start) + start) + suffix;
        //Math.floor(progress * (end - start) + start)  , (end - start) = hedef farkı (ör. 120 - 0 = 120). progress * (end - start) = bu farkın progress oranına göre kaç olduğunu verir (ör. 0.5 * 120 = 60). + start = başlangıç değerini ekleyerek gerçek anlık değeri elde eder (ör. 60 + 0 = 60). Math.floor(...) = ondalık kısmı aşağı yuvarlar. Yani 60.8 -> 60. Bu genelde sayaçlarda "kesin tam sayı" göstermek için tercih edilir. .Eğer end < start ise bu formül geriye doğru (azalan) animasyonu da destekler (ör. start=100 end=0).
       // + suffix hesaplanan sayıya suffix string'ini ekler. Örneğin suffix = ' <small>(%40.0)</small>' ise sonuç '60 <small>(%40.0)</small>'.
        //obj.innerHTML = ... Elementin HTML içeriğini (innerHTML) bu string ile değiştirir. innerHTML kullanıldığı için suffix içindeki HTML etiketleri (<small>, <span>) render edilir.


        // burası Animasyonun devam/bitim kontrolü
        if (progress < 1) window.requestAnimationFrame(step);
        // if (progress < 1): Animasyon henüz tamamlanmadıysa (progress 1'den küçükse), bir sonraki frame için step fonksiyonunu yeniden çağır.

    };
    window.requestAnimationFrame(step); // tarayıcıya "sonraki repaint (yeniden çizim) döngüsünde step fonksiyonunu çalıştır" demektir.requestAnimationFrame her çağrıldığında callback'e yeni bir timestamp gönderilir.
}                   // Sonuç olarak --> step kendini tekrar çağırarak animasyonu oluşturur; progress 1 olduğunda (veya aşarsa) döngü durur.


// konfeti gösteren küçük yardımcı fonksiyon. ekranda konfeti efekti başlatır
function triggerConfetti() {
    confetti({ particleCount: 150, spread: 80, origin: { y: 0.6 }, colors: ['#004aad', '#00cec9', '#ff7675'] });
} // Konfeti parametreleri  particleCount: 150 — kaç adet parçacık oluşturulsun (sayısı).  spread: 80 — konfeti yayılma açısı/dağılımı; daha büyük = daha geniş yayılır.
//origin: { y: 0.6 } — konfeti başlangıç noktası (x,y).   y: 0.6 demek ekranın yükseklik koordinatının %60'ından başla demektir. (x yoksa ortadan başlar) , colors: ['#004aad', '#00cec9', '#ff7675'] — parçacık renkleri; hex renk dizisi.



// document.getElementById('theme-toggle') Sayfada id="theme-toggle" olan elementi seçer.
const themeBtn = document.getElementById('theme-toggle');// const themeBtn: Buton referansını tutar.mesela bu değişken ile daha sonra event listener (ör. click) ekleyebiliriz
const body = document.body; // HTML belgesinin <body> elementini doğrudan döndürür. <body> sayfanın görünen tüm içeriğini kapsayan ana elementtir.mesela bu değişken ile sayfanın arka plan sınıfını değiştirmek gibi işlemler yapabiliriz; örneğin tema değiştirme:

function checkTheme() {

    //localStorage tarayıcının uzun süreli (kalıcı) anahtar-değer depolama alanıdır. Tarayıcı kapansa da veriler kalır.
    if (localStorage.getItem('theme') === 'dark') { // getItem('theme') ile 'theme' anahtarına karşılık gelen değeri alır.dönen değer stringtir
        //=== operatörü hem tip hem değer eşitliğini kontrol eder. Burada "eğer localStorage'daki tema 'dark' ise" anlamına gelir.

        body.classList.add('dark-mode');//burada body daha önce yukarıda const body = document.body; ile alınmış <body> elementimizdir..classList.add('dark-mode') ile <body> elementine dark-mode adında bir CSS sınıfı eklenir
        themeBtn.innerHTML = '<i class="fas fa-sun"></i>';
        //themeBtn daha önce document.getElementById('theme-toggle') ile alınmış buton elementimizdir.
     //.innerHTML butonun içinde HTML içeriğini değiştirir. Burada Font Awesome ikonları kullanan <i class="fas fa-sun"></i> HTML'si yerleştirilir; bu "güneş" ikonu gösterir (koyu moddayken kullanıcıya açık mod simgesi sunmak için).
    }
}


// burası tema butonuna click dinleyicisi — kullanıcı temayı değiştirince yapılacaklar
themeBtn.addEventListener('click', () => { //addEventListener bir DOM elementine olay (event) dinleyicisi ekler. 'click' olay tipi; kullanıcı butona tıkladığında iç fonksiyon çalışır. İkinci parametre bir fonksiyon (arrow function). Bu fonksiyon click olduğunda tetiklenir.
    body.classList.toggle('dark-mode'); // toggle eğer dark-mode sınıfı yoksa ekler, varsa çıkarır. Yani buton her tıklamada temayı açıp kapatır.
    if (body.classList.contains('dark-mode')) { // classList.contains('dark-mode') ile şu an body'de dark-mode var mı kontrol edilir. Varsa koyu tema aktif demektir.
        localStorage.setItem('theme', 'dark'); // setItem(key, value) ile tarayıcının localStorage'ına tema tercihi kaydedilir. Böylece sayfa yeniden yüklendiğinde checkTheme() ile aynı tercih uygulanabilir.
        themeBtn.innerHTML = '<i class="fas fa-sun"></i>';//Buton içeriğini güncel temaya göre değiştirir: koyu moddaysa güneş ikonu (kullanıcıya "tıkla, gündüze dön" mesajı), açık moddaysa ay ikonu.
    } else {
        localStorage.setItem('theme', 'light');
        themeBtn.innerHTML = '<i class="fas fa-moon"></i>';
    }
}); //butona tıklayan kullanıcı temayı değiştirir, tercih localStorage'a yazılır, ikon güncellenir.



// bu fonksiyon ekranda kısa bilgilendirme göstermek için
function showToast(message, type = "info") { // parametreler -->  message (string): Kullanıcıya gösterilecek yazı.type (string, opsiyonel): Mesaj türü; default değeri "info". Eğer çağırırken type verilmezse "info" kullanılır.
    let color = "#004aad"; // varsayılan renk.
    if (type === "error") color = "#ef4444"; // eğer type "error" ise kırmızı ton belirlenir.
    if (type === "success") color = "#10b981"; // Eğer type "success" ise yeşil ton belirlenir.

    Toastify({ // Toastify sayfadaki küçük bildirim/kutu (toast) gösterme kütüphanesidir
        text: message, duration: 3000, gravity: "top", position: "right", // text: message — gösterilecek metin. duration: 3000 — milisaniye cinsinden gösterim süresi (3000 ms = 3 saniye).   gravity: "top" — Y ekseninde nerede gösterilecek (top = üst). position: "right" — X ekseninde pozisyon (right = sağ).
        style: { background: color, borderRadius: "10px", boxShadow: "0 4px 6px rgba(0,0,0,0.1)" }// style: { ... } — inline CSS stilleri.  background: color — arka plan rengi (yukarıda belirlenen).    borderRadius: "10px" — köşe yuvarlama.   boxShadow: "0 4px 6px rgba(0,0,0,0.1)" — hafif gölge.
    }).showToast(); // Yapılandırılan toast'u ekranda gösterir.
}




// tabloyu CSV'ye dönüştürüp indirme
function exportTableToCSV(filename) {// filename: fonksiyona dışarıdan verilen dosya adı. (string): İndirilecek dosyanın adı (ör. "rapor.csv"). Fonksiyon bu adı download özelliğine atar. Bu isim, indirilecek dosyanın adı olur.
    const csv = []; // CSV formatlı her satırı geçici olarak tutacağı boş bir dizi. – En sonunda bu dizi birleştirilip gerçek CSV dosyası yapılacak.
    const rows = document.querySelectorAll("#result-table tr"); //querySelectorAll tüm eşleşen elementleri seçer ve bir NodeList döner (dizi benzeri) , burada #result-table id'li tablonun tüm tr (satır) elemanlarını seçer — hem başlık (th) hem veri (td) satırları."#result-table tr" --> id’si result-table olan tablonun tüm satırları (tr).


    if (rows.length <= 1) { showToast("İndirilecek veri yok!", "error"); return; } //Eğer toplam satır sayısı 1 veya 0 ise (genelde sadece başlık satırı varsa) indirilecek veri yok demektir. Kullanıcıya hata toast'u gösterir ve fonksiyonu return ile sonlandırır.rows.length Toplam kaç satır olduğunu gösterir.
//showToast("İndirilecek veri yok!", "error") ile kullanıcıya uyarı gösterilir  return ile fonksiyon durdurulur


    for (let i = 0; i < rows.length; i++) { // Her hücre için döngü
        const row = [], cols = rows[i].querySelectorAll("td, th"); // const row = [] --> Bu satıra ait CSV hücrelerinin geçici dizisi.     rows[i].querySelectorAll("td, th")  bu satırdaki tüm hücreleri seçer:  td --> normal veri hücreleri , th --> başlık hücreleri
        for (let j = 0; j < cols.length; j++) { // Bu döngü her hücre (sütun) için çalışır.
            let data = cols[j].innerText.replace(/"/g, '""');
            // innerText Hücrenin içindeki yazıyı (etiketler olmadan sadece metin) alır. replace(/"/g, '""') CSV formatında metin içinde çift tırnak varsa sorun çıkarır.  Ör:  Hello "World" --> CSV bozulur. Bu yüzden her " --> "" yapılıyor. CSV standardı bunu gerektirir.
            row.push('"' + data + '"'); //Bu satırın CSV sütun dizisine bir metin ekler. Neden string "\"" + data + "\"" ?  Çünkü CSV’de tüm hücreler çift tırnak içinde olmalıdır. Ör: "Ahmet"  ,"35"  , "Trabzon"
        }
        csv.push(row.join(","));  // row.join(",")  Satırdaki tüm hücreleri virgülle birleştirir.  CSV mantığı --> her sütun virgülle ayrılır. Ör: ["Ahmet", "35", "Erkek"] --> "Ahmet","35","Erkek"  csv.push()  Her satırı CSV dizisine ekler.
    }
   // Blob JavaScript içinde geçici dosya oluşturmaya yarayan bir nesne
    const csvFile = new Blob([csv.join("\n")], {type: "text/csv"}); // csv.join("\n") --> her satırı alt alta koy (CSV dosyası formatı).  – { type: "text/csv" } --> dosya türü CSV. Böylece tarayıcı içinde gerçek bir CSV dosyası oluşmuş olur.
    const downloadLink = document.createElement("a"); // document.createElement("a")  Yeni bir <a> (link) elementi oluşturur.  Bu gizli link → dosyayı indirmek için kullanılacak.
    downloadLink.download = filename; // download özelliği  Linke tıklanınca dosyanın ismini belirler. Ör: "rapor.csv"
    downloadLink.href = window.URL.createObjectURL(csvFile); // URL.createObjectURL()  Blob'dan geçici bir URL oluşturur. Ör: blob:http://localhost/.../83hf9djdj    Tarayıcı bu URL'yi indirilebilir bir dosya gibi gösterir.
    downloadLink.style.display = "none"; // Link görünmesin diye display: none.
    document.body.appendChild(downloadLink); // Gizli linki sayfaya ekler. Eklemeden tıklatılamaz.
    downloadLink.click(); // Bu satır --> Linke otomatik tıklama simülasyonu yapar. Sonuç --> dosya otomatik indirir. Kullanıcı hiçbir yere tıklamaz.
    showToast("Tablo başarıyla indirildi!", "success"); // İndirme tamamlanınca kullanıcıya bildirim gösterir.
}