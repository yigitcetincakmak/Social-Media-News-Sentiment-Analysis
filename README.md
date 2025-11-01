# Duygu Analizi Projesi (NLP ve Streamlit)

> **⚠️ Proje Durumu: Geliştirme Aşamasında (Work in Progress)**
-------------------------------------------------------------------
> Bu proje, bir bitirme projesi kapsamında aktif olarak geliştirilmektedir. 
> Ana özellikler eklenmekte ve test edilmektedir. 
> Güncel geliştirme planı ve commit geçmişi incelenebilir.

## Hakkında

Bu proje Türkçe tweet'lerde, haber yazılarında (RSS üzerinden) ve YouTube yorumlarında duyguları analiz etmek için NLP ve BERT modelini (savasy/bert-base-turkish-sentiment-cased) kullanan duygu analizi projesi.

## 🎯 Hedeflenen Özellikler (Yapılacaklar Listesi)

- [⬜] Temel Streamlit arayüzünün kurulması
- [✅] Metin ön işleme modülünün (`text_processor.py`) yazılması
- [✅] BERT modeli ile duygu analizi modülünün (`sentiment_analyzer.py`) yazılması
- [⏳] Plotly grafiğinin (`visualizer.py`) eklenmesi
- [⬜] Twitter (Hashtag ve Kullanıcı Adı) veri çekme
- [⬜] Haber Siteleri (RSS) ile kategorili veri çekme
- [⬜] YouTube yorumları ile veri çekme
- [⬜] Anlık sonuçlar için hafıza (`st.session_state`) yönetimi ve filtreleme

- [⬜] PostgreSQL veritabanı entegrasyonu
- [⬜] Geçmiş analizler için tarihsel grafiklerin eklenmesi
