# ============================================================
#                PERSONEL LİSTELE
# ============================================================

import tkinter as tk
from config import RENK, FONT_ALT_BASLIK, FONT_NORMAL, FONT_KUCUK, db_baglan, OTURUM
from utils import frame_temizle, sayfa_basligi, yuvarlak_buton, sayfa_git
from pages_personel_ara import personel_detay_tam_ekran
from log import log_ekle

# Sütun piksel genişlikleri
SUTUN_GENISLIKLERI = [120, 120, 120, 120, 230, 280, 100, 100]

def sutunlari_ayarla(frame_ref):
    for i, genislik in enumerate(SUTUN_GENISLIKLERI):
        frame_ref.grid_columnconfigure(i, minsize=genislik, weight=1)

def personel_listele_goster(sag_frame_ref, scroll_pos=0.0):
    frame_temizle()

    baglanti = db_baglan()
    imlec = baglanti.cursor()
    
    imlec.execute("""
        SELECT k.id, k.kullaniciAd, k.kullaniciSoyad, k.Tc, k.telefonNO, m.mudurlukAdi, d.daireAdi, k.aktif
        FROM kullanici k
        JOIN mudurlukler m ON k.mudurlukId = m.id
        JOIN daireler d ON m.daireId = d.id
        ORDER BY k.kullaniciAd, k.kullaniciSoyad
    """)
    kayitlar = imlec.fetchall()
    baglanti.close()

    toplam_personel = len(kayitlar)
    sayfa_basligi(sag_frame_ref, "Personel Listesi", f"Sistemde toplam {toplam_personel} personel bulunmaktadır.")

    disT = tk.Frame(sag_frame_ref, bg=RENK["icerik_zemin"])
    disT.pack(fill="both", expand=True, padx=30, pady=(0, 20))

    basliklar = ["Ad", "Soyad", "TC", "Telefon", "Müdürlük", "Daire", "Durum", "İşlemler"]

    baslik_satiri = tk.Frame(disT, bg=RENK["birincil"])
    baslik_satiri.pack(fill="x")
    sutunlari_ayarla(baslik_satiri)
    for i, baslik in enumerate(basliklar):
        tk.Label(baslik_satiri, text=baslik, font=FONT_ALT_BASLIK, bg=RENK["birincil"], fg=RENK["beyaz"],
                 anchor="w").grid(row=0, column=i, padx=6, pady=8, sticky="ew")

    canvas = tk.Canvas(disT, bg=RENK["icerik_zemin"], highlightthickness=0)
    scrollbar = tk.Scrollbar(disT, orient="vertical", command=canvas.yview)
    scroll_frame = tk.Frame(canvas, bg=RENK["icerik_zemin"])

    scroll_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    canvas_window = canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
    canvas.bind("<Configure>", lambda e: canvas.itemconfig(canvas_window, width=e.width))
    canvas.configure(yscrollcommand=scrollbar.set)

    def _on_mousewheel(event):
        if event.delta: canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        else:
            if event.num == 4: canvas.yview_scroll(-1, "units")
            elif event.num == 5: canvas.yview_scroll(1, "units")

    def _bind_mousewheel(event):
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        canvas.bind_all("<Button-4>", _on_mousewheel)
        canvas.bind_all("<Button-5>", _on_mousewheel)

    def _unbind_mousewheel(event):
        canvas.unbind_all("<MouseWheel>")
        canvas.unbind_all("<Button-4>")
        canvas.unbind_all("<Button-5>")

    disT.bind("<Enter>", _bind_mousewheel)
    disT.bind("<Leave>", _unbind_mousewheel)

    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    for sira, kisi in enumerate(kayitlar):
        # DÜZELTME BURADA: Eski #F1F5F9 yerine koyu temanın tonları kullanıldı
        zemin = RENK["kart_zemin"] if sira % 2 == 0 else RENK["icerik_zemin"]
        
        satir_frame = tk.Frame(scroll_frame, bg=zemin)
        satir_frame.pack(fill="x", expand=True)
        sutunlari_ayarla(satir_frame)

        degerler = [kisi.kullaniciAd, kisi.kullaniciSoyad, kisi.Tc, kisi.telefonNO, kisi.mudurlukAdi, kisi.daireAdi]

        for i, deger in enumerate(degerler):
            kopyalanabilir_kutu = tk.Entry(
                satir_frame, 
                font=FONT_NORMAL, 
                bg=zemin, 
                fg=RENK["metin_koyu"], 
                relief="flat", 
                readonlybackground=zemin,
                highlightthickness=0,
                justify="left"
            )
            kopyalanabilir_kutu.insert(0, str(deger))
            kopyalanabilir_kutu.config(state="readonly")
            kopyalanabilir_kutu.grid(row=0, column=i, padx=6, pady=6, sticky="ew")

        secili_id = kisi.id
        durum_text = "✓ Aktif" if kisi.aktif == 1 else "✗ Pasif"
        durum_bg = RENK["basarili"] if kisi.aktif == 1 else "#6B7280"

        def aktif_pasif_toggle(sid, ad_soyad, eski_durum):
            mevcut_pos = canvas.yview()[0]
            baglanti_t = db_baglan()
            imlec_t = baglanti_t.cursor()
            
            imlec_t.execute("UPDATE kullanici SET aktif = CASE WHEN aktif = 1 THEN 0 ELSE 1 END WHERE id = ?", sid)
            baglanti_t.commit()
            
            yapan_id = OTURUM.get("id")
            yeni_durum_str = "Pasif" if eski_durum == 1 else "Aktif"
            log_ekle(hedef_id=sid, yapan_id=yapan_id, aciklama=f"{ad_soyad} adlı personelin durumu '{yeni_durum_str}' olarak değiştirildi.")
            
            baglanti_t.close()
            personel_listele_goster(sag_frame_ref, scroll_pos=mevcut_pos)

        tk.Button(satir_frame, text=durum_text, command=lambda sid=secili_id, ad=kisi.kullaniciAd, soyad=kisi.kullaniciSoyad, akt=kisi.aktif: aktif_pasif_toggle(sid, f"{ad} {soyad}", akt),
                  bg=durum_bg, fg=RENK["beyaz"], font=FONT_KUCUK, relief="flat", bd=0, cursor="hand2",
                  padx=10, pady=4).grid(row=0, column=6, padx=6, pady=6, sticky="w")

        tk.Button(satir_frame, text="👁 Detay",
                  command=lambda sid=secili_id: sayfa_git(personel_detay_tam_ekran, sag_frame_ref, sid),
                  bg=RENK["birincil"], fg=RENK["beyaz"], relief="flat", bd=0, cursor="hand2",
                  font=FONT_KUCUK, padx=10, pady=4).grid(row=0, column=7, padx=3, pady=6, sticky="w")

    if scroll_pos > 0:
        sag_frame_ref.update_idletasks()
        canvas.yview_moveto(scroll_pos)