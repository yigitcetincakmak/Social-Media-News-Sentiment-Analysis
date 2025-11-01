import os
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"  # ileride ekleyeceğimiz kütüphaneler (PyTorch ve NumPy arasında olan yaygın teknik çakışmayı engellemek veya
# özellikle pyTorch kütüphanesinin birden fazla versiyonun çakışmasından kaynaklanan ve analizin donmasına neden olan hatayı(OMP:Error #15) engellemek
# için çünkü bu çakışma programı çökerten bir çakışma bizde --> (Duplicate Library OK = TRUE --> yani Tekrarlanan Kütüphane Tamam). ile çökme veya kilitlenme, programın çalışmasına izin ver demiş bulunuyoruz.
# ve bunu programın en başına koyduk ilk olarak çalışması ve ileride bu dosyada birçok işlem yapacağız , analiz sonuçlarını göstereceğiz problem çıkartmaması için şu anlık bunu ekledik. )

import streamlit as st
import pandas as pd




st.set_page_config(page_title="Duygu Analizi Projesi", page_icon="📊", layout="wide")


# --- Arayüz Başlığımız ---
st.title("📊 Sosyal Medya ve Haberler için Duygu Analizi")
st.markdown("Proje geliştirme aşamasındadır. Lütfen kenar çubuğundan ayarları seçin.")


with st.sidebar:
    st.header("⚙️ Analiz Ayarları")
    st.text("Ayarlar buraya gelecek.")

    if st.sidebar.button("🚀 Analizi Başlat", type="primary"):
        st.toast("Analiz başlatıldı!")  # Tıklandığında küçük bir toast mesajı gösterir
        pass  # şu an herhangi bir işlem yapıyoruz



# --- Ana İçerik Alanımız ---
st.header("Sonuçlar")
st.write("Analiz sonuçları burada gösterilecektir.")

















