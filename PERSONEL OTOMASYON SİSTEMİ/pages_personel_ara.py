# ============================================================
#              PERSONEL ARA
# ============================================================

import os
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
from config import RENK, FONT_BASLIK, FONT_NORMAL, FONT_KUCUK, db_baglan, OTURUM
from utils import frame_temizle, sayfa_basligi, form_alani, daire_listesi_getir, geri_git, sayfa_git, yuvarlak_buton


def mudurluk_isimleri_getir():
    """Tüm müdürlük adlarını döndürür."""
    baglanti = db_baglan()
    imlec = baglanti.cursor()
    imlec.execute("SELECT DISTINCT mudurlukAdi FROM mudurlukler ORDER BY mudurlukAdi")
    isimler = [s.mudurlukAdi for s in imlec.fetchall()]
    baglanti.close()
    return isimler


def personel_ara_goster(sag_frame_ref):
    """Personel ara sayfasını gösterir."""
    frame_temizle()
    sayfa_basligi(sag_frame_ref, "Personel Ara", "Kriterlere göre filtreleyin")

    # İnce Filtre Barı (Dış Çerçeve)
    filtre_ana_bar = tk.Frame(
        sag_frame_ref, 
        bg=RENK["kart_zemin"], 
        highlightthickness=1, 
        highlightbackground=RENK["border"]
    )
    filtre_ana_bar.pack(fill="x", padx=30, pady=(0, 10))

    # Üst İnce Şerit
    akordeon_ust = tk.Frame(filtre_ana_bar, bg=RENK["kart_zemin"])
    akordeon_ust.pack(fill="x", padx=12, pady=6)

    toggle_btn = tk.Button(
        akordeon_ust, text="🔍 Filtreleri Göster ▼",
        bg=RENK["kart_zemin"], fg=RENK["birincil"], font=FONT_KUCUK,
        relief="flat", bd=0, cursor="hand2", anchor="w"
    )
    toggle_btn.pack(side="left")

    sonuc_etiket = tk.Label(
        akordeon_ust, text="Aramaya uyan 0 personel bulundu",
        font=FONT_KUCUK, bg=RENK["kart_zemin"], fg=RENK["metin_gri"]
    )
    sonuc_etiket.pack(side="right")

    # Açılır/Kapanır Filtre İçeriği
    filtre_ic_frame = tk.Frame(filtre_ana_bar, bg=RENK["kart_zemin"])

    def filtre_toggle():
        if filtre_ic_frame.winfo_ismapped():
            filtre_ic_frame.pack_forget()
            toggle_btn.config(text="🔍 Filtreleri Göster ▼")
        else:
            filtre_ic_frame.pack(fill="x", padx=12, pady=(0, 10))
            toggle_btn.config(text="▲ Filtreleri Gizle")

    toggle_btn.config(command=filtre_toggle)

    # Arama Izgarası
    izgara = tk.Frame(filtre_ic_frame, bg=RENK["kart_zemin"])
    izgara.pack(fill="x")

    sutun1 = tk.Frame(izgara, bg=RENK["kart_zemin"])
    sutun1.grid(row=0, column=0, sticky="nsew", padx=(0, 15))
    sutun2 = tk.Frame(izgara, bg=RENK["kart_zemin"])
    sutun2.grid(row=0, column=1, sticky="nsew", padx=(15, 0))
    izgara.columnconfigure(0, weight=1)
    izgara.columnconfigure(1, weight=1)

    ara_ad_kutu = form_alani(sutun1, "Ad")
    ara_tc_kutu = form_alani(sutun1, "TC")

    tk.Label(sutun1, text="Müdürlük", font=FONT_KUCUK, bg=RENK["kart_zemin"], fg=RENK["metin_gri"]).pack(anchor="w", pady=(4, 2))
    mudurluk_isimleri = mudurluk_isimleri_getir()
    ara_mudurluk_combo = ttk.Combobox(sutun1, values=["(Hepsi)"] + mudurluk_isimleri, state="readonly", font=FONT_NORMAL)
    ara_mudurluk_combo.pack(fill="x", ipady=2)
    ara_mudurluk_combo.set("(Hepsi)")

    # Yeni Durum Filtresi (Sütun 1 altına)
    tk.Label(sutun1, text="Durum", font=FONT_KUCUK, bg=RENK["kart_zemin"], fg=RENK["metin_gri"]).pack(anchor="w", pady=(4, 2))
    ara_durum_combo = ttk.Combobox(sutun1, values=["(Hepsi)", "Aktif", "Pasif"], state="readonly", font=FONT_NORMAL)
    ara_durum_combo.pack(fill="x", ipady=2)
    ara_durum_combo.set("(Hepsi)")

    ara_soyad_kutu = form_alani(sutun2, "Soyad")
    ara_tel_kutu = form_alani(sutun2, "Telefon")

    tk.Label(sutun2, text="Daire", font=FONT_KUCUK, bg=RENK["kart_zemin"], fg=RENK["metin_gri"]).pack(anchor="w", pady=(4, 2))
    daire_isimleri, _ = daire_listesi_getir()
    ara_daire_combo = ttk.Combobox(sutun2, values=["(Hepsi)"] + daire_isimleri, state="readonly", font=FONT_NORMAL)
    ara_daire_combo.pack(fill="x", ipady=2)
    ara_daire_combo.set("(Hepsi)")

    # --- BUTONLAR İÇİN ALT FRAME ---
    buton_frame = tk.Frame(filtre_ic_frame, bg=RENK["kart_zemin"])
    buton_frame.pack(anchor="w", pady=(10, 0))

    def ara_ve_kapat():
        personel_ara(
            ara_tree, ara_ad_kutu, ara_soyad_kutu, ara_tc_kutu,
            ara_tel_kutu, ara_mudurluk_combo, ara_daire_combo, ara_durum_combo, sonuc_etiket
        )
        filtre_ic_frame.pack_forget()
        toggle_btn.config(text="🔍 Filtreleri Göster ▼")

    def filtre_temizle():
        """Tüm filtre kutularını sıfırlar ve tüm listeyi yeniden çeker."""
        ara_ad_kutu.delete(0, tk.END)
        ara_soyad_kutu.delete(0, tk.END)
        ara_tc_kutu.delete(0, tk.END)
        ara_tel_kutu.delete(0, tk.END)
        ara_mudurluk_combo.set("(Hepsi)")
        ara_daire_combo.set("(Hepsi)")
        ara_durum_combo.set("(Hepsi)")
        personel_ara(
            ara_tree, ara_ad_kutu, ara_soyad_kutu, ara_tc_kutu,
            ara_tel_kutu, ara_mudurluk_combo, ara_daire_combo, ara_durum_combo, sonuc_etiket
        )

    yuvarlak_buton(buton_frame, "🔍  Ara", ara_ve_kapat).pack(side="left", padx=(0, 8))
    yuvarlak_buton(
        buton_frame, "🧹  Temizle", filtre_temizle,
        renk="#6B7280", hover_renk="#4B5563"
    ).pack(side="left")

    # Sonuç Tablosu
    govde = tk.Frame(sag_frame_ref, bg=RENK["icerik_zemin"])
    govde.pack(fill="both", expand=True, padx=30, pady=(0, 20))

    # Sütun kaymalarını önlemek için anchor ve minwidth tanımları eklendi
    ara_tree = ttk.Treeview(
        govde,
        columns=("db_id", "sira", "ad", "soyad", "tc", "telefon", "birim", "daire", "durum"),
        displaycolumns=("sira", "ad", "soyad", "tc", "telefon", "birim", "daire", "durum"),
        show="headings"
    )

    basliklar = {
        "sira": "Sıra",
        "ad": "Ad",
        "soyad": "Soyad",
        "tc": "TC",
        "telefon": "Telefon",
        "birim": "Müdürlük",
        "daire": "Daire",
        "durum": "Durum"
    }
    
    # Sütun genişlikleri ve esneme / sabitleme ayarları
    genislikler = {
        "sira": 60,
        "ad": 110,
        "soyad": 110,
        "tc": 120,
        "telefon": 120,
        "birim": 180,
        "daire": 200,
        "durum": 90
    }

    for kolon in ("sira", "ad", "soyad", "tc", "telefon", "birim", "daire", "durum"):
        ara_tree.heading(kolon, text=basliklar[kolon], anchor="w")
        # Sütunların sola dayalı olması ve kaymayı önlemek için minwidth eklendi
        ara_tree.column(kolon, width=genislikler[kolon], minwidth=genislikler[kolon], anchor="w", stretch=True)

    ara_tree.pack(fill="both", expand=True)

    def on_tree_double_click(event):
        secili_item = ara_tree.selection()
        if secili_item:
            item_values = ara_tree.item(secili_item[0], "values")
            if item_values:
                kisi_id = item_values[0]
                sayfa_git(personel_detay_tam_ekran, sag_frame_ref, kisi_id)

    ara_tree.bind("<Double-1>", on_tree_double_click)

    personel_ara(
        ara_tree, ara_ad_kutu, ara_soyad_kutu, ara_tc_kutu,
        ara_tel_kutu, ara_mudurluk_combo, ara_daire_combo, ara_durum_combo, sonuc_etiket
    )


