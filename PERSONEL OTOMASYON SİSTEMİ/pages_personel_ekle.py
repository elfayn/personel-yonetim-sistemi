# ============================================================
#                    PERSONEL EKLE
# ============================================================

import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import os
from config import RENK, FONT_KUCUK, FONT_NORMAL, db_baglan, OTURUM
from utils import frame_temizle, sayfa_basligi, form_alani, kart_frame, yuvarlak_buton, tc_kontrol, telefon_kontrol, mudurluk_secenekleri_getir
from log import log_ekle

# Global değişkenler
ekle_ad_kutu = None
ekle_soyad_kutu = None
ekle_tc_kutu = None
ekle_tel_kutu = None
ekle_dogum_kutu = None
ekle_mudurluk_combo = None
secilen_foto_yolu = ""
ekle_sonuc_label = None
ekle_gosterim_bilgi = {}
foto_label = None
onizleme_label = None
ekle_onizleme_resmi = None

TARIH_PLACEHOLDER = "GG/AA/YYYY"

def fotograf_sec():
    """Fotoğraf seçer."""
    global secilen_foto_yolu, ekle_onizleme_resmi
    dosya_yolu = filedialog.askopenfilename(
        title="Fotoğraf Seç",
        filetypes=[("Resim Dosyaları", "*.jpg *.jpeg *.png")]
    )
    if dosya_yolu:
        secilen_foto_yolu = dosya_yolu
        foto_label.config(text="Seçildi ✓", fg=RENK["basarili"])
        try:
            img = Image.open(dosya_yolu)
            img.thumbnail((50, 50))
            ekle_onizleme_resmi = ImageTk.PhotoImage(img)
            onizleme_label.config(image=ekle_onizleme_resmi)
        except Exception:
            onizleme_label.config(image="")

def yeni_personel_kaydet():
    """Yeni personel kaydeder."""
    global secilen_foto_yolu

    ad = ekle_ad_kutu.get().strip()
    soyad = ekle_soyad_kutu.get().strip()
    tc = ekle_tc_kutu.get().strip()
    tel = ekle_tel_kutu.get().strip()
    dogum = ekle_dogum_kutu.get().strip()
    if dogum == TARIH_PLACEHOLDER:
        dogum = ""
    secili_gosterim = ekle_mudurluk_combo.get()

    if ad == "" or soyad == "" or tc == "" or tel == "":
        ekle_sonuc_label.config(text="Ad, Soyad, TC ve Telefon boş bırakılamaz!", fg=RENK["tehlike"])
        return

    if not tc_kontrol(tc):
        ekle_sonuc_label.config(text="TC 11 haneli olmalı!", fg=RENK["tehlike"])
        return

    if not telefon_kontrol(tel):
        ekle_sonuc_label.config(text="Telefon 11 haneli olmalı ve 05 ile başlamalı!", fg=RENK["tehlike"])
        return

    if secili_gosterim == "" or secili_gosterim not in ekle_gosterim_bilgi:
        ekle_sonuc_label.config(text="Lütfen bir Daire / Müdürlük seçin!", fg=RENK["tehlike"])
        return

    sifre = tc[-6:]

    dogum_db = None
    if dogum:
        digits = ''.join(c for c in dogum if c.isdigit())
        if len(digits) == 8:
            gg, aa, yyyy = digits[0:2], digits[2:4], digits[4:8]
            dogum_db = f"{yyyy}-{aa}-{gg}"

    mudurluk_id, mudurluk_adi, daire_adi = ekle_gosterim_bilgi[secili_gosterim]

    try:
        baglanti = db_baglan()
        imlec = baglanti.cursor()
        
        sorgu = """
            INSERT INTO kullanici
                (kullaniciAd, kullaniciSoyad, Tc, telefonNO, sifre, aktif, dogumTarihi, birim, daire, fotograf, mudurlukId, iseBaslamaTarihi)
            VALUES (?, ?, ?, ?, ?, 1, ?, ?, ?, ?, ?, GETDATE());
            SELECT SCOPE_IDENTITY();
        """
        imlec.execute(sorgu, ad, soyad, tc, tel, sifre, dogum_db, mudurluk_adi, daire_adi, secilen_foto_yolu, mudurluk_id)
        
        imlec.nextset()
        result = imlec.fetchone()
        yeni_personel_id = int(result[0]) if result and result[0] is not None else None

        baglanti.commit()
        baglanti.close()

        if yeni_personel_id:
            log_ekle(
                hedef_id=yeni_personel_id,
                yapan_id=OTURUM.get("id"),
                aciklama=f"Yeni personel sisteme eklendi: {ad} {soyad}"
            )

        ekle_sonuc_label.config(text=f"Personel eklendi! İlk Şifre: {sifre}", fg=RENK["basarili"])

        ekle_ad_kutu.delete(0, tk.END)
        ekle_soyad_kutu.delete(0, tk.END)
        ekle_tc_kutu.delete(0, tk.END)

        ekle_tel_kutu.delete(0, tk.END)
        ekle_tel_kutu.insert(0, "05")
        ekle_tel_kutu.icursor(tk.END)

        ekle_dogum_kutu.delete(0, tk.END)
        ekle_dogum_kutu.insert(0, TARIH_PLACEHOLDER)
        ekle_dogum_kutu.config(fg=RENK["metin_gri"])

        ekle_mudurluk_combo.set("")
        foto_label.config(text="Henüz seçilmedi", fg=RENK["metin_gri"])
        onizleme_label.config(image="")

        secilen_foto_yolu = ""
        ekle_ad_kutu.focus()

    except Exception as e:
        ekle_sonuc_label.config(text=f"Kayıt Hatası: {str(e)}", fg=RENK["tehlike"])

