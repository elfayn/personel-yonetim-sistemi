from config import db_baglan

def log_ekle(hedef_id, yapan_id, aciklama):
    """
    İşlem geçmişine (islem_gecmisi tablosuna) yeni bir log kaydı ekler.
    
    Parametreler:
        hedef_id (int): İşlemden etkilenen kullanıcının ID'si
        yapan_id (int): İşlemi gerçekleştiren (oturum açmış olan) kullanıcının ID'si
        aciklama (str): Yapılan işlemin detay açıklaması
    """
    try:
        baglanti = db_baglan()
        imlec = baglanti.cursor()
        
        sorgu = """
            INSERT INTO islem_gecmisi (hedefKullaniciId, yapanKullaniciId, aciklama, tarih) 
            VALUES (?, ?, ?, GETDATE())
        """
        imlec.execute(sorgu, (hedef_id, yapan_id, aciklama))
        
        baglanti.commit()
        baglanti.close()
        print(f"[LOG] Başarıyla kaydedildi: Hedef ID={hedef_id}, Yapan ID={yapan_id}")
        
    except Exception as e:
        print(f"!!! LOG EKLEME HATASI: {e}")