# ============================================================
#                 PERSONEL DÜZENLE
# ============================================================

import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import os
from config import RENK, FONT_KUCUK, FONT_NORMAL, db_baglan, OTURUM
from utils import (
    frame_temizle, sayfa_basligi, form_alani, kart_frame, yuvarlak_buton,
    tc_kontrol, telefon_kontrol, mudurluk_secenekleri_getir, geri_git
)
from log import log_ekle

# Sayfa durumu ve widget referanslarını tutan sözlük
state = {
    "ad_kutu": None,
    "soyad_kutu": None,
    "tc_kutu": None,
    "tel_kutu": None,
    "sifre_kutu": None,
    "dogum_kutu": None,
    "mudurluk_combo": None,
    "secilen_foto_yolu": "",
    "sonuc_label": None,
    "gosterim_bilgi": {},
    "foto_label": None,
    "onizleme_label": None,
    "onizleme_resmi": None,
    "secili_id": None,
    "sag_frame_ref": None
}

TARIH_PLACEHOLDER = "GG/AA/YYYY"

def fotograf_sec():
    """Fotoğraf seçme penceresini açar ve seçilen resmi önizler."""
    global state
    dosya_yolu = filedialog.askopenfilename(
        title="Fotoğraf Seç",
        filetypes=[("Resim Dosyaları", "*.jpg *.jpeg *.png")]
    )
    if dosya_yolu:
        state["secilen_foto_yolu"] = dosya_yolu
        state["foto_label"].config(text="Seçildi ✓", fg=RENK["basarili"])
        try:
            img = Image.open(dosya_yolu)
            img.thumbnail((100, 100))
            state["onizleme_resmi"] = ImageTk.PhotoImage(img)
            state["onizleme_label"].config(image=state["onizleme_resmi"])
        except Exception:
            state["onizleme_label"].config(image="")

def personel_guncelle():
    """Personel bilgilerini doğrular ve veritabanını günceller."""
    global state

    ad = state["ad_kutu"].get().strip()
    soyad = state["soyad_kutu"].get().strip()
    tc = state["tc_kutu"].get().strip()
    tel = state["tel_kutu"].get().strip()
    sifre = state["sifre_kutu"].get().strip()
    dogum = state["dogum_kutu"].get().strip()
    if dogum == TARIH_PLACEHOLDER:
        dogum = ""
    secili_gosterim = state["mudurluk_combo"].get()

    if ad == "" or soyad == "" or tc == "" or tel == "" or sifre == "":
        state["sonuc_label"].config(text="Ad, Soyad, TC, Telefon ve Şifre boş bırakılamaz!", fg=RENK["tehlike"])
        return

    if not tc_kontrol(tc):
        state["sonuc_label"].config(text="TC 11 haneli olmalı!", fg=RENK["tehlike"])
        return

    if not telefon_kontrol(tel):
        state["sonuc_label"].config(text="Telefon 11 haneli olmalı ve 05 ile başlamalı!", fg=RENK["tehlike"])
        return

    if secili_gosterim == "" or secili_gosterim not in state["gosterim_bilgi"]:
        state["sonuc_label"].config(text="Lütfen bir Daire / Müdürlük seçin!", fg=RENK["tehlike"])
        return

    # Tarihi veritabanı formatına (YYYY-MM-DD) dönüştür
    if dogum and len(dogum) == 10 and dogum[2] == '/' and dogum[5] == '/':
        try:
            gun, ay, yil = dogum.split('/')
            dogum_db = f"{yil}-{ay}-{gun}"
        except:
            dogum_db = None
    else:
        dogum_db = None

    mudurluk_id, mudurluk_adi, daire_adi = state["gosterim_bilgi"][secili_gosterim]

    try:
        baglanti = db_baglan()
        imlec = baglanti.cursor()
        imlec.execute(
            """UPDATE kullanici
               SET kullaniciAd = ?, kullaniciSoyad = ?, Tc = ?, telefonNO = ?, sifre = ?, dogumTarihi = ?,
                   birim = ?, daire = ?, fotograf = ?, mudurlukId = ?
               WHERE id = ?""",
            ad, soyad, tc, tel, sifre, dogum_db, mudurluk_adi, daire_adi, state["secilen_foto_yolu"], mudurluk_id, state["secili_id"]
        )
        baglanti.commit()

        try:
            yapan_id = OTURUM.get("id")
            log_ekle(
                hedef_id=state["secili_id"], 
                yapan_id=yapan_id, 
                aciklama="Personel bilgileri güncellendi."
            )
        except Exception as log_err:
            print(f"İşlem geçmişi log hatası: {log_err}")

        baglanti.close()

        messagebox.showinfo("Başarılı", "Personel bilgileri başarıyla güncellendi.")
        geri_git()
    except Exception as e:
        messagebox.showerror("Hata", f"Güncelleme sırasında bir hata oluştu:\n{e}")

