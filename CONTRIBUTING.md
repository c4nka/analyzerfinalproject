
---

## Siber Güvenlik Tarama Aracı - Kodlama Standartları

Bu belge, "Siber Güvenlik Tarama Aracı" projesindeki Python kodunun yazımında takip edilmesi gereken kuralları ve en iyi uygulamaları tanımlar. Bu standartlara uymak, kod kalitesini artırır, hata oranını düşürür ve gelecekteki bakımı kolaylaştırır.

## 1. Genel Kurallar ve PEP 8 Uyumu

* **Maximum Satır Uzunluğu:** Satırlar 79 karakteri geçmemelidir. Bu, kodun küçük ekranlarda veya yan yana pencerelerde okunmasını kolaylaştırır.
* **Boş Satırlar:**
    * Üst düzey fonksiyonlar ve sınıf tanımları arasına ikişer boş satır bırakılmalıdır.
    * Metot tanımları arasına birer boş satır bırakılmalıdır.
    * Mantıksal olarak ayrılmış kod blokları arasına tek boş satır bırakılabilir.
* **İçe Girintileme (Indentation):** Her zaman 4 boşluk bırakılarak içe girintileme yapılmalıdır. Tab karakterleri kullanılmamalıdır.

## 2. İsimlendirme Kuralları

* **Değişkenler ve Fonksiyonlar:** Küçük harf ve alt çizgi ile ayrılmış kelimeler (`snake_case`) kullanılmalıdır (örn. `risk_puanlari`, `yaz_log`).
* **Sabitler (Constants):** Tamamen büyük harf ve alt çizgi ile ayrılmış kelimeler kullanılmalıdır (örn. `RAPOR_TXT`, `RAPOR_PDF`).
* **Sınıflar:** Her kelimenin ilk harfi büyük, bitişik kelimeler (`CamelCase`) kullanılmalıdır (örn. `MacLookup`, `ThreadPoolExecutor`).
* **Modül İsimleri:** Kısa, küçük harfli ve alt çizgi ile ayrılmış kelimeler olmalıdır (örn. `main.py`).

## 3. Yorumlar ve Docstrings

Kodun anlaşılabilirliğini artırmak için yorumlar ve Docstrings (dokümantasyon dizgileri) etkin bir şekilde kullanılmalıdır.

* **Docstrings:** Her fonksiyon, sınıf ve metod için bir Docstring (üç tırnak içinde) eklenmelidir. Bu, fonksiyonun veya sınıfın ne işe yaradığını, aldığı argümanları ve döndürdüğü değeri kısaca açıklamalıdır.
    *Örnek:*
    ```python
    def yaz_log(veri, seviye="info"):
        """
        Hem dosyaya hem konsola log yazar.

        Args:
            veri (str): Loglanacak metin.
            seviye (str, optional): Log seviyesi (info, warning, error, debug). Varsayılan 'info'.
        """
        # ... kod ...
    ```
* **Satır İçi Yorumlar:** Karmaşık mantık içeren veya anlaşılması zor olabilecek kod blokları için açıklayıcı yorumlar kullanılmalıdır. Yorumlar, kodun "nasıl" çalıştığından ziyade "neden" çalıştığını açıklamalıdır.
    *Örnek:*
    ```python
    # Port sayısına göre risk puanını hesapla, maksimum 5 olsun
    puan = min(2 + acik_port_sayisi // 3, 5)
    ```

## 4. İçe Aktarmalar (Imports)

* İçe aktarmalar, dosyanın en üstünde, her satırda birer tane olacak şekilde düzenlenmelidir.
* Standart kütüphane içe aktarmaları, üçüncü taraf kütüphanelerden önce gelmeli, ardından kendi modülleriniz gelmelidir. Her kategori arasında boş bir satır bırakılmalıdır.
    *Örnek:*
    ```python
    import socket
    import subprocess
    import os

    import ipaddress
    import logging
    import re
    from datetime import datetime
    from concurrent.futures import ThreadPoolExecutor, as_completed

    from reportlab.lib.pagesizes import A4
    from reportlab.pdfgen import canvas
    from mac_vendor_lookup import MacLookup
    import idna # Yeni eklenenler veya özel sırası olanlar
    ```

## 5. Fonksiyonlar ve Metotlar

* **Tek Sorumluluk Prensibi (SRP):** Her fonksiyonun veya metodun tek bir işi olmalıdır. Karmaşık görevler, daha küçük, yönetilebilir fonksiyonlara bölünmelidir.
* **Parametreler:** Anlaşılır ve açıklayıcı parametre isimleri kullanılmalıdır.
* **Hata Yönetimi:** `try-except` blokları kullanarak beklenen hatalar ele alınmalı ve kullanıcıya veya log dosyasına anlamlı hata mesajları iletilmelidir. `run_command` fonksiyonunuzdaki hata yönetimi buna iyi bir örnektir.

## 6. Stringler ve Formatlama

* **F-stringler (Formatted String Literals):** Değişkenleri stringlere dahil etmek için `f-string`'ler tercih edilmelidir. Bu, daha okunabilir ve performanslıdır.
    *Örnek:* `f"Hedef URL veya IP adresini girin: {hedef}"`
* **Uzun Stringler:** Uzun stringler için parantez içinde bölme veya üç tırnaklı stringler kullanılabilir.

## 7. Güvenlik ve Komut Çalıştırma

* **`subprocess.getoutput`:** Mevcut kodunuzda `subprocess.getoutput` kullanıyorsunuz. Güvenlik açısından, kullanıcıdan alınan girdilerle doğrudan komut çalıştırmaktan kaçınmak önemlidir. Sizin durumunuzda hedef IP/URL doğrudan komuta aktarılıyor. Nmap, Nikto gibi araçlar zaten bu tür girdileri işlemek üzere tasarlandığı için bu risk yönetilebilir. Ancak, gelecekte betiğe yeni komutlar eklerken `subprocess.run` ve `shell=False` ile komut ve argümanları liste olarak geçirme gibi daha güvenli yöntemleri değerlendirin.
    *Örnek:* `subprocess.run(["nmap", "-sS", "-O", ip], capture_output=True, text=True)`

## 8. Global Değişkenler

* `risk_puanlari` ve `bulunan_aciklar` gibi **global değişkenler**, kodun takibini zorlaştırabilir. Mümkün olduğunda, bu tür verilerin fonksiyonlar arasında parametre olarak geçirilmesi veya bir sınıf yapısı içinde saklanması tercih edilebilir. Ancak mevcut projenizin boyutu göz önüne alındığında, bu kullanım şimdilik kabul edilebilir. Proje büyüdükçe bu yapıyı gözden geçirin.

## 9. Raporlama ve Çıktı

* **Tutarlılık:** Log mesajları ve rapor çıktıları arasında format tutarlılığı sağlanmalıdır. `yaz_log` fonksiyonunuz bu tutarlılığı destekliyor.
* **Türkçe Karakterler:** `turkce_karakter_duzelt` fonksiyonunuz, PDF raporunda Türkçe karakter sorunlarını çözmek için önemlidir. Kullanımının devamlılığı sağlanmalıdır.

## 10. Kod İncelemesi (Code Review)

* Mümkünse, kodunuzu başka bir geliştiricinin incelemesi, standartlara uyumu kontrol etmek ve potansiyel hataları veya iyileştirme alanlarını bulmak için çok faydalıdır.

---
