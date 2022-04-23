#! /usr/bin/env python3

import time
import click
from loguru import logger
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service
from webdriver_manager.firefox import GeckoDriverManager


# Firefox Web Driver: https://github.com/mozilla/geckodriver/releases
from selenium.common.exceptions import NoSuchElementException


def get_firefox_web_driver(headless: bool) -> webdriver:
    if headless:
        options = webdriver.FirefoxOptions()
        options.add_argument('-headless')
        d = webdriver.Firefox(
            service=Service(GeckoDriverManager().install()),
            options=options
        )

        return d
    else:
        d = webdriver.Firefox(
            service=Service(GeckoDriverManager().install()),
        )
        d.set_window_size(1440, 900)
        return d


# Chrome Web Driver: https://chromedriver.chromium.org
# Edge Web Driver: https://developer.microsoft.com/en-us/microsoft-edge/tools/webdriver
def get_web_driver(browser: str, headless: bool) -> webdriver:
    if browser.lower() == 'firefox':
        return get_firefox_web_driver(headless)
    else:
        logger.error(f'{browser} browser not supported')
        exit(-1)


def safeway_login(driver: webdriver, username, password) -> None:
    login_url = 'https://www.safeway.com/account/sign-in.html'

    logger.info(f'Login on {login_url} ...')
    driver.get(login_url)
    time.sleep(2)

    # enter login credentials
    driver.find_element(by=By.ID, value='label-email').send_keys(username)
    driver.find_element(by=By.ID, value='label-password').send_keys(password)

    # login
    driver.find_element(by=By.ID, value='btnSignIn').click()

    time.sleep(5)

    # verify login by checking text in 'sign-in-profile-text' button
    logger.info(f'Verifying login status ...')
    try:
        driver.find_element(by=By.CLASS_NAME, value='menu-nav__profile-button-sign-in-up')
        logger.info('Login success.')
    except NoSuchElementException:
        logger.error('Login failed.')
        driver.quit()
        exit(-1)


def safeway_clip_coupons(driver: webdriver) -> None:
    offer_url = 'https://www.safeway.com/justforu/coupons-deals.html'

    logger.info(f'Start clipping coupons on {offer_url} ...')
    driver.get(offer_url)

    time.sleep(5)

    scroll_count = 24
    for i in range(scroll_count):
        try:
            load_more_btn = driver.find_element(by=By.XPATH, value='//button[@class="btn load-more"]')
        except NoSuchElementException:
            break
        load_more_btn.click()
        time.sleep(1)

    try:
        add_buttons = driver.find_elements(by=By.XPATH, value='//button[@class="btn grid-coupon-btn btn-default"]')
        logger.info(f'Found {len(add_buttons)} coupons')
    except NoSuchElementException:
        logger.exception('No coupons found')
        driver.quit()
        exit(0)

    coupons_clipped = 0
    for btn in add_buttons:
        if btn.text.lower() == 'clip coupon':
            driver.execute_script('arguments[0].click();', btn)
            coupons_clipped += 1
            time.sleep(0.5)

    logger.info(f'clipped {coupons_clipped} coupons')


def safeway_get_coupons_details(driver: webdriver) -> None:
    driver.find_element(by=By.XPATH, value='//a[@class="grid-coupon-details-link"]')


@click.command()
@click.option('-b', '--browser', default='firefox', help='Browser')
@click.option('--headless/--no-headless', default=True, help='Headless mode')
@click.option('-u', '--username', required=True, help='Safeway username')
@click.option('-p', '--password', required=True, help='Safeway password')
def main(
        browser: str,
        headless: bool,
        username: str,
        password: str
):
    d = get_web_driver(browser, headless)
    safeway_login(d, username, password)
    safeway_clip_coupons(d)
    d.quit()


if __name__ == '__main__':
    main()
