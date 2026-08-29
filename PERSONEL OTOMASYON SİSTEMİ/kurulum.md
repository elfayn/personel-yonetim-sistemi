# Personel Otomasyon Sistemi - Kurulum Rehberi

## 📦 Dosya Listesi

Aşağıdaki dosyaları **aynı klasöre** kaydedin:

### Ana Dosyalar
- `main_app.py` ⭐ - Ana uygulama (BUNU ÇALIŞTIRIN)
- `config.py` - Konfigürasyon (renkler, fontlar, DB bağlantısı)
- `utils.py` - Ortak yardımcı fonksiyonlar
- `sidebar.py` - Sidebar butonları
- `log.py` - Logging sistemi

### Sayfa Dosyaları
- `pages_home.py` - Ana Sayfa (KPI kartları)
- `pages_giris.py` - Giriş Ekranı
- `pages_personel_ekle.py` - Personel Ekle
- `pages_personel_listele.py` - Personel Listele
- `pages_personel_ara.py` - Personel Ara
- `pages_personel_duzenle.py` - Personel Düzenle
- `pages_organizasyon.py` - Organizasyon Şeması
- `pages_daire_mudurluk.py` - Daire / Müdürlük Yönetimi
- `pages_loglar.py` - Sistem Logları
- `pages_duyurular.py` - Duyurular

## 🛠️ Bağımlılıklar Kurulumu

```bash
pip install pillow pyodbc tkcalendar
```

Veya tüm paketleri bir defada:
```bash
pip install pillow==10.0.0 pyodbc==5.0.4 tkcalendar==1.6.1
```

## 🗄️ Veritabanı Ayarı

### Adım 1: SQL Server Express Kurulumu
- SQL Server Express'in **çalıştığını** doğrulayın
- SQL Server Management Studio (SSMS) açın

### Adım 2: Veritabanı Oluşturma
SQL Server Management Studio'da aşağıdaki SQL'i çalıştırın:

```sql
CREATE DATABASE KullaniciDB;

USE KullaniciDB;

CREATE TABLE daireler (
    id INT PRIMARY KEY IDENTITY(1,1),
    daireAdi VARCHAR(100) NOT NULL
);

CREATE TABLE mudurlukler (
    id INT PRIMARY KEY IDENTITY(1,1),
    mudurlukAdi VARCHAR(100) NOT NULL,
    daireId INT NOT NULL,
    FOREIGN KEY (daireId) REFERENCES daireler(id)
);

CREATE TABLE kullanici (
    id INT PRIMARY KEY IDENTITY(1,1),
    kullaniciAd VARCHAR(50) NOT NULL,
    kullaniciSoyad VARCHAR(50) NOT NULL,
    Tc VARCHAR(11) NOT NULL UNIQUE,
    telefonNO VARCHAR(11),
    sifre VARCHAR(50) NOT NULL,
    dogumTarihi DATE,
    fotograf VARCHAR(255),
    birim VARCHAR(100),
    daire VARCHAR(100),
    mudurlukId INT,
    aktif BIT DEFAULT 1,
    FOREIGN KEY (mudurlukId) REFERENCES mudurlukler(id)
);
```

### Adım 3: Test Verileri Ekleme (İsteğe Bağlı)
```sql
INSERT INTO daireler (daireAdi) VALUES ('Mali Hizmetler Daire Başkanlığı');
INSERT INTO daireler (daireAdi) VALUES ('Fen İşleri Daire Başkanlığı');

INSERT INTO mudurlukler (mudurlukAdi, daireId) VALUES ('Muhasebe Müdürlüğü', 1);
INSERT INTO mudurlukler (mudurlukAdi, daireId) VALUES ('Bütçe Müdürlüğü', 1);

INSERT INTO kullanici 
(kullaniciAd, kullaniciSoyad, Tc, telefonNO, sifre, dogumTarihi, birim, daire, mudurlukId, aktif)
VALUES 
('TEST', 'KULLANICI', '12345678901', '05551234567', '123456', '1990-01-01', 'Test', 'Test', 1, 1);
```

### Adım 4: Config.py Ayarı
`config.py` dosyasını açın ve bağlantı stringini kontrol edin:

```python
DB_BAGLANTI_STR = (
    'DRIVER={ODBC Driver 17 for SQL Server};'
    'SERVER=ELIFMELEK2004\\SQLEXPRESS;'  # ⚠️ KENDI SERVER ADINIZI YAZIN
    'DATABASE=KullaniciDB;'
    'Trusted_Connection=yes;'
)
```

**Server Adınızı Nasıl Bulursunuz?**
1. SQL Server Management Studio açın
2. Üst kısımdaki "Server name" alanını kontrol edin
3. Format genellikle: `COMPUTERNAME\SQLEXPRESS`

## ▶️ Uygulamayı Çalıştırma

### Windows
```bash
cd C:\Users\YourName\Desktop\PERSONEL-SON
python main_app.py
```

