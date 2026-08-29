# ============================================================
#                    KONFİGURASYON / RENKLER
# ============================================================

import pyodbc

RENK = {
    "arka_plan": "#000000",       # Tam Siyah zemin
    "sidebar": "#09090B",         # Çok koyu gri / siyah menü
    "sidebar_buton": "#18181B",   # Menü buton zemin
    "sidebar_hover": "#27272A",   # Menü buton üzerine gelince
    "sidebar_aktif": "#DB2777",   # AKTİF MENÜ: Koyu Pembe
    "icerik_zemin": "#111827",    # Sağ taraf içerik arka planı (Koyu Gri)
    "kart_zemin": "#1F2937",      # Kartların arka planı (Daha belirgin Koyu Gri)
    "birincil": "#DB2777",        # ANA VURGU: Koyu Pembe (Butonlar, ikonlar vs)
    "birincil_hover": "#BE123C",  # Koyu Pembe hover (üzerine gelince biraz koyulaşır)
    "basarili": "#10B981",        # Başarılı (Yeşil sabit kalsın)
    "tehlike": "#EF4444",         # İptal/Sil (Kırmızı sabit kalsın)
    "tehlike_hover": "#DC2626",
    "metin_koyu": "#F9FAFB",      # DİKKAT: Zemin siyah olduğu için ana metinler BEYAZ'a yakın olmalı
    "metin_gri": "#E5E7EB",       # İkincil metinler, açıklamalar (Daha okunur açık gri)
    "beyaz": "#FFFFFF",
    "border": "#374151",          # Çizgiler ve sınırlar için koyu gri
}

# FONT BOYUTLARI BÜYÜTÜLDÜ (Daha net okunabilirlik için)
FONT_BASLIK = ("Segoe UI", 20, "bold")       # 18'den 20'ye çıkarıldı
FONT_ALT_BASLIK = ("Segoe UI", 14, "bold")   # 11'den 14'e çıkarıldı
FONT_NORMAL = ("Segoe UI", 12)               # 10'dan 12'ye çıkarıldı
FONT_BUTON = ("Segoe UI", 11, "bold")        # 10'dan 11'e çıkarıldı
FONT_KUCUK = ("Segoe UI", 10)                # 9'dan 10'a çıkarıldı

DB_BAGLANTI_STR = (
    'DRIVER={ODBC Driver 17 for SQL Server};'
    'SERVER=ELIFMELEK2004\\SQLEXPRESS;'
    'DATABASE=KullaniciDB;'
    'Trusted_Connection=yes;'
)

# Global oturum ve geçmiş yönetimi
OTURUM = {
    "id": None,
    "ad": "",
    "soyad": "",
    "rol": "personel"
}
gecmis = []

def db_baglan():
    """Veritabanına bağlanır."""
    return pyodbc.connect(DB_BAGLANTI_STR)