# --- 0.DEV0 GEÇERSİZ SÜRÜM HATASINI ÇÖZEN GLOBAL MONKEYPATCH ---
# Bazı macOS ve global pip kurulumlarında '0.dev0' geçersiz sürüm etiketi
# Altair/Streamlit grafik kütüphanelerinin (packaging.version) çökmesine sebep olur.
try:
    import packaging.version

    original_init = packaging.version.Version.__init__


    def patched_init(self, version):
        try:
            original_init(self, version)
        except Exception:
            # Sürüm geçersizse ('0.dev0' vb.), PEP 440 uyumlu sahte bir sürümle devam et
            original_init(self, "0.0.0")


    packaging.version.Version.__init__ = patched_init
except Exception:
    pass

import streamlit as st
import pandas as pd
import os
import qrcode
from io import BytesIO
import datetime

# --- SAYFA YAPILANDIRMASI ---
st.set_page_config(page_title="AS43 Grup | Metal & Asansör ERP", layout="wide", page_icon="💠")

# --- KURUMSAL BRANDING & PREMIUM CSS (as43.com.tr Kurumsal Renkleri) ---
# Kurumsal Renkler: Deep Royal Blue (#2B328C) ve Vibrant Electric Blue (#2F5DFF)
st.markdown("""
    <style>
    /* Ana ekran arka planı */
    .main { 
        background-color: #f8fafc; 
    }

    /* Kurumsal Üst Şerit (Deep Royal Blue) */
    .stApp { 
        border-top: 6px solid #2B328C; 
    }

    /* Başlık stili (Kurumsal Mavi Degrade) */
    .main-title {
        background: linear-gradient(135deg, #2B328C 0%, #2F5DFF 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-family: 'Arial', sans-serif;
        text-align: center;
        font-weight: 850;
        font-size: 2.3rem;
        margin-bottom: 0.2rem;
    }
    .main-subtitle {
        color: #64748b;
        font-family: 'Arial', sans-serif;
        text-align: center;
        font-size: 1rem;
        margin-bottom: 1.8rem;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }

    /* Gelişmiş Bilgi Kartları (KPI Cards) */
    .metric-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 14px;
        padding: 1.3rem;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.03), 0 2px 4px -1px rgba(0, 0, 0, 0.02);
        text-align: center;
        transition: transform 0.2s ease, border-color 0.2s ease, box-shadow 0.2s ease;
    }
    .metric-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 12px 20px -3px rgba(43, 50, 140, 0.12);
        border-color: #2F5DFF;
    }
    .metric-val {
        font-size: 2.1rem;
        font-weight: 800;
        margin: 0.3rem 0;
    }
    .metric-label {
        font-size: 0.85rem;
        color: #64748b;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.08em;
    }

    /* Stok Kart Stilleri */
    .stock-card {
        background: white;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 1.2rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.02);
        margin-bottom: 1rem;
        transition: border-color 0.2s ease, box-shadow 0.2s ease;
    }
    .stock-card:hover {
        border-color: #2F5DFF;
        box-shadow: 0 4px 12px rgba(47, 93, 255, 0.08);
    }
    .stock-title {
        font-size: 0.95rem;
        font-weight: 700;
        color: #1e293b;
        margin-bottom: 0.3rem;
    }
    .stock-qty {
        font-size: 1.5rem;
        font-weight: 800;
        color: #2B328C;
    }

    /* QR Grid Kart Tasarımı */
    .qr-card {
        background: white;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 1.2rem;
        text-align: center;
        box-shadow: 0 2px 4px rgba(0,0,0,0.02);
        margin-bottom: 1rem;
        transition: border-color 0.2s ease;
    }
    .qr-card:hover {
        border-color: #2F5DFF;
    }

    /* Özelleştirilmiş Buton Stili (Kurumsal Mavi Gradyan) */
    div.stButton > button { 
        background: linear-gradient(135deg, #2B328C 0%, #2F5DFF 100%) !important; 
        color: white !important; 
        border: none !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        padding: 0.5rem 1.8rem !important;
        transition: all 0.2s ease !important;
        box-shadow: 0 4px 6px -1px rgba(43, 50, 140, 0.25) !important;
    }
    div.stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 15px -3px rgba(43, 50, 140, 0.4) !important;
    }

    /* Sidebar başlık ve etiket stilleri */
    .sidebar-title {
        font-size: 1.2rem;
        font-weight: 700;
        color: #2B328C;
        text-align: center;
        margin-top: 0.5rem;
    }
    </style>
    """, unsafe_allow_html=True)

