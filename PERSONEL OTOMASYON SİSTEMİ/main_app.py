# ============================================================
#            PERSONEL OTOMASYON SİSTEMİ - ANA DOSYA
# ============================================================
# Modüler yapı - Her sayfa ayrı dosyada
# Kullanım: python main_app.py
# ============================================================

import os
import tkinter as tk
from tkinter import messagebox
import pyodbc
from PIL import Image, ImageTk, ImageOps, ImageDraw

# ===== İMPORT'LAR =====
from config import RENK, FONT_BASLIK, FONT_NORMAL, FONT_KUCUK, FONT_BUTON, db_baglan, OTURUM
from sidebar import create_sidebar, sidebar_buton
from utils import (
    set_sag_frame, set_geri_btn, frame_temizle, sayfa_basligi,
    yuvarlak_buton, stil_kur, tc_kontrol, telefon_kontrol, sayfa_git, geri_git, geri_buton_guncelle
)

# Sayfa import'ları
import pages_home
import pages_personel_ekle
import pages_personel_listele
import pages_personel_ara
import pages_organizasyon
import pages_daire_mudurluk
import pages_loglar  # <-- LOG SAYFASI İMPORT EDİLDİ

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

    # --- ŞİFRE INPUT + GÖZ İKONU (Kutunun İçinde) ---
    tk.Label(giris_karti, text="Şifre", font=FONT_KUCUK, bg=KART_BG, fg="#94A3B8").pack(anchor="w")
    
    sifre_cerceve = tk.Frame(giris_karti, bg=BORDER_RENK, bd=1)
    sifre_cerceve.pack(fill="x", pady=(4, 4))
    
    sifre_ic = tk.Frame(sifre_cerceve, bg=KART_BG)
    sifre_ic.pack(fill="x", padx=1, pady=1)

    # Göz butonunu iç kısıma sağa yaslıyoruz
    goz_btn = tk.Button(
        sifre_ic, text="👁", font=("Segoe UI", 10), bg=KART_BG, fg="#94A3B8",
        activebackground=KART_BG, activeforeground="#F8FAFC", bd=0, relief="flat", cursor="hand2", padx=6
    )
    goz_btn.pack(side="right", fill="y", padx=(0, 4))

    sifre_kutu = tk.Entry(
        sifre_ic, show="*", font=FONT_NORMAL, relief="flat", bg=KART_BG, 
        fg="#F8FAFC", insertbackground="#F8FAFC"
    )
    sifre_kutu.pack(side="left", fill="x", expand=True, ipady=8, ipadx=6)

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

