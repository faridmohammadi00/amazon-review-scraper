import os

from selenium import webdriver
from selenium.common import NoSuchElementException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time
import csv


def create_csv_file(product_name, fieldnames):
    if os.path.isfile('./data/bestbuy/' + product_name + '.csv') is not True:
        print("Creating File..")
        with open('./data/bestbuy/' + product_name + '.csv', 'a', newline='', encoding='utf-8') as csvFile:
            writer = csv.DictWriter(csvFile, fieldnames=fieldnames)
            writer.writeheader()

        csvFile.close()
    return True


def get_product_name(driver):
    p_name = driver.find_element(By.XPATH, '//h2[@class="heading-6 product-title mb-100"]').text.strip()

    bad_chars = ['/', ';', ':', '!', '*', ')', '(', '[', ']', '|', '_', '$', '#', ' ', '"', ',']
    for ch in bad_chars:
        if ch in p_name:
            p_name = p_name.replace(ch, '-')

    print("Product Name: ", p_name)
    return p_name


def get_review_data(review_el):

    profile_name = review_el.find_element(By.TAG_NAME, 'strong').text
    review_date_el = review_el.find_element(By.TAG_NAME, 'time')
    review_date_text = review_date_el.text + " | " + review_date_el.get_attribute("title")

    review_star_txt = review_el.find_element(By.TAG_NAME, 'p').text

    data_el = review_el.find_elements(By.TAG_NAME, 'p')
    data_text = data_el[1].text

    r_data_info = {
        'Profile Name': profile_name,
        'Date': review_date_text,
        'Data': data_text,
        'Star': review_star_txt
    }

    return r_data_info


def scrape_reviews(url):
    options = Options()
    user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 14_6_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Safari/605.1.15'
    options.add_argument(f'user-agent={user_agent}')
    driver = webdriver.Chrome(options=options)

    fieldnames = ['Profile Name', 'Date', 'Data', 'Star']

    for i in range(1, 61):
        print("Counter: ", i)
        s_url = url + str(i)

        if i == 1:
            driver.get(s_url)
        else:
            driver.switch_to.new_window('tab')
            driver.get(s_url)
        time.sleep(5)

        product_name = get_product_name(driver)

        create_csv_file(product_name, fieldnames)

        r_wrapper_ul = driver.find_elements(By.XPATH, '//*[@id="reviews-accordion"]/div[2]/ul/li')
        print("Count of Reviews in page: ", len(r_wrapper_ul))
        with open(f'./data/bestbuy/{product_name}.csv', "a", newline='', encoding='utf-8') as amzCSVFile:
            writer = csv.DictWriter(amzCSVFile, fieldnames=fieldnames)
            data_list = []
            for review in r_wrapper_ul:
                result = get_review_data(review)
                data_list.append(result)

            writer.writerows(data_list)

        i += 1
        time.sleep(5)

    driver.quit()
    print("Scrapping complete.")
    return True


if __name__ == "__main__":

    with open('bestbuy-urls.txt', 'r', newline='', encoding='utf-8') as bestbuy_file:
        for url in bestbuy_file:
            scrape_reviews(url)
