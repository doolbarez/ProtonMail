from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from fake_useragent import UserAgent
import time
import requests
import random
import string

# Настройка опций для веб-драйвера

with open('Useragent.txt', 'r') as file:
    useragents = file.read().splitlines()

# Случайный выбор User-Agent
random_useragent = random.choice(useragents)

# Использование случайного User-Agent в Selenium WebDriver
UserAgent = UserAgent()
options = webdriver.ChromeOptions()
options.add_argument("--incognito") 
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument(f"user-agent={random_useragent}")
# Тут добавить функцию proxy листов
# Запуск веб-драйвера с настройками прокси
driver = webdriver.Chrome(options=options)
# Открытие страницы
driver.get("https://account.proton.me/mail/signup")
time.sleep(7)


# Переключение на фрейм
frame = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "/html/body/div[1]/div[4]/div[1]/main/div[1]/div[2]/form/iframe")))
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
free_button.click()

import json
import requests
from image_detector import solve_image


def get_solutions(cs):
    return requests.post("http://127.0.0.1:8000/solve", json={
        "challenges": cs
    }).json()['solutions']
# Получение токена капчи
#verify_captcha = driver.find_element(By.XPATH, "Тут найти тег каптчи")
#if verify_captcha = тут сделать условие если присутствует
captcha_token = "EuNN2AjxcxgpKAxKCrcgIqwb"  # Значение токена капчи

# Инициализация капчи
first_request = requests.get(f"https://account-api.proton.me/captcha/v1/api/init?challengeType=2D&parentURL=https://account-api.proton.me/core/v4/captcha?Token={captcha_token}&ForceWebMessaging=1&displayedLang=en&supportedLangs=en-US,en-US,en,en-US,en&purpose=signup")

# Получение изображения капчи
img = requests.get("https://account-api.proton.me/captcha/v1/api/bg", params={
    "token": first_request.json()['token']
})

# Распознавание изображения капчи
t = solve_image(img.content)
if t is None:
    exit()

# Получение ответов на капчу
challenges = first_request.json()['challenges']
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


next_button = driver.find_element(By.XPATH, "/html/body/div/div/div/div/div/div/div[2]/button[1]")
activate_script = "arguments[0].removeAttribute('disabled');"
driver.execute_script(activate_script, next_button)


# Отправка ответа на капчу для верификации
submit_request = requests.get("https://account-api.proton.me/captcha/v1/api/validate", params={
    "token": first_request.json()['token'],
    "contestId": first_request.json()['contestId'],
    "purpose": "signup"
}, headers={
    "pcaptcha": json.dumps(captcha_object)
})
print(submit_request.text)
driver.execute_script("arguments[0].setAttribute('onclick', arguments[1]);", next_button, submit_request)
next_button.click()
time.sleep(100)
driver.quit()