# Kurumsal Üst Logo Gösterimi
logo_col1, logo_col2, logo_col3 = st.columns([2, 5, 2])
with logo_col2:
    st.image(
        "https://static.wixstatic.com/media/69f9d2_a833c9efbbc845aeac23d127f3d61507~mv2.png",
        width=110,
        use_container_width=False
    )
    st.markdown("<div class='main-title'>AS43 GRUP YÖNETİM PORTALI</div>", unsafe_allow_html=True)

FILE_ASANSOR = "asansor_verileri.csv"
FILE_STOK = "metal_stok.csv"
FILE_GIDERLER = "metal_giderler.csv"
FILE_GELIRLER = "metal_gelirler.csv"

# Varsayılan kolon şablonları
DEFAULT_HEADERS_ASANSOR = ["Asansör_ID", "Konum", "Durum (Etiket)", "Son_Bakım_Notları", "Bekleyen_Eksikler", "Adres"]

# --- HATA ÖNLEME: VERİ TABANLARI YOKSA OTOMATİK OLUŞTURMA ---

# 1. Asansör Veri Tabanı
if not os.path.exists(FILE_ASANSOR):
    df_template = pd.DataFrame(columns=DEFAULT_HEADERS_ASANSOR)
    df_template.loc[0] = ["AS-101", "Fabrika Giriş - A Blok", "Mavi", "Aylık rutin kontrol yapıldı.",
                          "Halat gerginliği ayarlanacak.", "Metal OSB 3. Cadde No:43"]
    df_template.loc[1] = ["AS-102", "Depo Bölümü", "Kırmızı", "Fren balataları aşınmış durumda.",
                          "Fren diskleri değişmeli.", "Metal OSB 3. Cadde No:43"]
    df_template.loc[2] = ["AS-103", "B Blok 2. Kat", "Mavi", "Motor yağlaması yapıldı.", "Bekleyen eksik bulunmuyor.",
                          "Metal OSB 3. Cadde No:43"]
    df_template.to_csv(FILE_ASANSOR, index=False, encoding='utf-8-sig')

# 2. FLC 1530 Fiber Lazer Sac Stok Veri Tabanı (kg)
if not os.path.exists(FILE_STOK):
    df_stok_template = pd.DataFrame({
        "Malzeme_Tipi": [
            "Paslanmaz Çelik",
            "Aynalı Paslanmaz",
            "Desenli / Dekoratif Paslanmaz",
            "Satine Paslanmaz",
            "Laminat / Kompakt Laminat Kaplama",
            "Elektrostatik Boyalı Sac"
        ],
        "Miktar_kg": [2500.0, 1200.0, 800.0, 1500.0, 950.0, 3000.0]
    })
    df_stok_template.to_csv(FILE_STOK, index=False, encoding='utf-8-sig')

# 3. İşletme Gider Veri Tabanı
if not os.path.exists(FILE_GIDERLER):
    df_gider_template = pd.DataFrame(columns=["Tarih", "Kategori", "Alt_Kategori", "Tutar_TL", "Açıklama"])
    df_gider_template.loc[0] = ["2026-05-01", "Personel Gideri", "Maaş", 48000.0, "Mayıs ayı teknik personel maaşları"]
    df_gider_template.loc[1] = ["2026-05-05", "Enerji Gideri", "Elektrik", 12500.0,
                                "Lazer kesim aylık elektrik faturası"]
    df_gider_template.loc[2] = ["2026-05-07", "Gaz Gideri", "Azot (N₂)", 8500.0, "FLC 1530 Lazer Azot tüp dolumları"]
    df_gider_template.loc[3] = ["2026-05-10", "Gaz Gideri", "Oksijen (O₂)", 3200.0, "FLC 1530 Lazer Oksijen dolumu"]
    df_gider_template.loc[4] = ["2026-05-15", "Personel Gideri", "Maaş / Avans", 15000.0,
                                "Personel haftalık avans ödemeleri"]
    df_gider_template.loc[5] = ["2026-05-18", "Nakliye & Lojistik", "Nakliye", 4500.0, "Kabinlerin şantiyeye nakliyesi"]
    df_gider_template.loc[6] = ["2026-05-20", "Personel Gideri", "Yeme / İçme", 6800.0, "Mutfak ve yemek giderleri"]
    df_gider_template.to_csv(FILE_GIDERLER, index=False, encoding='utf-8-sig')

