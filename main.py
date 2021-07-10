from selenium import webdriver
from PIL import Image
from dotenv import load_dotenv
import os
import time
import pytesseract
import re
import requests as req

load_dotenv(encoding='utf-8')

browser = webdriver.Chrome()
UserROCID = os.getenv('USER_ROCID')
UserName = os.getenv('USER_NAME')
UserPhone= os.getenv('USER_PHONE')
url = os.getenv('BOOKING_URL')

apiURL = ('https://maker.ifttt.com/trigger/{evt}' + '/with/key/{key}').format(
    evt=os.getenv('IFTTT_EVENT_NAME'),
    key=os.getenv('IFTTT_WEB_HOOK_KEY'),
)


def goooo():

    browser.get(url)

    for xpath in ['/html/body/div[2]/form/div[1]/div/div/div/h4[1]/span[1]/input',
                  '/html/body/div[2]/form/div[1]/div/div/div/h4[2]/span[3]/input',
                  '/html/body/div[2]/form/div[1]/div/div/div/h4[3]/span[1]/input',
                  '/html/body/div[2]/form/div[1]/div/div/div/div/button']:

        next_button = browser.find_element_by_xpath(xpath)
        next_button.click()

    time.sleep(1)

    browser.execute_script("$('.TimeTableData').show()")

    time.sleep(1)

    print('return_', int(browser.execute_script(
        "return $('#HospDT').children().length") + 1))
    count = ''

    for i in range(1, int(browser.execute_script("return $('#HospDT').children().length") + 1)):
        print('HospDT_ Date_ ', i)
        # print('return_' , "return $('#tb" + str(i) + " > table > tbody').children()")

        for row in range(1, int(browser.execute_script("return $('#tb" + str(i) + " > table > tbody').children().length")) + 1):
            _date = browser.execute_script(
                "return $('#tb" + str(i) + " > table > tbody > tr:nth-child(" + str(row) + ") > td:nth-child(2)').text()")
            _time = browser.execute_script(
                "return $('#tb" + str(i) + " > table > tbody > tr:nth-child(" + str(row) + ") > td:nth-child(3)').text()")
            count = browser.execute_script(
                "return $('#tb" + str(i) + " > table > tbody > tr:nth-child(" + str(row) + ") > td:nth-child(4)').text()")

            print('row', row, '數量', count, count.isdigit())

            if(count.isdigit()):
                browser.execute_script(
                    "$('#tb" + str(i) + " > table > tbody > tr:nth-child(" + str(row) + ") > td:nth-child(1) > input').click()")
                r = req.post(
                    apiURL, json={"value1": url, "value2": _date, "value3": _time})
                break
        else:
            continue  # only executed if the inner loop did NOT break
        break

    if(count.isdigit()):
        ROCID = browser.find_element_by_xpath(
            '/html/body/div[2]/form/div[2]/div/div/div[5]/div[1]/input')
        ROCID.clear()
        ROCID.send_keys(UserROCID)

        PHONE = browser.find_element_by_xpath(
            '/html/body/div[2]/form/div[2]/div/div/div[5]/div[2]/table/tbody/tr/td/input')
        PHONE.clear()
        PHONE.send_keys(UserPhone)

        NAME = browser.find_element_by_xpath(
            '/html/body/div[2]/form/div[2]/div/div/div[5]/div[3]/input')
        NAME.clear()
        NAME.send_keys(UserName)

        with open('filename.png', 'wb') as file:
            file.write(browser.find_element_by_xpath(
                '/html/body/div[2]/form/div[2]/div/div/div[5]/div[6]/img').screenshot_as_png)

        pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
        config = '--psm 8 --oem 3 -c tessedit_char_whitelist=0123456789'
        text = pytesseract.image_to_string(
            Image.open(r'.\filename.png'), config=config)

        if re.search(r'\d+', text) is not None:
            text = int(re.search(r'\d+', text).group())
            print("text_ ", text)

        AGREE = browser.find_element_by_xpath(
            '/html/body/div[2]/form/div[2]/div/div/div[5]/div[8]/input')
        AGREE.click()

        browser.execute_script("$('#authCode').val(" + str(text) + ")")
        time.sleep(5)


while True:
    goooo()
    time.sleep(1)
