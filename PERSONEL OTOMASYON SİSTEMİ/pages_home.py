# ============================================================
#                    ANA SAYFA (HOME PAGE)
# ============================================================

import tkinter as tk
from datetime import datetime
from config import RENK, FONT_ALT_BASLIK, FONT_NORMAL, FONT_KUCUK, db_baglan, OTURUM
from utils import frame_temizle, sayfa_git

def bugun_tarihi_getir():
    aylar = ["Ocak", "Şubat", "Mart", "Nisan", "Mayıs", "Haziran", 
             "Temmuz", "Ağustos", "Eylül", "Ekim", "Kasım", "Aralık"]
    gunler = ["Pazartesi", "Salı", "Çarşamba", "Perşembe", "Cuma", "Cumartesi", "Pazar"]
    now = datetime.now()
    return f"{now.day} {aylar[now.month - 1]} {now.year}, {gunler[now.weekday()]}"

def kullanici_adini_coz(aktif_kullanici):
    if not aktif_kullanici:
        return "Kullanıcı"
    if isinstance(aktif_kullanici, str):
        return aktif_kullanici
    if isinstance(aktif_kullanici, dict):
        return (
            aktif_kullanici.get("ad_soyad") or 
            f"{aktif_kullanici.get('kullaniciAd', '')} {aktif_kullanici.get('kullaniciSoyad', '')}".strip() or 
            aktif_kullanici.get("kullaniciAd") or 
            "Kullanıcı"
        )
    if hasattr(aktif_kullanici, "kullaniciAd"):
        return getattr(aktif_kullanici, "kullaniciAd")
    return "Kullanıcı"

def get_personel_ek_veriler(kullanici_id):
    try:
        baglanti = db_baglan()
        imlec = baglanti.cursor()
        
        imlec.execute("SELECT iseBaslamaTarihi, format(iseBaslamaTarihi, 'dd.MM.yyyy') FROM kullanici WHERE id = ?", (kullanici_id,))
        row = imlec.fetchone()
        
        formatli_tarih = "-"
        ise_baslama_obj = None
        if row and row[0]:
            ise_baslama_obj = row[0]
            formatli_tarih = row[1]
        
        calisma_suresi = "-"
        if ise_baslama_obj:
            fark = datetime.now() - datetime.combine(ise_baslama_obj, datetime.min.time())
            yil = fark.days // 365
            ay = (fark.days % 365) // 30
            if yil > 0 and ay > 0:
                calisma_suresi = f"{yil} yıl {ay} ay"
            elif yil > 0:
                calisma_suresi = f"{yil} yıl"
            elif ay > 0:
                calisma_suresi = f"{ay} ay"
            else:
                calisma_suresi = "Yeni başladı"

        imlec.execute("""
            SELECT TOP 2 aciklama, format(tarih, 'dd.MM.yyyy HH:mm') 
            FROM islem_gecmisi 
            WHERE hedefKullaniciId = ? 
            ORDER BY tarih DESC
        """, (kullanici_id,))
        islemler = imlec.fetchall()

        imlec.execute("SELECT TOP 3 id, baslik, format(tarih, 'dd.MM.yyyy') FROM duyurular ORDER BY tarih DESC")
        son_duyurular = imlec.fetchall()
        
        baglanti.close()
        return formatli_tarih, calisma_suresi, islemler, son_duyurular
    except Exception as e:
        print(f"Ana sayfa veri çekme hatası: {e}")
        return "-", "-", [], []

