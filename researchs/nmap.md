---

## NMAP Paketinin Derinlemesine Analizi

### 1. Giriş

Nmap (Network Mapper), Gordon Lyon (Fyodor) tarafından geliştirilen, ağ keşfi ve güvenlik denetimi için kullanılan, açık kaynaklı, çok yönlü ve güçlü bir yardımcı programdır. Ağ yöneticileri ve sızma testi uzmanları tarafından hedef sistemler hakkında bilgi toplamak, güvenlik açıklarını belirlemek ve ağ topolojilerini haritalamak amacıyla yaygın olarak kullanılır. Nmap, raw IP paketlerini kullanarak ana bilgisayarların (hosts) ağda mevcut olup olmadığını, hangi servislerin (uygulama adı ve versiyonu dahil) çalıştığını, hangi işletim sistemlerinin (OS) kullanıldığını, ne tür paket filtrelerinin/güvenlik duvarlarının (firewalls) devrede olduğunu ve diğer birçok karakteristik özelliği belirleyebilir. Basit port taramalarından karmaşık komut dosyası çalıştırmalarına kadar geniş bir yetenek yelpazesine sahiptir.

### 2. Nmap'in Temel İşlevleri ve Kullanım Alanları

Nmap'in temel işlevleri ve siber güvenlik ekosistemindeki rolleri şunlardır:

* **Ana Bilgisayar Keşfi (Host Discovery):** Bir ağda hangi ana bilgisayarların çevrimiçi olduğunu belirlemek. Ping taramaları (ICMP echo request), TCP SYN/ACK pingleri, ARP pingleri gibi çeşitli yöntemler kullanır.
* **Port Taraması (Port Scanning):** Hedef sistem üzerindeki hangi portların açık, kapalı veya filtrelenmiş olduğunu tespit etmek. En yaygın ve temel kullanım alanıdır. Çeşitli port tarama teknikleri mevcuttur (SYN, Connect, UDP, FIN, Xmas, Null vb.).
* **Servis Sürümü Tespiti (Service Version Detection):** Açık portlarda çalışan servislerin (HTTP, FTP, SSH vb.) türünü ve sürüm numarasını belirlemek. Bu bilgi, bilinen zafiyetlere sahip eski veya hatalı yapılandırılmış servisleri tespit etmek için kritik öneme sahiptir.
* **İşletim Sistemi Tespiti (OS Detection):** Hedef ana bilgisayarın işletim sistemini (Windows, Linux, macOS vb.) ve bazen dağıtımını ve sürümünü parmak izi (fingerprinting) tekniğiyle belirlemek. TCP/IP yığını farklılıklarını analiz ederek çalışır.
* **Güvenlik Duvarı/Paket Filtreleme Tespiti (Firewall/Packet Filtering Detection):** Hedef ile tarayıcı arasındaki güvenlik duvarlarının varlığını ve bunların hangi kurallarla çalıştığını belirlemeye çalışmak.
* **Nmap Komut Dosyası Motoru (Nmap Scripting Engine - NSE):** Nmap'in en güçlü özelliklerinden biridir. Kullanıcıların (veya topluluğun) özel güvenlik açığı tespiti, gelişmiş keşif veya hatta sömürü (exploitation) görevleri için kendi komut dosyalarını (script) yazmalarına ve çalıştırmalarına olanak tanır. Binlerce yerleşik NSE betiği bulunmaktadır.

### 3. Nmap'in Çalışma Mekanizması ve Temel Kavramlar

Nmap, ağa özel paketler göndererek ve gelen yanıtları analiz ederek çalışır. İşte bazı temel kavramlar:

