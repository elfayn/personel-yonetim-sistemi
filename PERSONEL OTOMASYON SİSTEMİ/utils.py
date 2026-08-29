# ============================================================
#                  ORTAK YARDIMCI FONKSİYONLAR
# ============================================================

import tkinter as tk
from tkinter import ttk
from config import RENK, FONT_BASLIK, FONT_ALT_BASLIK, FONT_NORMAL, FONT_KUCUK, FONT_BUTON, db_baglan, gecmis

# Global değişkenler
sag_frame = None
geri_btn = None

def set_sag_frame(frame):
    """Sağ taraf frame'ini ayarla."""
    global sag_frame
    sag_frame = frame

def set_geri_btn(btn):
    """Geri butonunu ayarla."""
    global geri_btn
    geri_btn = btn

def frame_temizle():
    """Sağ taraf frame'ini temizle."""
    for widget in sag_frame.winfo_children():
        widget.destroy()

def sayfa_basligi(parent, baslik, alt_yazi=""):
    """Her sayfanın en üstüne başlık bloğu koyar."""
    ust = tk.Frame(parent, bg=RENK["icerik_zemin"])
    ust.pack(fill="x", padx=30, pady=(25, 10))

    tk.Label(ust, text=baslik, font=FONT_BASLIK, bg=RENK["icerik_zemin"], fg=RENK["metin_koyu"]).pack(anchor="w")
    if alt_yazi:
        tk.Label(ust, text=alt_yazi, font=FONT_NORMAL, bg=RENK["icerik_zemin"], fg=RENK["metin_gri"]).pack(anchor="w")

    ayirici = tk.Frame(parent, bg=RENK["border"], height=1)
    ayirici.pack(fill="x", padx=30, pady=(0, 15))
    return ust

def yuvarlak_buton(parent, text, command, renk=None, hover_renk=None, fg=None, font=None, genislik=None):
    """Hover efektli, düz/modern görünümlü buton."""
    renk = renk or RENK["birincil"]
    hover_renk = hover_renk or RENK["birincil_hover"]
    fg = fg or RENK["beyaz"]
    font = font or FONT_BUTON

    btn = tk.Button(
        parent, text=text, command=command,
        bg=renk, fg=fg, font=font,
        activebackground=hover_renk, activeforeground=fg,
        relief="flat", bd=0, cursor="hand2",
        padx=14, pady=8,
    )
    if genislik:
        btn.config(width=genislik)

    btn.bind("<Enter>", lambda e: btn.config(bg=hover_renk))
    btn.bind("<Leave>", lambda e: btn.config(bg=renk))
    return btn

def form_alani(parent, etiket_text):
    """Etiket + modern koyu tema Entry çifti."""
    tk.Label(parent, text=etiket_text, font=FONT_KUCUK, bg=RENK["kart_zemin"], fg=RENK["metin_gri"]).pack(anchor="w", pady=(8, 2))
    kutu = tk.Entry(parent, font=FONT_NORMAL, relief="flat", 
                    bg=RENK["icerik_zemin"], fg=RENK["metin_koyu"],
                    insertbackground="white",
                    highlightthickness=1, highlightbackground=RENK["border"], highlightcolor=RENK["birincil"])
    kutu.pack(fill="x", ipady=6)
    return kutu

def kart_frame(parent):
    """Formların içine konduğu koyu tema kart alanı."""
    dis = tk.Frame(parent, bg=RENK["icerik_zemin"])
    dis.pack(fill="both", expand=True, padx=30, pady=5)

    kart = tk.Frame(dis, bg=RENK["kart_zemin"], padx=30, pady=25,
                     highlightthickness=1, highlightbackground=RENK["border"])
    kart.pack(fill="x")
    return kart