### Linux/Mac
```bash
cd ~/Desktop/PERSONEL-SON
python3 main_app.py
```

### Test Hesabı
Giriş ekranında:
- **TC**: 12345678901
- **Şifre**: 123456

## 🎯 Program Akışı

```
main_app.py (Başla)
    ↓
Giriş Ekranı (TC + Şifre)
    ↓
Ana Menu (Sidebar)
    ↓
📄 Sayfa Seçim (6 ana sayfa)
    ├─ 🏠 Ana Sayfa
    ├─ ➕ Personel Ekle
    ├─ 📋 Personel Listele
    ├─ 🔍 Personel Ara
    ├─ 🗂 Organizasyon Şeması
    └─ 🏢 Daire / Müdürlük
```

## ⚙️ Dosya Yapısı

```
PERSONEL-SON/
├── 🟢 main_app.py              ← BUNU ÇALIŞTIR
├── config.py
├── utils.py
├── sidebar.py
├── log.py
│
├── 📁 pages/
│   ├── pages_home.py
│   ├── pages_giris.py
│   ├── pages_personel_ekle.py
│   ├── pages_personel_listele.py
│   ├── pages_personel_ara.py
│   ├── pages_personel_duzenle.py
│   ├── pages_organizasyon.py
│   ├── pages_daire_mudurluk.py
│   ├── pages_loglar.py
│   └── pages_duyurular.py
│
└── 📁 __pycache__/             (Otomatik oluşur)
```

## 🆘 Hata Giderme

### ❌ "ODBC Driver 17 not found"
**Çözüm:**
1. ODBC 17'yi indir: https://www.microsoft.com/download/details.aspx?id=56567
2. Yönetici olarak kur
3. Bilgisayarı yeniden başlat

### ❌ "Connection to server failed"
**Çözüm:**
1. SQL Server Express'in çalışıyor olduğunu kontrol et
   - Windows'ta: Services → SQL Server (SQLEXPRESS) → "Running" mi?
2. Server adını doğrula
   ```bash
   sqlcmd -S (local)\SQLEXPRESS
   ```
3. Veritabanın oluşturulduğunu kontrol et
   - SSMS'te KullaniciDB'yi görebiliyor musun?

### ❌ "No module named 'pages_home'"
**Çözüm:**
- Dosya adlarını kontrol et (büyük küçük harf önemli)
- Tüm dosyaların aynı klasörde olduğundan emin ol
- main_app.py ile aynı dizinde pages_*.py dosyaları olmalı

### ❌ "Too early to create variable"
**Çözüm:**
- Bu hata normalde alınmaz, eğer alırsan config.py'yi kontrol et
- Tkinter değişkenleri tanımlamaya çalışmıyorsun mu?

### ❌ Giriş yapamıyorum
**Çözüm:**
1. Test verileri ekledin mi? (Yukarı bakın)
2. TC: 12345678901
3. Şifre: 123456
4. Veritabanın kullanici tablosuna bak

## 📝 Önemli Notlar

- ✅ **Dosyalar aynı klasörde olmalı**
- ✅ **SQL Server çalışır durumda olmalı**
- ✅ **ODBC Driver 17 kurulu olmalı**
- ✅ **Python 3.8+ gerekli**
- ✅ **İlk çalıştırıldığında yavaş olabilir**

## 🔒 Güvenlik Önerileri

⚠️ **Üretim Ortamında:**
- Şifreleri düz metin yerine hash'leyin
- Veritabanı bağlantısını şifreleyin
- User roles (Admin, Müdür, Personel) ekleyin
- Audit log tutun

## 🚀 Şimdi Başla!

```bash
# 1. Bağımlılıkları kur
pip install pillow pyodbc tkcalendar

# 2. Veritabanını oluştur (SQL Server Management Studio'da)

# 3. config.py'yi düzenle (server adınızı yazın)

# 4. Uygulamayı çalıştır
python main_app.py

# 5. Giriş yap (TC: 12345678901, Şifre: 123456)
```

## 📚 Ek Kaynaklar

- [Tkinter Dokümantasyonu](https://docs.python.org/3/library/tkinter.html)
- [PyODBC Rehberi](https://github.com/mkleehammer/pyodbc/wiki)
- [SQL Server Express İndir](https://www.microsoft.com/tr-tr/sql-server/sql-server-express)

## 💡 İpuçları

1. **Hızlı Giriş**: Test hesabı kullanarak geliştirmeyi hızlandır
2. **Debug Mode**: print() kullanarak hataları takip et
3. **Veritabanı**: SQL Server Management Studio ile sorguları test et
4. **Kod**: İlk çalıştırmada main_app.py'de break noktası koy

---

**Kurulum başarılı olursa "Ana Sayfa" açılacak ve KPI kartları görünecektir.** ✅

**Sorun yaşarsan**: `main_app.py`'yi açarak önceki hatayı oku.

---

**Başarılar!** 🎉