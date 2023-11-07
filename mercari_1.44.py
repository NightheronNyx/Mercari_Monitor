# Mercari Monitor

# Preparation:
# 1. install all the packages need to be imported.
# 2. make sure your chrome is on the last version (>115).
# 3. create a telegram bot and get its token (can get it when the bot is created),
# and chat_id(please refer to https://stackoverflow.com/questions/32423837/telegram-bot-how-to-get-a-group-chat-id).
# 4. replace the keyword, token and chat_id with your own content.
# 5. run the .py code and check your telegram bot.

# Note:
# 1. this code can be run on linux and Windows devices, but larger RAM (at least 1G) is recommended.
#
# 2. selenium and chrome may generate log files, which need to be cleared regularly. my solution: add the line below
# to your crontab: 0 */2 * * * find /tmp -type d -name ".org.chromium*" -exec rm -rf {} +
#
# 3. mercari seems to have modified its search strategy recently.
#   it's normal if irrelevant products are frequently detected. Machine learning may be adopted to address this problem.
#


import requests
from bs4 import BeautifulSoup
import schedule
import time
import hashlib
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime
import subprocess

old_page_source = ""
old_hash_value = ""
check_count = 0


def get_page_source_for_page_token(page_token):
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
    chrome_options.add_argument('--disable-dev-shm-usage')

    driver = webdriver.Chrome(options=chrome_options)

    # modify “apple” to the keyword you want
    url = f"https://jp.mercari.com/search?keyword=apple&order=desc&sort=created_time&status=on_sale&page_token={page_token}"
    driver.get(url)
    # wait until "item-grid" is fully loaded
    try:
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.ID, "item-grid"))
        )
    except:
        return None
    # get the page source
    page_source = driver.page_source
    driver.quit()

    return page_source


# notify=True -- notification will be send to your telegram bot
# max_page=3 -- only the first 3 pages will be read.
# heart_beat=True -- all the check result will be send to telegram bot; False: only change record will be send.
def check_updates(notify=True, max_page=3, heart_beat=False):
    global old_page_source, current_products
    global old_hash_value
    global check_count

    check_count += 1

    is_diff = False

    aggregated_page_source = ""
    aggregated_content = ""

    for i in range(max_page):
        page_token = f"v1%3A{i}"
        page_source = get_page_source_for_page_token(page_token)
        if page_source is None:
            break
        print(f"capture code of the {i + 1} th page...")
        aggregated_page_source += page_source
        soup = BeautifulSoup(page_source, 'html.parser')
        content = soup.find(id="item-grid")
        aggregated_content += str(content)

    clear_chrome_process()

    hash_value = hashlib.sha256(aggregated_content.encode()).hexdigest()
    diff_log = ""

    if hash_value != old_hash_value:

        if check_count == 1:
            init_products = set(extract_product_names(aggregated_page_source))
            product_save(init_products)

        if check_count != 1:
            is_diff = True

        if is_diff:
            previous_products = set(extract_product_names(old_page_source))
            current_products = set(extract_product_names(aggregated_page_source))

            product_save(current_products)

            if current_products == set():
                diff_log = "\nfailed to capture gird information\n"
                is_diff = False
                aggregated_page_source = old_page_source
            else:
                new_list = current_products - previous_products
                sold_list = previous_products - current_products
                if new_list == sold_list == set():
                    diff_log = "\nsome goods might be refreshed\n"
                    is_diff = False
                else:
                    diff_log = f"\nNew on sale：\n{get_diff_log(new_list)}\nNew Sold：\n{get_diff_log(sold_list)}\n"

        old_page_source = aggregated_page_source
        old_hash_value = hash_value

    log = f"the {check_count}th check，time：{str(datetime.now())[:-7]}，change：{is_diff}， hash：{hash_value[-5:]}。 "

    if notify:
        if heart_beat:
            notify_user(log + diff_log, notification=is_diff)
        elif is_diff:
            notify_user(log + diff_log, notification=is_diff)

    print(log + diff_log)
    return aggregated_page_source


# notification=True -- the notification will come with ringbell and vibration.
def notify_user(input, notification=True):
    input = "from mericari: \n" + input + "\n"
    TOKEN = 'your_bot_token'
    chat_id = 'your_chat_id'
    url = f'https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={chat_id}&text=Attention:\n{input}'
    if not notification:
        url = f'https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={chat_id}&text={input}&disable_notification=true'
    requests.get(url)
    # print(response.json())


def extract_product_names(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    item_grid = soup.find(id='item-grid')
    if not item_grid:
        return []
    aria_label_list = {div.get('aria-label') for div in item_grid.find_all('div', "aria-label" == True)}
    product_set = {item.replace("の画像", "") for item in aria_label_list if item is not None and item.endswith("円")}
    return product_set


def get_diff_log(list):
    diff_list = ""
    for i, each in enumerate(list):
        diff_list += (str(i + 1) + " - " + each + "\n")
    return diff_list


def clear_chrome_process():
    command = "sudo pkill -f chrome"
    subprocess.run(command, shell=True)


# main work flow
def main_logic():
    print("service start.")
    notify_user("service start.", notification=False)
    schedule.every(120).seconds.do(check_updates)
    while True:
        schedule.run_pending()
        time.sleep(1)


# this function is used for extracting names of goods and saving them to a txt file.
# this file might be used as dataset for machine learning.
def product_save(product_set, filename="products.txt"):
    product_names = {item.rsplit(' ', 1)[0] for item in product_set}

    existing_names = set()
    try:
        with open(filename, "r", encoding="utf-8") as file:
            for line in file:
                existing_names.add(line.strip())
    except FileNotFoundError:
        pass
    product_names -= existing_names
    with open(filename, "a", encoding="utf-8") as file:
        for name in product_names:
            file.write(name + '\n')


# some method can be adapted to filter un-relevant goods
def valid_check(product_set):
    pass


if __name__ == '__main__':
    alert = 0
    while True:
        try:
            main_logic()
            alert = 0
        except Exception as e:
            error_message = f"Error: \n{str(e)}\nrestart...\n"
            schedule.clear()
            clear_chrome_process()
            print(error_message)
            notify_user(error_message, notification=False)
            alert += 1
            if alert >= 3:
                notify_user("too many errors occurred. Please check.", notification=True)
            time.sleep(15)
