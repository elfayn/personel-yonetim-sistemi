# ============================================================
#                    SIDEBAR / MENÜ
# ============================================================

import tkinter as tk
from config import RENK, FONT_NORMAL, OTURUM
from utils import sayfa_git

def create_sidebar(parent, callbacks):
    sol_frame = tk.Frame(parent, bg=RENK["sidebar"], width=230)
    sol_frame.pack(side="left", fill="y")
    sol_frame.pack_propagate(False)

    # --- Logo Alanı ---
    logo_alani = tk.Frame(sol_frame, bg=RENK["sidebar"])
    logo_alani.pack(fill="x", pady=(25, 15))
    tk.Label(logo_alani, text="🏛️", font=("Segoe UI Emoji", 28), bg=RENK["sidebar"]).pack()
    tk.Label(logo_alani, text="PERSONEL", font=("Segoe UI", 13, "bold"), bg=RENK["sidebar"], fg=RENK["beyaz"]).pack()
    tk.Label(logo_alani, text="OTOMASYON", font=("Segoe UI", 9), bg=RENK["sidebar"], fg="#94A3B8").pack(pady=(0, 10))

    ayirici = tk.Frame(sol_frame, bg=RENK["sidebar_hover"], height=1)
    ayirici.pack(fill="x", padx=15, pady=(0, 10))

    aktif_rol = OTURUM.get("rol", "personel")

    butonlar = [
        ("🏠", "Ana Sayfa", callbacks['ana_sayfa'], "herkes"),
        ("🪪", "Bilgilerim", callbacks.get('bilgilerim'), "personel"),
        ("➕", "Personel Ekle", callbacks['personel_ekle'], "admin"),
        ("📋", "Personel Listele", callbacks['personel_listele'], "admin"),
        ("🔍", "Personel Ara", callbacks.get('personel_ara'), "admin"),
        ("🗂️", "Organizasyon Şeması", callbacks.get('organizasyon'), "admin"),
        ("🏢", "Daire / Müdürlük", callbacks['daire_mudurluk'], "admin"),
        ("📜", "İşlem Geçmişi", callbacks.get('loglar'), "admin"),
    ]

    for icon, text, command, yetki in butonlar:
        if not command:
            continue
        if yetki == "admin" and aktif_rol != "admin":
            continue
        if yetki == "personel" and aktif_rol == "admin":
            continue 

        sidebar_buton(sol_frame, text, command, icon)

    alt_bosluk = tk.Frame(sol_frame, bg=RENK["sidebar"])
    alt_bosluk.pack(side="bottom", fill="x", pady=15, padx=10)
    
    # Çıkış Butonu
    cikis_frame = tk.Frame(alt_bosluk, bg=RENK["tehlike"], cursor="hand2")
    cikis_frame.pack(fill="x")
    
    c_ic = tk.Frame(cikis_frame, bg=RENK["tehlike"])
    c_ic.pack(fill="x", padx=16, pady=10)
    
    tk.Label(c_ic, text="⏻", font=("Segoe UI", 10, "bold"), bg=RENK["tehlike"], fg=RENK["beyaz"]).pack(side="left")
    tk.Label(c_ic, text="Çıkış Yap", font=("Segoe UI", 10, "bold"), bg=RENK["tehlike"], fg=RENK["beyaz"]).pack(side="left", padx=(12, 0))

    def cikis_gir(e):
        cikis_frame.config(bg=RENK["tehlike_hover"])
        c_ic.config(bg=RENK["tehlike_hover"])
        for child in c_ic.winfo_children(): child.config(bg=RENK["tehlike_hover"])

    def cikis_cik(e):
        cikis_frame.config(bg=RENK["tehlike"])
        c_ic.config(bg=RENK["tehlike"])
        for child in c_ic.winfo_children(): child.config(bg=RENK["tehlike"])

    cikis_frame.bind("<Enter>", cikis_gir)
    cikis_frame.bind("<Leave>", cikis_cik)
    c_ic.bind("<Enter>", cikis_gir)
    c_ic.bind("<Leave>", cikis_cik)
    for child in c_ic.winfo_children():
        child.bind("<Button-1>", lambda e: callbacks['cikis']() if 'cikis' in callbacks else None)
    cikis_frame.bind("<Button-1>", lambda e: callbacks['cikis']())

    return sol_frame


def sidebar_buton(parent, text, command, ikon=""):
    btn_frame = tk.Frame(parent, bg=RENK["sidebar_buton"], cursor="hand2")
    btn_frame.pack(fill="x", padx=10, pady=3)

    icerik_frame = tk.Frame(btn_frame, bg=RENK["sidebar_buton"])
    icerik_frame.pack(fill="x", padx=16, pady=10)

    # İkonun sola kaymasını ve metinle üst üste binmesini önlemek için sabit genişlik (width=2) verildi
    icon_lbl = tk.Label(icerik_frame, text=ikon, font=("Segoe UI Emoji", 11), bg=RENK["sidebar_buton"], fg="#CBD5E1", width=2, anchor="w")
    icon_lbl.pack(side="left")

    text_lbl = tk.Label(icerik_frame, text=text, font=FONT_NORMAL, bg=RENK["sidebar_buton"], fg="#CBD5E1")
    text_lbl.pack(side="left", padx=(8, 0))

    def gir(e):
        btn_frame.config(bg=RENK["sidebar_hover"])
        icerik_frame.config(bg=RENK["sidebar_hover"])
        icon_lbl.config(bg=RENK["sidebar_hover"], fg=RENK["beyaz"])
        text_lbl.config(bg=RENK["sidebar_hover"], fg=RENK["beyaz"])

    def cik(e):
        btn_frame.config(bg=RENK["sidebar_buton"])
        icerik_frame.config(bg=RENK["sidebar_buton"])
        icon_lbl.config(bg=RENK["sidebar_buton"], fg="#CBD5E1")
        text_lbl.config(bg=RENK["sidebar_buton"], fg="#CBD5E1")

    for w in [btn_frame, icerik_frame, icon_lbl, text_lbl]:
        w.bind("<Enter>", gir)
        w.bind("<Leave>", cik)
        w.bind("<Button-1>", lambda e: command())

    return btn_frame