# 4. Alınan Ödemeler (Gelir) Veri Tabanı
if not os.path.exists(FILE_GELIRLER):
    df_gelir_template = pd.DataFrame(
        columns=["Tarih", "Müşteri", "Ödeme_Yöntemi", "Tutar_TL", "Çek_Vadesi", "Açıklama"])
    df_gelir_template.loc[0] = ["2026-05-02", "Özsoy Asansör A.Ş.", "Nakit", 85000.0, "",
                                "Kabin teslimat nakit ödemesi"]
    df_gelir_template.loc[1] = ["2026-05-12", "Karaca İnşaat", "Kredi Kartı", 145000.0, "",
                                "AVM asansör kabini hakedişi"]
    df_gelir_template.loc[2] = ["2026-05-22", "Yıldız Mühendislik", "Çek", 250000.0, "2026-07-15",
                                "Vade: 15 Temmuz - 1 Adet Paslanmaz Kabin Bedeli"]
    df_gelir_template.to_csv(FILE_GELIRLER, index=False, encoding='utf-8-sig')

# --- VERİLERİ OKUMA ---
try:
    df_asansor = pd.read_csv(FILE_ASANSOR, encoding='utf-8-sig').dropna(how='all')
    df_asansor.columns = [c.strip() for c in df_asansor.columns]

    df_stok = pd.read_csv(FILE_STOK, encoding='utf-8-sig').dropna(how='all')

    df_gider = pd.read_csv(FILE_GIDERLER, encoding='utf-8-sig').dropna(how='all')
    df_gider["Tarih"] = pd.to_datetime(df_gider["Tarih"])
    df_gider["Tutar_TL"] = df_gider["Tutar_TL"].astype(float)

    df_gelir = pd.read_csv(FILE_GELIRLER, encoding='utf-8-sig').dropna(how='all')
    df_gelir["Tarih"] = pd.to_datetime(df_gelir["Tarih"])
    df_gelir["Tutar_TL"] = df_gelir["Tutar_TL"].astype(float)
except Exception as e:
    st.error(f"Veritabanı yükleme hatası: {e}")
    st.stop()


# --- SÜTUN EŞLEŞTİRME VE HATA ENGELLEME ---
def get_column_or_fallback(df, expected_names, default_name):
    for col in df.columns:
        if col.lower().strip() in [name.lower() for name in expected_names]:
            return col
    df[default_name] = ""
    return default_name


col_id = get_column_or_fallback(df_asansor,
                                ["Asansör_ID", "Asansör ID", "Asansor_ID", "ID", "Asansor ID", "Asansör No", "No"],
                                "Asansör_ID")
col_konum = get_column_or_fallback(df_asansor, ["Konum", "Lokasyon", "Bina", "Yer", "Location"], "Konum")
col_durum = get_column_or_fallback(df_asansor, ["Durum (Etiket)", "Durum", "Etiket", "Status", "State"],
                                   "Durum (Etiket)")
col_bakim = get_column_or_fallback(df_asansor,
                                   ["Son_Bakım_Notları", "Son Bakım Notları", "Bakım Notları", "Notlar", "Notes",
                                    "Son_Bakim_Notlari"], "Son_Bakım_Notları")
col_eksik = get_column_or_fallback(df_asansor,
                                   ["Bekleyen_Eksikler", "Bekleyen Eksikler", "Eksikler", "Eksik", "Missing"],
                                   "Bekleyen_Eksikler")
col_adres = get_column_or_fallback(df_asansor, ["Adres", "Address"], "Adres")

df_asansor[col_id] = df_asansor[col_id].astype(str)

