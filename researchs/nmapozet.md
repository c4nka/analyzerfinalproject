---

## Nmap: Ağ Keşfinin ve Güvenlik Denetiminin Temel Aracı

Nmap (Network Mapper), siber güvenlik dünyasında ağ keşfi ve güvenlik denetimi için vazgeçilmez, açık kaynaklı bir araçtır. Geliştiricisi Gordon Lyon (Fyodor) olan Nmap, ham IP paketlerini kullanarak ağdaki sistemler hakkında derinlemesine bilgi toplar.

---

### Temel Yetenekleri Nelerdir?

* **Ana Bilgisayar Keşfi:** Ağdaki aktif cihazları belirler.
* **Port Taraması:** Hedef sistemdeki açık, kapalı veya filtrelenmiş portları tespit eder.
* **Servis Sürümü Tespiti:** Açık portlarda çalışan uygulamaların türünü ve versiyonunu belirler, bu da bilinen zafiyetleri ortaya çıkarır.
* **İşletim Sistemi Tespiti:** Hedef sistemin işletim sistemini parmak izi tekniğiyle tanımlar.
* **Güvenlik Duvarı Tespiti:** Hedef ile tarayıcı arasındaki güvenlik duvarlarının varlığını ve kurallarını anlamaya çalışır.
* **Nmap Komut Dosyası Motoru (NSE):** Lua tabanlı betikler aracılığıyla Nmap'in yeteneklerini büyük ölçüde genişletir. Bu betikler, zafiyet tespiti, gelişmiş keşif ve hatta basit sömürü görevleri için kullanılabilir.

---

### Nasıl Çalışır?

Nmap, özel olarak hazırlanmış ağ paketleri gönderir ve hedeften gelen yanıtları analiz eder. **Raw soketler** kullanarak TCP/IP yığınının normal işlevlerini atlar ve **paket başlıklarındaki bayrakları manipüle** ederek farklı tarama teknikleri (SYN Scan, Connect Scan, UDP Scan, FIN/Xmas/Null Scan, ACK Scan) uygular. Bu teknikler, farklı güvenlik duvarı yapılandırmalarını atlatmaya veya farklı türde bilgiler toplamaya yarar.

---

### Kullanım İpuçları ve Etik Sorumluluk

Nmap, tarama hızını ayarlama (`-T4`), farklı çıktı formatları (`-oX` for XML), hedef listesi okuma (`-iL`) gibi birçok özelliğe sahiptir.

**Unutulmaması Gereken En Önemli Nokta:** Nmap güçlü bir araçtır ve **sadece yetkilendirilmiş ortamlarda kullanılmalıdır**. İzinsiz taramalar yasa dışıdır ve ciddi sonuçları olabilir. Agresif taramalar, hedef sistemlerde **hizmet kesintilerine** neden olabilir.

---

### Sonuç

Nmap, ağ güvenliği profesyonellerinin ve penetrasyon test uzmanlarının en temel araçlarından biridir. Ağları anlamak, zafiyetleri tespit etmek ve güvenlik duruşunu güçlendirmek için kritik bilgiler sağlar. NSE'nin esnekliği sayesinde sürekli güncel kalır ve yeni tehditlere karşı koyabilir. Ancak, Nmap'in gücüyle birlikte etik kullanım ve yasalara uygunluk sorumluluğu da gelir.
