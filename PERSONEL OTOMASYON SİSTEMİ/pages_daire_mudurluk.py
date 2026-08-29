# ============================================================
#                 DAİRE / MÜDÜRLÜK YÖNETİMİ
# ============================================================

import tkinter as tk
from tkinter import messagebox, ttk
import os
from PIL import Image, ImageTk
from config import RENK, FONT_ALT_BASLIK, FONT_NORMAL, FONT_KUCUK, db_baglan
from utils import frame_temizle, sayfa_basligi, form_alani, kart_frame, yuvarlak_buton, daire_listesi_getir, sayfa_git
from pages_personel_ara import personel_detay_tam_ekran

# Global değişkenler
sema_liste_alani = None
mudurluk_resimleri = []

# ------------------------------------------------------------
#   ANA SAYFA - Sadece Daire / Müdürlük Şeması
# ------------------------------------------------------------
def daire_mudurluk_goster(sag_frame_ref):
    """Daire/Müdürlük şema sayfasını gösterir (sadece görüntüleme)."""
    global sema_liste_alani

    frame_temizle()
    sayfa_basligi(sag_frame_ref, "Daire / Müdürlük Yönetimi", "Daireler ve bağlı oldukları müdürlükler")

    # --- Üst bar: Ekle butonu ---
    ust_bar = tk.Frame(sag_frame_ref, bg=RENK["icerik_zemin"])
    ust_bar.pack(fill="x", padx=30, pady=(0, 15))

    yuvarlak_buton(
        ust_bar, "➕  Daire / Müdürlük Ekle",
        lambda: sayfa_git(daire_mudurluk_ekle_goster, sag_frame_ref)
    ).pack(anchor="w")

    # --- Daire / Müdürlük Şeması ---
    govde = tk.Frame(sag_frame_ref, bg=RENK["icerik_zemin"])
    govde.pack(fill="both", expand=True, padx=30, pady=(0, 20))

    tk.Label(govde, text="Daire / Müdürlük Şeması", font=FONT_ALT_BASLIK,
             bg=RENK["icerik_zemin"], fg=RENK["metin_koyu"]).pack(anchor="w", pady=(0, 8))

    sema_disT = tk.Frame(govde, bg=RENK["kart_zemin"], highlightthickness=1, highlightbackground=RENK["border"])
    sema_disT.pack(fill="both", expand=True)

    canvas = tk.Canvas(sema_disT, bg=RENK["kart_zemin"], highlightthickness=0)
    scrollbar = tk.Scrollbar(sema_disT, orient="vertical", command=canvas.yview)
    sema_liste_alani = tk.Frame(canvas, bg=RENK["kart_zemin"])

    sema_liste_alani.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    
    canvas_window = canvas.create_window((0, 0), window=sema_liste_alani, anchor="nw")
    canvas.bind("<Configure>", lambda e: canvas.itemconfig(canvas_window, width=e.width))
    canvas.configure(yscrollcommand=scrollbar.set)

    # --- FARE TEKERLEĞİ (MOUSE WHEEL) İLE KAYDIRMA EKLENTİSİ ---
    def _on_mousewheel(event):
        if event.delta:
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        else:
            if event.num == 4:
                canvas.yview_scroll(-1, "units")
            elif event.num == 5:
                canvas.yview_scroll(1, "units")

    def _bind_mousewheel(event):
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        canvas.bind_all("<Button-4>", _on_mousewheel)
        canvas.bind_all("<Button-5>", _on_mousewheel)

    def _unbind_mousewheel(event):
        canvas.unbind_all("<MouseWheel>")
        canvas.unbind_all("<Button-4>")
        canvas.unbind_all("<Button-5>")

    sema_disT.bind("<Enter>", _bind_mousewheel)
    sema_disT.bind("<Leave>", _unbind_mousewheel)
    # -----------------------------------------------------------

    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    dm_semayi_yenile(sag_frame_ref)

