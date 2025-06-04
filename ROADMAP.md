---

## Siber Güvenlik Tarama Aracının Geliştirme Yol Haritası

### 1. Giriş

Bu yol haritası, kapsamlı bir siber güvenlik tarama aracı oluşturma sürecini özetler. Araç, belirlenen bir IP adresi veya URL üzerindeki potansiyel zafiyetleri tespit etmek için çeşitli Kali Linux araçlarını ve özel Python kodunu kullanır. Geliştirme süreci; ön koşulları, test ortamı kurulumunu, temel bileşenlerin geliştirilmesini, Kali araçlarının entegrasyonunu, test etmeyi ve son olarak karşı önlemleri ve en iyi uygulamaları kapsar.

### 2. Ön Koşullar

Geliştirmeye başlamadan önce, aşağıdaki ön koşulların karşılandığından emin olun:

* **İşletim Sistemi:** Tercihen **Kali Linux** veya **Parrot OS** gibi sızma testi dağıtımlarından biri. Bu dağıtımlar, araçların çoğunu önceden yüklenmiş olarak sunar ve bağımlılık yönetimi daha kolaydır.
* **Python 3:** Sisteminizde Python 3'ün yüklü olması gerekir.
* **Temel Python Bilgisi:** `socket`, `subprocess`, `os`, `re`, `logging`, `concurrent.futures` gibi modüllerin kullanımı hakkında bilgi sahibi olmak.
* **Temel Ağ Bilgisi:** IP adresleri, portlar, DNS çözünürlüğü ve ağ protokolleri hakkında bilgi.
* **Siber Güvenlik Bilgisi:** Sızma testleri, zafiyet taramaları, web zafiyetleri (XSS, SQLi vb.) ve ağ güvenliği konularına aşina olmak.

### 3. Test Ortamını Kurma

Geliştirme ve test süreçleri için kontrollü bir ortam şarttır. **Asla canlı veya üretim sistemlerinde bu aracı test etmeyin!**

* **Sanal Makine Kurulumu:**
    * **VirtualBox** veya **VMware Workstation/Player** gibi bir sanallaştırma yazılımı kurun.
    * Bir **Kali Linux** sanal makinesi oluşturun.
* **Hedef Sistem Kurulumu:**
    * Zafiyetleri test etmek için **MetaSploitable2**, **OWASP Broken Web Applications Project (BWA)** veya **DVWA (Damn Vulnerable Web Application)** gibi kasıtlı olarak zafiyetli makinelerden birini kurun. Bu, aracınızın zafiyetleri doğru bir şekilde tespit edip edemediğini kontrol etmenizi sağlar.
    * Ağ ayarlarını, Kali sanal makineniz ve hedef sanal makineniz arasında iletişim kurabilecekleri şekilde yapılandırın (örn. NAT Network veya Host-only Adapter).
* **Ortam Doğrulaması:**
    * Kali makinenizden hedef makineye ping atarak ağ bağlantısını doğrulayın.
    * Hedef makinedeki bazı temel hizmetlerin (örn. HTTP) çalıştığından emin olun.

---

### 4. Temel Bileşenlerin Geliştirilmesi

Bu aşamada Python betiğinizin temel işlevlerini oluşturacaksınız.

* **Dosya Yönetimi ve Temizleme (`if __name__ == "__main__":`)**
    * Rapor dosyalarının (TXT ve PDF) her çalıştırmadan önce temizlenmesi.
* **Loglama ve Raporlama Altyapısı (`yaz_log`, `risk_ekle`)**
    * Konsola ve bir log dosyasına (örn. `tarama.log`) çıktı yazmak için merkezi bir fonksiyon.
    * Tespit edilen riskleri puanlamak ve depolamak için bir yapı (`risk_puanlari`, `bulunan_aciklar`). Bu, raporlamanın temelini oluşturacak.
