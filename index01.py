import pandas as pd
from bs4 import BeautifulSoup
import undetected_chromedriver as uc
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time

results = []
driver = None

def makeDriver():
    global driver
    co = uc.ChromeOptions()
    co.add_argument('--disable-infobars')
    co.add_argument('--disable-extensions')
    co.add_argument('--profile-directory=Default')
    # co.add_argument("--incognito")
    # co.add_argument("--headless")
    co.add_argument("--disable-plugins-discovery")
    co.add_argument("--start-maximized")
    co.add_argument("--no-sandbox")  # bypass OS security model
    co.add_argument("--disable-dev-shm-usage")
    co.add_argument("--disable-popup-blocking")
    co.add_argument('--disable-blink-features=AutomationControlled')

    driver = uc.Chrome(options=co)
    driver.maximize_window()
    try:
        driver.get('https://afgoerelsesdatabasen.dk/Soeg?search=%7B%22v%22:2,%22f%22:%22o-rison%22,%22p%22:%22c:!((c:!((da:Effective,go:0)),pk:status)),fsn:SearchResultFields,page:1,rvn:Liste,skip:0,slices:!t,snippets:!t,soo:(descending:!t,fieldName:date_release),take:15%22%7D')
        while len(driver.find_elements(By.CLASS_NAME, "search-item")) == 0 :
            time.sleep(0.5)
    except Exception as e:
        print(e)
        pass

def capture():
    while len(driver.find_elements(By.CLASS_NAME, "MuiTypography-root")) == 0 :
        time.sleep(0.5)
    title = driver.find_element(By.CLASS_NAME, 'MuiTypography-h1').text
    header = driver.find_element(By.XPATH, '//section/p[1]').text
    content = [];
    content_list = driver.find_elements(By.CLASS_NAME, "foldable-section-with-menu")
    for one in content_list:
        content.append({'title': one.find_element(By.CLASS_NAME, 'MuiAccordionSummary-root').text, "content": one.find_element(By.CLASS_NAME, 'MuiCollapse-container').text})

    result = {'title': title, 'header': header, 'content': content}
    driver.back
    time.sleep(1)
    return result
    # print(title)
    # print()
    # print(header)
    # print()
    # print(content)

def scrapList():
    while len(driver.find_elements(By.CLASS_NAME, "item-cursor-hand")) == 0 :
        time.sleep(0.5)

    url_list = []
    flag = False
    while True:
        all_list = driver.find_elements(By.CLASS_NAME, 'search-item-right')
        for one in all_list:
            url = one.find_element(By.TAG_NAME, 'a').get_property('href')
            date = one.find_elements(By.CLASS_NAME, 'col-xs-6')[1].find_elements(By.TAG_NAME, 'div')[1].text
            doctype = one.find_elements(By.CLASS_NAME, 'col-xs-6')[2].find_elements(By.TAG_NAME, 'div')[1].text
            if url in url_list:
                flag = True
                break
            url_list.append({'url': url, 'date': date, 'doctype': doctype})
        if flag == True:
            break
        
        driver.find_element(By.CLASS_NAME, 'pagination-next').find_element(By.TAG_NAME, 'a').click()
        while len(driver.find_elements(By.CLASS_NAME, "item-cursor-hand")) == 0 :
            time.sleep(0.5)

    # return url_list
    for url in url_list:
        driver.get(url)
        tmp = capture()
        for one in tmp:
            results.append(one)
        
    # print(url_list)

def doit(year):    
    global driver
    all_chkBox = driver.find_elements(By.TAG_NAME, "md-checkbox")
    for one in all_chkBox:
        txt = one.get_attribute('aria-label')
        # print(txt[-4:])
        if txt[-4:] == str(year):
            one.click()
            scrapList()

    # time.sleep(3)
    df = pd.DataFrame(results)
    df.to_json('data.json')

if __name__ == "__main__":    
    makeDriver()
    doit(2007)
    driver.quit()

