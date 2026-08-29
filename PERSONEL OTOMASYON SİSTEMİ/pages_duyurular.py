# ============================================================
#                    DUYURULAR YÖNETİMİ VE LİSTESİ
# ============================================================

import tkinter as tk
from tkinter import messagebox, filedialog
from PIL import Image, ImageTk
import os
from config import RENK, FONT_ALT_BASLIK, FONT_NORMAL, FONT_KUCUK, db_baglan, OTURUM
from utils import frame_temizle, sayfa_git

# Global değişkenler: Resim yolu ve önizleme referansı için
secilen_resim_yolu = ""
onizleme_resmi_ref = None
detay_resim_ref = None

def duyuru_detay_sayfasi(sag_frame_ref, duyuru_id):
    """Seçilen duyurunun detaylarını (resim, içerik, başlık) yeni bir sayfada gösterir."""
    frame_temizle()
    global detay_resim_ref

    ZEMIN_BG = RENK.get("icerik_zemin", "#0F172A")
    KART_BG = RENK.get("kart_zemin", "#1E293B")
    KART_BORDER = RENK.get("border", "#334155")
    METIN_KOYU = RENK.get("metin_koyu", "#F8FAFC")
    METIN_GRI = RENK.get("metin_gri", "#94A3B8")
    PEMBE_RENK = "#BE185D"

    ust_frame = tk.Frame(sag_frame_ref, bg=ZEMIN_BG)
    ust_frame.pack(fill="x", padx=30, pady=(20, 15))

    def geri_don():
        if OTURUM.get("rol") == "admin":
            duyuru_yonetim_sayfasi(sag_frame_ref)
        else:
            personel_duyuru_listesi_sayfasi(sag_frame_ref)

    tk.Button(
        ust_frame, text="← Geri Dön", command=geri_don,
        bg=ZEMIN_BG, fg=PEMBE_RENK, font=FONT_KUCUK, relief="flat", bd=0, cursor="hand2"
    ).pack(anchor="w", pady=(0, 5))

    try:
        baglanti = db_baglan()
        imlec = baglanti.cursor()
        imlec.execute("SELECT baslik, icerik, format(tarih, 'dd.MM.yyyy HH:mm'), resimYolu FROM duyurular WHERE id = ?", (duyuru_id,))
        duyuru = imlec.fetchone()
        baglanti.close()
    except Exception:
        duyuru = None

    if not duyuru:
        tk.Label(sag_frame_ref, text="Duyuru bulunamadı veya silinmiş.", font=FONT_NORMAL, bg=ZEMIN_BG, fg="#EF4444").pack(padx=30, pady=20)
        return

    baslik, icerik, tarih, resim = duyuru

    kart = tk.Frame(sag_frame_ref, bg=KART_BG, highlightthickness=1, highlightbackground=KART_BORDER, padx=25, pady=20)
    kart.pack(fill="both", expand=True, padx=30, pady=(0, 20))

    tk.Label(kart, text=baslik, font=("Segoe UI", 16, "bold"), bg=KART_BG, fg=METIN_KOYU).pack(anchor="w", pady=(0, 5))
    tk.Label(kart, text=f"Yayınlanma Tarihi: {tarih}", font=FONT_KUCUK, bg=KART_BG, fg=METIN_GRI).pack(anchor="w", pady=(0, 15))

    if resim and os.path.exists(resim):
        try:
            img = Image.open(resim)
            img.thumbnail((300, 300))
            detay_resim_ref = ImageTk.PhotoImage(img)
            tk.Label(kart, image=detay_resim_ref, bg=KART_BG).pack(anchor="w", pady=(0, 15))
        except Exception as e:
            print(f"Resim yükleme hatası: {e}")

    tk.Label(kart, text=icerik, font=FONT_NORMAL, bg=KART_BG, fg=METIN_KOYU, wraplength=750, justify="left").pack(anchor="w")


