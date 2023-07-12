import requests
import pandas as pd
from airflow.decorators import dag, task
from pendulum import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup


@dag(
    dag_id="maybelline-scrapping",
    schedule_interval="0 0 * * *",
    start_date=datetime(2023, 4, 23),
    catchup=False,
    depends_on_past=False,
    dagrun_timeout=datetime.timedelta(minutes=60),
)
@task
def scrapping_data():
    names = []
    prices = []
    colors = []
    error_urls = []

    driver = webdriver.Chrome()
    wait = WebDriverWait(driver, 10)

    driver.get("https://www.maybelline.com/lip-makeup")

    button = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "shop-all__load-more")))
    button.click()

    html = driver.page_source
    soup = BeautifulSoup(html, "html.parser")

    li_elements = soup.find_all("li", class_="shop-all__item")
    url_contexts = [a.get('href') for i in li_elements for a in i.find_all('a')]
    urls = [str("https://www.maybelline.com" + i) for i in url_contexts]

    for url in urls[2:]:
        response = requests.get(url)
        soup = BeautifulSoup(response.content, "html.parser")

        try:
            name = soup.find(class_="prod-item__name").text.strip()
            price = float(soup.find(class_="prod-price").text.strip("$ MSRP"))
            color = ", ".join(
                [elem.span.get("data-itemname") for elem in soup.find_all(class_="color-picker__swatch-new")])
        except:
            error_urls.append(url)
            continue
        names.append(name)
        prices.append(price)
        colors.append(color)