def sifre_sifirla_penceresi_ac(parent_window):
    """Koyu pembe tonlarına uyumlu, odaklanınca pembeleşen şifre sıfırlama ekranı."""
    pencere = tk.Toplevel(parent_window)
    pencere.title("Şifre Sıfırlama")
    pencere.geometry("380x480")
    
    P_BG = "#1E293B"
    P_ZEMIN = "#0F172A"
    BORDER_RENK = "#475569"
    PEMBE_RENK = "#BE185D"
    
    pencere.configure(bg=P_ZEMIN)
    pencere.resizable(False, False)
    pencere.grab_set()

    ust_frame = tk.Frame(pencere, bg=P_ZEMIN)
    ust_frame.pack(fill="x", padx=15, pady=(15, 0))

    def pencereyi_kapat():
        pencere.destroy()

    geri_btn = tk.Button(
        ust_frame, text="← Geri", command=pencereyi_kapat,
        bg=P_ZEMIN, fg="#94A3B8", font=("Segoe UI", 9, "bold"),
        activebackground=P_ZEMIN, activeforeground="#F8FAFC",
        relief="flat", bd=0, cursor="hand2"
    )
    geri_btn.pack(side="left")

    tk.Label(pencere, text="🔑 Şifre Sıfırlama", font=("Segoe UI", 14, "bold"), bg=P_ZEMIN, fg="#F8FAFC").pack(pady=(10, 4))
    tk.Label(pencere, text="TC No bilginiz ile yeni şifrenizi belirleyin.", font=("Segoe UI", 9), bg=P_ZEMIN, fg="#94A3B8").pack(pady=(0, 15))

    f = tk.Frame(pencere, bg=P_ZEMIN)
    f.pack(fill="x", padx=30)

    def koyu_entry_olustur(parent, label_text, is_password=False):
        tk.Label(parent, text=label_text, font=("Segoe UI", 9, "bold"), bg=P_ZEMIN, fg="#94A3B8").pack(anchor="w")
        
        cerceve = tk.Frame(parent, bg=BORDER_RENK, bd=1)
        cerceve.pack(fill="x", pady=(2, 10))
        ic_cerceve = tk.Frame(cerceve, bg=P_BG)
        ic_cerceve.pack(fill="x", padx=1, pady=1)
        
        ent = tk.Entry(ic_cerceve, font=("Segoe UI", 10), show="*" if is_password else "", relief="flat", 
                       bg=P_BG, fg="#F8FAFC", insertbackground="#F8FAFC")
        ent.pack(fill="x", ipady=5, ipadx=6)

        ent.bind("<FocusIn>", lambda e: cerceve.config(bg=PEMBE_RENK))
        ent.bind("<FocusOut>", lambda e: cerceve.config(bg=BORDER_RENK))

        return ent

    tc_ent = koyu_entry_olustur(f, "TC Kimlik No")
    yeni_sifre_ent = koyu_entry_olustur(f, "Yeni Şifre", is_password=True)
    yeni_sifre_tekrar_ent = koyu_entry_olustur(f, "Yeni Şifre (Tekrar)", is_password=True)

    sifre_goster_var = tk.BooleanVar(value=False)

    def toggle_sifreleri_goster():
        yeni_show = "" if sifre_goster_var.get() else "*"
        yeni_sifre_ent.config(show=yeni_show)
        yeni_sifre_tekrar_ent.config(show=yeni_show)

    sifre_chk = tk.Checkbutton(
        f, text="Şifreleri Göster", variable=sifre_goster_var, command=toggle_sifreleri_goster,
        bg=P_ZEMIN, fg="#94A3B8", activebackground=P_ZEMIN, activeforeground="#F8FAFC", font=("Segoe UI", 9),
        cursor="hand2", selectcolor=P_BG
    )
    sifre_chk.pack(anchor="w", pady=(0, 15))

    def sifreyi_guncelle():
        tc = tc_ent.get().strip()
        s1 = yeni_sifre_ent.get().strip()
        s2 = yeni_sifre_tekrar_ent.get().strip()

        if not tc or not s1 or not s2:
            messagebox.showwarning("Uyarı", "Tüm alanları doldurunuz!", parent=pencere)
            return

        if not tc_kontrol(tc):
            messagebox.showwarning("Uyarı", "Geçerli bir TC Kimlik No giriniz!", parent=pencere)
            return

        if s1 != s2:
            messagebox.showerror("Hata", "Girdiğiniz yeni şifreler eşleşmiyor!", parent=pencere)
            return

        try:
            baglanti = db_baglan()
            imlec = baglanti.cursor()
            imlec.execute("SELECT id FROM kullanici WHERE Tc = ?", (tc,))
            kisi = imlec.fetchone()

            if not kisi:
                messagebox.showerror("Hata", "Bu TC Kimlik No ile kayıtlı kullanıcı bulunamadı!", parent=pencere)
                baglanti.close()
                return

            imlec.execute("UPDATE kullanici SET sifre = ? WHERE Tc = ?", (s1, tc))
            baglanti.commit()
            baglanti.close()

            messagebox.showinfo("Başarılı", "Şifreniz başarıyla güncellendi! Giriş yapabilirsiniz.", parent=pencere)
            pencere.destroy()
        except Exception as e:
            messagebox.showerror("Hata", f"İşlem tamamlanamadı: {str(e)}", parent=pencere)

    tk.Button(f, text="Şifreyi Güncelle", font=("Segoe UI", 10, "bold"),
              bg=PEMBE_RENK, fg="#FFFFFF", activebackground="#9D174D",
              bd=0, relief="flat", cursor="hand2", command=sifreyi_guncelle).pack(fill="x", ipady=7)

# ============================================================
#                         ANA MENÜ
# ============================================================

