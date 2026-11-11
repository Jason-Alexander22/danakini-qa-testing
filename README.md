# Danakini Mobile QA Testing (Manual & Automation)

Automation Testing for Danakini Login Feature

## Struktur File
- `conftest.py` : Konfigurasi driver Appium dan capabilities perangkat Android.
- `test_login.py` : Suite otomasi pengujian fitur Login (`TC_Log_Pos_01`, `TC_Log_Neg_02`, `TC_Log_Neg_03`).
- `Danakini Testcase - Sheet1.pdf` : Dokumen Test Case lengkap beserta Expected & Actual Result (Register & Login).
- `Dokumentasi Hasil Testing Danakini.pdf` : Ringkasan temuan bug/anomali selama pengujian.
- `requirements.txt` : Daftar dependensi Python.

## Cakupan Skenario Otomasi (`test_login.py`)
1. **`TC_Log_Pos_01` (`test_login_positive_success`)**: Login menggunakan nomor HP valid dan PIN benar hingga masuk ke halaman post-login (*Lengkapi Data Diri*).
2. **`TC_Log_Neg_02` (`test_login_negative_invalid_pin`)**: Login menggunakan nomor HP valid namun PIN salah (`123456`), memvalidasi munculnya modal *Login Gagal* dan memastikan pengguna tertahan di `PinInputActivity`.
3. **`TC_Log_Neg_03` (`test_login_negative_unregistered_phone`)**: Menguji input nomor HP yang belum terdaftar (`08123456789`) terhadap validasi halaman `NewLoginActivity`.

## Ringkasan Temuan Pengujian (Bug / UX Findings)

3**Login (`TC_Log_Neg_03` - Unregistered Phone Navigation)**: Saat memasukkan nomor HP yang belum terdaftar dan menekan tombol Login, sistem tidak menampilkan pesan error di halaman Login (`NewLoginActivity`), melainkan tetap mengarahkan pengguna ke halaman `PinInputActivity`.

## Cara Menjalankan Automation Test
1. Pastikan Appium Server aktif di terminal:
   ```bash
   appium
