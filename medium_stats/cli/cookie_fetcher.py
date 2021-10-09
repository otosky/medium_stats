from medium_stats.utils import check_dependencies_missing

missing = check_dependencies_missing()
if missing:
    print(missing)
    imperative = 'Please install by executing "pip install medium_stats[selenium]"'
    raise ImportError(f"Dependencies missing: {missing}. \n{imperative}")

import configparser
import logging

from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

logger = logging.getLogger(__name__)

sign_in_url = "https://medium.com/m/signin?operation=login&redirect=https%3A%2F%2Fmedium.com%2F"

chrome_options = Options()
chrome_options.add_argument("--headless")


class MediumAuthorizer:
    def __init__(self, handle, email, password):

        self.handle = handle
        self.email = email
        self.password = password
        self.driver = None

    def _go_to_password_prompt(self, input_form, headless: bool):
        if headless:
            input_form.find_element_by_id("next").click()
        else:
            input_form.find_element_by_xpath('//input[@role="button"]').click()

    def _click_sign_in(self, driver, headless):
        password_element_id = "signIn" if headless else "passwordNext"
        driver.find_element_by_id(password_element_id).click()

    def _get_password_locator(self, headless):
        return (By.ID, "Passwd") if headless else (By.XPATH, '//form[@action="/signin/v2/challenge/password/empty"]')

    def sign_in(self, headless=True):

        print("\nSigning In and Getting Cookies...")
        driver = Chrome(ChromeDriverManager().install(), options=chrome_options)
        driver.get(sign_in_url)

        google_auth = driver.find_element_by_xpath('//button[@data-action="google-auth"]')
        google_auth.click()

        email_form_visible = expected_conditions.visibility_of_element_located((By.TAG_NAME, "form"))
        email_input_form = WebDriverWait(driver, 10).until(email_form_visible)
        email_input_form.find_element_by_xpath('//input[@type="email"]').send_keys(self.email)
        self._go_to_password_prompt(email_input_form, headless)

        password_form_visible = expected_conditions.visibility_of_element_located(self._get_password_locator(headless))
        password_input_form = WebDriverWait(driver, 10).until(password_form_visible)
        password_input_form.find_element_by_xpath('//input[@type="password"]').send_keys(self.password)
        self._click_sign_in(driver, headless)

        try:
            # if the next page loads with meta content you've successfully authenticated
            medium_meta = (
                By.XPATH,
                '//meta[@property="og:url" and @content="https://medium.com/"]',
            )
            WebDriverWait(driver, 10).until(expected_conditions.presence_of_element_located(medium_meta))
        except Exception:
            raise ValueError("Authentication failed - incorrect email & password combination")

        self.driver = driver

    def get_cookies(self, headless=True):
        if not self.driver:
            logger.info("Driver not yet initialized - signing into Medium...")
            self.sign_in(headless)

        cookies = self.driver.get_cookies()
        ids = {c["name"]: c["value"] for c in cookies if c["name"] in {"sid", "uid"}}
        if len(ids) < 2:
            raise ValueError("Cookies not found")

        return ids

    def save_cookies(self, path, headless=True):
        logger.info("Extracting session cookies...")
        config = configparser.ConfigParser()
        config[self.handle] = self.get_cookies(headless)

        logger.info("Writing cookies to credentials file...")
        with open(path, "w") as f:
            config.write(f)
