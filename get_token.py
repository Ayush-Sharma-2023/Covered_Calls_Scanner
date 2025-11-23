import pyotp
import requests
import json
from urllib.parse import urlparse, parse_qs
from playwright.sync_api import sync_playwright
from dotenv import load_dotenv
import os
load_dotenv() 

API_KEY = os.getenv("API_KEY")
SECRET_KEY = os.getenv("SECRET_KEY")
REDIRECT_URI = os.getenv("REDIRECT_URI")
MOBILE_NO = os.getenv("MOBILE_NO")
PIN = os.getenv("PIN")
TOTP_SECRET = os.getenv("TOTP_SECRET")

AUTH_URL = f'https://api.upstox.com/v2/login/authorization/dialog?response_type=code&client_id={API_KEY}&redirect_uri={REDIRECT_URI}'
totp = pyotp.TOTP(TOTP_SECRET)
print("Current TOTP:", totp.now())

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    context = browser.new_context()
    page = context.new_page()

    with page.expect_request("**/callback?code=*") as request_info:
        page.goto(AUTH_URL)

        page.locator("#mobileNum").click()
        page.locator("#mobileNum").fill(MOBILE_NO)
        page.get_by_role("button", name="Get OTP").click()

        otp = totp.now()
        page.locator("#otpNum").click()
        page.locator("#otpNum").fill(otp)
        page.get_by_role("button", name="Continue").click()

        page.get_by_label("Enter 6-digit PIN").click()
        page.get_by_label("Enter 6-digit PIN").fill(PIN)
        page.get_by_role("button", name="Continue").click()

        page.wait_for_load_state()

    request = request_info.value
    redirected_url = request.url
    parsed = urlparse(redirected_url)
    auth_code = parse_qs(parsed.query)['code'][0]

    print(f"\n🔗 Redirected URL: {redirected_url}")
    print(f"✅ Extracted Auth Code: {auth_code}")

    context.close()
    browser.close()

token_url = 'https://api.upstox.com/v2/login/authorization/token'
token_headers = {
    'accept': 'application/json',
    'Api-Version': '2.0',
    'Content-Type': 'application/x-www-form-urlencoded',
}
token_data = {
    'code': auth_code,
    'client_id': API_KEY,
    'client_secret': SECRET_KEY,
    'redirect_uri': REDIRECT_URI,
    'grant_type': 'authorization_code',
}

response = requests.post(token_url, headers=token_headers, data=token_data)
json_response = response.json()

with open('json/token.json', 'w') as json_file:
    json.dump(json_response, json_file, indent=4)

print(f"\n🪙 Access Token: {json_response['access_token']}")