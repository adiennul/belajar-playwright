import pytest
import re
from playwright.sync_api import Page, expect

# Data test: (user, password, expected_result)
credentials = [
    ("testlogin", "Testlogin1!", "Success"),          # user benar, pass benar
    ("testloginx", "Testlogin1!", "Invalid username or password!"),       # user salah, pass benar
    ("testlogin", "Testlogin1!x", "Invalid username or password!"),     # user benar, pass salah
    ("testloginx", "Testlogin1!x", "Invalid username or password!")          # user salah, pass salah
]

@pytest.mark.parametrize('username, password, expected_result', credentials)
def test_login(page: Page, username, password, expected_result):
    # 0. Blokir iklan & tracking agar DemoQA tidak macet/timeout saat memuat script iklan
    page.route(
        re.compile(r"(google|doubleclick|adservice|analytics|adsbygoogle|amazon-adsystem)"),
        lambda route: route.abort()
    )

    # 1. Buka halaman login (gunakan domcontentloaded)
    page.goto("https://demoqa.com/login", wait_until="domcontentloaded", timeout=45000)

    # 2. Isi form login
    user_input = page.locator("#userName")
    user_input.wait_for(state="visible")
    user_input.fill(username)   

    pass_input = page.locator("#password")
    pass_input.fill(password)

    # 3. Klik tombol login (di demoqa elemennya adalah <button id="login">, bukan <input>)
    login_btn = page.locator("#login")
    login_btn.scroll_into_view_if_needed()
    login_btn.click()

    # 4. Validasi hasil login
    if expected_result == "Success":
        # Di DemoQA, login berhasil mengarahkan ke halaman /profile
        expect(page).to_have_url(re.compile(r".*profile.*"), timeout=10000)
        print("Login berhasil!")

    elif expected_result == "Invalid username or password!":
        # Validasi pesan error
        error_element = page.locator("#name")
        expect(error_element).to_have_text("Invalid username or password!", timeout=5000)
        print("Login gagal terkonfirmasi: Pesan error muncul.")
