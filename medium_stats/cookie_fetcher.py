from medium_stats.utils import check_dependencies_missing

missing = check_dependencies_missing()
if missing:
    print(missing)
    imperative = 'Please install by executing "pip install medium_stats[selenium]"'
    raise ImportError(f'Dependencies missing: {missing}. \n{imperative}')

from selenium.webdriver import Chrome
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import configparser
import os

sign_in_url = 'https://medium.com/m/signin?operation=login&redirect=https%3A%2F%2Fmedium.com%2F'

chrome_options = Options()  
chrome_options.add_argument("--headless")

class MediumAuthorizer:

    def __init__(self, handle, email, password):
        
        self.handle = handle
        self.email = email
        self.password = password
        
    def sign_in(self, headless=True):
        
        print('\nSigning In and Getting Cookies...')
        driver = Chrome(ChromeDriverManager().install(), options=chrome_options)
        driver.get(sign_in_url)

        google_auth = driver.find_element_by_xpath('//button[@data-action="google-auth"]')
        google_auth.click()

        form1_locator = (By.TAG_NAME, 'form')
        email_input = WebDriverWait(driver, 10).until(EC.visibility_of_element_located(form1_locator))
        
        email_input.find_element_by_xpath('//input[@type="email"]').send_keys(self.email)
        if headless:
            email_input.find_element_by_id('next').click()
            form2_locator = (By.ID, 'Passwd')
        else:
            # Non-headless versions might be v2?
            email_input.find_element_by_xpath('//input[@role="button"]').click()
            form2_locator = (By.XPATH, '//form[@action="/signin/v2/challenge/password/empty"]')
        
        password_input = WebDriverWait(driver, 10).until(EC.presence_of_element_located(form2_locator))
        password_input.find_element_by_xpath('//input[@type="password"]').send_keys(self.password)
        
        if headless:
            driver.find_element_by_id('signIn').click()
        else:
            driver.find_element_by_id('passwordNext').click()

        medium_meta = (By.XPATH, '//meta[@property="og:url" and @content="https://medium.com/"]')
        try:
            WebDriverWait(driver, 10).until(EC.presence_of_element_located(medium_meta))
        except:
            raise ValueError('Authentication failed - incorrect email & password combination')
        
        self.driver = driver

    def save_cookies(self, path):
        print('\nExtracting session cookies...', end='\n\n')
        cookies = self.driver.get_cookies()
        config = configparser.ConfigParser()
        config[self.handle] = {}
        for c in cookies:
            if c['name'] in ['sid', 'uid']:
                k = c['name']
                config[self.handle][k] = c['value']
        ## write cookies out to .ini file
        print('Writing cookies to credentials file...')
        with open(path, 'w') as f:
            config.write(f)

if __name__ == "__main__":
    pass