def ana_sayfa_goster(sag_frame_ref, aktif_kullanici=None):
    frame_temizle()

    kullanici_adi = kullanici_adini_coz(aktif_kullanici)
    bugun_tarih = bugun_tarihi_getir()
    aktif_rol = OTURUM.get("rol", "personel")

    ZEMIN_BG = RENK.get("icerik_zemin", "#F8FAFC")
    KART_BG = RENK.get("kart_zemin", "#FFFFFF")
    KART_BORDER = RENK.get("border", "#E2E8F0")
    METIN_KOYU = RENK.get("metin_koyu", "#0F172A")
    METIN_GRI = RENK.get("metin_gri", "#64748B")
    MAVI_RENK = RENK.get("birincil", "#2563EB")

    baslik_frame = tk.Frame(sag_frame_ref, bg=ZEMIN_BG)
    baslik_frame.pack(fill="x", padx=30, pady=(20, 15))

    tk.Label(baslik_frame, text="Ana Sayfa", font=FONT_KUCUK, bg=ZEMIN_BG, fg=METIN_GRI).pack(anchor="w")
    tk.Label(baslik_frame, text=f"Hoş geldin, {kullanici_adi}", font=("Segoe UI", 20, "bold"), bg=ZEMIN_BG, fg=METIN_KOYU).pack(anchor="w", pady=(2, 0))
    tk.Label(baslik_frame, text=bugun_tarih, font=FONT_KUCUK, bg=ZEMIN_BG, fg=METIN_GRI).pack(anchor="w", pady=(2, 0))

    govde = tk.Frame(sag_frame_ref, bg=ZEMIN_BG)
    govde.pack(fill="both", expand=True, padx=30, pady=(0, 20))

    if aktif_rol == "admin":
        _admin_govde_olustur(govde, sag_frame_ref, ZEMIN_BG, KART_BG, KART_BORDER, METIN_KOYU, METIN_GRI, MAVI_RENK)
    else:
        _personel_govde_olustur(govde, sag_frame_ref, ZEMIN_BG, KART_BG, KART_BORDER, METIN_KOYU, METIN_GRI, MAVI_RENK)

def _admin_govde_olustur(govde, sag_frame_ref, ZEMIN_BG, KART_BG, KART_BORDER, METIN_KOYU, METIN_GRI, MAVI_RENK):
    kartlar_frame = tk.Frame(govde, bg=ZEMIN_BG)
    kartlar_frame.pack(fill="x", pady=(0, 20))

    # Dinamik istatistikleri veritabanından çek
    aktif_pers = "0"
    pasif_pers = "0"
    daire_s = "0"
    mudur_s = "0"

    try:
        baglanti = db_baglan()
        imlec = baglanti.cursor()
        imlec.execute("SELECT COUNT(*) FROM kullanici WHERE aktif = 1")
        aktif_pers = str(imlec.fetchone()[0])
        imlec.execute("SELECT COUNT(*) FROM kullanici WHERE aktif = 0")
        pasif_pers = str(imlec.fetchone()[0])
        imlec.execute("SELECT COUNT(*) FROM daireler")
        daire_s = str(imlec.fetchone()[0])
        imlec.execute("SELECT COUNT(*) FROM mudurlukler")
        mudur_s = str(imlec.fetchone()[0])
        baglanti.close()
    except Exception as e:
        print(f"İstatistik yüklenemedi: {e}")

    istatistikler = [
        {"baslik": "👥  Aktif personel", "deger": aktif_pers, "renk": "#16A34A"},
        {"baslik": "🔒  Pasif personel", "deger": pasif_pers, "renk": "#DC2626"},
        {"baslik": "🏢  Daire", "deger": daire_s, "renk": MAVI_RENK},
        {"baslik": "📁  Müdürlük", "deger": mudur_s, "renk": MAVI_RENK}
    ]

    for i, item in enumerate(istatistikler):
        k = tk.Frame(kartlar_frame, bg=KART_BG, highlightthickness=1, highlightbackground=KART_BORDER)
        k.pack(side="left", fill="both", expand=True, padx=(0 if i == 0 else 10, 0))
        tk.Label(k, text=item["baslik"], font=FONT_NORMAL, bg=KART_BG, fg=METIN_GRI).pack(anchor="w", padx=15, pady=(14, 4))
        tk.Label(k, text=item["deger"], font=("Segoe UI", 22, "bold"), bg=KART_BG, fg=item["renk"]).pack(anchor="w", padx=15, pady=(0, 14))

    yonetim_kard = tk.Frame(govde, bg=KART_BG, highlightthickness=1, highlightbackground=KART_BORDER, padx=20, pady=20)
    yonetim_kard.pack(fill="both", expand=True)

    tk.Label(yonetim_kard, text="📢 Kurum Duyuruları Yönetimi", font=FONT_ALT_BASLIK, bg=KART_BG, fg=METIN_KOYU).pack(anchor="w", pady=(0, 5))
    tk.Label(yonetim_kard, text="Kurum genelindeki duyuruları ekleyebilir, güncel duyuruları listeleyebilir ve silebilirsiniz.", font=FONT_NORMAL, bg=KART_BG, fg=METIN_GRI).pack(anchor="w", pady=(0, 15))

    def duyuru_paneline_git():
        from pages_duyurular import duyuru_yonetim_sayfasi
        sayfa_git(duyuru_yonetim_sayfasi, sag_frame_ref)

    tk.Button(
        yonetim_kard, text="Duyuruları Yönet / Ekle →", command=duyuru_paneline_git,
        bg=MAVI_RENK, fg="#FFFFFF", font=FONT_NORMAL, relief="flat", padx=15, pady=8, cursor="hand2"
    ).pack(anchor="w")