def personel_ara(ara_tree, ara_ad_kutu, ara_soyad_kutu, ara_tc_kutu, ara_tel_kutu, ara_mudurluk_combo, ara_daire_combo, ara_durum_combo, sonuc_etiket):
    """Arama işlemini gerçekleştirir."""
    ad = ara_ad_kutu.get().strip()
    soyad = ara_soyad_kutu.get().strip()
    tc = ara_tc_kutu.get().strip()
    tel = ara_tel_kutu.get().strip()
    mudurluk = ara_mudurluk_combo.get()
    daire = ara_daire_combo.get()
    durum_secim = ara_durum_combo.get()

    sorgu = """
        SELECT k.id, k.kullaniciAd, k.kullaniciSoyad, k.Tc, k.telefonNO, m.mudurlukAdi, d.daireAdi, k.aktif
        FROM kullanici k
        JOIN mudurlukler m ON k.mudurlukId = m.id
        JOIN daireler d ON m.daireId = d.id
        WHERE 1=1
    """
    parametreler = []

    if ad:
        sorgu += " AND k.kullaniciAd LIKE ?"
        parametreler.append(f"%{ad}%")
    if soyad:
        sorgu += " AND k.kullaniciSoyad LIKE ?"
        parametreler.append(f"%{soyad}%")
    if tc:
        sorgu += " AND k.Tc LIKE ?"
        parametreler.append(f"%{tc}%")
    if tel:
        sorgu += " AND k.telefonNO LIKE ?"
        parametreler.append(f"%{tel}%")
    if mudurluk and mudurluk != "(Hepsi)":
        sorgu += " AND m.mudurlukAdi = ?"
        parametreler.append(mudurluk)
    if daire and daire != "(Hepsi)":
        sorgu += " AND d.daireAdi = ?"
        parametreler.append(daire)
    
    # Durum filtresi eklemesi
    if durum_secim == "Aktif":
        sorgu += " AND k.aktif = 1"
    elif durum_secim == "Pasif":
        sorgu += " AND k.aktif = 0"

    sorgu += " ORDER BY k.aktif DESC, k.kullaniciAd"

    for row in ara_tree.get_children():
        ara_tree.delete(row)

    try:
        baglanti = db_baglan()
        imlec = baglanti.cursor()
        imlec.execute(sorgu, parametreler)
        kayitlar = imlec.fetchall()
        baglanti.close()

        for idx, kisi in enumerate(kayitlar, start=1):
            durum_str = "✓ Aktif" if kisi.aktif == 1 else "✗ Pasif"
            ara_tree.insert("", "end", values=(
                kisi.id,
                idx,
                kisi.kullaniciAd,
                kisi.kullaniciSoyad,
                kisi.Tc,
                kisi.telefonNO,
                kisi.mudurlukAdi,
                kisi.daireAdi,
                durum_str
            ))

        sonuc_etiket.config(text=f"Aramaya uyan {len(kayitlar)} personel bulundu")

    except Exception as e:
        messagebox.showerror("Hata", f"Arama işlemi sırasında bir hata oluştu:\n{e}")


