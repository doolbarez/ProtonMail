from seleniumwire import webdriver
from seleniumwire.utils import decode
from image_detector import solve_image
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import requests as rs
import random
import string
import json
from urllib.parse import quote

def get_solutions(cs):
    try:
        response = rs.post("http://127.0.0.1:8000/solve", json={
            "challenges": cs
        })
        response.raise_for_status()  # Проверка статуса ответа
        return response.json().get('solutions', [])
    except (rs.exceptions.RequestException, ValueError):
        return []

# Настройка опций для веб-драйвера

with open('Useragent.txt', 'r') as file:
    useragents = file.read().splitlines()

# Случайный выбор User-Agent
random_useragent = random.choice(useragents)

# Использование случайного User-Agent в Selenium WebDriver
seleniumwire_options = webdriver.ChromeOptions()
seleniumwire_options .add_argument("--disable-blink-features=AutomationControlled")
seleniumwire_options .add_argument(f"user-agent={random_useragent}")
seleniumwire_options .add_argument('--ignore-certificate-errors-spki-list')
seleniumwire_options .add_argument('--ignore-ssl-errors')
options= {
    'proxy': {
        'http': 'http://brd-customer-hl_ce63cbe3-zone-data_center:47go741wi9a6@brd.superproxy.io:22225',
        'https': 'http://brd-customer-hl_ce63cbe3-zone-data_center:47go741wi9a6@brd.superproxy.io:22225',
        'no_proxy': 'localhost,127.0.0.1:8000'
    }
}
proxies = {
    'http': 'http://brd-customer-hl_ce63cbe3-zone-data_center:47go741wi9a6@brd.superproxy.io:22225',
    'https': 'http://brd-customer-hl_ce63cbe3-zone-data_center:47go741wi9a6@brd.superproxy.io:22225',
    'no_proxy': 'localhost,127.0.0.1:8000'
}
# Запуск веб-драйвера с настройками прокси
driver = webdriver.Chrome(seleniumwire_options=options)
# Открытие страницы
driver.get("https://account.proton.me/mail/signup")
time.sleep(7)

# Переключение на фрейм
frame = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH, "/html/body/div[1]/div[4]/div[1]/main/div[1]/div[2]/form/iframe")))
driver.switch_to.frame(frame)
# Нахождение полей и ввод данных
email_field = driver.find_element(By.ID, "email")
# Генерация случайной почты
email = ''.join(random.choice(string.ascii_lowercase) for _ in range(10))
email_field.send_keys(email)
time.sleep(1)
# Переключение с фрейма
driver.switch_to.parent_frame()
time.sleep(1)
password_field = driver.find_element(By.ID, "password")
# Генерация случайного пароля
password = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(8))
password_field.send_keys(password)
time.sleep(1)
repeat_password_field = driver.find_element(By.ID, "repeat-password")
repeat_password_field.send_keys(password)
time.sleep(1)
# Нахождение и нажатие кнопки
create_button = driver.find_element(By.XPATH, "/html/body/div[1]/div[4]/div[1]/main/div[1]/div[2]/form/button")
create_button.click()
time.sleep(2)
free_button = driver.find_element(By.XPATH, "/html/body/div[1]/div[4]/div/main/div/div[1]/div[2]/div[3]/button")
driver.scopes = ['.*']
requests = driver.requests
token = None
contest_id = None
challenges = None
def intercept_response(request, response):
    global token, contest_id, challenges
    if request.url.startswith('https://account-api.proton.me/captcha/v1/api/init?'):
        response = request.response
        body = decode(response.body, response.headers.get('Content-Encoding','identity'))
        decoded_body = body.decode('utf-8')
        json_data = json.loads(decoded_body)
        token = json_data['token']
        contest_id = json_data['contestId']
        challenges = json_data['challenges']
driver.response_interceptor = intercept_response
free_button.click()
waitframe= WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH, "/html/body/div[1]/div[4]/div/main/div/div[2]/div/div[2]/iframe")))
time.sleep(7)
# Окно с капчей
img = rs.get("https://account-api.proton.me/captcha/v1/api/bg", proxies=proxies, params={
    "token": token
})

# Распознавание изображения капчи
t = solve_image(img.content)
if t is None:
    exit()

# Получение ответов на капчу
answers = get_solutions(challenges)
print(t, answers)

# Составление объекта капчи
captcha_object = {
    "x": t[0],
    "y": t[1],
    "answers": answers,
    "clientData": None,
    "pieceLoadElapsedMs": 140,
    "bgLoadElapsedMs": 180,
    "challengeLoadElapsedMs": 180,
    "solveChallengeMs": 5000,
    "powElapsedMs": 540
}
pcaptcha = json.dumps(captcha_object)

url = f"https://account-api.proton.me/captcha/v1/api/validate?token={quote(token.encode('utf-8'))}&contestId={quote(contest_id.encode('utf-8'))}&purpose=signup"

headers = {
    "Content-Type": "application/json",
    "pcaptcha": pcaptcha
}

captcha_frame = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH, "/html/body/div[1]/div[4]/div/main/div/div[2]/div/div[2]/iframe")))
driver.switch_to.frame(captcha_frame)
captcha_frame2 = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH, "/html/body/iframe")))
driver.switch_to.frame(captcha_frame2)

next_button = driver.find_element(By.XPATH, "/html/body/div/div/div/div/div/div/div[2]/button[1]")
file_request = None
def intercept_response2(request):
    global file_request
    # Проверить URL запроса и сохранить его, если он соответствует вашим требованиям
    if request.url.startswith('https://account-api.proton.me/captcha/v1/api/validate?token'):
        request.create_response(
        status_code = 200,
        headers = {"Content-Type": "application/json",    "pcaptcha": pcaptcha}
        )
        file_request = 1

# Установить функцию перехвата запроса перед отправкой
driver.request_interceptor = intercept_response2
next_button.click()
time.sleep(200)
driver.quit()
