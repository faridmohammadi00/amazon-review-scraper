import os
import itertools

from amazoncaptcha import AmazonCaptcha
from selenium import webdriver
from selenium.common import NoSuchElementException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time
import csv


def captcha_solver(driver):
    print("Start Captcha Solver..")

    solution = None
    while solution is None:
        captcha = AmazonCaptcha.fromdriver(driver)
        solution = captcha.solve()

        # Captcha Input ID: captchacharacters
        #  Submit Button Class: a-button-text
        captcha_input_el = driver.find_element(By.ID, "captchacharacters")
        captcha_input_el.send_keys(solution)

        submit_button = driver.find_element(By.XPATH, '//button[@class="a-button-text"]')
        submit_button.click()
    return True


def create_csv_file(product_name, fieldnames):
    if os.path.isfile('./data/' + product_name + '.csv') is not True:
        print("Creating File..")
        with open('./data/' + product_name + '.csv', 'a', newline='', encoding='utf-8') as csvFile:
            writer = csv.DictWriter(csvFile, fieldnames=fieldnames)
            writer.writeheader()

        csvFile.close()
    return True


def get_product_name(driver):
    p_name = driver.find_element(By.XPATH, '//h1[@class="a-size-large a-text-ellipsis"]').text.strip()

    bad_chars = ['/', ';', ':', '!', '*', ')', '(', '[', ']', '|', '_', '$', '#', ' ', '"', ',']
    for ch in bad_chars:
        if ch in p_name:
            p_name = p_name.replace(ch, '-')

    print("Product Name: ", p_name)
    return p_name


def get_review_data(driver, rId):
    r_profile_name = driver.find_element(By.XPATH, f'//div[@id="{rId}"]//div[@class="a-profile-content"]').text
    r_date = driver.find_element(By.XPATH,
                                 f'//div[@id="{rId}"]//span[@class="a-size-base a-color-secondary review-date"]').text
    r_data = driver.find_element(By.XPATH,
                                 f'//div[@id="{rId}"]//div[@class="a-row a-spacing-small review-data"]').text
    r_star = driver.find_element(By.XPATH, f'//div[@id="{rId}"]//span[@class="a-icon-alt"]').get_attribute(
        'textContent')

    r_data_info = {
        'Profile Name': r_profile_name,
        'Date': r_date,
        'Data': r_data,
        'Star': r_star
    }
    return r_data_info


def scrape_reviews(url, state):
    options = Options()
    user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 14_6_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Safari/605.1.15'
    options.add_argument(f'user-agent={user_agent}')
    driver = webdriver.Chrome(options=options)

    fieldnames = ['Profile Name', 'Date', 'Data', 'Star']

    for i in range(1, 11):
        print("Counter: ", i)
        if state == 'main' and state == 'star':
            s_url = url + str(i)
            print("Scrapping URL: ", s_url)
        else:
            s_url = url + str(i) + f"&sortBy={state}"
        if i == 1:
            driver.get(s_url)
        else:
            driver.switch_to.new_window('tab')
            driver.get(s_url)
        time.sleep(7)

        try:
            captcha_exist = driver.find_element(By.ID, "captchacharacters")

        except NoSuchElementException:
            print('No captcha Found.')
            captcha_exist = None

        if captcha_exist is not None:
            cap_result = captcha_solver(driver)

        time.sleep(5)
        product_name = get_product_name(driver)
        create_csv_file(product_name, fieldnames)

        all_reviews_wrapper = driver.find_element(By.ID, "cm_cr-review_list")
        all_reviews = all_reviews_wrapper.find_elements(By.XPATH, '//div[@class="a-section celwidget"]')

        r_id_list = []
        for review in all_reviews:
            r_id_list.append(review.get_attribute('id'))

        with open(f'./data/{product_name}.csv', "a", newline='', encoding='utf-8') as amzCSVFile:
            writer = csv.DictWriter(amzCSVFile, fieldnames=fieldnames)
            data_list = []
            for idx, rId in enumerate(r_id_list):
                res = get_review_data(driver, rId)
                data_list.append(res)

            writer.writerows(data_list)

        i += 1
        time.sleep(10)

    driver.quit()
    print("Scrapping complete.")
    return True


if __name__ == "__main__":

    star_filter_list = ['one', 'two', 'three', 'four', 'five']
    sort_filter_list = ['recent', 'helpful']

    with open('./urls.txt', 'r') as urlsFile:
        for l1, l2 in itertools.zip_longest(*[urlsFile]*2):
            main_url = l1
            star_filter_url = l2

            scrape_reviews(main_url, state='main')

            print("Scrapping Main URL completed.")

            if 'one_star' in star_filter_url:
                rep_string_star = 'one_star'
            elif 'two_star' in star_filter_url:
                rep_string_star = 'two_star'
            elif 'three_star' in star_filter_url:
                rep_string_star = 'three_star'
            elif 'four_star' in star_filter_url:
                rep_string_star = 'four_star'
            else:
                rep_string_star = 'five_star'

            for star in star_filter_list:
                print("Scrapping Star: ", star)
                url_for_scrapping = star_filter_url.replace(rep_string_star, star + "_star")
                scrape_reviews(url_for_scrapping, state='star')

            print("Scrapping Stars URL completed.")

            for sort_by in sort_filter_list:
                print('Sorting by: ', sort_by)
                scrape_reviews(main_url, sort_by)

            print("Scrapping Sorted URL completed.")

            with open('./done-urls.txt', 'a') as doneFile:
                doneFile.write(l1.strip() + '\n')
                doneFile.write(l2.strip() + '\n')

            doneFile.close()
