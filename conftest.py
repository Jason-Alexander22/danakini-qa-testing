import pytest
from appium import webdriver
from appium.options.android import UiAutomator2Options

@pytest.fixture(scope="function")
def driver():
    options = UiAutomator2Options()
    options.platform_name = "Android"
    options.automation_name = "UiAutomator2"
    options.device_name = "Samsung Device"
    options.app_package = "com.dkf.danakinifinance"
    options.app_activity = "com.dkf.danakinifinance.view.login.NewLoginActivity"
    options.no_reset = True
    options.auto_grant_permissions = True

    driver = webdriver.Remote("http://127.0.0.1:4723", options=options)
    yield driver
    driver.quit()