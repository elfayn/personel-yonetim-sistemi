# ============================================================
#                    İŞLEM GEÇMİŞİ (LOGLAR SAYFASI)
# ============================================================

import tkinter as tk
from tkinter import ttk, messagebox
from config import RENK, FONT_BASLIK, FONT_NORMAL, FONT_KUCUK, db_baglan
from utils import frame_temizle, sayfa_basligi

def loglar_sayfasi_goster(sag_frame_ref):
    """Sistem loglarını (işlem geçmişini) modern bir tabloda gösterir."""
    frame_temizle()
    sayfa_basligi(sag_frame_ref, "İşlem Geçmişi", "Sistemde yapılan tüm işlemlerin kayıtları")

    # Arama / Bilgi şeridi
    ust_bar = tk.Frame(sag_frame_ref, bg=RENK["kart_zemin"], highlightthickness=1, highlightbackground=RENK["border"])
    ust_bar.pack(fill="x", padx=30, pady=(0, 10))

    bilgi_etiket = tk.Label(
        ust_bar, text="Kayıtlar listeleniyor...",
        font=FONT_KUCUK, bg=RENK["kart_zemin"], fg=RENK["metin_gri"]
    )
    bilgi_etiket.pack(side="left", padx=15, pady=10)

    def loglari_yenile():
        for row in log_tree.get_children():
            log_tree.delete(row)

        try:
            baglanti = db_baglan()
            imlec = baglanti.cursor()
            # Doğru orijinal sütun adlarıyla sorgu
            sorgu = """
                SELECT l.id, 
                       COALESCE(y.kullaniciAd + ' ' + y.kullaniciSoyad, 'Sistem / Bilinmiyor') as yapan,
                       COALESCE(h.kullaniciAd + ' ' + h.kullaniciSoyad, 'Genel / Silinmiş') as hedef,
                       l.aciklama, 
                       l.tarih
                FROM islem_gecmisi l
                LEFT JOIN kullanici y ON l.yapanKullaniciId = y.id
                LEFT JOIN kullanici h ON l.hedefKullaniciId = h.id
                ORDER BY l.id DESC
            """
            imlec.execute(sorgu)
            kayitlar = imlec.fetchall()
            baglanti.close()

            for idx, kayit in enumerate(kayitlar, start=1):
                tarih_str = str(kayit.tarih) if kayit.tarih else "-"
                log_tree.insert("", "end", values=(
                    idx,
                    kayit.yapan,
                    kayit.hedef,
                    kayit.aciklama,
                    tarih_str
                ))

            bilgi_etiket.config(text=f"Toplam {len(kayitlar)} işlem kaydı listeleniyor.")
        except Exception as e:
            messagebox.showerror("Hata", f"Loglar yüklenirken bir hata oluştu:\n{e}")

    # Yenile Butonu
    yenile_btn = tk.Button(
        ust_bar, text="🔄 Listeyi Yenile",
        bg=RENK["birincil"], fg="white", font=FONT_KUCUK,
        relief="flat", padx=10, pady=4, cursor="hand2", command=loglari_yenile
    )
    yenile_btn.pack(side="right", padx=15, pady=8)

    # Tablo Alanı
    govde = tk.Frame(sag_frame_ref, bg=RENK["icerik_zemin"])
    govde.pack(fill="both", expand=True, padx=30, pady=(0, 20))

    log_tree = ttk.Treeview(
        govde,
        columns=("sira", "yapan", "hedef", "aciklama", "tarih"),
        show="headings"
    )

    basliklar = {
        "sira": "Sıra",
        "yapan": "İşlemi Yapan",
        "hedef": "İşlem Yapılan Personel",
        "aciklama": "İşlem Açıklaması",
        "tarih": "Tarih / Saat"
    }
    genislikler = {
        "sira": 60,
        "yapan": 180,
        "hedef": 180,
        "aciklama": 400,
        "tarih": 160
    }

    for kolon in ("sira", "yapan", "hedef", "aciklama", "tarih"):
        log_tree.heading(kolon, text=basliklar[kolon], anchor="w")
        # Sıra sütunu sabit kalır, diğerleri esneyebilir
        is_stretch = False if kolon == "sira" else True
        log_tree.column(kolon, width=genislikler[kolon], minwidth=genislikler[kolon], anchor="w", stretch=is_stretch)

    log_tree.pack(fill="both", expand=True)

    # İlk açılışta verileri doldur
    loglari_yenile()