def personel_ekle_goster(sag_frame_ref):
    """Personel ekle sayfasını gösterir."""
    global ekle_ad_kutu, ekle_soyad_kutu, ekle_tc_kutu, ekle_tel_kutu, ekle_dogum_kutu, ekle_mudurluk_combo
    global ekle_sonuc_label, ekle_gosterim_bilgi, foto_label, onizleme_label

    frame_temizle()
    sayfa_basligi(sag_frame_ref, "Personel Ekle", "Yeni personel kaydı oluşturun")

    kart = kart_frame(sag_frame_ref)

    sol = tk.Frame(kart, bg=RENK["kart_zemin"])
    sol.pack(side="left", fill="both", expand=True, padx=(0, 15))
    sag = tk.Frame(kart, bg=RENK["kart_zemin"])
    sag.pack(side="left", fill="both", expand=True, padx=(15, 0))

    ekle_ad_kutu = form_alani(sol, "Ad")
    ekle_soyad_kutu = form_alani(sol, "Soyad")

    # TC Kimlik No - Koyu Tema Uyumlu form_alani kullanıldı
    tk.Label(sol, text="TC Kimlik No", font=FONT_KUCUK, bg=RENK["kart_zemin"], fg=RENK["metin_gri"]).pack(anchor="w", pady=(8, 2))
    ekle_tc_kutu = tk.Entry(sol, font=FONT_NORMAL, relief="flat", 
                            bg=RENK["icerik_zemin"], fg=RENK["metin_koyu"],
                            insertbackground="white",
                            highlightthickness=1, highlightbackground=RENK["border"], highlightcolor=RENK["birincil"])
    ekle_tc_kutu.pack(fill="x", ipady=6)

    def tc_input_kontrol(event=None):
        deger = ekle_tc_kutu.get()
        cleaned = ''.join(c for c in deger if c.isdigit())
        if len(cleaned) > 11:
            cleaned = cleaned[:11]
        ekle_tc_kutu.delete(0, tk.END)
        ekle_tc_kutu.insert(0, cleaned)
    ekle_tc_kutu.bind('<KeyRelease>', tc_input_kontrol)

    # Telefon - Koyu Tema Uyumlu
    tk.Label(sol, text="Telefon", font=FONT_KUCUK, bg=RENK["kart_zemin"], fg=RENK["metin_gri"]).pack(anchor="w", pady=(8, 2))
    ekle_tel_kutu = tk.Entry(sol, font=FONT_NORMAL, relief="flat", 
                             bg=RENK["icerik_zemin"], fg=RENK["metin_koyu"],
                             insertbackground="white",
                             highlightthickness=1, highlightbackground=RENK["border"], highlightcolor=RENK["birincil"])
    ekle_tel_kutu.pack(fill="x", ipady=6)
    ekle_tel_kutu.insert(0, "05")

    def tel_input_kontrol(event=None):
        deger = ekle_tel_kutu.get()
        cleaned = ''.join(c for c in deger if c.isdigit())
        if len(cleaned) > 11:
            cleaned = cleaned[:11]
        if cleaned == "":
            cleaned = "05"
        elif not cleaned.startswith("05"):
            cleaned = ("05" + cleaned)[:11]
        ekle_tel_kutu.delete(0, tk.END)
        ekle_tel_kutu.insert(0, cleaned)
        ekle_tel_kutu.icursor(tk.END)
    ekle_tel_kutu.bind('<KeyRelease>', tel_input_kontrol)
    ekle_tel_kutu.bind('<FocusIn>', lambda e: ekle_tel_kutu.icursor(tk.END))

    def dogum_input_kontrol(event=None):
        deger = ekle_dogum_kutu.get()
        cleaned = ''.join(c for c in deger if c.isdigit())
        if len(cleaned) > 8:
            cleaned = cleaned[:8]

        parcalar = []
        if len(cleaned) > 0:
            parcalar.append(cleaned[0:2])
        if len(cleaned) > 2:
            parcalar.append(cleaned[2:4])
        if len(cleaned) > 4:
            parcalar.append(cleaned[4:8])
        formatli = "/".join(parcalar)

        ekle_dogum_kutu.delete(0, tk.END)
        ekle_dogum_kutu.insert(0, formatli)
        ekle_dogum_kutu.icursor(tk.END)

    # Doğum Tarihi - Koyu Tema Uyumlu
    tk.Label(sol, text="Doğum Tarihi", font=FONT_KUCUK, bg=RENK["kart_zemin"], fg=RENK["metin_gri"]).pack(anchor="w", pady=(8, 2))
    ekle_dogum_kutu = tk.Entry(sol, font=FONT_NORMAL, relief="flat", 
                               bg=RENK["icerik_zemin"], fg=RENK["metin_koyu"],
                               insertbackground="white",
                               highlightthickness=1, highlightbackground=RENK["border"], highlightcolor=RENK["birincil"])
    ekle_dogum_kutu.pack(fill="x", ipady=6)
    ekle_dogum_kutu.insert(0, TARIH_PLACEHOLDER)
    ekle_dogum_kutu.config(fg=RENK["metin_gri"])
    ekle_dogum_kutu.bind('<KeyRelease>', dogum_input_kontrol)

    def dogum_focus_in(event=None):
        if ekle_dogum_kutu.get() == TARIH_PLACEHOLDER:
            ekle_dogum_kutu.delete(0, tk.END)
            ekle_dogum_kutu.config(fg=RENK["metin_koyu"])

    def dogum_focus_out(event=None):
        if ekle_dogum_kutu.get().strip() == "":
            ekle_dogum_kutu.insert(0, TARIH_PLACEHOLDER)
            ekle_dogum_kutu.config(fg=RENK["metin_gri"])

    ekle_dogum_kutu.bind('<FocusIn>', dogum_focus_in)
    ekle_dogum_kutu.bind('<FocusOut>', dogum_focus_out)

    tk.Label(sol, text="Şifre", font=FONT_KUCUK, bg=RENK["kart_zemin"], fg=RENK["metin_gri"]).pack(anchor="w", pady=(8, 2))
    tk.Label(sol, text="Şifre sistem tarafından otomatik atanacaktır. İlk şifre: TC'nin son 6 hanesi",
             font=FONT_KUCUK, bg=RENK["kart_zemin"], fg=RENK["metin_gri"], wraplength=500).pack(anchor="w", pady=(0, 8))

    tk.Label(sag, text="Daire / Müdürlük", font=FONT_KUCUK, bg=RENK["kart_zemin"], fg=RENK["metin_gri"]).pack(anchor="w", pady=(8, 2))
    gosterim_listesi, ekle_gosterim_bilgi, _ = mudurluk_secenekleri_getir()

    from tkinter import ttk
    ekle_mudurluk_combo = ttk.Combobox(sag, values=gosterim_listesi, state="readonly", font=FONT_NORMAL, style="TCombobox")
    ekle_mudurluk_combo.pack(fill="x", ipady=4)

    tk.Label(sag, text="Fotoğraf", font=FONT_KUCUK, bg=RENK["kart_zemin"], fg=RENK["metin_gri"]).pack(anchor="w", pady=(8, 2))
    foto_satiri = tk.Frame(sag, bg=RENK["kart_zemin"])
    foto_satiri.pack(fill="x", pady=(0, 5))
    yuvarlak_buton(foto_satiri, "📁  Fotoğraf Seç", fotograf_sec,
                   renk=RENK["sidebar_buton"], hover_renk=RENK["sidebar_hover"]).pack(side="left")
    foto_label = tk.Label(foto_satiri, text="Henüz seçilmedi", bg=RENK["kart_zemin"], fg=RENK["metin_gri"], font=FONT_KUCUK)
    foto_label.pack(side="left", padx=10)
    onizleme_label = tk.Label(foto_satiri, bg=RENK["kart_zemin"], highlightthickness=1, highlightbackground=RENK["border"])
    onizleme_label.pack(side="left", padx=(0, 10))

    alt = tk.Frame(sag_frame_ref, bg=RENK["icerik_zemin"])
    alt.pack(fill="x", padx=30, pady=10)
    yuvarlak_buton(alt, "✓  Kaydet", yeni_personel_kaydet).pack(side="left")

    ekle_sonuc_label = tk.Label(alt, text="", bg=RENK["icerik_zemin"], font=FONT_NORMAL)
    ekle_sonuc_label.pack(side="left", padx=15)