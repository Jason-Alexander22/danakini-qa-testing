import subprocess
import time
from appium.webdriver.common.appiumby import AppiumBy
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

PIN_SETTLE_SECONDS = 1.5
PIN_DIGIT_DELAY = 0.3
HIDE_KEYBOARD = False
SPEEDUP_SETTINGS = False
DEBUG_DUMP_PIN_PAGE = False

LOGIN_ACTIVITY = "com.dkf.danakinifinance.view.login.NewLoginActivity"
PIN_ACTIVITY = "com.dkf.danakinifinance.view.pin.PinInputActivity"

POST_LOGIN_SELECTOR = (
    'new UiSelector().textMatches('
    '"(?i).*Lengkapi Data Diri.*|.*Lewati.*|^Hai,.*")'
)

# Selector untuk bottom sheet PIN salah (TC_Log_Neg_02)
WRONG_PIN_MODAL_SELECTOR = (
    'new UiSelector().textMatches('
    '"(?i)^Login Gagal$|.*Pastikan data yang kamu masukkan sudah benar.*")'
)

# Selector untuk pesan error nomor HP belum/tidak terdaftar (TC_Log_Neg_03)
UNREGISTERED_ERROR_SELECTOR = (
    'new UiSelector().textMatches('
    '"(?i).*belum terdaftar.*|.*tidak terdaftar.*|.*tidak ditemukan.*|'
    '.*Login Gagal.*|.*Pastikan data.*|.*Daftar Sekarang.*")'
)


def adb_input_text(driver, text):
    """Kirim teks angka lewat satu panggilan `adb shell input text`. Return True kalau sukses."""
    caps = driver.capabilities
    udid = caps.get("udid") or caps.get("deviceUDID")
    cmd = ["adb"] + (["-s", udid] if udid else []) + ["shell", "input", "text", text]
    try:
        subprocess.run(cmd, check=True, timeout=10, capture_output=True)
        return True
    except Exception:
        return False


def type_digits_native(driver, number_string):
    """Ketik nomor HP. Utama: adb (cepat). Fallback: press_keycode per digit."""
    if adb_input_text(driver, number_string):
        return
    for d in number_string:
        if d.isdigit():
            driver.press_keycode(int(d) + 7)


def enter_pin(driver, pin_code):
    """Masukkan PIN di PinInputActivity."""
    time.sleep(PIN_SETTLE_SECONDS)

    if DEBUG_DUMP_PIN_PAGE:
        with open("pin_page.xml", "w", encoding="utf-8") as f:
            f.write(driver.page_source)

    has_keypad = bool(driver.find_elements(AppiumBy.XPATH, f"//*[@text='{pin_code[0]}']"))

    if has_keypad:
        for digit in pin_code:
            try:
                driver.find_element(AppiumBy.XPATH, f"//*[@text='{digit}']").click()
            except Exception:
                driver.press_keycode(int(digit) + 7)
            time.sleep(PIN_DIGIT_DELAY)
    else:
        if not adb_input_text(driver, pin_code):
            for digit in pin_code:
                driver.press_keycode(int(digit) + 7)
                time.sleep(PIN_DIGIT_DELAY)


def find_login_button(driver, wait):
    """
    Ada 2 elemen bertuliskan 'Login': judul halaman (atas) dan tombol (bawah).
    Ambil elemen dengan posisi y paling bawah = tombol.
    """
    wait.until(EC.presence_of_element_located((AppiumBy.XPATH, "//*[@text='Login']")))
    candidates = driver.find_elements(AppiumBy.XPATH, "//*[@text='Login']")
    return max(candidates, key=lambda el: el.rect["y"])


def input_phone_and_click_login(driver, wait, phone_number):
    """Mengisi nomor HP di NewLoginActivity dan menekan tombol Login bawah."""
    input_field = wait.until(EC.presence_of_element_located((
        AppiumBy.CLASS_NAME, "android.widget.EditText"
    )))
    input_field.click()
    input_field.clear()

    type_digits_native(driver, phone_number)

    if HIDE_KEYBOARD:
        try:
            driver.hide_keyboard()
        except Exception:
            pass

    btn_login = find_login_button(driver, wait)
    rect = btn_login.rect
    center_x = rect["x"] + rect["width"] // 2
    center_y = rect["y"] + rect["height"] // 2

    try:
        btn_login.click()
    except Exception:
        driver.execute_script("mobile: clickGesture", {"x": center_x, "y": center_y})


def perform_phone_input_and_submit(driver, wait, phone_number):
    """Mengisi nomor HP, klik tombol Login, dan tunggu sampai pindah ke PinInputActivity."""
    input_phone_and_click_login(driver, wait, phone_number)
    wait.until(EC.invisibility_of_element_located((
        AppiumBy.XPATH, "//*[contains(@text, 'Belum punya akun')]"
    )))