def personel_duzenle_goster(sag_frame_ref, secili_id):
    """Personel düzenleme arayüzünü oluşturur ve verileri yükler."""
    global state
    state["secili_id"] = secili_id
    state["sag_frame_ref"] = sag_frame_ref

    aktif_rol = OTURUM.get("rol", "personel")

    frame_temizle()
    sayfa_basligi(sag_frame_ref, "Personel Düzenle", "Personel bilgilerini güncelleyin")

    try:
        baglanti = db_baglan()
        imlec = baglanti.cursor()
        imlec.execute("""
            SELECT kullaniciAd, kullaniciSoyad, Tc, telefonNO, sifre, dogumTarihi, fotograf, mudurlukId
            FROM kullanici
            WHERE id = ?
        """, secili_id)
        kisi = imlec.fetchone()
        baglanti.close()
    except Exception as e:
        messagebox.showerror("Hata", f"Veri çekme hatası:\n{e}")
        return

    if not kisi:
        tk.Label(sag_frame_ref, text="Personel bulunamadı.", bg=RENK["icerik_zemin"],
                 fg=RENK["tehlike"], font=FONT_NORMAL).pack(anchor="w", padx=30, pady=20)
        return

    state["secilen_foto_yolu"] = kisi.fotograf if kisi.fotograf else ""

    kart = kart_frame(sag_frame_ref)

    sol = tk.Frame(kart, bg=RENK["kart_zemin"])
    sol.pack(side="left", fill="both", expand=True, padx=(0, 15))
    sag = tk.Frame(kart, bg=RENK["kart_zemin"])
    sag.pack(side="left", fill="both", expand=True, padx=(15, 0))

    # --- SOL SÜTUN ---
    state["ad_kutu"] = form_alani(sol, "Ad")
    state["ad_kutu"].insert(0, kisi.kullaniciAd if kisi.kullaniciAd else "")

    state["soyad_kutu"] = form_alani(sol, "Soyad")
    state["soyad_kutu"].insert(0, kisi.kullaniciSoyad if kisi.kullaniciSoyad else "")

    # TC Kimlik No - Koyu Tema Uyumlu
    tk.Label(sol, text="TC Kimlik No", font=FONT_KUCUK, bg=RENK["kart_zemin"], fg=RENK["metin_gri"]).pack(anchor="w", pady=(8, 2))
    state["tc_kutu"] = tk.Entry(sol, font=FONT_NORMAL, relief="flat", 
                                bg=RENK["icerik_zemin"], fg=RENK["metin_koyu"],
                                insertbackground="white",
                                highlightthickness=1, highlightbackground=RENK["border"], highlightcolor=RENK["birincil"])
    state["tc_kutu"].pack(fill="x", ipady=6)
    state["tc_kutu"].insert(0, kisi.Tc if kisi.Tc else "")

    def tc_input_kontrol(event=None):
        deger = state["tc_kutu"].get()
        cleaned = ''.join(c for c in deger if c.isdigit())
        if len(cleaned) > 11:
            cleaned = cleaned[:11]
        state["tc_kutu"].delete(0, tk.END)
        state["tc_kutu"].insert(0, cleaned)
    state["tc_kutu"].bind('<KeyRelease>', tc_input_kontrol)

    # Telefon - Koyu Tema Uyumlu
    tk.Label(sol, text="Telefon", font=FONT_KUCUK, bg=RENK["kart_zemin"], fg=RENK["metin_gri"]).pack(anchor="w", pady=(8, 2))
    state["tel_kutu"] = tk.Entry(sol, font=FONT_NORMAL, relief="flat", 
                                 bg=RENK["icerik_zemin"], fg=RENK["metin_koyu"],
                                 insertbackground="white",
                                 highlightthickness=1, highlightbackground=RENK["border"], highlightcolor=RENK["birincil"])
    state["tel_kutu"].pack(fill="x", ipady=6)
    state["tel_kutu"].insert(0, kisi.telefonNO if kisi.telefonNO else "05")

    def tel_input_kontrol(event=None):
        deger = state["tel_kutu"].get()
        cleaned = ''.join(c for c in deger if c.isdigit())
        if len(cleaned) > 11:
            cleaned = cleaned[:11]
        if cleaned == "":
            cleaned = "05"
        elif not cleaned.startswith("05"):
            cleaned = ("05" + cleaned)[:11]
        state["tel_kutu"].delete(0, tk.END)
        state["tel_kutu"].insert(0, cleaned)
        state["tel_kutu"].icursor(tk.END)
    state["tel_kutu"].bind('<KeyRelease>', tel_input_kontrol)
    state["tel_kutu"].bind('<FocusIn>', lambda e: state["tel_kutu"].icursor(tk.END))

    # Şifre alanı - Koyu Tema Uyumlu
    tk.Label(sol, text="Şifre", font=FONT_KUCUK, bg=RENK["kart_zemin"], fg=RENK["metin_gri"]).pack(anchor="w", pady=(8, 2))
    sifre_satiri = tk.Frame(sol, bg=RENK["kart_zemin"])
    sifre_satiri.pack(fill="x")

    state["sifre_kutu"] = tk.Entry(sifre_satiri, font=FONT_NORMAL, show="*", relief="flat", 
                                   bg=RENK["icerik_zemin"], fg=RENK["metin_koyu"],
                                   insertbackground="white",
                                   highlightthickness=1, highlightbackground=RENK["border"], highlightcolor=RENK["birincil"])
    state["sifre_kutu"].pack(side="left", fill="x", expand=True, ipady=6)
    state["sifre_kutu"].insert(0, kisi.sifre if kisi.sifre else "")

    def sifre_goster_gizle():
        if state["sifre_kutu"].cget("show") == "*":
            state["sifre_kutu"].config(show="")
            goz_btn.config(text="🙈")
        else:
            state["sifre_kutu"].config(show="*")
            goz_btn.config(text="👁")

    goz_btn = tk.Button(sifre_satiri, text="👁", command=sifre_goster_gizle,
                        bg=RENK["sidebar_buton"], fg=RENK["beyaz"], relief="flat", cursor="hand2",
                        font=FONT_KUCUK, padx=8, pady=4)
    goz_btn.pack(side="right", padx=(5, 0))


    # --- SAĞ SÜTUN ---
    # Doğum Tarihi - Koyu Tema Uyumlu
    tk.Label(sag, text="Doğum Tarihi", font=FONT_KUCUK, bg=RENK["kart_zemin"], fg=RENK["metin_gri"]).pack(anchor="w", pady=(8, 2))
    state["dogum_kutu"] = tk.Entry(sag, font=FONT_NORMAL, relief="flat", 
                                   bg=RENK["icerik_zemin"], fg=RENK["metin_koyu"],
                                   insertbackground="white",
                                   highlightthickness=1, highlightbackground=RENK["border"], highlightcolor=RENK["birincil"])
    state["dogum_kutu"].pack(fill="x", ipady=6)

    if kisi.dogumTarihi:
        if hasattr(kisi.dogumTarihi, "strftime"):
            dogum_str = kisi.dogumTarihi.strftime("%d/%m/%Y")
        else:
            dogum_str = str(kisi.dogumTarihi)
        state["dogum_kutu"].insert(0, dogum_str)
    else:
        state["dogum_kutu"].insert(0, TARIH_PLACEHOLDER)
        state["dogum_kutu"].config(fg=RENK["metin_gri"])

    def dogum_focus_in(event=None):
        if state["dogum_kutu"].get() == TARIH_PLACEHOLDER:
            state["dogum_kutu"].delete(0, tk.END)
            state["dogum_kutu"].config(fg=RENK["metin_koyu"])

    def dogum_focus_out(event=None):
        if state["dogum_kutu"].get().strip() == "":
            state["dogum_kutu"].insert(0, TARIH_PLACEHOLDER)
            state["dogum_kutu"].config(fg=RENK["metin_gri"])

    def dogum_input_kontrol(event=None):
        deger = state["dogum_kutu"].get()
        cleaned = ''.join(c for c in deger if c.isdigit() or c == '/')
        if len(cleaned) > 10:
            cleaned = cleaned[:10]

        if len(cleaned) == 2 and cleaned != "GG":
            cleaned += "/"
        elif len(cleaned) == 5 and cleaned[2] == "/" and cleaned != "GG/AA":
            if cleaned[3:5] != "AA":
                cleaned += "/"

        state["dogum_kutu"].delete(0, tk.END)
        state["dogum_kutu"].insert(0, cleaned)

    state["dogum_kutu"].bind('<FocusIn>', dogum_focus_in)
    state["dogum_kutu"].bind('<FocusOut>', dogum_focus_out)
    state["dogum_kutu"].bind('<KeyRelease>', dogum_input_kontrol)

    # Daire / Müdürlük Combobox
    tk.Label(sag, text="Daire / Müdürlük", font=FONT_KUCUK, bg=RENK["kart_zemin"], fg=RENK["metin_gri"]).pack(anchor="w", pady=(8, 2))
    gosterim_listesi, gosterim_to_bilgi, id_to_gosterim = mudurluk_secenekleri_getir()
    state["gosterim_bilgi"] = gosterim_to_bilgi

    from tkinter import ttk
    state["mudurluk_combo"] = ttk.Combobox(sag, values=gosterim_listesi, state="readonly", font=FONT_NORMAL, style="TCombobox")
    state["mudurluk_combo"].pack(fill="x", ipady=4)

    if kisi.mudurlukId in id_to_gosterim:
        state["mudurluk_combo"].set(id_to_gosterim[kisi.mudurlukId])

    if aktif_rol != "admin":
        state["mudurluk_combo"].config(state="disabled")
        tk.Label(sag, text="Daire/Müdürlük değişikliği için yöneticinize başvurun.",
                 font=FONT_KUCUK, bg=RENK["kart_zemin"], fg=RENK["metin_gri"], wraplength=220).pack(anchor="w", pady=(4, 0))

    # Fotoğraf
    tk.Label(sag, text="Fotoğraf", font=FONT_KUCUK, bg=RENK["kart_zemin"], fg=RENK["metin_gri"]).pack(anchor="w", pady=(8, 2))
    foto_satiri = tk.Frame(sag, bg=RENK["kart_zemin"])
    foto_satiri.pack(fill="x", pady=(0, 5))
    
    yuvarlak_buton(foto_satiri, "📁  Yeni Fotoğraf", fotograf_sec,
                   renk=RENK["sidebar_buton"], hover_renk=RENK["sidebar_hover"]).pack(side="left")

    foto_durum = "Mevcut fotoğraf var ✓" if kisi.fotograf else "Henüz seçilmedi"
    foto_durum_renk = RENK["basarili"] if kisi.fotograf else RENK["metin_gri"]
    state["foto_label"] = tk.Label(foto_satiri, text=foto_durum, bg=RENK["kart_zemin"], fg=foto_durum_renk, font=FONT_KUCUK)
    state["foto_label"].pack(side="left", padx=10)

    state["onizleme_label"] = tk.Label(sag, bg=RENK["kart_zemin"], highlightthickness=1, highlightbackground=RENK["border"])
    state["onizleme_label"].pack(anchor="w", pady=(5, 0))

    if kisi.fotograf and os.path.exists(kisi.fotograf):
        try:
            img = Image.open(kisi.fotograf)
            img.thumbnail((100, 100))
            state["onizleme_resmi"] = ImageTk.PhotoImage(img)
            state["onizleme_label"].config(image=state["onizleme_resmi"])
        except Exception:
            pass

    # --- ALT BUTONLAR (KAYDET & İPTAL) ---
    alt = tk.Frame(sag_frame_ref, bg=RENK["icerik_zemin"])
    alt.pack(fill="x", padx=30, pady=10)
    
    yuvarlak_buton(alt, "✓  Kaydet", personel_guncelle).pack(side="left")
    yuvarlak_buton(alt, "←  İptal", geri_git, renk="#6B7280", hover_renk="#4B5563").pack(side="left", padx=10)

    state["sonuc_label"] = tk.Label(alt, text="", bg=RENK["icerik_zemin"], font=FONT_NORMAL)
    state["sonuc_label"].pack(side="left", padx=15)