def personel_duyuru_listesi_sayfasi(sag_frame_ref):
    """Personel için tüm duyuruların listelendiği sayfa."""
    frame_temizle()

    ZEMIN_BG = RENK.get("icerik_zemin", "#0F172A")
    KART_BG = RENK.get("kart_zemin", "#1E293B")
    KART_BORDER = RENK.get("border", "#334155")
    METIN_KOYU = RENK.get("metin_koyu", "#F8FAFC")
    METIN_GRI = RENK.get("metin_gri", "#94A3B8")
    PEMBE_RENK = "#BE185D"

    ust_frame = tk.Frame(sag_frame_ref, bg=ZEMIN_BG)
    ust_frame.pack(fill="x", padx=30, pady=(20, 15))

    def geri_don():
        from pages_home import ana_sayfa_goster
        sayfa_git(ana_sayfa_goster, sag_frame_ref)

    tk.Button(
        ust_frame, text="← Ana Sayfaya Dön", command=geri_don,
        bg=ZEMIN_BG, fg=PEMBE_RENK, font=FONT_KUCUK, relief="flat", bd=0, cursor="hand2"
    ).pack(anchor="w", pady=(0, 5))

    tk.Label(ust_frame, text="Kurum Duyuruları", font=("Segoe UI", 20, "bold"), bg=ZEMIN_BG, fg=METIN_KOYU).pack(anchor="w")

    govde = tk.Frame(sag_frame_ref, bg=ZEMIN_BG)
    govde.pack(fill="both", expand=True, padx=30, pady=(0, 20))

    try:
        baglanti = db_baglan()
        imlec = baglanti.cursor()
        imlec.execute("SELECT id, baslik, format(tarih, 'dd.MM.yyyy HH:mm') FROM duyurular ORDER BY tarih DESC")
        duyurular = imlec.fetchall()
        baglanti.close()
    except Exception:
        duyurular = []

    if duyurular:
        for d_id, baslik, tarih in duyurular:
            kart = tk.Frame(govde, bg=KART_BG, highlightthickness=1, highlightbackground=KART_BORDER, padx=20, pady=15)
            kart.pack(fill="x", pady=(0, 10))

            ust_r = tk.Frame(kart, bg=KART_BG)
            ust_r.pack(fill="x")
            
            btn_baslik = tk.Button(
                ust_r, text=baslik, font=FONT_ALT_BASLIK, bg=KART_BG, fg=PEMBE_RENK, 
                activebackground=KART_BG, activeforeground=PEMBE_RENK,
                relief="flat", bd=0, cursor="hand2", anchor="w",
                command=lambda idsi=d_id: duyuru_detay_sayfasi(sag_frame_ref, idsi)
            )
            btn_baslik.pack(side="left")
            tk.Label(ust_r, text=tarih, font=FONT_KUCUK, bg=KART_BG, fg=METIN_GRI).pack(side="right")
    else:
        tk.Label(govde, text="Henüz yayınlanmış bir duyuru bulunmuyor.", font=FONT_NORMAL, bg=ZEMIN_BG, fg=METIN_GRI).pack(anchor="w", pady=20)


