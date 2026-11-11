# Danakini Mobile QA Testing (Manual & Automation)

Automation Testing for Danakini Login Feature

## Struktur File

* `conftest.py` : Konfigurasi driver Appium dan capabilities perangkat Android.
* `test_login.py` : Suite otomasi pengujian fitur Login (`TC_Log_Pos_01`, `TC_Log_Neg_02`, `TC_Log_Neg_03`).
* `Danakini Testcase - Sheet1.pdf` : Dokumen Test Case lengkap beserta Expected & Actual Result (Register & Login).
* `Dokumentasi Hasil Testing Danakini.pdf` : Ringkasan temuan bug/anomali selama pengujian.
* `requirements.txt` : Daftar dependensi Python.

## Cakupan Skenario Otomasi (`test_login.py`)

1. `TC_Log_Pos_01` (`test_login_positive_success`): Login menggunakan nomor HP valid dan PIN benar hingga masuk ke halaman post-login (*Lengkapi Data Diri*).
2. `TC_Log_Neg_02` (`test_login_negative_invalid_pin`): Login menggunakan nomor HP valid namun PIN salah (`123456`), memvalidasi munculnya modal *Login Gagal* dan memastikan pengguna tertahan di `PinInputActivity`.
3. `TC_Log_Neg_03` (`test_login_negative_unregistered_phone`): Menguji input nomor HP yang belum terdaftar (`08123456789`) terhadap validasi halaman `NewLoginActivity`.

## Ringkasan Temuan Pengujian (Bug / UX Findings)

* **Login (`TC_Log_Neg_03` - Unregistered Phone Navigation):** Saat memasukkan nomor HP yang belum terdaftar dan menekan tombol Login, sistem tidak menampilkan pesan error di halaman Login (`NewLoginActivity`), melainkan tetap mengarahkan pengguna ke halaman `PinInputActivity`.

## Requirements:

1. **Python 3.8+** terpasang di sistem.
2. **Appium Server (v2.x)** beserta driver **UiAutomator2** sudah terpasang (`appium driver install uiautomator2`).
3. **Android SDK / ADB** sudah terpasang dan terdaftar di Environment Variables (`ANDROID_HOME` & `platform-tools`).
4. **Perangkat Android (Real Device / Emulator)** terhubung dengan opsi **USB Debugging** aktif, dan aplikasi **Danakini Finance** sudah terinstal.
5. Pastikan `deviceName` / `udid` dan kredensial akun uji pada `conftest.py` / `test_login.py` sudah disesuaikan dengan perangkat yang digunakan.