* **Raw Sockets (Ham Soketler):** Nmap, işletim sisteminin TCP/IP yığınının normal işlevlerini atlayarak kendi özel paketlerini oluşturmak için ham soketleri kullanır. Bu, Nmap'in çok çeşitli tarama tekniklerini uygulayabilmesini sağlar.
* **Paket Başlıkları Manipülasyonu:** Nmap, gönderdiği paketlerin TCP, UDP ve IP başlıklarındaki bayrakları (flags), sıra numaralarını (sequence numbers) ve diğer alanları değiştirerek farklı tarama türleri gerçekleştirir.
* **Zaman Aşımı ve Tekrar Deneme (Timeout and Retries):** Ağ koşullarına ve hedef duyarlılığına göre yanıt gelmemesi durumunda paketleri yeniden gönderir ve zaman aşımı sürelerini ayarlar.
* **Paralelleştirme:** Birden fazla hedefi veya portu eş zamanlı olarak tarayarak tarama süresini optimize eder.
* **Çıktı Formatları:** Nmap, tarama sonuçlarını çeşitli formatlarda (normal, XML, Grepable, s_canner_able) kaydedebilir, bu da sonuçların diğer araçlar veya betikler tarafından işlenmesini kolaylaştırır.

### 4. Nmap Tarama Teknikleri (Derinlemesine)

Nmap'in esnekliği, kullandığı çeşitli tarama tekniklerinden gelir:

* **TCP SYN Scan (`-sS`): "Yarım Açık" Tarama**
    * Nmap bir `SYN` paketi gönderir.
    * Eğer port açıksa, hedef bir `SYN/ACK` paketiyle yanıt verir. Nmap hemen bir `RST` (Reset) paketi göndererek üçlü el sıkışmayı tamamlamaz. Bu, hedefin loglarında tam bir bağlantı kaydı bırakmadığı için "gizli" veya "yarım açık" olarak adlandırılır.
    * Eğer port kapalıysa, hedef bir `RST` paketiyle yanıt verir.
    * Eğer port filtrelenmişse (güvenlik duvarı gibi), yanıt gelmez.
* **TCP Connect Scan (`-sT`): Tam Bağlantı Tarama**
    * Nmap, standart bir `connect()` sistem çağrısı kullanarak tam bir TCP üçlü el sıkışması gerçekleştirir.
    * Avantajı: Ham soketlere ihtiyaç duymaz, bu da her kullanıcı tarafından çalıştırılabileceği anlamına gelir.
    * Dezavantajı: Hedef sistemde tam bağlantı logları bırakır, bu da daha kolay tespit edilmesini sağlar.
* **UDP Scan (`-sU`): UDP Port Tarama**
    * Nmap, her hedeflenen UDP portuna bir UDP paketi gönderir.
    * Eğer port kapalıysa, hedef bir "ICMP port unreachable" hatasıyla yanıt verir.
    * Eğer port açıksa, genellikle bir yanıt gelmez (UDP bağlantısızdır) veya servis özel bir yanıt paketi gönderir. Bu, UDP taramasını yavaş ve belirsiz hale getirebilir.
    * Nmap, belirli yaygın UDP servisleri için (DNS, SNMP vb.) özel yükler (payloads) göndererek daha kesin sonuçlar elde etmeye çalışır.
* **FIN, Xmas, Null Scans (`-sF`, `-sX`, `-sN`): Gizli Tarama Teknikleri**
    * Bu taramalar, TCP bayraklarını manipüle ederek çalışır.
    * **FIN Scan:** `FIN` bayrağı ayarlanmış bir paket gönderir. RFC 793'e göre, kapalı bir port `RST` ile yanıt vermeli, açık bir port ise yanıt vermemelidir.
    * **Xmas Scan:** `FIN`, `PSH`, `URG` gibi tüm bayrakları ayarlar ("Noel ağacı" gibi ışıklar yanıp söner).
    * **Null Scan:** Hiçbir TCP bayrağı ayarlanmaz.
    * Bu taramalar, bazı basit durum bilgisi olmayan (stateless) güvenlik duvarlarını atlatabilir, ancak çoğu modern güvenlik duvarı bu teknikleri kolayca tespit edebilir.
