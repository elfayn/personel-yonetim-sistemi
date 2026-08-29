# ============================================================
#                   ORGANİZASYON ŞEMASI
# ============================================================

import tkinter as tk
from tkinter import ttk
import os
from PIL import Image, ImageTk
from config import RENK, FONT_ALT_BASLIK, FONT_NORMAL, FONT_KUCUK, db_baglan
from utils import frame_temizle, sayfa_basligi, sayfa_git
from pages_personel_ara import personel_detay_tam_ekran

organizasyon_resimleri = []

def personel_organizasyon_goster(sag_frame_ref):
    """Daire ve Müdürlük hiyerarşik bağlantılı Açılır Menü (Combobox) Organizasyon Şeması."""
    global organizasyon_resimleri
    organizasyon_resimleri = []

    frame_temizle()
    sayfa_basligi(sag_frame_ref, "Organizasyon Şeması", "Daire → Müdürlük → Personel hiyerarşisi")

    # --- ÜST FİLTRE ALANI ---
    filtre_frame = tk.Frame(sag_frame_ref, bg=RENK["icerik_zemin"])
    filtre_frame.pack(fill="x", padx=30, pady=(0, 15))

    # Sol: Daire Seçimi (Önce Daire)
    tk.Label(filtre_frame, text="Daire", font=FONT_KUCUK, bg=RENK["icerik_zemin"], fg=RENK["metin_gri"]).grid(row=0, column=0, sticky="w", padx=(0, 15))
    daire_combo = ttk.Combobox(filtre_frame, font=FONT_NORMAL, width=32, state="readonly")
    daire_combo.grid(row=1, column=0, ipady=4, padx=(0, 15), pady=(2, 10), sticky="w")

    # Sağ: Müdürlük Seçimi
    tk.Label(filtre_frame, text="Müdürlük", font=FONT_KUCUK, bg=RENK["icerik_zemin"], fg=RENK["metin_gri"]).grid(row=0, column=1, sticky="w", padx=(0, 15))
    mudurluk_combo = ttk.Combobox(filtre_frame, font=FONT_NORMAL, width=32, state="readonly")
    mudurluk_combo.grid(row=1, column=1, ipady=4, padx=(0, 15), pady=(2, 10), sticky="w")

    # Butonlar Alanı
    btn_frame = tk.Frame(filtre_frame, bg=RENK["icerik_zemin"])
    btn_frame.grid(row=2, column=0, columnspan=2, sticky="w", pady=(5, 0))

    ara_btn = tk.Button(
        btn_frame, text="🔍  Ara", command=lambda: semayi_yukle(),
        bg=RENK.get("birincil", "#4F46E5"), fg="#FFFFFF", font=("Segoe UI", 10, "bold"),
        relief="flat", bd=0, cursor="hand2", padx=20, pady=6
    )
    ara_btn.pack(side="left", padx=(0, 10))

    temizle_btn = tk.Button(
        btn_frame, text="🧹  Temizle", command=lambda: filtreleri_temizle(),
        bg="#64748B", fg="#FFFFFF", font=("Segoe UI", 10, "bold"),
        relief="flat", bd=0, cursor="hand2", padx=20, pady=6
    )
    temizle_btn.pack(side="left")

    # --- İÇERİK ALANI (SCROLLAREA) ---
    disT = tk.Frame(sag_frame_ref, bg=RENK["icerik_zemin"])
    disT.pack(fill="both", expand=True, padx=30, pady=(0, 20))

    canvas = tk.Canvas(disT, bg=RENK["icerik_zemin"], highlightthickness=0)
    scrollbar = tk.Scrollbar(disT, orient="vertical", command=canvas.yview)
    scroll_frame = tk.Frame(canvas, bg=RENK["icerik_zemin"])

    scroll_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    canvas_window = canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)
    canvas.bind("<Configure>", lambda e: canvas.itemconfig(canvas_window, width=e.width))

    # Fare Tekerleği Desteği
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

    disT.bind("<Enter>", _bind_mousewheel)
    disT.bind("<Leave>", _unbind_mousewheel)

    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    # --- VERİTABANINDAN COMBOBOX LİSTELERİNİ DOLDURMA ---
    daire_haritasi = {}
    mudurluk_daire_haritasi = {}

    def combobox_verilerini_doldur():
        nonlocal daire_haritasi, mudurluk_daire_haritasi
        try:
            baglanti = db_baglan()
            imlec = baglanti.cursor()

            # 1. Tüm Daireleri Yükle
            imlec.execute("SELECT id, daireAdi FROM daireler")
            daireler = imlec.fetchall()
            daire_listesi = ["(Hepsi)"]
            daire_haritasi = {}
            for d in daireler:
                daire_listesi.append(d.daireAdi)
                daire_haritasi[d.daireAdi] = d.id

            daire_combo['values'] = daire_listesi
            daire_combo.set("(Hepsi)")

            # 2. Tüm Müdürlükleri Ve Bağlı Oldukları Daire İsimlerini Yükle
            imlec.execute("SELECT m.mudurlukAdi, d.daireAdi FROM mudurlukler m LEFT JOIN daireler d ON m.daireId = d.id")
            mudurlukler = imlec.fetchall()
            
            mudurluk_listesi = ["(Hepsi)"]
            mudurluk_daire_haritasi = {}
            for m in mudurlukler:
                mudurluk_listesi.append(m.mudurlukAdi)
                mudurluk_daire_haritasi[m.mudurlukAdi] = m.daireAdi

            mudurluk_combo['values'] = mudurluk_listesi
            mudurluk_combo.set("(Hepsi)")

            baglanti.close()
        except Exception as e:
            print("Combobox doldurma hatası:", e)

    # Daire seçilince Müdürlük listesini güncelle
    def daire_degisti(event=None):
        secilen_daire = daire_combo.get()
        try:
            baglanti = db_baglan()
            imlec = baglanti.cursor()

            if secilen_daire == "(Hepsi)" or not secilen_daire:
                # Daire seçili değilse TÜM müdürlükler görünsün
                imlec.execute("SELECT mudurlukAdi FROM mudurlukler")
            else:
                # Daire seçildiyse SADECE o daireye bağlı müdürlükler görünsün
                d_id = daire_haritasi.get(secilen_daire)
                imlec.execute("SELECT mudurlukAdi FROM mudurlukler WHERE daireId = ?", d_id)

            m_list = ["(Hepsi)"] + [m.mudurlukAdi for m in imlec.fetchall()]
            mudurluk_combo['values'] = m_list
            mudurluk_combo.set("(Hepsi)")

            baglanti.close()
        except Exception as e:
            print("Daire değişimi hatası:", e)

    # Müdürlük direkt seçilirse bağlı olduğu Daireyi otomatik seç
    def mudurluk_degisti(event=None):
        secilen_mudurluk = mudurluk_combo.get()
        if secilen_mudurluk and secilen_mudurluk != "(Hepsi)":
            ait_oldugu_daire = mudurluk_daire_haritasi.get(secilen_mudurluk)
            if ait_oldugu_daire and daire_combo.get() == "(Hepsi)":
                daire_combo.set(ait_oldugu_daire)
                daire_degisti()
                mudurluk_combo.set(secilen_mudurluk)

    daire_combo.bind("<<ComboboxSelected>>", daire_degisti)
    mudurluk_combo.bind("<<ComboboxSelected>>", mudurluk_degisti)

    # --- ŞEMA YÜKLEME FONKSİYONU ---
    def semayi_yukle():
        global organizasyon_resimleri
        organizasyon_resimleri = []

        for widget in scroll_frame.winfo_children():
            widget.destroy()

        daire_secim = daire_combo.get()
        mudurluk_secim = mudurluk_combo.get()

        try:
            baglanti = db_baglan()
            imlec = baglanti.cursor()

            imlec.execute("SELECT id, daireAdi FROM daireler")
            daireler = imlec.fetchall()
            eslese_bulundu = False

            for daire in daireler:
                daire_id = daire.id
                daire_adi = daire.daireAdi

                # Daire Filtre Kontrolü
                if daire_secim != "(Hepsi)" and daire_secim != "" and daire_secim != daire_adi:
                    continue

                imlec.execute("SELECT id, mudurlukAdi FROM mudurlukler WHERE daireId = ?", daire_id)
                mudurlukler = imlec.fetchall()

                süzülmüş_mudurlukler = []
                for mud in mudurlukler:
                    # Müdürlük Filtre Kontrolü
                    if mudurluk_secim != "(Hepsi)" and mudurluk_secim != "" and mudurluk_secim != mud.mudurlukAdi:
                        continue
                    süzülmüş_mudurlukler.append(mud)

                if not süzülmüş_mudurlukler:
                    continue

                eslese_bulundu = True

                # Daire Kartı
                daire_kutu_frame = tk.Frame(scroll_frame, bg=RENK["birincil"])
                daire_kutu_frame.pack(fill="x", pady=(18, 0), padx=5)
                tk.Label(
                    daire_kutu_frame, text=f"🏢  {daire_adi}", font=FONT_ALT_BASLIK,
                    bg=RENK["birincil"], fg=RENK["beyaz"]
                ).pack(anchor="w", padx=14, pady=8)

                for mudurluk in süzülmüş_mudurlukler:
                    mudurluk_id = mudurluk.id
                    mudurluk_adi = mudurluk.mudurlukAdi

                    # Müdürlük Kartı
                    mud_kutu = tk.Frame(scroll_frame, bg="#A5B4FC")
                    mud_kutu.pack(fill="x", padx=(25, 5), pady=(6, 0))
                    tk.Label(
                        mud_kutu, text=f"📁  {mudurluk_adi}", font=FONT_KUCUK,
                        bg="#A5B4FC", fg="#1E1B4B"
                    ).pack(anchor="w", padx=12, pady=5)

                    imlec.execute(
                        "SELECT id, kullaniciAd, kullaniciSoyad, fotograf FROM kullanici WHERE mudurlukId = ? AND aktif = 1",
                        mudurluk_id
                    )
                    personeller = imlec.fetchall()

                    personel_satiri = tk.Frame(scroll_frame, bg=RENK["icerik_zemin"])
                    personel_satiri.pack(fill="x", padx=(45, 5), pady=8)

                    if not personeller:
                        tk.Label(
                            personel_satiri, text="Bu müdürlükte kayıtlı personel yok",
                            bg=RENK["icerik_zemin"], fg=RENK["metin_gri"], font=FONT_KUCUK
                        ).grid(row=0, column=0, padx=5, sticky="w")

                    cards = []
                    for index, kisi in enumerate(personeller):
                        kisi_id = kisi.id

                        kisi_kutu = tk.Frame(
                            personel_satiri, bg=RENK["kart_zemin"], highlightthickness=1,
                            highlightbackground=RENK["border"], cursor="hand2", width=140, height=120
                        )
                        kisi_kutu.grid(row=index // 3, column=index % 3, padx=6, pady=6, sticky="w")
                        kisi_kutu.pack_propagate(False)
                        cards.append(kisi_kutu)

                        foto_goster = None
                        if kisi.fotograf and os.path.exists(kisi.fotograf):
                            try:
                                img = Image.open(kisi.fotograf)
                                img = img.resize((55, 55))
                                foto_goster = ImageTk.PhotoImage(img)
                                organizasyon_resimleri.append(foto_goster)
                            except Exception:
                                foto_goster = None

                        foto_konteyner = tk.Frame(kisi_kutu, bg=RENK["kart_zemin"], width=55, height=55)
                        foto_konteyner.pack(pady=(10, 5))
                        foto_konteyner.pack_propagate(False)

                        if foto_goster:
                            foto_label = tk.Label(foto_konteyner, image=foto_goster, bg=RENK["kart_zemin"], cursor="hand2")
                        else:
                            foto_label = tk.Label(foto_konteyner, text="👤", font=("Arial", 26), bg=RENK["kart_zemin"], cursor="hand2")
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

                    def make_adjust_layout(ps=personel_satiri, c=cards):
                        def adjust_layout(event):
                            width = event.width
                            cols = max(1, (width - 10) // 152)
                            for i, card in enumerate(c):
                                card.grid(row=i // cols, column=i % cols, padx=6, pady=6, sticky="w")
                        return adjust_layout

                    if cards:
                        personel_satiri.bind("<Configure>", make_adjust_layout())

            if not eslese_bulundu:
                tk.Label(
                    scroll_frame, text="⚠️ Aranan kriterlere uygun kayıt bulunamadı.",
                    font=FONT_NORMAL, bg=RENK["icerik_zemin"], fg=RENK["tehlike"]
                ).pack(pady=30)

            baglanti.close()
        except Exception as e:
            print("Hata:", e)

    def filtreleri_temizle():
        combobox_verilerini_doldur()
        semayi_yukle()

    # Sayfa Başlangıcı
    combobox_verilerini_doldur()
    semayi_yukle()