# ============================================================
#         PERSONEL DETAYI - YENİLENMİŞ PROFİL KARTI
# ============================================================

def personel_detay_tam_ekran(sag_frame_ref, secili_id):
    """Personel detaylarını ekranı tam dolduran modern bir profil kartı olarak gösterir."""
    frame_temizle()
    sayfa_basligi(sag_frame_ref, "Personel Detayı", "Personel bilgilerini görüntüleyin ve yönetin")

    baglanti = db_baglan()
    imlec = baglanti.cursor()
    imlec.execute("""
        SELECT k.id, k.kullaniciAd, k.kullaniciSoyad, k.Tc, k.telefonNO, k.dogumTarihi,
               k.fotograf, k.aktif, m.mudurlukAdi, d.daireAdi,
               format(k.iseBaslamaTarihi, 'dd.MM.yyyy') as iseBaslamaFormatli
        FROM kullanici k
        JOIN mudurlukler m ON k.mudurlukId = m.id
        JOIN daireler d ON m.daireId = d.id
        WHERE k.id = ?
    """, (secili_id,))
    kisi = imlec.fetchone()
    baglanti.close()

    if not kisi:
        tk.Label(sag_frame_ref, text="Personel bulunamadı.", bg=RENK["icerik_zemin"],
                 fg=RENK["tehlike"], font=FONT_NORMAL).pack(anchor="w", padx=30, pady=20)
        return

    aktif_rol = OTURUM.get("rol", "personel")

    ana_kart = tk.Frame(sag_frame_ref, bg=RENK["kart_zemin"], highlightthickness=1, highlightbackground=RENK["border"])
    ana_kart.pack(fill="both", expand=True, padx=30, pady=(0, 20))

    # --- SOL PANEL: Büyük fotoğraf + isim/müdürlük + aksiyonlar ---
    sol_panel = tk.Frame(ana_kart, bg=RENK["kart_zemin"], width=300)
    sol_panel.pack(side="left", fill="y", padx=30, pady=30)
    sol_panel.pack_propagate(False)

    foto_cerceve = tk.Frame(sol_panel, bg=RENK["kart_zemin"], highlightthickness=1, highlightbackground=RENK["border"])
    foto_cerceve.pack(pady=(0, 15))
    foto_etiketi = tk.Label(foto_cerceve, bg=RENK["kart_zemin"])
    foto_etiketi.pack()

    try:
        if kisi.fotograf and os.path.exists(kisi.fotograf):
            img = Image.open(kisi.fotograf)
            img.thumbnail((240, 240))
            foto_img = ImageTk.PhotoImage(img)
            foto_etiketi.image = foto_img
            foto_etiketi.config(image=foto_img)
        else:
            foto_etiketi.config(text="📷\nFotoğraf Yok", fg=RENK["metin_gri"], font=FONT_KUCUK, width=20, height=10)
    except Exception:
        foto_etiketi.config(text="Fotoğraf yüklenemedi", fg=RENK["metin_gri"], font=FONT_KUCUK, width=20, height=10)

    # İsim
    tk.Label(sol_panel, text=f"{kisi.kullaniciAd} {kisi.kullaniciSoyad}", font=FONT_BASLIK,
             bg=RENK["kart_zemin"], fg=RENK["metin_koyu"], wraplength=260, justify="center").pack(pady=(0, 2))

    # Müdürlük adı alt başlık
    tk.Label(sol_panel, text=kisi.mudurlukAdi or "-", font=FONT_NORMAL,
             bg=RENK["kart_zemin"], fg=RENK["metin_gri"], wraplength=260, justify="center").pack(pady=(0, 8))

    durum_str = "✓ Aktif Personel" if kisi.aktif == 1 else "✗ Pasif Personel"
    durum_renk = RENK["basarili"] if kisi.aktif == 1 else RENK["tehlike"]
    tk.Label(sol_panel, text=durum_str, font=FONT_KUCUK, bg=RENK["kart_zemin"], fg=durum_renk).pack(pady=(0, 20))

    def duzenle_tikla():
        try:
            from pages_personel_duzenle import personel_duzenle_goster
            sayfa_git(personel_duzenle_goster, sag_frame_ref, secili_id)
        except ImportError:
            messagebox.showinfo("Bilgi", "Düzenleme sayfası henüz bağlanmadı.")

    def aktif_pasif_tikla():
        baglanti2 = db_baglan()
        imlec2 = baglanti2.cursor()
        
        # Personelin mevcut durumunu ve bilgilerini alalım
        imlec2.execute("SELECT aktif, kullaniciAd, kullaniciSoyad FROM kullanici WHERE id = ?", (secili_id,))
        kisi_bilgi = imlec2.fetchone()
        
        yeni_durum = 0 if kisi_bilgi.aktif == 1 else 1
        durum_metni = "Aktif" if yeni_durum == 1 else "Pasif"
        
        # Durumu güncelle
        imlec2.execute("UPDATE kullanici SET aktif = ? WHERE id = ?", (yeni_durum, secili_id))
        baglanti2.commit()
        
        # İşlem geçmişine log kaydı ekleme
        try:
            from log import log_ekle
            yapan_id = OTURUM.get("id", 1)
            aciklama_metni = f"{kisi_bilgi.kullaniciAd} {kisi_bilgi.kullaniciSoyad} adlı personelin durumu '{durum_metni}' olarak değiştirildi."
            log_ekle(secili_id, yapan_id, aciklama_metni)
        except Exception as e:
            print(f"Log atılamadı: {e}")
            
        baglanti2.close()
        personel_detay_tam_ekran(sag_frame_ref, secili_id)

    yuvarlak_buton(sol_panel, "✎  Personel Düzenle", duzenle_tikla).pack(fill="x", pady=4)

    if aktif_rol == "admin":
        yuvarlak_buton(sol_panel, "↔  Durum Değiştir", aktif_pasif_tikla,
                       renk=RENK["sidebar_buton"], hover_renk=RENK["sidebar_hover"]).pack(fill="x", pady=4)

    yuvarlak_buton(sol_panel, "←  Geri Dön", lambda: geri_git(),
                   renk="#6B7280", hover_renk="#4B5563").pack(fill="x", pady=4)

    # --- SAĞ PANEL: Detay bilgi kartları ---
    sag_panel = tk.Frame(ana_kart, bg=RENK["kart_zemin"])
    sag_panel.pack(side="left", fill="both", expand=True, padx=(0, 30), pady=30)

    dogum_str = kisi.dogumTarihi.strftime("%d/%m/%Y") if (hasattr(kisi.dogumTarihi, 'strftime') and kisi.dogumTarihi) else str(kisi.dogumTarihi or "-")
    baslama_tarihi_str = kisi.iseBaslamaFormatli if kisi.iseBaslamaFormatli else "-"

    bilgiler = [
        ("TC Kimlik No", kisi.Tc, "💳"),
        ("Telefon No", kisi.telefonNO, "📞"),
        ("Doğum Tarihi", dogum_str, "📅"),
        ("İşe Başlama Tarihi", baslama_tarihi_str, "⏱️"),
        ("Müdürlük", kisi.mudurlukAdi, "🏢"),
        ("Daire Başkanlığı", kisi.daireAdi, "🏛️"),
    ]

    for etiket, deger, ikon in bilgiler:
        kutucuk = tk.Frame(sag_panel, bg=RENK["icerik_zemin"], highlightthickness=1, highlightbackground=RENK["border"])
        kutucuk.pack(fill="x", pady=5, ipady=3, ipadx=12)

        # Dikey ortalanmış kusursuz ikon + etiket satırı
        ust_satir = tk.Frame(kutucuk, bg=RENK["icerik_zemin"])
        ust_satir.pack(fill="x", pady=(2, 0))

        icon_lbl = tk.Label(ust_satir, text=ikon, font=("Segoe UI Emoji", 10), bg=RENK["icerik_zemin"], fg=RENK["metin_gri"])
        icon_lbl.pack(side="left", padx=(0, 6))

        etiket_lbl = tk.Label(ust_satir, text=etiket, font=("Segoe UI", 10, "bold"), bg=RENK["icerik_zemin"], fg=RENK["metin_gri"])
        etiket_lbl.pack(side="left")

        val_str = str(deger) if deger else "-"
        kopyalanabilir_kutu = tk.Entry(
            kutucuk,
            font=("Segoe UI", 11),
            bg=RENK["icerik_zemin"],
            fg=RENK["metin_koyu"],
            relief="flat",
            readonlybackground=RENK["icerik_zemin"],
            highlightthickness=0,
            justify="left"
        )
        kopyalanabilir_kutu.insert(0, val_str)
        kopyalanabilir_kutu.config(state="readonly")
        kopyalanabilir_kutu.pack(fill="x", anchor="w", pady=(2, 4))