* **ACK Scan (`-sA`): Güvenlik Duvarı Kural Tespiti**
    * Sadece `ACK` bayrağı ayarlanmış bir paket gönderir.
    * Eğer port filtrelenmemişse (açık veya kapalı), hedef bir `RST` paketiyle yanıt vermelidir.
    * Eğer port filtrelenmişse, yanıt gelmez.
    * Bu tarama portların açık olup olmadığını belirlemek için değil, güvenlik duvarı kurallarını ve durum bilgisi olan güvenlik duvarlarını test etmek için kullanılır.
* **IP Protokol Scan (`-sO`): IP Protokol Tespiti**
    * Desteklenen IP protokollerini (TCP, UDP, ICMP vb.) belirlemek için her bir IP protokol numarasına başlıklar gönderir.

### 5. Nmap Komut Dosyası Motoru (NSE)

NSE, Nmap'in modüler yapısını sağlayan ve yeteneklerini büyük ölçüde artıran güçlü bir bileşendir. Lua programlama diliyle yazılan betikler, Nmap'in tarama sürecini zenginleştirir.

* **NSE Kullanım Alanları:**
    * **Keşif (Discovery):** Daha ayrıntılı bilgi toplama (örn. HTTP başlıkları, DNS kayıtları, SMB paylaşımları).
    * **Zafiyet Tespiti (Vulnerability Detection):** Yaygın zafiyetleri (örn. Heartbleed, Shellshock) tarama, varsayılan kimlik bilgilerini kontrol etme.
    * **Kötüye Kullanım (Exploitation):** Basit zafiyetleri istismar etme (örn. zayıf parolaları deneme).
    * **Kaba Kuvvet (Brute Force):** Şifre veya kimlik doğrulama denemeleri.
    * **Arka Kapı Tespiti (Backdoor Detection):** Bilinen arka kapıları veya kötü amaçlı yazılım imzalarını arama.
* **NSE Kategori ve Betik Seçimi:** NSE betikleri kategorilere ayrılmıştır (örn. `auth`, `brute`, `vuln`, `discovery`, `dos`). Kullanıcılar `--script <kategori>` veya `--script <betik_adı>` ile belirli betikleri çalıştırabilirler.
    * Örnek: `nmap -sV -sC <ip>` (`-sC` varsayılan NSE betiklerini çalıştırır).
    * Örnek: `nmap --script http-enum <ip>` (HTTP dizin ve dosya keşfi).
    * Örnek: `nmap --script smb-vuln* <ip>` (SMB zafiyetlerini arar).

### 6. Nmap Kullanım Senaryoları ve İpuçları

* **Temel Hızlı Tarama:** `nmap <hedef>` (Varsayılan olarak ilk 1000 TCP portunu SYN taraması yapar).
* **Versiyon ve İşletim Sistemi Tespiti:** `nmap -sV -O <hedef>`
* **Tüm Portları Tarama:** `nmap -p- <hedef>`
* **Hızlandırma:**
    * `-T<0-5>`: Zamanlama şablonu (0: paranoyak, 5: manyak). Çoğu durumda `-T4` veya `-T3` önerilir.
    * `--min-rate <num>`, `--max-rate <num>`: Paket gönderme hızını kontrol etme.
* **Çıktı Yönetimi:**
    * `-oN <dosya.txt>`: Normal çıktı.
    * `-oX <dosya.xml>`: XML çıktı (diğer araçlar için ideal).
    * `-oG <dosya.grep>`: Grepable çıktı.
* **Hedef Listesi:** `-iL <hedef_listesi.txt>`: Birden fazla hedefi bir dosyadan okuma.
* **Bant Genişliği Kullanımı:** Güvenli olmayan ağlarda veya üretim sistemlerinde dikkatli kullanılmalıdır. Yüksek hızlı taramalar, hizmet kesintilerine veya IDS/IPS alarmlarına neden olabilir.

### 7. Güvenlik Duvarlarını ve IDS/IPS Sistemlerini Atlatma Teknikleri (Nmap Perspektifinden)

