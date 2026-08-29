# ============================================================
#                     GİRİŞ PENCERESİ
# ============================================================

def login_screen():
    """Koyu temaya tam uyumlu, odaklanınca pembeleşen giriş ekranı."""
    pencere = tk.Tk()
    pencere.title("Sisteme Giriş")
    pencere.geometry("420x580")
    
    ZEMIN_BG = RENK.get("icerik_zemin", "#0F172A") 
    KART_BG = RENK.get("kart_zemin", "#1E293B")
    BORDER_RENK = RENK.get("border", "#334155")
    PEMBE_RENK = "#BE185D"
    
    pencere.config(bg=ZEMIN_BG)
    pencere.resizable(False, False)

    sifre_gizli = [True]

    kart_dis = tk.Frame(pencere, bg=ZEMIN_BG)
    kart_dis.pack(expand=True, fill="both", padx=25, pady=25)

    giris_karti = tk.Frame(
        kart_dis, bg=KART_BG, padx=30, pady=25,
        highlightthickness=1, highlightbackground=BORDER_RENK
    )
    giris_karti.pack(expand=True, fill="both")

    tk.Label(giris_karti, text="🏛️", font=("Segoe UI Emoji", 34), bg=KART_BG).pack(pady=(0, 4))
    tk.Label(giris_karti, text="Sisteme Giriş", font=("Segoe UI", 16, "bold"), bg=KART_BG, fg="#F8FAFC").pack()
    tk.Label(giris_karti, text="Personel Otomasyon Sistemi", font=FONT_KUCUK, bg=KART_BG, fg="#94A3B8").pack(pady=(2, 18))

    # --- TC KİMLİK INPUT ---
    tk.Label(giris_karti, text="TC Kimlik No", font=FONT_KUCUK, bg=KART_BG, fg="#94A3B8").pack(anchor="w")
    
    tc_cerceve = tk.Frame(giris_karti, bg=BORDER_RENK, bd=1)
    tc_cerceve.pack(fill="x", pady=(4, 12))
    tc_ic = tk.Frame(tc_cerceve, bg=KART_BG)
    tc_ic.pack(fill="x", padx=1, pady=1)

    tc_kutu = tk.Entry(
        tc_ic, font=FONT_NORMAL, relief="flat", bg=KART_BG, 
        fg="#F8FAFC", insertbackground="#F8FAFC"
    )
    tc_kutu.pack(fill="x", ipady=8, ipadx=6)

    # --- ŞİFRE INPUT + GÖZ BUTONU KONTEYNERİ ---
    tk.Label(giris_karti, text="Şifre", font=FONT_KUCUK, bg=KART_BG, fg="#94A3B8").pack(anchor="w")
    
    sifre_dis_satir = tk.Frame(giris_karti, bg=KART_BG)
    sifre_dis_satir.pack(fill="x", pady=(4, 4))

    sifre_cerceve = tk.Frame(sifre_dis_satir, bg=BORDER_RENK, bd=1)
    sifre_cerceve.pack(side="left", fill="x", expand=True)
    sifre_ic = tk.Frame(sifre_cerceve, bg=KART_BG)
    sifre_ic.pack(fill="x", padx=1, pady=1)

    sifre_kutu = tk.Entry(
        sifre_ic, show="*", font=FONT_NORMAL, relief="flat", bg=KART_BG, 
        fg="#F8FAFC", insertbackground="#F8FAFC"
    )
    sifre_kutu.pack(fill="x", ipady=8, ipadx=6)

    # Göz butonu dikeyde ortalandı (pack side left/right yerine aynı hizada durması için)
    goz_btn = tk.Button(
        sifre_dis_satir, text="👁", font=("Segoe UI", 10), bg=KART_BG, fg="#94A3B8",
        activebackground=KART_BG, activeforeground="#F8FAFC", bd=0, relief="flat", cursor="hand2", padx=8
    )
    goz_btn.pack(side="right", padx=(6, 0), anchor="c")

    # Odaklanınca çerçeveyi pembe yapma fonksiyonları
    def odak_kazandi(cerceve):
        cerceve.config(bg=PEMBE_RENK)

    def odak_kaybetti(cerceve):
        cerceve.config(bg=BORDER_RENK)

    tc_kutu.bind("<FocusIn>", lambda e: odak_kazandi(tc_cerceve))
    tc_kutu.bind("<FocusOut>", lambda e: odak_kaybetti(tc_cerceve))

    sifre_kutu.bind("<FocusIn>", lambda e: odak_kazandi(sifre_cerceve))
    sifre_kutu.bind("<FocusOut>", lambda e: odak_kaybetti(sifre_cerceve))

    def sifre_gorunurluk_degistir():
        if sifre_gizli[0]:
            sifre_kutu.config(show="")
            goz_btn.config(text="🙈", fg=PEMBE_RENK)
            sifre_gizli[0] = False
        else:
            sifre_kutu.config(show="*")
            goz_btn.config(text="👁", fg="#94A3B8")
            sifre_gizli[0] = True

    goz_btn.config(command=sifre_gorunurluk_degistir)

    sifremi_unuttum_lbl = tk.Label(
        giris_karti, text="Şifremi Unuttum?", font=("Segoe UI", 9, "underline"),
        bg=KART_BG, fg=PEMBE_RENK, cursor="hand2"
    )
    sifremi_unuttum_lbl.pack(anchor="e", pady=(2, 12))
    sifremi_unuttum_lbl.bind("<Button-1>", lambda e: sifre_sifirla_penceresi_ac(pencere))

    sonuc_label = tk.Label(giris_karti, text="", bg=KART_BG, font=FONT_KUCUK)
    sonuc_label.pack(pady=(0, 8))

    def giris_alanlarini_temizle():
        tc_kutu.delete(0, tk.END)
        sifre_kutu.delete(0, tk.END)
        sonuc_label.config(text="")

    def giris_penceresine_don():
        giris_alanlarini_temizle()
        pencere.deiconify()
        tc_kutu.focus()

    def giris_yap():
        tc_yazi = tc_kutu.get().strip()
        sifre_yazi = sifre_kutu.get().strip()

        if tc_yazi == "" or sifre_yazi == "":
            sonuc_label.config(text="TC ve şifre boş bırakılamaz!", fg="#EF4444")
            return

        if not tc_kontrol(tc_yazi):
            sonuc_label.config(text="TC 11 haneli ve sadece rakam olmalı!", fg="#EF4444")
            return

        try:
            baglanti = db_baglan()
            imlec = baglanti.cursor()
            imlec.execute(
                "SELECT id, kullaniciAd, kullaniciSoyad, rol, fotograf FROM kullanici WHERE Tc = ? AND sifre = ? AND aktif = 1",
                tc_yazi, sifre_yazi
            )
            kullanici = imlec.fetchone()
            baglanti.close()

            if kullanici:
                OTURUM["id"] = kullanici.id
                OTURUM["ad"] = kullanici.kullaniciAd
                OTURUM["soyad"] = kullanici.kullaniciSoyad
                OTURUM["rol"] = getattr(kullanici, "rol", "personel") or "personel"
                OTURUM["fotograf"] = getattr(kullanici, "fotograf", None)

                sonuc_label.config(text="Giriş başarılı!", fg="#22C55E")
                pencere.withdraw()
                ana_menu_ac(giris_penceresine_don)
            else:
                sonuc_label.config(text="TC veya şifre hatalı!", fg="#EF4444")
        except Exception as e:
            sonuc_label.config(text="Veritabanı bağlantı hatası!", fg="#EF4444")

    gir_btn = tk.Button(
        giris_karti, text="Giriş Yap", command=giris_yap,
        bg=PEMBE_RENK, fg="#FFFFFF",
        activebackground="#9D174D", activeforeground="#FFFFFF",
        font=("Segoe UI", 11, "bold"), relief="flat", bd=0, cursor="hand2"
    )
    gir_btn.pack(fill="x", ipady=8)

    pencere.mainloop()