def duyuru_yonetim_sayfasi(sag_frame_ref):
    """Admin için duyuru ekleme, resim önizleme ve silme paneli."""
    global secilen_resim_yolu, onizleme_resmi_ref
    secilen_resim_yolu = ""

    frame_temizle()

    ZEMIN_BG = RENK.get("icerik_zemin", "#0F172A")
    KART_BG = RENK.get("kart_zemin", "#1E293B")
    KART_BORDER = RENK.get("border", "#334155")
    METIN_KOYU = RENK.get("metin_koyu", "#F8FAFC")
    METIN_GRI = RENK.get("metin_gri", "#94A3B8")
    PEMBE_RENK = "#BE185D"

    ust_frame = tk.Frame(sag_frame_ref, bg=ZEMIN_BG)
    ust_frame.pack(fill="x", padx=30, pady=(20, 15))

    def geri_don():
        from pages_home import ana_sayfa_goster
        sayfa_git(ana_sayfa_goster, sag_frame_ref)

    tk.Button(
        ust_frame, text="← Ana Sayfaya Dön", command=geri_don,
        bg=ZEMIN_BG, fg=PEMBE_RENK, font=FONT_KUCUK, relief="flat", bd=0, cursor="hand2"
    ).pack(anchor="w", pady=(0, 5))

    tk.Label(ust_frame, text="Duyuru Yönetim Paneli", font=("Segoe UI", 20, "bold"), bg=ZEMIN_BG, fg=METIN_KOYU).pack(anchor="w")

    govde = tk.Frame(sag_frame_ref, bg=ZEMIN_BG)
    govde.pack(fill="both", expand=True, padx=30, pady=(0, 20))

    # Yeni Duyuru Ekleme Kartı
    ekle_kard = tk.Frame(govde, bg=KART_BG, highlightthickness=1, highlightbackground=KART_BORDER, padx=20, pady=15)
    ekle_kard.pack(fill="x", pady=(0, 20))

    tk.Label(ekle_kard, text="➕ Yeni Duyuru Yayınla", font=FONT_ALT_BASLIK, bg=KART_BG, fg=METIN_KOYU).pack(anchor="w", pady=(0, 10))

    tk.Label(ekle_kard, text="Duyuru Başlığı:", font=FONT_KUCUK, bg=KART_BG, fg=METIN_GRI).pack(anchor="w")
    
    baslik_cerceve = tk.Frame(ekle_kard, bg=KART_BORDER, bd=1)
    baslik_cerceve.pack(fill="x", pady=(2, 10))
    baslik_ic = tk.Frame(baslik_cerceve, bg=KART_BG)
    baslik_ic.pack(fill="x", padx=1, pady=1)

    baslik_entry = tk.Entry(
        baslik_ic, font=FONT_NORMAL, relief="flat", bg=KART_BG, 
        fg=METIN_KOYU, insertbackground=METIN_KOYU
    )
    baslik_entry.pack(fill="x", ipady=6, ipadx=6)

    tk.Label(ekle_kard, text="Duyuru İçeriği:", font=FONT_KUCUK, bg=KART_BG, fg=METIN_GRI).pack(anchor="w")
    
    icerik_cerceve = tk.Frame(ekle_kard, bg=KART_BORDER, bd=1)
    icerik_cerceve.pack(fill="x", pady=(2, 10))
    icerik_ic = tk.Frame(icerik_cerceve, bg=KART_BG)
    icerik_ic.pack(fill="x", padx=1, pady=1)

    icerik_text = tk.Text(
        icerik_ic, font=FONT_NORMAL, height=4, relief="flat", bg=KART_BG, 
        fg=METIN_KOYU, insertbackground=METIN_KOYU
    )
    icerik_text.pack(fill="x", padx=4, pady=4)

    baslik_entry.bind("<FocusIn>", lambda e: baslik_cerceve.config(bg=PEMBE_RENK))
    baslik_entry.bind("<FocusOut>", lambda e: baslik_cerceve.config(bg=KART_BORDER))

    icerik_text.bind("<FocusIn>", lambda e: icerik_cerceve.config(bg=PEMBE_RENK))
    icerik_text.bind("<FocusOut>", lambda e: icerik_cerceve.config(bg=KART_BORDER))

    resim_onizleme_lbl = tk.Label(ekle_kard, bg=KART_BG)
    resim_onizleme_lbl.pack(anchor="w", pady=(0, 5))

    resim_bilgi_lbl = tk.Label(ekle_kard, text="Resim seçilmedi", font=FONT_KUCUK, bg=KART_BG, fg=METIN_GRI)
    
    def resim_sec():
        global secilen_resim_yolu, onizleme_resmi_ref
        dosya = filedialog.askopenfilename(title="Duyuru Resmi Seç", filetypes=[("Resim Dosyaları", "*.jpg *.jpeg *.png")])
        if dosya:
            secilen_resim_yolu = dosya
            dosya_adi = os.path.basename(dosya)
            resim_bilgi_lbl.config(text=f"Seçilen: {dosya_adi}", fg="#10B981")
            
            try:
                img = Image.open(dosya)
                img.thumbnail((120, 120))
                onizleme_resmi_ref = ImageTk.PhotoImage(img)
                resim_onizleme_lbl.config(image=onizleme_resmi_ref)
            except Exception as e:
                print(f"Önizleme oluşturulamadı: {e}")

    resim_sec_btn = tk.Button(
        ekle_kard, text="📁 Resim Ekle (İsteğe Bağlı)", command=resim_sec,
        bg="#334155", fg="#FFFFFF", font=FONT_KUCUK, relief="flat", padx=10, pady=4, cursor="hand2"
    )
    resim_sec_btn.pack(anchor="w", pady=(0, 5))
    resim_bilgi_lbl.pack(anchor="w", pady=(0, 10))

    def duyuru_kaydet():
        global secilen_resim_yolu
        baslik = baslik_entry.get().strip()
        icerik = icerik_text.get("1.0", tk.END).strip()
        olusturan_id = OTURUM.get("id")

        if not baslik or not icerik:
            messagebox.showwarning("Uyarı", "Lütfen başlık ve içerik alanlarını doldurun.")
            return

        try:
            baglanti = db_baglan()
            imlec = baglanti.cursor()
            imlec.execute(
                "INSERT INTO duyurular (baslik, icerik, olusturanId, resimYolu) VALUES (?, ?, ?, ?)",
                (baslik, icerik, olusturan_id, secilen_resim_yolu if secilen_resim_yolu else None)
            )
            baglanti.commit()
            baglanti.close()

            messagebox.showinfo("Başarılı", "Duyuru başarıyla yayınlandı.")
            duyuru_yonetim_sayfasi(sag_frame_ref)
        except Exception as e:
            messagebox.showerror("Hata", f"Duyuru eklenirken hata oluştu:\n{e}")

    tk.Button(
        ekle_kard, text="Yayınla", command=duyuru_kaydet,
        bg=PEMBE_RENK, fg="#FFFFFF", font=FONT_NORMAL, relief="flat", padx=20, pady=6, cursor="hand2"
    ).pack(anchor="w")

    # Mevcut Duyuruları Listele ve Silme Alanı
    tk.Label(govde, text="Mevcut Duyurular", font=FONT_ALT_BASLIK, bg=ZEMIN_BG, fg=METIN_KOYU).pack(anchor="w", pady=(0, 10))

    try:
        baglanti = db_baglan()
        imlec = baglanti.cursor()
        imlec.execute("SELECT id, baslik, format(tarih, 'dd.MM.yyyy HH:mm') FROM duyurular ORDER BY tarih DESC")
        liste = imlec.fetchall()
        baglanti.close()
    except Exception:
        liste = []

    if liste:
        for duyuru_id, baslik, tarih in liste:
            row = tk.Frame(govde, bg=KART_BG, highlightthickness=1, highlightbackground=KART_BORDER, padx=15, pady=10)
            row.pack(fill="x", pady=(0, 6))

            btn_detay = tk.Button(
                row, text=baslik, font=FONT_ALT_BASLIK, bg=KART_BG, fg=METIN_KOYU,
                activebackground=KART_BG, activeforeground=METIN_KOYU,
                relief="flat", bd=0, cursor="hand2", anchor="w",
                command=lambda idsi=duyuru_id: duyuru_detay_sayfasi(sag_frame_ref, idsi)
            )
            btn_detay.pack(side="left")

            tk.Label(row, text=tarih, font=FONT_KUCUK, bg=KART_BG, fg=METIN_GRI).pack(side="left", padx=(15, 0))

            def duyuru_sil(d_id=duyuru_id):
                if messagebox.askyesno("Onay", "Bu duyuruyu silmek istediğinize emin misiniz?"):
                    try:
                        bag = db_baglan()
                        im = bag.cursor()
                        im.execute("DELETE FROM duyurular WHERE id = ?", (d_id,))
                        bag.commit()
                        bag.close()
                        duyuru_yonetim_sayfasi(sag_frame_ref)
                    except Exception as ex:
                        messagebox.showerror("Hata", f"Silinemedi:\n{ex}")

            tk.Button(
                row, text="Sil", command=duyuru_sil,
                bg="#DC2626", fg="#FFFFFF", font=FONT_KUCUK, relief="flat", padx=10, cursor="hand2"
            ).pack(side="right")
    else:
        tk.Label(govde, text="Sistemde kayıtlı duyuru bulunmuyor.", font=FONT_KUCUK, bg=ZEMIN_BG, fg=METIN_GRI).pack(anchor="w")