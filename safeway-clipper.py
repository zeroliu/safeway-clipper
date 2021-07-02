#! /usr/bin/env python3

import time
import click
from loguru import logger
from selenium import webdriver


# Firefox Web Driver: https://github.com/mozilla/geckodriver/releases
def get_firefox_web_driver(driver: str, headless: bool) -> webdriver:
    if headless:
        options = webdriver.FirefoxOptions()
        options.add_argument('-headless')
        d = webdriver.Firefox(
            executable_path=driver,
            options=options
        )
        return d
    else:
        d = webdriver.Firefox(
            executable_path=driver
        )
        d.set_window_size(1440, 900)
        return d


# Chrome Web Driver: https://chromedriver.chromium.org
# Edge Web Driver: https://developer.microsoft.com/en-us/microsoft-edge/tools/webdriver
def get_web_driver(browser: str, driver: str, headless: bool) -> webdriver:
    if browser.lower() == 'firefox':
        return get_firefox_web_driver(driver, headless)
    else:
        logger.error(f'{browser} browser not supported')
        exit(-1)


def safeway_login(driver: webdriver, username, password) -> None:
    login_url = 'https://www.safeway.com/account/sign-in.html'

    logger.info(f'Login on {login_url} ...')
    driver.get(login_url)
    time.sleep(2)

    # enter login credentials
    driver.find_element_by_id('label-email').send_keys(username)
    driver.find_element_by_id('label-password').send_keys(password)

    # login
    driver.find_element_by_id('btnSignIn').click()

    time.sleep(5)

    # verify login by checking text in 'sign-in-profile-text' button
    logger.info(f'Verifying login status ...')
    login_button = driver.find_element_by_class_name('menu-nav__profile-button-sign-in-up')

    if login_button.text == 'Sign In / Up':
        logger.error('Login failed.')
        driver.close()
        exit(-1)
    else:
        logger.info('Login success.')


def safeway_clip_coupons(driver: webdriver) -> None:
    offer_url = 'https://www.safeway.com/justforu/coupons-deals.html'

    logger.info(f'Start clipping coupons on {offer_url} ...')
    driver.get(offer_url)

    time.sleep(5)

    scroll_count = 12
    for i in range(scroll_count):
        load_more_btn = driver.find_element_by_xpath('//button[text()="Load more"]')
        load_more_btn.click()
        time.sleep(1)

    try:
        add_buttons = driver.find_elements_by_xpath('//button[text()="Clip Coupon"]')
        logger.info(f'Found {len(add_buttons)} coupons')
    except:
        logger.exception('No coupons found')
        driver.close()
        exit(0)
        return

    coupons_clipped = 0
    for btn in add_buttons:
        if btn.text.lower() == 'clip coupon':
            driver.execute_script('arguments[0].click();', btn)
            coupons_clipped += 1
            time.sleep(0.5)

    logger.info(f'clipped {coupons_clipped} coupons')


@click.command()
@click.option('-b', '--browser', default='firefox', help='Browser')
@click.option('-d', '--driver', default='firefox-driver.exe', help='Web driver binary')
@click.option('--headless/--no-headless', default=True, help='Headless mode')
@click.option('-u', '--username', required=True, help='Safeway username')
@click.option('-p', '--password', required=True, help='Safeway password')
def main(
        browser: str,
        driver: str,
        headless: bool,
        username: str,
        password: str
):
    d = get_web_driver(browser, driver, headless)
    safeway_login(d, username, password)
    safeway_clip_coupons(d)
    d.close()


if __name__ == '__main__':
    main()