Nmap, güvenlik duvarları ve saldırı tespit/engelleme sistemleri (IDS/IPS) tarafından tespit edilmeyi zorlaştırmak için çeşitli teknikler sunar:

* **Parçalı Paketler (`-f`):** Paket başlıklarını küçük parçalara bölerek bazı filtreleme kurallarını atlatmaya çalışır.
* **Sahte Kaynak IP (`-S <ip_adresi>`):** Kaynak IP adresini sahte olarak değiştirir. Ancak yanıtlar sahte IP'ye gideceği için doğrudan sonuç alınamaz, genellikle aldatma amaçlıdır.
* **Decoy (Yemleme) Taraması (`-D <ip1,ip2,ME,ip3>`):** Gerçek tarayıcı (ME) ile birlikte birkaç sahte IP adresinden de paketler gönderir gibi görünerek gerçek tarayıcının kimliğini gizlemeye çalışır.
* **Yanlış Checksum (`--badsum`):** Geçersiz TCP/UDP/IP checksum'larına sahip paketler göndererek, bazı düşük kaliteli güvenlik duvarlarının bu paketleri işlemesi durumunda bilgi sızdırmaya çalışır.
* **Kaynak Port Belirleme (`--source-port <port>`):** Belirli bir kaynak porttan tarama yapar (örn. 53 DNS veya 80 HTTP gibi yaygın portlar), bu da güvenlik duvarı kurallarını atlatmaya yardımcı olabilir.
* **Randomize Hosts (`--randomize-hosts`):** Hedef IP adreslerinin tarama sırasını rastgele hale getirir, bu da zamana dayalı tespitleri zorlaştırır.
* **Paket Zamanlaması Ayarı (`--scan-delay`, `--max-rate`, `--min-rate`):** Tarama hızını ayarlayarak IDS/IPS eşiklerini aşmamaya çalışır. Yavaş taramalar daha az fark edilir ancak daha uzun sürer.

### 8. Nmap Kullanımının Etik Boyutları ve Yasal Uyarılar

Nmap son derece güçlü bir araçtır ve yanlış ellerde kötüye kullanılabilir.

* **Yetkilendirme:** Bir ağda Nmap taraması yapmadan önce her zaman **açık ve yazılı izin** alınmalıdır. İzinsiz tarama, siber suç olarak kabul edilebilir ve yasal sonuçları olabilir.
* **Etik Sorumluluk:** Nmap, potansiyel zafiyetleri ortaya çıkarır. Bu bilgilerin sorumlu bir şekilde kullanılması, sistem sahiplerine bildirilmesi ve düzeltmelerin yapılması için çalışılması önemlidir.
* **Hizmet Kesintisi Riski:** Özellikle agresif tarama yöntemleri (`-T5`, UDP taramaları, NSE exploit betikleri) veya çok sayıda portun taranması, hedef sistemlerde veya ağ cihazlarında hizmet kesintilerine, yavaşlamalara veya çökmelere neden olabilir.

### 9. Sonuç

Nmap, siber güvenlik uzmanlarının cephaneliğindeki en temel ve vazgeçilmez araçlardan biridir. Ağ keşfinden detaylı zafiyet tespitine kadar geniş bir yelpazede kullanılabilen yetenekleri, onu her penetrasyon testi ve güvenlik denetimi sürecinin önemli bir parçası haline getirir. NSE'nin esnekliği sayesinde sürekli olarak yeni zafiyetleri ve keşif tekniklerini destekleyecek şekilde güncellenebilir. Ancak, Nmap'in gücü, onu kullanan kişinin sorumluluğunu da beraberinde getirir. Etik kurallara ve yasalara uygun hareket etmek, bu güçlü aracı siber güvenliği artırma yolunda etkin bir şekilde kullanmanın anahtarıdır. Nmap'in derinlemesine anlaşılması, herhangi bir ağ güvenliği profesyonelinin yetkinliklerini önemli ölçüde artırır.