# -----------------------------------------------------------------------------
# TC_Log_Pos_01: Nomor HP Valid (081318312114), PIN Benar (763298)
# -----------------------------------------------------------------------------
def test_login_positive_success(driver):
    if SPEEDUP_SETTINGS:
        try:
            driver.update_settings({
                "waitForIdleTimeout": 300,
                "actionAcknowledgmentTimeout": 300,
            })
        except Exception:
            pass

    wait = WebDriverWait(driver, 15)

    # 1 & 2. Masukkan Nomor HP dan tekan tombol Login
    perform_phone_input_and_submit(driver, wait, "081318312114")

    # 3. Masukkan 6 digit PIN yang benar
    enter_pin(driver, "763298")

    # 4. Validasi login berhasil: muncul halaman "Lengkapi Data Diri" / Home
    try:
        post_login = wait.until(EC.presence_of_element_located((
            AppiumBy.ANDROID_UIAUTOMATOR, POST_LOGIN_SELECTOR
        )))
    except TimeoutException:
        driver.save_screenshot("after_pin.png")
        with open("after_pin.xml", "w", encoding="utf-8") as f:
            f.write(driver.page_source)
        raise

    assert post_login.is_displayed(), "Login gagal: halaman setelah PIN tidak tampil."
    print("\nTC_Log_Pos_01 PASSED: Berhasil login, halaman 'Lengkapi Data Diri' tampil!")


# -----------------------------------------------------------------------------
# TC_Log_Neg_02: Nomor HP Valid (081318312114), PIN Salah (123456)
# -----------------------------------------------------------------------------
def test_login_negative_invalid_pin(driver):
    if SPEEDUP_SETTINGS:
        try:
            driver.update_settings({
                "waitForIdleTimeout": 300,
                "actionAcknowledgmentTimeout": 300,
            })
        except Exception:
            pass

    wait = WebDriverWait(driver, 15)

    # 1 & 2. Masukkan Nomor HP dan tekan tombol Login
    perform_phone_input_and_submit(driver, wait, "081318312114")

    assert "PinInputActivity" in driver.current_activity, (
        f"Expected PinInputActivity, tapi berada di {driver.current_activity}"
    )

    # 3. Masukkan 6 digit PIN yang salah
    enter_pin(driver, "123456")

    # 4. Validasi muncul pop-up bottom sheet "Login Gagal"
    try:
        error_modal = wait.until(EC.presence_of_element_located((
            AppiumBy.ANDROID_UIAUTOMATOR, WRONG_PIN_MODAL_SELECTOR
        )))
    except TimeoutException:
        driver.save_screenshot("after_wrong_pin.png")
        with open("after_wrong_pin.xml", "w", encoding="utf-8") as f:
            f.write(driver.page_source)
        raise

    assert error_modal.is_displayed(), "Pop-up 'Login Gagal' tidak tampil saat PIN salah."

    # 5. Klik tombol "OK" pada pop-up dan pastikan tetap berada di PinInputActivity
    btn_ok = wait.until(EC.element_to_be_clickable((
        AppiumBy.XPATH, "//*[@text='OK']"
    )))
    btn_ok.click()
    time.sleep(1)

    assert "PinInputActivity" in driver.current_activity, (
        "User tidak tertahan di halaman PinInputActivity setelah menutup pop-up error."
    )
    print("\nTC_Log_Neg_02 PASSED: Pop-up 'Login Gagal' tampil dan user tertahan di PinInputActivity!")


# -----------------------------------------------------------------------------
# TC_Log_Neg_03: Nomor HP Belum Terdaftar (08123456789)
# -----------------------------------------------------------------------------
def test_login_negative_unregistered_phone(driver):
    if SPEEDUP_SETTINGS:
        try:
            driver.update_settings({
                "waitForIdleTimeout": 300,
                "actionAcknowledgmentTimeout": 300,
            })
        except Exception:
            pass

    wait = WebDriverWait(driver, 15)

    # 1 & 2. Masukkan Nomor HP yang belum terdaftar dan klik tombol Login
    input_phone_and_click_login(driver, wait, "08123456789")
    time.sleep(1.5)

    # 3. Validasi 1: Cek apakah muncul pesan error nomor HP tidak/belum terdaftar
    try:
        error_msg = wait.until(EC.presence_of_element_located((
            AppiumBy.ANDROID_UIAUTOMATOR, UNREGISTERED_ERROR_SELECTOR
        )))
        print(f"\nPesan error terdeteksi: '{error_msg.text}'")
    except TimeoutException:
        driver.save_screenshot("after_unregistered_phone.png")
        with open("after_unregistered_phone.xml", "w", encoding="utf-8") as f:
            f.write(driver.page_source)
        raise

    assert error_msg.is_displayed(), "Pesan error nomor HP belum terdaftar tidak muncul."

    # 4. Validasi 2: Pastikan masih berada di halaman Login (NewLoginActivity)
    assert "NewLoginActivity" in driver.current_activity, (
        f"Expected tetap di NewLoginActivity, tapi pindah ke {driver.current_activity}"
    )

    # Jika error berupa pop-up yang memiliki tombol OK / Tutup, tutup agar bersih untuk tes berikutnya
    ok_buttons = driver.find_elements(
        AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().textMatches("(?i)^OK$|^Tutup$|^Mengerti$")'
    )
    if ok_buttons:
        ok_buttons[0].click()
        time.sleep(0.5)

    print("TC_Log_Neg_03 PASSED: Pesan error tampil dan user tetap berada di NewLoginActivity!")