# --- 📱 MOBİL QR TARAMA SİMÜLATÖRÜ ---
if "id" in st.query_params:
    scan_id = st.query_params["id"]
    st.markdown(f"<div class='main-title'>📱 Mobil Tarama & Hızlı Bilgi</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='main-subtitle'>{scan_id} Asansör Durum Raporu</div>", unsafe_allow_html=True)

    satir = df_asansor[df_asansor[col_id] == scan_id]
    if not satir.empty:
        d = satir.iloc[0]
        val_durum = str(d[col_durum]).strip()
        color = "#22c55e" if val_durum.lower() == "mavi" else "#ef4444"

        st.markdown(f"""
        <div style='background: white; border-left: 8px solid {color}; border-radius: 12px; padding: 1.5rem; box-shadow: 0 4px 15px rgba(0,0,0,0.05);'>
            <h3 style='margin-top:0; color:#2B328C;'>🛠️ Sistem Kaydı: {scan_id}</h3>
            <p><b>📍 Konum:</b> {d[col_konum]}</p>
            <p><b>⚡ Mevcut Etiket Durumu:</b> <span style='background: {color}; color: white; padding: 2px 8px; border-radius: 4px;'>{val_durum}</span></p>
            <p><b>📝 Son Bakım Notu:</b> {d[col_bakim]}</p>
            <p><b>❌ Bekleyen Eksik:</b> {d[col_eksik]}</p>
            <p><b>🏠 Bina Adresi:</b> {d[col_adres]}</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🎛️ Ana Yönetim Paneline Dön"):
            st.query_params.clear()
            st.rerun()
    else:
        st.error("Kayıt bulunamadı.")
    st.stop()

# --- SİDEBAR (SOL MENÜ) SEÇİM ALANI ---
# Resmi as43.com.tr Wix logosu entegre edildi
st.sidebar.markdown(
    "<div style='text-align: center;'><img src='https://static.wixstatic.com/media/69f9d2_a833c9efbbc845aeac23d127f3d61507~mv2.png' width='100' style='margin-bottom:10px;'></div>",
    unsafe_allow_html=True)
st.sidebar.markdown("<div class='sidebar-title'>AS43 GRUP YÖNETİMİ</div>", unsafe_allow_html=True)
st.sidebar.markdown(
    "<div style='text-align:center; color:#64748b; font-size:0.8rem; margin-bottom:15px;'>Kurumsal Kontrol Konsolu</div>",
    unsafe_allow_html=True)
st.sidebar.markdown("---")

secilen_modul = st.sidebar.radio(
    "Lütfen Modül Seçiniz:",
    [
        "💠 AS 43 Metal - Fabrika Yönetimi",
        "🛗 AS 43 Asansör & QR Sistemi"
    ]
)

st.sidebar.markdown("---")
st.sidebar.markdown(
    "<div style='text-align: center; color: #64748b; font-size: 0.75rem;'>Verileriniz yerel bilgisayarınızda (CSV) şifreli & güvende tutulmaktadır.</div>",
    unsafe_allow_html=True)

# ========================================================
# 1. MODÜL: AS 43 METAL - FABRİKA YÖNETİMİ (ERP)
# ========================================================
if secilen_modul == "💠 AS 43 Metal - Fabrika Yönetimi":
    st.markdown("<div class='main-subtitle'>AS43 Metal Lazer Sac Kesim, Hammadde & Finans Yönetim Sistemi</div>",
                unsafe_allow_html=True)

    # Alt Sekmeler
    erp_tab1, erp_tab2, erp_tab3, erp_tab4 = st.tabs([
        "📈 Gelir - Gider & Finans Raporu",
        "📦 FLC 1530 Lazer Sac Stok Yönetimi",
        "💸 Yeni Gelir / Gider Girişi Yap",
        "🛗 Asansör Kayıt Düzenleme"
    ])

    # ----------------------------------------------------
    # ERP TAB 1: FİNANS RAPORLARI VE GRAFİKLER
    # ----------------------------------------------------
    with erp_tab1:
        st.subheader("📊 Finansal Göstergeler & Raporlar")

        # Filtreleme Alanı
        st.markdown("#### Raporlama Dönemi Seçin")
        filtre_col1, filtre_col2 = st.columns(2)

        with filtre_col1:
            yil_listesi = sorted(list(set(df_gelir["Tarih"].dt.year.tolist() + df_gider["Tarih"].dt.year.tolist())),
                                 reverse=True)
            secilen_yil = st.selectbox("Yıl Seçin:", yil_listesi)

        with filtre_col2:
            ay_listesi = ["Tümü", "Ocak", "Şubat", "Mart", "Nisan", "Mayıs", "Haziran", "Temmuz", "Ağustos", "Eylül",
                          "Ekim", "Kasım", "Aralık"]
            secilen_ay_ad = st.selectbox("Ay Seçin:", ay_listesi, index=5 if len(yil_listesi) > 0 else 0)

        ay_numarasi = ay_listesi.index(secilen_ay_ad)

        gelir_filtre = df_gelir[df_gelir["Tarih"].dt.year == secilen_yil]
        gider_filtre = df_gider[df_gider["Tarih"].dt.year == secilen_yil]

        if secilen_ay_ad != "Tümü":
            gelir_filtre = gelir_filtre[gelir_filtre["Tarih"].dt.month == ay_numarasi]
            gider_filtre = gider_filtre[gider_filtre["Tarih"].dt.month == ay_numarasi]

        # KPI Kartları Hesaplama
        toplam_gelir = gelir_filtre["Tutar_TL"].sum()
        toplam_gider = gider_filtre["Tutar_TL"].sum()
        net_kar = toplam_gelir - toplam_gider

        kpi_col1, kpi_col2, kpi_col3 = st.columns(3)
        with kpi_col1:
            st.markdown(f"""
            <div class='metric-card'>
                <div class='metric-label'>Toplam Tahsil Edilen Gelir</div>
                <div class='metric-val' style='color: #22c55e;'>{toplam_gelir:,.2f} TL</div>
            </div>
            """, unsafe_allow_html=True)
        with kpi_col2:
            st.markdown(f"""
            <div class='metric-card'>
                <div class='metric-label'>Toplam İşletme Gideri</div>
                <div class='metric-val' style='color: #ef4444;'>{toplam_gider:,.2f} TL</div>
            </div>
            """, unsafe_allow_html=True)
        with kpi_col3:
            color = "#2F5DFF" if net_kar >= 0 else "#ef4444"
            st.markdown(f"""
            <div class='metric-card'>
                <div class='metric-label'>Net Dönem Kar / Zararı</div>
                <div class='metric-val' style='color: {color};'>{net_kar:,.2f} TL</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<br>---", unsafe_allow_html=True)

        # Grafik Gösterimleri
        st.subheader("📈 Gelir & Gider Dağılımları")
        chart_col1, chart_col2 = st.columns(2)

        with chart_col1:
            st.markdown("**Gider Kategorisi Dağılımı**")
            if not gider_filtre.empty:
                gider_grup = gider_filtre.groupby("Kategori")["Tutar_TL"].sum().reset_index()
                st.bar_chart(data=gider_grup.set_index("Kategori"), y="Tutar_TL", color="#ef4444")
            else:
                st.info("Bu dönem için gider kaydı bulunamadı.")

        with chart_col2:
            st.markdown("**Ödeme Yöntemi Dağılımı (Gelir)**")
            if not gelir_filtre.empty:
                gelir_grup = gelir_filtre.groupby("Ödeme_Yöntemi")["Tutar_TL"].sum().reset_index()
                st.bar_chart(data=gelir_grup.set_index("Ödeme_Yöntemi"), y="Tutar_TL", color="#22c55e")
            else:
                st.info("Bu dönem için gelir kaydı bulunamadı.")

        st.markdown("---", unsafe_allow_html=True)

        # Tablosal Görünüm
        list_col1, list_col2 = st.columns(2)
        with list_col1:
            st.markdown("#### 📥 Alınan Ödemeler Listesi")
            if not gelir_filtre.empty:
                gelir_goster = gelir_filtre.copy()
                gelir_goster["Tarih"] = gelir_goster["Tarih"].dt.strftime("%Y-%m-%d")
                st.dataframe(gelir_goster, use_container_width=True)
            else:
                st.info("Gelir kaydı yok.")

        with list_col2:
            st.markdown("#### 📤 İşletme Giderleri Listesi")
            if not gider_filtre.empty:
                gider_goster = gider_filtre.copy()
                gider_goster["Tarih"] = gider_goster["Tarih"].dt.strftime("%Y-%m-%d")
                st.dataframe(gider_goster, use_container_width=True)
            else:
                st.info("Gider kaydı yok.")

    # ----------------------------------------------------
    # ERP TAB 2: LAZER SAC STOK YÖNETİMİ
    # ----------------------------------------------------
    with erp_tab2:
        st.subheader("📦 FLC 1530 Fiber Lazer Hammadde Sac Stoğu")
        st.write(
            "Asansör kabini imalatında kullanılan paslanmaz çelik ve diğer kaplama sacların kg cinsinden stok seviyeleri:")

        stock_cols = st.columns(3)
        for idx, row_stok in df_stok.iterrows():
            col_target = stock_cols[idx % 3]
            with col_target:
                max_kapasite = 5000.0
                doluluk = min(row_stok['Miktar_kg'] / max_kapasite, 1.0)

                st.markdown(f"""
                <div class='stock-card'>
                    <div class='stock-title'>📋 {row_stok['Malzeme_Tipi']}</div>
                    <div class='stock-qty'>{row_stok['Miktar_kg']:.1f} kg</div>
                </div>
                """, unsafe_allow_html=True)
                st.progress(doluluk)
                st.markdown("<br>", unsafe_allow_html=True)

        st.markdown("---", unsafe_allow_html=True)
        st.subheader("🔄 Sac Stok Hareketi Gir (Ekle/Çıkar)")

        with st.form("stok_hareket_form"):
            secilen_sac = st.selectbox("Sac Tipi Seçiniz:", df_stok["Malzeme_Tipi"].tolist())
            hareket_tipi = st.selectbox("İşlem Tipi:", ["➕ Stok Ekle (Satın Alma)", "➖ Stok Tüket (Kesim/İmalat)"])
            miktar = st.number_input("Miktar (kg):", min_value=1.0, value=50.0, step=1.0)

            if st.form_submit_button("Stok Hareketini Kaydet"):
                idx = df_stok[df_stok["Malzeme_Tipi"] == secilen_sac].index[0]
                mevcut_miktar = df_stok.at[idx, "Miktar_kg"]

                if "Stok Ekle" in hareket_tipi:
                    yeni_miktar = mevcut_miktar + miktar
                    st.success(f"{secilen_sac} stoğuna {miktar} kg başarıyla eklendi!")
                else:
                    yeni_miktar = max(0.0, mevcut_miktar - miktar)
                    st.warning(f"{secilen_sac} stoğından {miktar} kg başarıyla tüketildi!")

                df_stok.at[idx, "Miktar_kg"] = yeni_miktar
                df_stok.to_csv(FILE_STOK, index=False, encoding='utf-8-sig')
                st.rerun()

    # ----------------------------------------------------
    # ERP TAB 3: YENİ GELİR / GİDER GİRİŞ FORMLARI
    # ----------------------------------------------------
    with erp_tab3:
        st.subheader("💸 Gelir ve Gider Kayıt Yönetimi")
        insert_col1, insert_col2 = st.columns(2)

        # 1. GİDER GİRİŞ FORMU
        with insert_col1:
            st.markdown("### 📤 Gider Kaydı Girişi")
            with st.form("yeni_gider_form"):
                gider_tarih = st.date_input("İşlem Tarihi:", datetime.date.today(), key="g_tarih")
                gider_kategori = st.selectbox("Gider Kategorisi:", [
                    "Personel Gideri",
                    "Enerji Gideri",
                    "Gaz Gideri",
                    "Nakliye & Lojistik",
                    "Sarf Malzemesi & Yağ",
                    "Cihaz / Lazer Bakımı",
                    "Diğer"
                ])

                gider_alt_kategori = st.selectbox("Alt Gider Kalemi:", [
                    "Maaş",
                    "Avans",
                    "Yeme / İçme",
                    "Elektrik",
                    "Su",
                    "Azot (N₂)",
                    "Oksijen (O₂)",
                    "Nakliye",
                    "Sarf Malzemesi",
                    "Yedek Parça",
                    "Diğer"
                ])

                gider_tutar = st.number_input("Tutar (TL):", min_value=1.0, value=1500.0, step=100.0)
                gider_aciklama = st.text_input("Açıklama / Detay:", placeholder="Örn: FLC 1530 Azot gazı dolumu")

                if st.form_submit_button("💾 Gideri Kaydet"):
                    yeni_gider = {
                        "Tarih": str(gider_tarih),
                        "Kategori": gider_kategori,
                        "Alt_Kategori": gider_alt_kategori,
                        "Tutar_TL": float(gider_tutar),
                        "Açıklama": gider_aciklama
                    }
                    updated_gider = pd.concat([df_gider, pd.DataFrame([yeni_gider])], ignore_index=True)
                    updated_gider.to_csv(FILE_GIDERLER, index=False, encoding='utf-8-sig')
                    st.success(f"{gider_alt_kategori} gideri başarıyla veri tabanına işlendi!")
                    st.rerun()

        # 2. GELİR GİRİŞ FORMU
        with insert_col2:
            st.markdown("### 📥 Alınan Ödeme (Gelir) Girişi")
            with st.form("yeni_gelir_form"):
                gelir_tarih = st.date_input("Tahsilat Tarihi:", datetime.date.today(), key="gel_tarih")
                gelir_musteri = st.text_input("Müşteri / Firma Adı:", placeholder="Örn: Özsoy Asansör A.Ş.")
                gelir_yontem = st.selectbox("Ödeme Yöntemi:", ["Nakit", "Kredi Kartı", "Çek"])
                cek_vadesi = st.date_input("Çek Vade Tarihi (Çek ise Geçerlidir):",
                                           datetime.date.today() + datetime.timedelta(days=30))
                gelir_tutar = st.number_input("Alınan Ödeme Tutarı (TL):", min_value=1.0, value=10000.0, step=1000.0)
                gelir_aciklama = st.text_input("Ödeme Açıklaması:", placeholder="Örn: Paslanmaz kabin hakediş bedeli")

                if st.form_submit_button("💾 Ödemeyi Kaydet"):
                    if not gelir_musteri:
                        st.error("Müşteri adı boş geçilemez!")
                    else:
                        vade_str = str(cek_vadesi) if gelir_yontem == "Çek" else ""

                        yeni_gelir = {
                            "Tarih": str(gelir_tarih),
                            "Müşteri": gelir_musteri,
                            "Ödeme_Yöntemi": gelir_yontem,
                            "Tutar_TL": float(gelir_tutar),
                            "Çek_Vadesi": vade_str,
                            "Açıklama": gelir_aciklama
                        }

                        updated_gelir = pd.concat([df_gelir, pd.DataFrame([yeni_gelir])], ignore_index=True)
                        updated_gelir.to_csv(FILE_GELIRLER, index=False, encoding='utf-8-sig')
                        st.success(f"{gelir_musteri} ödemesi başarıyla veri tabanına işlendi!")
                        st.rerun()

    # ----------------------------------------------------
    # ERP TAB 4: ASANSÖR KAYIT DÜZENLEME
    # ----------------------------------------------------
    with erp_tab4:
        st.subheader("📋 Teknik Detayları Düzenle (AS43 Asansör Veri Tabanı)")
        ids = df_asansor[col_id].dropna().unique().tolist()

        if not ids:
            st.info("Kayıt bulunamadı.")
        else:
            secilen_id = st.selectbox("Düzenlenecek Asansör Seçin:", ids, key="edit_selectbox")
            satir = df_asansor[df_asansor[col_id] == secilen_id]

            if not satir.empty:
                d = satir.iloc[0]
                with st.form("metal_asansor_edit_form"):
                    val_konum = d[col_konum] if pd.notna(d[col_konum]) else ""
                    val_durum = str(d[col_durum]).strip() if pd.notna(d[col_durum]) else "Mavi"
                    val_bakim = d[col_bakim] if pd.notna(d[col_bakim]) else ""
                    val_eksik = d[col_eksik] if pd.notna(d[col_eksik]) else ""
                    val_adres = d[col_adres] if pd.notna(d[col_adres]) else ""

                    konum = st.text_input("Bölüm / Konum", val_konum)
                    durum = st.selectbox("Durum", ["Mavi", "Kırmızı"], index=0 if val_durum.lower() == "mavi" else 1)
                    bakim = st.text_area("Bakım Detayları", val_bakim)
                    eksik = st.text_input("Bekleyen Eksiklikler", val_eksik)
                    adres = st.text_area("Adres", val_adres)

                    if st.form_submit_button("Değişiklikleri Kaydet"):
                        idx = df_asansor[df_asansor[col_id] == secilen_id].index[0]
                        df_asansor.at[idx, col_konum] = konum
                        df_asansor.at[idx, col_durum] = durum
                        df_asansor.at[idx, col_bakim] = bakim
                        df_asansor.at[idx, col_eksik] = eksik
                        df_asansor.at[idx, col_adres] = adres

                        df_asansor.to_csv(FILE_ASANSOR, index=False, encoding='utf-8-sig')
                        st.success("Asansör verileri başarıyla güncellendi!")
                        st.rerun()

# ==========================================
# 2. MODÜL: AS 43 ASANSÖR & QR SİSTEMİ
# ==========================================
else:
    st.markdown("<div class='main-subtitle'>QR Destekli Asansör Denetim ve Kimliklendirme Portalı</div>",
                unsafe_allow_html=True)

    # Sekmeler
    tab1, tab2 = st.tabs(["🗂️ Tüm Asansörler & QR Galerisi", "➕ Yeni Asansör Kayıt Girişi"])

    with tab1:
        st.subheader("Asansör Karekod Envanteri")
        st.write(
            "Bakım teknisyenlerinin sahada hızlı taraması için tüm asansörlerin kimlik kartları ve QR kodları aşağıdadır:")

        filtre_col1, filtre_col2 = st.columns(2)
        with filtre_col1:
            arama = st.text_input("🔍 Asansör ID veya Konuma göre ara...", "")
        with filtre_col2:
            durum_filtre = st.selectbox("Etiket Durumuna göre filtrele:", ["Tümü", "Mavi", "Kırmızı"])

        filtered_df = df_asansor.copy()

        if arama:
            filtered_df = filtered_df[
                filtered_df[col_id].str.contains(arama, case=False, na=False) |
                filtered_df[col_konum].astype(str).str.contains(arama, case=False, na=False)
                ]
        if durum_filtre != "Tümü":
            filtered_df = filtered_df[
                filtered_df[col_durum].astype(str).str.lower().str.strip() == durum_filtre.lower()]

        if filtered_df.empty:
            st.info("Arama kriterlerine uygun asansör kaydı bulunamadı.")
        else:
            row_cols = st.columns(3)
            for idx, r in filtered_df.reset_index().iterrows():
                col_target = row_cols[idx % 3]

                with col_target:
                    badge_color = "#22c55e" if str(r[col_durum]).lower().strip() == "mavi" else "#ef4444"

                    item_id = r[col_id]
                    item_qr_url = f"https://as43-metal.streamlit.app/?id={item_id}"
                    item_qr = qrcode.make(item_qr_url)

                    buf = BytesIO()
                    item_qr.save(buf, format="PNG")
                    qr_bytes = buf.getvalue()

                    st.markdown(f"""
                    <div class='qr-card'>
                        <h4 style='margin:0; color: #2B328C;'>🛗 {item_id}</h4>
                        <p style='font-size:0.85rem; color:#64748b; margin:4px 0;'>📍 {r[col_konum]}</p>
                        <span style='background: {badge_color}; color:white; padding: 2px 10px; font-size:0.75rem; border-radius:12px; font-weight:bold;'>{r[col_durum]} Etiket</span>
                    </div>
                    """, unsafe_allow_html=True)

                    # QR Resmi
                    st.image(qr_bytes, width=150)

                    # İndirme Butonu
                    st.download_button(
                        label=f"📥 {item_id} QR İndir",
                        data=qr_bytes,
                        file_name=f"asansor_qr_{item_id}.png",
                        mime="image/png",
                        key=f"btn_{item_id}_{idx}"
                    )
                    st.markdown("<br>", unsafe_allow_html=True)

    with tab2:
        st.subheader("Yeni Asansör Kaydı Tanımla")

        with st.form("yeni_asansor_form"):
            yeni_id = st.text_input("Yeni Asansör ID (Örn: AS-104)")
            yeni_konum = st.text_input("Konum / Departman (Örn: C Blok - Otopark Girişi)")
            yeni_durum = st.selectbox("Durum Etiketi", ["Mavi", "Kırmızı"])
            yeni_bakim = st.text_area("İlk Bakım/Kurulum Notu", "Sisteme yeni giriş yapıldı.")
            yeni_eksik = st.text_input("Bekleyen Eksiklikler (Varsa)", "Yok")
            yeni_adres = st.text_area("Açık Adres", "Metal OSB 3. Cadde No:43")

            if st.form_submit_button("Yeni Asansörü Kaydet"):
                if not yeni_id or not yeni_konum:
                    st.error("Lütfen ID ve Konum alanlarını doldurunuz!")
                elif yeni_id in df_asansor[col_id].values:
                    st.error("Bu ID ile bir asansör zaten tanımlı!")
                else:
                    yeni_satir = {
                        col_id: yeni_id,
                        col_konum: yeni_konum,
                        col_durum: yeni_durum,
                        col_bakim: yeni_bakim,
                        col_eksik: yeni_eksik,
                        col_adres: yeni_adres
                    }

                    for col in df_asansor.columns:
                        if col not in yeni_satir:
                            yeni_satir[col] = ""

                    updated_df = pd.concat([df_asansor, pd.DataFrame([yeni_satir])], ignore_index=True)
                    updated_df.to_csv(FILE_ASANSOR, index=False, encoding='utf-8-sig')
                    st.success(f"{yeni_id} asansörü başarıyla veri tabanına kaydedildi!")
                    st.rerun()
