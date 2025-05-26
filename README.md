# AirType - Parmakla Havada Yazma Sistemi

AirType, web kamerası aracılığıyla el ve parmak hareketlerinizi algılayarak ekrandaki sanal bir klavye üzerinde yazı yazmanızı sağlayan bir Python projesidir. OpenCV ile görüntü işleme ve MediaPipe ile el takibi teknolojilerini kullanır.

##  Özellikler

*   Gerçek zamanlı el ve parmak ucu algılama (MediaPipe).
*   Ekranda gösterilen sanal QWERTY klavye.
*   Parmak ucunu bir tuş üzerinde bekleterek (dwell-to-click) yazma.
*   Yazılan metnin ekranda anlık olarak gösterilmesi.
*   Temel sesli komut işlevselliği:
    *   'v' tuşu ile sesli komut modunu etkinleştirme.
    *   "bilgisayar" uyandırma kelimesi.
    *   "Google'da ara \[sorgu]" komutu ile web tarayıcısında arama yapma.

##  Kullanılan Teknolojiler

*   **Python 3.10.3**
*   **OpenCV (`opencv-python`):** Kamera erişimi, görüntü işleme ve arayüz çizimi.
*   **MediaPipe (`mediapipe`):** El ve parmak ucu takibi.
*   **NumPy (`numpy`):** Sayısal işlemler ve dizi manipülasyonları.
*   **SpeechRecognition (`SpeechRecognition`):** Ses tanıma.
*   **PyAudio (`PyAudio`):** Mikrofon erişimi için (bazı sistemlerde gereklidir).
*   **`webbrowser`:** Varsayılan web tarayıcısını kontrol etme.
*   **`threading`:** Eş zamanlı işlemler (ses tanıma için).

##  Dosya Yapısı

```
AirType/
├── main.py                 # Ana uygulama mantığı, modülleri entegre eder
├── hand_detector.py        # MediaPipe ile el algılama sınıfı (HandDetector)
├── virtual_keyboard.py     # Sanal klavye çizimi ve tuş etkileşimi sınıfı (VirtualKeyboard)
├── utils.py                # (Gelecekteki yardımcı fonksiyonlar için)
├── requirements.txt        # Gerekli Python paketleri listesi
└── README.md               # Bu dosya
```

##  Kurulum ve Başlatma

### Gereksinimler
*   Python 3.10.3
*   Web kamerası
*   Mikrofon (sesli komutlar için)

### Adımlar
1.  **Proje Dosyalarını Alın (Clone):**
    ```bash
    git clone https://github.com/Artupak/AirType.git # Eğer repoyu bu isimle oluşturduysanız
    cd AirType
    ```
    *(Not: Yukarıdaki `git clone` komutundaki URL'yi kendi GitHub reponuzun URL'si ile güncelleyin.)*

2.  **Sanal Ortam Oluşturun ve Aktifleştirin (Önerilir):**
    ```bash
    python -m venv venv
    ```
    *   Windows'ta:
        ```bash
        .\\venv\\Scripts\\activate
        ```
    *   macOS/Linux'ta:
        ```bash
        source venv/bin/activate
        ```

3.  **Gerekli Paketleri Yükleyin:**
    ```bash
    pip install -r requirements.txt
    ```
    *(Not: `PyAudio` kurulumu Windows'ta sorun çıkarırsa, Microsoft Visual C++ Build Tools yüklemeniz veya [Christoph Gohlke's Unofficial Windows Binaries for Python Extension Packages](https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio) sayfasından sisteminize uygun PyAudio wheel dosyasını indirip `pip install PyAudio‑XYZ.whl` şeklinde kurmanız gerekebilir.)*

### Uygulamayı Çalıştırma
```bash
python main.py
```

##  Kullanım

*   **Yazma:**
    *   Elinizi kameranın görebileceği bir şekilde konumlandırın.
    *   Parmak ucunuzu (veya uçlarınızı) sanal klavyedeki istediğiniz tuşun üzerine getirin.
    *   Seçmek için parmak ucunuzu tuşun üzerinde yaklaşık **0.75 saniye** bekletin.
    *   Yazdığınız metin, ekranın altındaki metin alanında görünecektir.
    *   Özel tuşlar: Klavyedeki `'<'` tuşu silme (backspace), `'_'` tuşu ise boşluk işlevi görür.

*   **Sesli Komutlar:**
    1.  Sesli komut dinleme modunu etkinleştirmek için klavyeden `'v'` tuşuna basın.
    2.  Ekranın sol üst köşesinde bir durum mesajı belirecektir.
    3.  Önce uyandırma kelimesi olan "**bilgisayar**" deyin.
    4.  Ardından komutunuzu söyleyin. Örneğin: "**Google'da ara hava durumu**".
    5.  Komut başarılı olursa, varsayılan web tarayıcınızda ilgili Google arama sonuçları açılacaktır.

*   **Çıkış:** Uygulamadan çıkmak için klavyeden `'q'` tuşuna basın.

##  Gelecek Geliştirmeler (Planlanan)

*   Harfleri hece düzeyinde otomatikleştirme.
*   Sesli geri bildirim (örneğin, tuşa basıldığında veya komut algılandığında gTTS entegrasyonu).
*   Klavye yerine sanal çizim (air-draw) modu.
*   Daha gelişmiş metin düzenleme özellikleri.

##  Yazar

*   **Arda Çınar (Artupak)**
*   GitHub: [https://github.com/Artupak](https://github.com/Artupak)