def ana_menu_ac(giris_penceresine_don):
    """Ana menüyü tam ekranda açar ve sağ üst köşeye profil görseli/ikonu ekler."""
    menu_penceresi = tk.Toplevel()
    menu_penceresi.title("Personel Otomasyon Sistemi")
    
    menu_penceresi.state('zoomed')
    menu_penceresi.config(bg=RENK["icerik_zemin"])
    menu_penceresi.protocol("WM_DELETE_WINDOW", lambda: cikis_yap(menu_penceresi, giris_penceresine_don))

    stil_kur()

    sag_govde = tk.Frame(menu_penceresi, bg=RENK["icerik_zemin"])
    sag_govde.pack(side="right", fill="both", expand=True)

    ust_bar = tk.Frame(sag_govde, bg=RENK["icerik_zemin"])
    ust_bar.pack(fill="x")

    geri_btn = tk.Button(
        ust_bar, text="←   Geri", command=geri_git,
        bg=RENK["icerik_zemin"], fg=RENK["metin_gri"], font=("Segoe UI", 11, "bold"),
        activebackground=RENK["icerik_zemin"], activeforeground=RENK["metin_koyu"],
        relief="flat", bd=0, cursor="hand2", anchor="w",
        padx=20, pady=12,
        highlightthickness=0, takefocus=0,
    )

    def geri_gir(e):
        geri_btn.config(fg=RENK["metin_koyu"])

    def geri_cik(e):
        geri_btn.config(fg=RENK["metin_gri"])

    geri_btn.bind("<Enter>", geri_gir)
    geri_btn.bind("<Leave>", geri_cik)
    geri_btn.pack(side="left")

    profil_container = tk.Frame(ust_bar, bg=RENK["icerik_zemin"])
    profil_container.pack(side="right", padx=20, pady=8)

    foto_yolu = OTURUM.get("fotograf")

    def yuvarlak_resim_olustur(yol, boyut=(36, 36)):
        try:
            if yol and os.path.exists(yol):
                im = Image.open(yol).convert("RGBA")
            else:
                return None
            im = ImageOps.fit(im, boyut, centering=(0.5, 0.5))
            mask = Image.new("L", boyut, 0)
            draw = ImageDraw.Draw(mask)
            draw.ellipse((0, 0) + boyut, fill=255)
            cikti = Image.new("RGBA", boyut, (0, 0, 0, 0))
            cikti.paste(im, (0, 0), mask)
            return ImageTk.PhotoImage(cikti)
        except Exception:
            return None

    avatar_tk = yuvarlak_resim_olustur(foto_yolu)

    if avatar_tk:
        profil_lbl = tk.Label(profil_container, image=avatar_tk, bg=RENK["icerik_zemin"], cursor="hand2")
        profil_lbl.image = avatar_tk
        profil_lbl.pack(side="left")
    else:
        profil_lbl = tk.Label(
            profil_container, text="👤", font=("Segoe UI Emoji", 16),
            bg="#334155", fg="#F8FAFC", width=2, height=1, cursor="hand2"
        )
        profil_lbl.pack(side="left")

    tam_ad_str = f"{OTURUM['ad']} {OTURUM['soyad']}".strip() or "Kullanıcı"
    ad_lbl = tk.Label(
        profil_container, text=tam_ad_str, font=("Segoe UI", 10, "bold"),
        bg=RENK["icerik_zemin"], fg=RENK.get("metin_koyu", "#F8FAFC")
    )
    ad_lbl.pack(side="left", padx=(10, 0))

    def profil_tikla(e):
        if pages_personel_ara:
            sayfa_git(pages_personel_ara.personel_detay_tam_ekran, sag_frame, OTURUM["id"])

    profil_lbl.bind("<Button-1>", profil_tikla)
    ad_lbl.bind("<Button-1>", profil_tikla)

    sag_frame = tk.Frame(sag_govde, bg=RENK["icerik_zemin"])
    sag_frame.pack(fill="both", expand=True)

    set_sag_frame(sag_frame)
    set_geri_btn(geri_btn)

    # --- SIDEBAR CALLBACKS ---
    callbacks = {
        'ana_sayfa': lambda: sayfa_git(pages_home.ana_sayfa_goster, sag_frame, tam_ad_str),
        'bilgilerim': lambda: sayfa_git(pages_personel_ara.personel_detay_tam_ekran, sag_frame, OTURUM["id"]),
        'personel_ekle': lambda: sayfa_git(pages_personel_ekle.personel_ekle_goster, sag_frame),
        'personel_listele': lambda: sayfa_git(pages_personel_listele.personel_listele_goster, sag_frame),
        'personel_ara': lambda: sayfa_git(pages_personel_ara.personel_ara_goster, sag_frame),
        'organizasyon': lambda: sayfa_git(pages_organizasyon.personel_organizasyon_goster, sag_frame),
        'daire_mudurluk': lambda: sayfa_git(pages_daire_mudurluk.daire_mudurluk_goster, sag_frame),
        'loglar': lambda: sayfa_git(pages_loglar.loglar_sayfasi_goster, sag_frame),
        'cikis': lambda: cikis_yap(menu_penceresi, giris_penceresine_don),
    }

    create_sidebar(menu_penceresi, callbacks)

    sayfa_git(pages_home.ana_sayfa_goster, sag_frame, tam_ad_str)

def cikis_yap(menu_penceresi, giris_penceresine_don):
    OTURUM["id"] = None
    OTURUM["ad"] = ""
    OTURUM["soyad"] = ""
    OTURUM["rol"] = "personel"
    OTURUM["fotograf"] = None
    
    menu_penceresi.destroy()
    giris_penceresine_don()

# ============================================================
#                            BAŞLAT
# ============================================================

if __name__ == "__main__":
    login_session_init = login_screen()