def stil_kur():
    """Tüm ttk bileşenlerini karanlık temaya gömüyoruz."""
    stil = ttk.Style()
    stil.theme_use("clam")

    # Treeview Stilleri
    stil.configure(
        "Treeview",
        background=RENK["kart_zemin"],
        fieldbackground=RENK["kart_zemin"],
        foreground=RENK["metin_koyu"],
        rowheight=30,
        font=FONT_NORMAL,
        borderwidth=0,
    )
    stil.configure(
        "Treeview.Heading",
        background=RENK["birincil"],
        foreground=RENK["beyaz"],
        font=FONT_ALT_BASLIK,
        borderwidth=0,
        relief="flat",
    )
    stil.map(
        "Treeview.Heading",
        background=[("active", RENK["birincil_hover"])],
    )
    stil.map(
        "Treeview",
        background=[("selected", RENK["birincil"])],
        foreground=[("selected", RENK["beyaz"])],
    )

    # Combobox Stilleri (Beyazlığı önlemek için)
    stil.configure(
        "TCombobox", 
        fieldbackground=RENK["icerik_zemin"], 
        background=RENK["kart_zemin"], 
        foreground=RENK["metin_koyu"], 
        bordercolor=RENK["border"]
    )
    stil.map("TCombobox", fieldbackground=[("readonly", RENK["icerik_zemin"])])

def tc_kontrol(tc):
    """TC doğrulama."""
    if len(tc) != 11:
        return False
    if not tc.isdigit():
        return False
    return True

def telefon_kontrol(tel):
    """Telefon doğrulama."""
    if len(tel) != 11:
        return False
    if not tel.isdigit():
        return False
    if not tel.startswith("05"):
        return False
    return True

def mudurluk_secenekleri_getir():
    """Daire+Müdürlük birleşik listesi."""
    baglanti = db_baglan()
    imlec = baglanti.cursor()
    imlec.execute("""
        SELECT m.id, m.mudurlukAdi, d.daireAdi
        FROM mudurlukler m
        JOIN daireler d ON m.daireId = d.id
        ORDER BY d.daireAdi, m.mudurlukAdi
    """)
    satirlar = imlec.fetchall()
    baglanti.close()

    gosterim_listesi = []
    gosterim_to_bilgi = {}
    id_to_gosterim = {}

    for satir in satirlar:
        gosterim = f"{satir.daireAdi}   >   {satir.mudurlukAdi}"
        gosterim_listesi.append(gosterim)
        gosterim_to_bilgi[gosterim] = (satir.id, satir.mudurlukAdi, satir.daireAdi)
        id_to_gosterim[satir.id] = gosterim

    return gosterim_listesi, gosterim_to_bilgi, id_to_gosterim

def daire_listesi_getir():
    """Tüm daireleri döndürür."""
    baglanti = db_baglan()
    imlec = baglanti.cursor()
    imlec.execute("SELECT id, daireAdi FROM daireler ORDER BY daireAdi")
    satirlar = imlec.fetchall()
    baglanti.close()
    isimler = [s.daireAdi for s in satirlar]
    isim_to_id = {s.daireAdi: s.id for s in satirlar}
    return isimler, isim_to_id

def sayfa_git(fonksiyon, *args):
    """Bir sayfaya gider ve geçmişe kaydeder."""
    global gecmis
    if not gecmis or gecmis[-1] != (fonksiyon, args):
        gecmis.append((fonksiyon, args))
    fonksiyon(*args)
    geri_buton_guncelle()

def geri_git():
    """Geçmişteki bir önceki sayfaya döner."""
    global gecmis
    if len(gecmis) <= 1:
        return
    gecmis.pop()
    fonksiyon, args = gecmis[-1]
    fonksiyon(*args)
    geri_buton_guncelle()

def geri_buton_guncelle():
    """Geri butonunu göster/gizle."""
    try:
        if len(gecmis) > 1:
            if geri_btn:
                geri_btn.pack(anchor="w")
        else:
            if geri_btn:
                geri_btn.pack_forget()
    except Exception:
        pass