def _personel_govde_olustur(govde, sag_frame_ref, ZEMIN_BG, KART_BG, KART_BORDER, METIN_KOYU, METIN_GRI, MAVI_RENK):
    kendi_id = OTURUM.get("id")
    kisi = None
    tarih_str, calisma_suresi_str, islemler, son_duyurular = "-", "-", [], []

    if kendi_id:
        try:
            baglanti = db_baglan()
            imlec = baglanti.cursor()
            imlec.execute("""
                SELECT k.aktif, m.mudurlukAdi, d.daireAdi
                FROM kullanici k
                JOIN mudurlukler m ON k.mudurlukId = m.id
                JOIN daireler d ON m.daireId = d.id
                WHERE k.id = ?
            """, (kendi_id,))
            kisi = imlec.fetchone()
            baglanti.close()
        except Exception:
            kisi = None
        tarih_str, calisma_suresi_str, islemler, son_duyurular = get_personel_ek_veriler(kendi_id)

    kart = tk.Frame(govde, bg=KART_BG, highlightthickness=1, highlightbackground=KART_BORDER)
    kart.pack(fill="x", pady=(0, 15))
    ic = tk.Frame(kart, bg=KART_BG)
    ic.pack(fill="x", padx=20, pady=18)

    baslik_str = OTURUM.get("ad", "") + " " + OTURUM.get("soyad", "")
    tk.Label(ic, text=baslik_str.strip() or "Kullanıcı", font=FONT_ALT_BASLIK, bg=KART_BG, fg=METIN_KOYU).pack(anchor="w")

    if kisi:
        tk.Label(ic, text=kisi.mudurlukAdi or "-", font=FONT_NORMAL, bg=KART_BG, fg=METIN_GRI).pack(anchor="w", pady=(2, 0))
        tk.Label(ic, text=kisi.daireAdi or "-", font=FONT_KUCUK, bg=KART_BG, fg=METIN_GRI).pack(anchor="w", pady=(0, 8))
        durum_str = "✓ Aktif" if kisi.aktif == 1 else "✗ Pasif"
        durum_renk = "#16A34A" if kisi.aktif == 1 else "#DC2626"
        tk.Label(ic, text=durum_str, font=FONT_KUCUK, bg=KART_BG, fg=durum_renk).pack(anchor="w")
    else:
        tk.Label(ic, text="Bilgiler yüklenemedi.", font=FONT_KUCUK, bg=KART_BG, fg=METIN_GRI).pack(anchor="w", pady=(2, 8))

    def bilgilerim_tikla():
        from pages_personel_ara import personel_detay_tam_ekran
        sayfa_git(personel_detay_tam_ekran, sag_frame_ref, kendi_id)

    tk.Button(
        ic, text="Bilgilerimi Görüntüle →", command=bilgilerim_tikla,
        bg=KART_BG, fg=MAVI_RENK, font=FONT_KUCUK,
        activebackground=KART_BG, activeforeground=MAVI_RENK,
        relief="flat", bd=0, cursor="hand2", anchor="w"
    ).pack(anchor="w", pady=(10, 0))

    kpi_frame = tk.Frame(govde, bg=ZEMIN_BG)
    kpi_frame.pack(fill="x", pady=(0, 15))

    def kpi_karti_olustur(parent_frame, baslik, deger):
        k = tk.Frame(parent_frame, bg=KART_BG, highlightthickness=1, highlightbackground=KART_BORDER, padx=15, pady=12)
        k.pack(side="left", fill="both", expand=True, padx=(0, 10))
        tk.Label(k, text=baslik, font=FONT_KUCUK, bg=KART_BG, fg=METIN_GRI).pack(anchor="w")
        tk.Label(k, text=deger, font=("Segoe UI", 14, "bold"), bg=KART_BG, fg=METIN_KOYU).pack(anchor="w", pady=(4, 0))

    kpi_karti_olustur(kpi_frame, "📅 İşe Başlama Tarihi", tarih_str)
    kpi_karti_olustur(kpi_frame, "⏱️ Toplam Çalışma Süresi", calisma_suresi_str)

    alt_frame = tk.Frame(govde, bg=ZEMIN_BG)
    alt_frame.pack(fill="both", expand=True)

    islem_kard = tk.Frame(alt_frame, bg=KART_BG, highlightthickness=1, highlightbackground=KART_BORDER, padx=15, pady=15)
    islem_kard.pack(side="left", fill="both", expand=True, padx=(0, 10))

    tk.Label(islem_kard, text="🕒 Son İşlemlerim", font=FONT_ALT_BASLIK, bg=KART_BG, fg=METIN_KOYU).pack(anchor="w", pady=(0, 10))

    if islemler:
        for aciklama, tarih in islemler:
            row = tk.Frame(islem_kard, bg=KART_BG)
            row.pack(fill="x", pady=4)
            tk.Label(row, text=aciklama, font=FONT_NORMAL, bg=KART_BG, fg=METIN_KOYU).pack(anchor="w")
            tk.Label(row, text=tarih, font=FONT_KUCUK, bg=KART_BG, fg=METIN_GRI).pack(anchor="w")
    else:
        tk.Label(islem_kard, text="Henüz kayıtlı bir işlem bulunmuyor.", font=FONT_KUCUK, bg=KART_BG, fg=METIN_GRI).pack(anchor="w", pady=5)

    duyuru_kard = tk.Frame(alt_frame, bg=KART_BG, highlightthickness=1, highlightbackground=KART_BORDER, padx=15, pady=15)
    duyuru_kard.pack(side="left", fill="both", expand=True)

    tk.Label(duyuru_kard, text="📢 Kurum Duyuruları", font=FONT_ALT_BASLIK, bg=KART_BG, fg=METIN_KOYU).pack(anchor="w", pady=(0, 8))

    if son_duyurular:
        for d_id, d_baslik, d_tarih in son_duyurular:
            def detay_ac(did=d_id):
                from pages_duyurular import duyuru_detay_sayfasi
                duyuru_detay_sayfasi(sag_frame_ref, did)
            satir = tk.Frame(duyuru_kard, bg=KART_BG)
            satir.pack(fill="x", pady=3)
            tarih_lbl = tk.Label(satir, text=d_tarih, font=FONT_KUCUK, bg=KART_BG, fg=METIN_GRI, cursor="hand2")
            tarih_lbl.pack(side="right", padx=(5, 0))
            tarih_lbl.bind("<Button-1>", lambda e, did=d_id: detay_ac(did))
            baslik_btn = tk.Button(
                satir, text=d_baslik, font=FONT_NORMAL, bg=KART_BG, fg=METIN_KOYU,
                activebackground=KART_BG, activeforeground=MAVI_RENK,
                relief="flat", bd=0, cursor="hand2", anchor="w", command=detay_ac
            )
            baslik_btn.pack(side="left", fill="x", expand=True)
    else:
        tk.Label(duyuru_kard, text="Aktif duyuru bulunmuyor.", font=FONT_KUCUK, bg=KART_BG, fg=METIN_GRI).pack(anchor="w", pady=5)

    def duyurulari_ac():
        from pages_duyurular import personel_duyuru_listesi_sayfasi
        sayfa_git(personel_duyuru_listesi_sayfasi, sag_frame_ref)

    tk.Button(
        duyuru_kard, text="Tüm Duyuruları Görüntüle →", command=duyurulari_ac,
        bg=KART_BG, fg=MAVI_RENK, font=FONT_KUCUK,
        activebackground=KART_BG, activeforeground=MAVI_RENK,
        relief="flat", bd=0, cursor="hand2", anchor="w"
    ).pack(anchor="w", pady=(10, 0))