* **Girdi Doğrulama ve IP Çözümleme (`is_valid_ip_or_url`, `resolve_ip`)**
    * Kullanıcının girdiği hedefin geçerli bir IP adresi veya URL olup olmadığını kontrol etme.
    * URL girilirse, `socket.gethostbyname` kullanarak IP adresine çözümleme. `idna` kütüphanesi ile uluslararası alan adlarını (punycode) destekleme.
* **Komut Çalıştırma Fonksiyonu (`run_command`)**
    * Kali araçlarını çağırmak ve çıktısını almak için güvenli bir yöntem. `subprocess.getoutput` kullanın. Hata yakalamayı unutmayın.
* **Türkçe Karakter Düzeltme (`turkce_karakter_duzelt`)**
    * Raporlamada ve dosya isimlerinde Türkçe karakter sorunlarını gidermek için basit bir fonksiyon.
* **PDF Raporlama (`pdf_olustur`)**
    * `reportlab` kütüphanesini kullanarak `tarama_raporu.txt` dosyasındaki logları PDF formatına dönüştürme.

---

### 5. Tüm Kullanılan Kali Araçları için Betikler

Bu bölüm, her bir Kali aracının Python betiği içine nasıl entegre edileceğini ve çıktılarının nasıl işleneceğini detaylandırır. Her fonksiyon, `run_command` fonksiyonunu kullanarak ilgili Kali aracını çağırır ve çıktıyı loglar.

* **Whois Sorgusu (`whois_lookup`)**
    * `whois <ip>` komutunu çalıştırın.
* **Nmap Taraması (`nmap_scan`)**
    * **Komut:** `nmap -sS -O <ip>` (SYN taraması, OS tespiti)
    * **Çıktı İşleme:** Açık port sayısını tespit edin ve buna göre risk puanı ekleyin. Basit CVE desenlerini (örn. `CVE-YYYY-XXXX`) arayarak zafiyetleri işaretleyin.
* **Nikto Taraması (`nikto_scan`)**
    * **Komut:** `nikto -h http://<ip>`
    * **Çıktı İşleme:** "vulnerable", "issues", "dangerous" gibi anahtar kelimeleri arayarak web zafiyetlerini tespit edin ve risk ekleyin. CVE desenlerini de arayın.
* **Gobuster Taraması (`gobuster_scan`)**
    * **Komut:** `gobuster dir -u http://<ip> -w /usr/share/wordlists/dirb/common.txt`
    * **Çıktı İşleme:** "Status: 200" gibi başarılı durum kodlarını veya ilginç dizinleri gösteren çıktıları arayarak risk ekleyin.
* **WPScan Taraması (`wpscan_scan`)**
    * **Komut:** `wpscan --url http://<ip> --no-update` (Güncelleme kontrolünü atlayın)
    * **Çıktı İşleme:** "vulnerable" kelimesini arayarak WordPress zafiyetlerini tespit edin ve risk ekleyin.
* **SSLscan Taraması (`sslscan_scan`)**
    * **Komut:** `sslscan <ip>`
    * **Çıktı İşleme:** Zayıf SSL/TLS konfigürasyonlarını veya eski protokolleri (örn. SSLv2, SSLv3) işaret ederek risk ekleyin.
* **ARP-Scan (MAC Taraması) (`mac_tarama`)**
    * **Komut:** `arp-scan <ip_range>` (örn. `192.168.1.0/24`)
    * **Çıktı İşleme:** MAC adreslerini yakalayın ve `mac_vendor_lookup` kütüphanesi ile üretici bilgilerini çözümleyin.
* **Cihaz Keşfi (`device_discovery`)**
    * **Komut:** `nmap -sn <ip_range>` (Ping taraması)
    * **Çıktı İşleme:** Ağdaki aktif cihazları loglayın.
* **SQLmap Önerisi (`sqlmap_suggestion`)**
    * Doğrudan SQLmap çalıştırmak yerine, kullanıcının elle deneyebileceği bir örnek komut sağlayın. Bu, SQLmap'in etkileşimli doğası gereği daha güvenlidir.
