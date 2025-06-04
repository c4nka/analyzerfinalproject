import socket
import subprocess
import os
import re
import ipaddress
import logging
import idna  # en üstte importlara ekle
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from mac_vendor_lookup import MacLookup

# --- Sabitler ---
RAPOR_TXT = "tarama_raporu.txt"
RAPOR_PDF = "tarama_raporu.pdf"

# --- Global Değişkenler ---
risk_puanlari = []
bulunan_aciklar = []

# --- Logger Ayarları ---
logging.basicConfig(
    filename="tarama.log",
    filemode="a",
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.DEBUG,
    encoding="utf-8"
)
console = logging.StreamHandler()
console.setLevel(logging.INFO)
formatter = logging.Formatter("%(levelname)s - %(message)s")
console.setFormatter(formatter)
logging.getLogger().addHandler(console)

def yaz_log(veri, seviye="info"):
    """Hem dosyaya hem konsola log yaz"""
    getattr(logging, seviye)(veri)
    with open(RAPOR_TXT, "a", encoding="utf-8") as f:
        f.write(veri + "\n")

def risk_ekle(kaynak, puan, acik_detay=""):
    yaz_log(f"[!] Risk Tespiti: {kaynak} -> Risk Puani: {puan}/10", "warning")
    risk_puanlari.append(puan)
    bulunan_aciklar.append((kaynak, acik_detay))

def turkce_karakter_duzelt(metin):
    duzeltmeler = {
        'ç': 'c', 'Ç': 'C', 'ğ': 'g', 'Ğ': 'G', 'ı': 'i', 'İ': 'I',
        'ö': 'o', 'Ö': 'O', 'ş': 's', 'Ş': 'S', 'ü': 'u', 'Ü': 'U',
    }
    for turkce, ingilizce in duzeltmeler.items():
        metin = metin.replace(turkce, ingilizce)
    return metin

def is_valid_ip_or_url(hedef):
    try:
        # IP mi?
        ipaddress.ip_address(hedef)
        return True
    except ValueError:
        # Değilse domain adı mı?
        try:
            # Punycode'a çevirip kontrol et
            punycode = idna.encode(hedef).decode("utf-8")
        except idna.IDNAError:
            return False

        # Punycode domain regex kontrolü
        if re.match(r"^(?:[a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}$", punycode):
            return True
    return False

def resolve_ip(url):
    yaz_log(f"\n[+] URL'den IP cozumleme islemi baslatildi: {url}")
    try:
        punycode = idna.encode(url).decode("utf-8")
        ip = socket.gethostbyname(punycode)
        yaz_log(f"   Cozunurluk Basarili: {url} -> IP: {ip}")
        return ip
    except (socket.gaierror, idna.IDNAError) as e:
        yaz_log(f"   Hata: IP adresi cozulmedi: {e}", "error")
        return None

def resolve_ip(url):
    yaz_log(f"\n[+] URL'den IP cozumleme islemi baslatildi: {url}")
    try:
        ip = socket.gethostbyname(url)
        yaz_log(f"   Cozunurluk Basarili: {url} -> IP: {ip}")
        return ip
    except socket.gaierror:
        yaz_log("   Hata: IP adresi cozulmedi.", "error")
        return None

def run_command(cmd):
    try:
        yaz_log(f"[CMD] {cmd}", "debug")
        result = subprocess.getoutput(cmd)
        return result
    except Exception as e:
        yaz_log(f"Komut calistirilirken hata: {e}", "error")
        return ""

def whois_lookup(ip):
    yaz_log(f"\n[+] Whois Sorgusu ({ip}):")
    result = run_command(f"whois {ip}")
    yaz_log(result)