def dm_semayi_yenile(sag_frame_ref):
    """Daire / Müdürlük şemasını yeniden çizer ve müdürlüklere personel tıklama katmanı ekler."""
    global mudurluk_resimleri
    mudurluk_resimleri = []

    for widget in sema_liste_alani.winfo_children():
        widget.destroy()

    baglanti = db_baglan()
    imlec = baglanti.cursor()

    imlec.execute("SELECT id, daireAdi FROM daireler ORDER BY daireAdi")
    daireler = imlec.fetchall()

    if not daireler:
        tk.Label(sema_liste_alani, text="Henüz daire eklenmedi", bg=RENK["kart_zemin"],
                 fg=RENK["metin_gri"], font=FONT_KUCUK).pack(anchor="w", padx=14, pady=12)
        baglanti.close()
        return

    for daire in daireler:
        # --- Daire başlığı ---
        daire_satir = tk.Frame(sema_liste_alani, bg=RENK["birincil"])
        daire_satir.pack(fill="x", pady=(10 if daire != daireler[0] else 0, 0))

        tk.Label(daire_satir, text=f"🏛  {daire.daireAdi}", font=FONT_NORMAL, bg=RENK["birincil"],
                 fg=RENK["beyaz"]).pack(side="left", padx=14, pady=8, fill="x", expand=True)

        daire_buton_alani = tk.Frame(daire_satir, bg=RENK["birincil"])
        daire_buton_alani.pack(side="right", padx=10)
        tk.Button(
            daire_buton_alani, text="✎", command=lambda did=daire.id: daire_duzenle_ac(did, sag_frame_ref),
            bg=RENK["sidebar_buton"], fg=RENK["beyaz"], relief="flat", bd=0, cursor="hand2",
            font=FONT_KUCUK, padx=8, pady=3
        ).pack(side="left", padx=(0, 4))
        tk.Button(
            daire_buton_alani, text="🗑", command=lambda did=daire.id, dad=daire.daireAdi: daire_sil_onayla(did, dad, sag_frame_ref),
            bg=RENK["tehlike"], fg=RENK["beyaz"], relief="flat", bd=0, cursor="hand2",
            font=FONT_KUCUK, padx=8, pady=3
        ).pack(side="left")

        # --- Bu daireye bağlı müdürlükler ---
        imlec.execute("SELECT id, mudurlukAdi FROM mudurlukler WHERE daireId = ? ORDER BY mudurlukAdi", (daire.id,))
        mudurlukler = imlec.fetchall()

        if not mudurlukler:
            tk.Label(sema_liste_alani, text="↳  Bu daireye bağlı müdürlük yok", bg=RENK["kart_zemin"],
                     fg=RENK["metin_gri"], font=FONT_KUCUK).pack(anchor="w", padx=34, pady=6)
            continue

        for sira, m in enumerate(mudurlukler):
            zemin = RENK["kart_zemin"] if sira % 2 == 0 else RENK["icerik_zemin"]
            
            # Müdürlük Tıklanabilir Satırı
            m_satir = tk.Frame(sema_liste_alani, bg=zemin, cursor="hand2")
            m_satir.pack(fill="x")

            m_sol = tk.Frame(m_satir, bg=zemin, cursor="hand2")
            m_sol.pack(side="left", fill="both", expand=True)

            ok_lbl = tk.Label(m_sol, text="▶", font=("Segoe UI", 8), bg=zemin, fg=RENK["metin_gri"], cursor="hand2")
            ok_lbl.pack(side="left", padx=(14, 5))

            m_label = tk.Label(m_sol, text=f"↳  📂  {m.mudurlukAdi}", bg=zemin, fg=RENK["metin_koyu"], font=FONT_NORMAL,
                              anchor="w", cursor="hand2")
            m_label.pack(side="left", pady=7, fill="x", expand=True)

            m_buton_alani = tk.Frame(m_satir, bg=zemin)
            m_buton_alani.pack(side="right", padx=10)
            tk.Button(
                m_buton_alani, text="✎", command=lambda mid=m.id: mudurluk_duzenle_ac(mid, sag_frame_ref),
                bg=RENK["sidebar_buton"], fg=RENK["beyaz"], relief="flat", bd=0, cursor="hand2",
                font=FONT_KUCUK, padx=8, pady=3
            ).pack(side="left", padx=(0, 4))
            tk.Button(
                m_buton_alani, text="🗑", command=lambda mid=m.id, mad=m.mudurlukAdi: mudurluk_sil_onayla(mid, mad, sag_frame_ref),
                bg=RENK["tehlike"], fg=RENK["beyaz"], relief="flat", bd=0, cursor="hand2",
                font=FONT_KUCUK, padx=8, pady=3
            ).pack(side="left")

            # --- MÜDÜRLÜĞE BAĞLI PERSONEL KONTEYNERİ (BAŞLANGIÇTA GİZLİ) ---
            personel_konteyner = tk.Frame(sema_liste_alani, bg=RENK["icerik_zemin"])

            imlec.execute(
                "SELECT id, kullaniciAd, kullaniciSoyad, fotograf FROM kullanici WHERE mudurlukId = ? AND aktif = 1",
                (m.id,)
            )
            personeller = imlec.fetchall()

            if personeller:
                for index, kisi in enumerate(personeller):
                    kisi_id = kisi.id
                    kisi_kutu = tk.Frame(
                        personel_konteyner, bg=RENK["kart_zemin"], highlightthickness=1,
                        highlightbackground=RENK["border"], cursor="hand2", width=140, height=120
                    )
                    kisi_kutu.grid(row=index // 4, column=index % 4, padx=6, pady=6, sticky="w")
                    kisi_kutu.pack_propagate(False)

                    foto_goster = None
                    if kisi.fotograf and os.path.exists(kisi.fotograf):
                        try:
                            img = Image.open(kisi.fotograf).resize((50, 50))
                            foto_goster = ImageTk.PhotoImage(img)
                            mudurluk_resimleri.append(foto_goster)
                        except Exception:
                            foto_goster = None

                    foto_konteyner = tk.Frame(kisi_kutu, bg=RENK["kart_zemin"], width=50, height=50)
                    foto_konteyner.pack(pady=(8, 4))
                    foto_konteyner.pack_propagate(False)

                    if foto_goster:
                        foto_label = tk.Label(foto_konteyner, image=foto_goster, bg=RENK["kart_zemin"], cursor="hand2")
                    else:
                        foto_label = tk.Label(foto_konteyner, text="👤", font=("Arial", 22), bg=RENK["kart_zemin"], fg=RENK["metin_gri"], cursor="hand2")
                    foto_label.pack(expand=True, fill="both")

                    isim_label = tk.Label(
                        kisi_kutu, text=f"{kisi.kullaniciAd} {kisi.kullaniciSoyad}", bg=RENK["kart_zemin"],
                        font=FONT_KUCUK, fg=RENK["metin_koyu"], cursor="hand2", wraplength=125, justify="center"
                    )
                    isim_label.pack(fill="x", padx=5)

                    def kisi_detay_ac(event=None, kid=kisi_id):
                        sayfa_git(personel_detay_tam_ekran, sag_frame_ref, kid)

                    kisi_kutu.bind("<Button-1>", kisi_detay_ac)
                    foto_konteyner.bind("<Button-1>", kisi_detay_ac)
                    foto_label.bind("<Button-1>", kisi_detay_ac)
                    isim_label.bind("<Button-1>", kisi_detay_ac)
            else:
                tk.Label(
                    personel_konteyner, text="ℹ️ Bu müdürlükte kayıtlı aktif personel bulunmuyor.",
                    font=FONT_KUCUK, bg=RENK["icerik_zemin"], fg=RENK["metin_gri"]
                ).pack(anchor="w", padx=35, pady=8)

            # --- AÇILIR / KAPANIR MANTIĞI (TOGGLE) ---
            def toggle_personeller(e=None, pk=personel_konteyner, o_lbl=ok_lbl, ms=m_satir):
                if pk.winfo_viewable():
                    pk.pack_forget()
                    o_lbl.config(text="▶")
                else:
                    pk.pack(fill="x", padx=(40, 10), pady=6, after=ms)
                    o_lbl.config(text="▼")

            m_satir.bind("<Button-1>", toggle_personeller)
            m_sol.bind("<Button-1>", toggle_personeller)
            m_label.bind("<Button-1>", toggle_personeller)
            ok_lbl.bind("<Button-1>", toggle_personeller)

    baglanti.close()

# ------------------------------------------------------------
#   EKLEME SAYFASI - Yeni Daire / Müdürlük Ekle
# ------------------------------------------------------------
def daire_mudurluk_ekle_goster(sag_frame_ref):
    """Yeni daire / müdürlük ekleme sayfasını gösterir."""
    frame_temizle()
    sayfa_basligi(sag_frame_ref, "Daire / Müdürlük Ekle", "Yeni daire veya müdürlük kaydı oluşturun")

    kart = kart_frame(sag_frame_ref)
    sol = tk.Frame(kart, bg=RENK["kart_zemin"])
    sol.pack(side="left", fill="both", expand=True, padx=(0, 15))
    sag = tk.Frame(kart, bg=RENK["kart_zemin"])
    sag.pack(side="left", fill="both", expand=True, padx=(15, 0))

    # --- Yeni Daire Ekle ---
    tk.Label(sol, text="Yeni Daire Ekle", font=FONT_ALT_BASLIK, bg=RENK["kart_zemin"], fg=RENK["metin_koyu"]).pack(anchor="w", pady=(0, 5))
    yeni_daire_kutu = form_alani(sol, "Daire Adı")
    yuvarlak_buton(sol, "➕  Daire Ekle", lambda: yeni_daire_ekle(yeni_daire_kutu, sag_frame_ref),
                   renk=RENK["sidebar_buton"], hover_renk=RENK["sidebar_hover"]).pack(anchor="w", pady=(8, 0))

    # --- Yeni Müdürlük Ekle ---
    tk.Label(sag, text="Yeni Müdürlük Ekle", font=FONT_ALT_BASLIK, bg=RENK["kart_zemin"], fg=RENK["metin_koyu"]).pack(anchor="w", pady=(0, 5))
    yeni_mudurluk_kutu = form_alani(sag, "Müdürlük Adı")

    tk.Label(sag, text="Bağlı Olduğu Daire", font=FONT_KUCUK, bg=RENK["kart_zemin"], fg=RENK["metin_gri"]).pack(anchor="w", pady=(8, 2))
    isimler, daire_isim_to_id = daire_listesi_getir()

    daire_combo = ttk.Combobox(sag, values=isimler, state="readonly", font=FONT_NORMAL, style="TCombobox")
    daire_combo.pack(fill="x", ipady=4)

    yuvarlak_buton(sag, "➕  Müdürlük Ekle", lambda: yeni_mudurluk_ekle(yeni_mudurluk_kutu, daire_combo, daire_isim_to_id, sag_frame_ref),
                   renk=RENK["sidebar_buton"], hover_renk=RENK["sidebar_hover"]).pack(anchor="w", pady=(8, 0))

def yeni_daire_ekle(kutu, sag_frame_ref):
    """Yeni daire ekler, ardından şema sayfasına döner."""
    ad = kutu.get().strip()
    if ad == "":
        messagebox.showwarning("Uyarı", "Daire adı boş olamaz!")
        return

    try:
        baglanti = db_baglan()
        imlec = baglanti.cursor()
        imlec.execute("INSERT INTO daireler (daireAdi) VALUES (?)", (ad,))
        baglanti.commit()
        baglanti.close()
        messagebox.showinfo("Başarılı", "Daire başarıyla eklendi.")
        sayfa_git(daire_mudurluk_goster, sag_frame_ref)
    except Exception as e:
        messagebox.showerror("Hata", f"Daire eklenirken hata oluştu:\n{e}")

def yeni_mudurluk_ekle(kutu, combo, daire_isim_to_id, sag_frame_ref):
    """Yeni müdürlük ekler, ardından şema sayfasına döner."""
    ad = kutu.get().strip()
    secili_daire = combo.get()

    if ad == "":
        messagebox.showwarning("Uyarı", "Müdürlük adı boş olamaz!")
        return

    if secili_daire == "" or secili_daire not in daire_isim_to_id:
        messagebox.showwarning("Uyarı", "Lütfen geçerli bir daire seçin!")
        return

    daire_id = daire_isim_to_id[secili_daire]

    try:
        baglanti = db_baglan()
        imlec = baglanti.cursor()
        imlec.execute("INSERT INTO mudurlukler (mudurlukAdi, daireId) VALUES (?, ?)", (ad, daire_id))
        baglanti.commit()
        baglanti.close()
        messagebox.showinfo("Başarılı", "Müdürlük başarıyla eklendi.")
        sayfa_git(daire_mudurluk_goster, sag_frame_ref)
    except Exception as e:
        messagebox.showerror("Hata", f"Müdürlük eklenirken hata oluştu:\n{e}")

# ------------------------------------------------------------
#   DÜZENLEME VE SİLME FONKSİYONLARI
# ------------------------------------------------------------
def daire_duzenle_ac(daire_id, sag_frame_ref):
    """Daire adını güncellemek için küçük bir prompt penceresi açar."""
    baglanti = db_baglan()
    imlec = baglanti.cursor()
    imlec.execute("SELECT daireAdi FROM daireler WHERE id = ?", (daire_id,))
    sonuc = imlec.fetchone()
    baglanti.close()

    if not sonuc:
        messagebox.showerror("Hata", "Daire bulunamadı.")
        return

    mevcut_ad = sonuc.daireAdi

    pencere = tk.Toplevel()
    pencere.title("Daire Düzenle")
    pencere.geometry("350x180")
    pencere.config(bg=RENK["icerik_zemin"])
    pencere.grab_set()

    tk.Label(pencere, text="Yeni Daire Adı:", font=FONT_KUCUK, bg=RENK["icerik_zemin"], fg=RENK["metin_koyu"]).pack(anchor="w", padx=20, pady=(20, 5))
    kutu = tk.Entry(pencere, font=FONT_NORMAL, bg=RENK["kart_zemin"], fg=RENK["metin_koyu"], insertbackground="white")
    kutu.pack(fill="x", padx=20, ipady=4)
    kutu.insert(0, mevcut_ad)

    def kaydet():
        yeni_ad = kutu.get().strip()
        if not yeni_ad:
            messagebox.showwarning("Uyarı", "Daire adı boş olamaz!", parent=pencere)
            return
        try:
            bag = db_baglan()
            imp = bag.cursor()
            imp.execute("UPDATE daireler SET daireAdi = ? WHERE id = ?", (yeni_ad, daire_id))
            bag.commit()
            bag.close()
            pencere.destroy()
            dm_semayi_yenile(sag_frame_ref)
        except Exception as e:
            messagebox.showerror("Hata", f"Güncelleme başarısız:\n{e}", parent=pencere)

    yuvarlak_buton(pencere, "Kaydet", kaydet).pack(anchor="e", padx=20, pady=15)

def daire_sil_onayla(daire_id, daire_adi, sag_frame_ref):
    """Daireyi silmeden önce onay alır ve bağlı müdürlükleri kontrol eder."""
    cevap = messagebox.askyesno("Onay", f"'{daire_adi}' adlı daireyi ve bağlı tüm müdürlükleri silmek istediğinize emin misiniz?")
    if cevap:
        try:
            baglanti = db_baglan()
            imlec = baglanti.cursor()
            imlec.execute("DELETE FROM mudurlukler WHERE daireId = ?", (daire_id,))
            imlec.execute("DELETE FROM daireler WHERE id = ?", (daire_id,))
            baglanti.commit()
            baglanti.close()
            dm_semayi_yenile(sag_frame_ref)
        except Exception as e:
            messagebox.showerror("Hata", f"Silme işlemi başarısız:\n{e}")

def mudurluk_duzenle_ac(mudurluk_id, sag_frame_ref):
    """Müdürlük adını ve bağlı olduğu daireyi güncellemek için pencere açar."""
    baglanti = db_baglan()
    imlec = baglanti.cursor()
    imlec.execute("SELECT mudurlukAdi, daireId FROM mudurlukler WHERE id = ?", (mudurluk_id,))
    sonuc = imlec.fetchone()
    baglanti.close()

    if not sonuc:
        messagebox.showerror("Hata", "Müdürlük bulunamadı.")
        return

    mevcut_ad, mevcut_daire_id = sonuc.mudurlukAdi, sonuc.daireId

    pencere = tk.Toplevel()
    pencere.title("Müdürlük Düzenle")
    pencere.geometry("350x240")
    pencere.config(bg=RENK["icerik_zemin"])
    pencere.grab_set()

    tk.Label(pencere, text="Yeni Müdürlük Adı:", font=FONT_KUCUK, bg=RENK["icerik_zemin"], fg=RENK["metin_koyu"]).pack(anchor="w", padx=20, pady=(15, 5))
    kutu = tk.Entry(pencere, font=FONT_NORMAL, bg=RENK["kart_zemin"], fg=RENK["metin_koyu"], insertbackground="white")
    kutu.pack(fill="x", padx=20, ipady=4)
    kutu.insert(0, mevcut_ad)

    tk.Label(pencere, text="Bağlı Olduğu Daire:", font=FONT_KUCUK, bg=RENK["icerik_zemin"], fg=RENK["metin_koyu"]).pack(anchor="w", padx=20, pady=(10, 5))
    isimler, daire_isim_to_id = daire_listesi_getir()
    id_to_isim_daire = {v: k for k, v in daire_isim_to_id.items()}

    combo = ttk.Combobox(pencere, values=isimler, state="readonly", font=FONT_NORMAL, style="TCombobox")
    combo.pack(fill="x", padx=20, ipady=4)
    if mevcut_daire_id in id_to_isim_daire:
        combo.set(id_to_isim_daire[mevcut_daire_id])

    def kaydet():
        yeni_ad = kutu.get().strip()
        secili_daire_isim = combo.get()
        if not yeni_ad:
            messagebox.showwarning("Uyarı", "Müdürlük adı boş olamaz!", parent=pencere)
            return
        if not secili_daire_isim or secili_daire_isim not in daire_isim_to_id:
            messagebox.showwarning("Uyarı", "Lütfen geçerli bir daire seçin!", parent=pencere)
            return

        yeni_daire_id = daire_isim_to_id[secili_daire_isim]

        try:
            bag = db_baglan()
            imp = bag.cursor()
            imp.execute("UPDATE mudurlukler SET mudurlukAdi = ?, daireId = ? WHERE id = ?", (yeni_ad, yeni_daire_id, mudurluk_id))
            bag.commit()
            bag.close()
            pencere.destroy()
            dm_semayi_yenile(sag_frame_ref)
        except Exception as e:
            messagebox.showerror("Hata", f"Güncelleme başarısız:\n{e}", parent=pencere)

    yuvarlak_buton(pencere, "Kaydet", kaydet).pack(anchor="e", padx=20, pady=15)

def mudurluk_sil_onayla(mudurluk_id, mudurluk_adi, sag_frame_ref):
    """Müdürlüğü silmeden önce onay alır."""
    cevap = messagebox.askyesno("Onay", f"'{mudurluk_adi}' adlı müdürlüğü silmek istediğinize emin misiniz?")
    if cevap:
        try:
            baglanti = db_baglan()
            imlec = baglanti.cursor()
            imlec.execute("DELETE FROM mudurlukler WHERE id = ?", (mudurluk_id,))
            baglanti.commit()
            baglanti.close()
            dm_semayi_yenile(sag_frame_ref)
        except Exception as e:
            messagebox.showerror("Hata", f"Silme işlemi başarısız:\n{e}")