* **Paralel Tarama (`paralel_tarama_fonksiyonlari`)**
    * `concurrent.futures.ThreadPoolExecutor` kullanarak zaman alıcı tarama fonksiyonlarını eş zamanlı çalıştırın. Bu, aracın hızını artırır. Hata yönetimini unutmayın.

---

### 6. Geliştirmelerin Test Edilmesi

Test, kodunuzun doğru çalıştığından ve beklenen sonuçları verdiğinden emin olmak için kritik bir aşamadır.

* **Birim Testleri (Unit Tests):**
    * Her bir fonksiyonu (örn. `is_valid_ip_or_url`, `resolve_ip`, `turkce_karakter_duzelt`) ayrı ayrı test edin.
    * `run_command` fonksiyonunu, basit komutlarla (örn. `echo "test"`) test ederek doğru çıktıyı aldığından ve hataları yönettiğinden emin olun.
* **Entegrasyon Testleri (Integration Tests):**
    * Her bir Kali aracı entegrasyon fonksiyonunu (örn. `nmap_scan`, `nikto_scan`) test edin.
    * **Gerçek bir zafiyetli sanal makineye karşı** taramaları çalıştırın ve beklenen zafiyetlerin tespit edilip edilmediğini kontrol edin.
* **Uçtan Uca Testler (End-to-End Tests):**
    * `saldiri` ve `savunma` modlarının her ikisini de çalıştırın.
    * `tarama_raporu.txt` ve `tarama_raporu.pdf` dosyalarının doğru oluşturulduğunu, içeriklerinin eksiksiz ve okunabilir olduğunu doğrulayın.
    * Risk puanlarının doğru hesaplandığını kontrol edin.
* **Performans Testleri:**
    * Paralel çalıştırmanın gerçekten performansı artırıp artırmadığını gözlemleyin.
    * Büyük ağ aralıkları için `mac_tarama` ve `device_discovery` gibi fonksiyonların ne kadar sürdüğünü test edin.
* **Hata Yakalama Testleri:**
    * Geçersiz IP/URL girişleri yapın.
    * Kali araçlarının yüklü olmadığı durumları simüle edin (örn. PATH'ten kaldırarak) ve hata mesajlarının doğru bir şekilde loglandığını kontrol edin.
    * Ağ bağlantısı olmayan bir durumda taramaları başlatın.

---

### 7. Karşı Önlemler ve En İyi Uygulamalar

Tespit edilen zafiyetlere yönelik karşı önlemler ve genel güvenlik iyileştirmeleri hakkında kullanıcıya bilgi sağlamak önemlidir.

* **Saldırı Yöntemi Önerileri (`saldiri_onerileri`)**
    * Tespit edilen zafiyetlere göre spesifik saldırı araçları ve yöntemleri önerecek mantık.
* **Güvenlik Önlemleri ve Savunma Önerileri (`savunma_onerileri`)**
    * Tespit edilen zafiyetlere karşı alınabilecek somut güvenlik önlemleri.
    * Genel güvenlik en iyi uygulamaları (güncellemeler, IDS/IPS, WAF, log izleme, vb.) hakkında tavsiyeler.
* **Genel Risk Hesaplama (`genel_risk_hesapla`)**
    * Toplanan risk puanlarına dayanarak genel bir risk seviyesi (Düşük, Orta, Yüksek) belirleme ve bunu kullanıcıya raporlama.

---

### 8. Sonuç

Bu yol haritasını takip ederek, hem etkili hem de bilgilendirici bir siber güvenlik tarama aracı geliştirebilirsiniz. Geliştirme süresince sürekli test etmek, kodunuzun sağlamlığını ve doğruluğunu sağlayacaktır. Unutmayın, güvenlik araçları sürekli gelişir, bu nedenle kodunuzu ve kullandığınız araçları güncel tutmak hayati önem taşır.