def nmap_scan(ip):
    yaz_log(f"\n[+] Nmap ile port ve isletim sistemi taraması:")
    result = run_command(f"nmap -sS -O {ip}")
    yaz_log(result)
    acik_port_sayisi = result.count("/tcp")
    if acik_port_sayisi > 0:
        puan = min(2 + acik_port_sayisi // 3, 5)
        risk_ekle("Açık Portlar", puan, f"{acik_port_sayisi} adet açık port bulundu.")

    # Basit CVE veya açık analizi (örnek)
    cve_pattern = re.compile(r'CVE-\d{4}-\d{4,7}', re.IGNORECASE)
    cve_list = cve_pattern.findall(result)
    if cve_list:
        cve_unique = set(cve_list)
        yaz_log(f"[!] Tespit edilen CVE'ler: {', '.join(cve_unique)}", "warning")
        risk_ekle("Nmap CVE Tespiti", 6, f"Bulunan CVE'ler: {', '.join(cve_unique)}")

def nikto_scan(ip):
    yaz_log(f"\n[+] Nikto ile web uygulama güvenlik taraması:")
    result = run_command(f"nikto -h {ip}")
    yaz_log(result)
    # Basit açık tespiti
    if re.search(r"(vulnerabilities|issues|dangerous|exploitable)", result, re.IGNORECASE):
        risk_ekle("Nikto Web Açıkları", 6, "Web sunucusu üzerinde açıklık bulundu.")

    # Örnek CVE çıkarma
    cve_pattern = re.compile(r'CVE-\d{4}-\d{4,7}', re.IGNORECASE)
    cve_list = cve_pattern.findall(result)
    if cve_list:
        cve_unique = set(cve_list)
        yaz_log(f"[!] Nikto'dan tespit edilen CVE'ler: {', '.join(cve_unique)}", "warning")

def sqlmap_suggestion(ip):
    yaz_log(f"\n[+] SQLmap komutu önerisi:")
    yaz_log(f"   Örnek komut: sqlmap -u http://{ip}/ornek.php?id=1 --risk=3 --level=5")
    risk_ekle("Olası SQL Injection", 8, "Dinamik parametrelerde SQL Injection denenebilir.")

def get_mac_vendor_cached():
    """MacLookup objesini önbellek olarak saklar."""
    if not hasattr(get_mac_vendor_cached, "mac_lookup"):
        get_mac_vendor_cached.mac_lookup = MacLookup()
        try:
            get_mac_vendor_cached.mac_lookup.update_vendors()  # Offline vendor veritabanını güncelle
        except Exception as e:
            yaz_log(f"MAC vendor database güncellemesi başarısız: {e}", "warning")
    return get_mac_vendor_cached.mac_lookup

def get_mac_vendor(mac_address):
    try:
        mac_lookup = get_mac_vendor_cached()
        mac = mac_lookup.lookup(mac_address)
        return mac
    except Exception as e:
        return f"Belirlenemedi ({e})"

def mac_tarama(ip_range):
    yaz_log(f"\n[+] MAC Adresi ve Cihaz Markası Tespiti ({ip_range}):")
    result = run_command(f"arp-scan {ip_range}")
    yaz_log(result)
    mac_adresleri = re.findall(r"([0-9A-Fa-f]{2}(?::[0-9A-Fa-f]{2}){5})", result)
    for mac in mac_adresleri:
        vendor = get_mac_vendor(mac)
        yaz_log(f"MAC: {mac} -> Üretici: {vendor}")

def device_discovery(ip_range):
    yaz_log(f"\n[+] Ağ cihazları taraması ({ip_range}):")
    result = run_command(f"nmap -sn {ip_range}")
    yaz_log(result)

def gobuster_scan(ip):
    yaz_log(f"\n[+] Gobuster ile dizin taraması ({ip}):")
    result = run_command(f"gobuster dir -u http://{ip} -w /usr/share/wordlists/dirb/common.txt")
    yaz_log(result)
    # Basit açık tespiti
    if "Status: 200" in result:
        risk_ekle("Gobuster Dizin Taraması", 5, "Dizin keşfi sonucu ilginç kaynaklar bulundu.")

def wpscan_scan(ip):
    yaz_log(f"\n[+] WPScan ile WordPress güvenlik taraması ({ip}):")
    result = run_command(f"wpscan --url http://{ip} --no-update")
    yaz_log(result)
    if "vulnerable" in result.lower():
        risk_ekle("WPScan Açıkları", 7, "WordPress zafiyetleri tespit edildi.")

def sslscan_scan(ip):
    yaz_log(f"\n[+] SSL/TLS güvenlik taraması ({ip}):")
    result = run_command(f"sslscan {ip}")
    yaz_log(result)
    if "SSL" in result:
        risk_ekle("SSL/TLS Zafiyetleri", 5, "SSL/TLS konfigürasyonunda potansiyel riskler var.")

def paralel_tarama_fonksiyonlari(ip):
    """Bazı zaman alıcı fonksiyonları paralel çalıştır"""
    fonksiyonlar = [
        whois_lookup,
        nmap_scan,
        nikto_scan,
        gobuster_scan,
        wpscan_scan,
        sslscan_scan,
    ]
    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = [executor.submit(f, ip) for f in fonksiyonlar]
        for future in as_completed(futures):
            try:
                future.result()
            except Exception as e:
                yaz_log(f"Paralel taramada hata: {e}", "error")

def saldiri_onerileri():
    yaz_log("\n[+] Saldırı Yöntemi Önerileri:")
    for kaynak, detay in bulunan_aciklar:
        if "Port" in kaynak:
            yaz_log("- Açık portlar üzerinden brute-force veya servis exploitleri denenebilir (Hydra, Metasploit)")
        elif "Nikto" in kaynak:
            yaz_log("- Web açığı varsa XSS, file inclusion gibi yöntemler uygulanabilir (Burp Suite, OWASP ZAP)")
        elif "SQL" in kaynak:
            yaz_log("- SQL Injection için SQLmap kullanılabilir.")
        elif "Gobuster" in kaynak:
            yaz_log("- Bulunan dizinlere yönelik içerik keşfi ve exploit yapılabilir.")
        elif "WPScan" in kaynak:
            yaz_log("- WordPress zafiyetleri değerlendirilip uygun exploitler denenebilir.")
        else:
            yaz_log(f"- {kaynak}: {detay}")

def savunma_onerileri():
    yaz_log("\n[+] Güvenlik Önlemleri ve Savunma Önerileri:")
    for kaynak, detay in bulunan_aciklar:
        if "Port" in kaynak:
            yaz_log("- Gereksiz portlar kapatılmalı. Güvenlik duvarı ile filtrelenmeli.")
        elif "Nikto" in kaynak:
            yaz_log("- Web sunucusu güncellenmeli, WAF kurulmalı.")
        elif "SQL" in kaynak:
            yaz_log("- Girdi kontrolleri yapılmalı. Hazır sorgular (prepared statements) kullanılmalı.")
        elif "Gobuster" in kaynak:
            yaz_log("- Dizin izinleri gözden geçirilmeli. Gereksiz dosyalar kaldırılmalı.")
        elif "WPScan" in kaynak:
            yaz_log("- WordPress ve eklentileri güncellenmeli, güvenlik eklentileri kurulmalı.")
        else:
            yaz_log(f"- {kaynak} için manuel analiz yapılmalı. Detay: {detay}")
    yaz_log("- Güncellemeler yapılmalı, IDS/IPS sistemleri kurulmalı, loglar izlenmeli.")

def genel_risk_hesapla():
    ort = sum(risk_puanlari) / len(risk_puanlari) if risk_puanlari else 0
    yaz_log(f"\n[+] ORTALAMA RİSK SKORU: {round(ort, 2)} / 10")
    if ort < 3:
        yaz_log("Güvenlik durumu: Düşük risk 👍")
    elif ort < 6:
        yaz_log("Güvenlik durumu: Orta seviye risk ⚠️")
    else:
        yaz_log("Güvenlik durumu: Yüksek risk! 🔥")

def pdf_olustur():
    pdf = canvas.Canvas(RAPOR_PDF, pagesize=A4)
    pdf.setTitle("Siber Güvenlik Tarama Raporu")

    olusturma_zamani = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    width, height = A4
    x = 40
    y = height - 40

    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(x, y, "Siber Güvenlik Tarama Raporu")
    y -= 20
    pdf.setFont("Helvetica", 9)
    pdf.drawString(x, y, f"Olusturulma Tarihi: {olusturma_zamani}")
    y -= 30

    with open(RAPOR_TXT, "r", encoding="utf-8") as f:
        lines = f.readlines()

    for line in lines:
        line = turkce_karakter_duzelt(line.strip())
        if y < 40:
            pdf.showPage()
            pdf.setFont("Helvetica", 9)
            y = height - 40
        pdf.drawString(x, y, line)
        y -= 12

    pdf.save()

if __name__ == "__main__":
    os.system(f"rm -f {RAPOR_TXT} {RAPOR_PDF}")

    mod = input("Tarama modu seçin (saldiri / savunma): ").strip().lower()
    hedef = input("Hedef URL veya IP adresini girin: ").strip()

    if not is_valid_ip_or_url(hedef):
        yaz_log("Hata: Geçersiz IP adresi veya URL girdiniz.", "error")
        exit(1)

    ip = resolve_ip(hedef)
    if not ip:
        yaz_log("IP cozumleme basarisiz, cikiliyor.", "error")
        exit(1)

    # Paralel çalışan taramalar
    paralel_tarama_fonksiyonlari(ip)

    if mod == "saldiri":
        saldiri_onerileri()
    elif mod == "savunma":
        device_discovery(f"{ip}/24")
        mac_tarama(f"{ip}/24")
        savunma_onerileri()
    else:
        yaz_log("Geçersiz mod seçildi. Sadece 'saldiri' veya 'savunma' yazabilirsiniz.", "error")
        exit(1)

    genel_risk_hesapla()
    pdf_olustur()
    yaz_log(f"\n[✓] Tarama tamamlandı. Rapor dosyası: {RAPOR_PDF}", "info")
