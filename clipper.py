#! /usr/bin/env python3

"""Safeway Coupon Clipper using Selenium

Uses a Selenium web driver Firefox Gecko or Chrome browser to clip Safeway
coupons. Relies on passed username and password else defualt sto environment
variables. Offers page is dynamically loaded, so this script keeps track of
new found coupons after each scroll and can be limited.  default behavior is
to scroll until no more un-clipped coupons are found.

This script is dumb, and relies on the the css Class of coupons and their
buttons to identify click targets.  As the css changes, this script will need
to be updated.

Writes data log of the run datetime, number of coupons clipped, and the number
of coupons found.  Keep in mind that this number of coupons found may be
truncated from the total number of available coupons by the scroll limit.

Use CalVer versioning from here https://calver.org/

"""

__authors__ = ["Sam Gutentag"]
__email__ = "developer@samgutentag.com"
__maintainer__ = "Sam Gutentag"
__version__ = "2020.07.24dev"
# "dev", "alpha", "beta", "rc1"


import argparse
import logging
import os
import time
from datetime import datetime
from selenium import webdriver

MIN_CHROME_DRIVER_VERSION = 79
MIN_GECKO_DRIVER_VERSION = 26


def setup_logging():
    """Set up  logging filename and ensure logging directory exists."""
    # name of this file
    this_file = os.path.splitext(os.path.basename(__file__))[0]

    log_datetag = datetime.today().strftime("%Y%m%d")

    # construct name of log file
    log_file = f"{this_file}_logfile_{log_datetag}.txt"

    # ensure logging directory exists
    this_dir = os.path.dirname(os.path.realpath(__file__))
    log_dir = os.path.join(this_dir, "logs")
    if not os.path.isdir(log_dir):
        os.makedirs(log_dir)

    # logging settings
    logging.basicConfig(filename=os.path.join(log_dir, log_file),
                        level=logging.INFO,
                        format="%(asctime)s - %(levelname)s - %(message)s")

    # logging.disable(logging.CRITICAL)
    logging.info("\n\n\n\n")
    logging.info("-" * 80)


def parse_arguments():
    """Parse arguments from command line.

    Returns:
        args (dict): dictionary of input command line arguments

    """

    logging.info("parsing command line arguements")
    parser = argparse.ArgumentParser(description=("Clipping coupons from "
                                                  "Safeway.com Just4U page."))

    parser.add_argument("-headless", "--headless_mode", action="store_true",
                        required=False, default=False,
                        help="run in headless browser mode.")

    parser.add_argument("-driver", "--which_driver", dest="which_driver",
                        required=False, default="gecko",
                        help="Use gecko or chrome driver, gecko default.")

    parser.add_argument("-u", "--username", dest="username",
                        required=False,
                        default=os.environ.get("SAFEWAY_USERNAME"),
                        help=("user login, defaults to env variable "
                              "'SAFEWAY_USERNAME'."))

    parser.add_argument("-p", "--password", dest="password",
                        required=False,
                        default=os.environ.get("SAFEWAY_PASSWORD"),
                        help=("user password, defaults to env variable "
                              "'SAFEWAY_PASSWORD'."))

    args = vars(parser.parse_args())
    logging.info(f"arguments: {args}")

    return args


def get_webdriver(which_driver="gecko", headless=False):
    """Initialize web driver.

    Will use the Gecko web driver unless an "chrome" is passed to
    the "which_driver" argument.

    Args:
        which_driver (string): use either gecko or chrome webdriver.
        headless (bool): initialize webdriver in headless mode.

    Returns:
        driver (web driver object): -1 on failure

    Raises:
        Exception: something wrong with web driver

    """
    driver_path = os.path.dirname(os.path.realpath(__file__))

    # Gecko Driver Usage
    if which_driver == "gecko":
        geckodriver = os.path.join(driver_path,
                                   "webdrivers",
                                   f"geckodriver_{MIN_GECKO_DRIVER_VERSION}")
        logging.info(f"using webdriver version {MIN_GECKO_DRIVER_VERSION}")
        logging.info(f"webdriver located at: {geckodriver}")

        try:

            if headless:
                logging.info("running headless")

                options = webdriver.FirefoxOptions()
                options.add_argument("-headless")

                logging.info("initializing headless Gecko webdriver")
                driver = webdriver.Firefox(executable_path=geckodriver,
                                           firefox_options=options,
                                           service_log_path="/dev/null")

                # specify webdriver window resolution, helps clicking
                driver.set_window_size(1440, 900)

            else:

                logging.info("initializing Gecko webdriver")
                driver = webdriver.Firefox(executable_path=geckodriver,
                                           service_log_path="/dev/null")

        except Exception as err:
            logging.debug(err)
            return -1
        logging.info(f"geckodriver ready.")
        return driver

    # ChromeDriver Usage
    else:
        chromedriver = os.path.join(driver_path,
                                    "webdrivers",
                                    f"chromedriver_{MIN_CHROME_DRIVER_VERSION}")

        logging.info(f"using webdriver version {MIN_CHROME_DRIVER_VERSION}")
        logging.info(f"webdriver located at: {chromedriver}")

        try:

            if headless:
                logging.info("running headless")
                options = webdriver.ChromeOptions()
                options.add_argument("headless")
                logging.info("initializing headless Chrome webdriver")
                driver = webdriver.Chrome(chromedriver, options=options,
                                          service_log_path="/dev/null")

                # specify webdriver window resolution, helps clicking
                driver.set_window_size(1440, 900)

            else:

                logging.info("initializing Chrome webdriver")
                driver = webdriver.Chrome(chromedriver,
                                          service_log_path="/dev/null")

        except Exception as err:
            logging.debug(err)
            return -1

        logging.info(f"chromedriver ready.")
        return driver


def safeway_login(driver, username, password):
    """Log in to safeway site.

    Verifies login success by searching for a "Sign In/Up" button. If
    this button is not found, assumes login was successful.

    Args:
        driver (webdriver): selenium webdriver session
        username (string): username for login authentication
        password (string): password for login authentication

    Returns:
        result (int): 0 on success, -1 on failure

    """
    logging.info("navigating to login page...")
    login_page = "https://www.safeway.com/account/sign-in.html"

    driver.get(login_page)
    time.sleep(3)

    # refresh the page, helps slow loading
    logging.info("refresh page to ensure all elements have loaded")
    driver.refresh()
    time.sleep(3)

    # enter login credentials
    logging.info("filling in username field")
    username_field = driver.find_element_by_id("label-email")
    username_field.send_keys(username)

    logging.info("filling in password field")
    password_field = driver.find_element_by_id("label-password")
    password_field.send_keys(password)

    # attempt to login
    logging.info("attempting to log in")
    login_button = driver.find_element_by_id("btnSignIn")
    login_button.click()

    # verify login by checking text in "sign-in-profile-text" button
    time.sleep(10)
    logging.info("verifying login status...")
    login_button = driver.find_element_by_class_name("menu-nav__profile-button-sign-in-up")

    if login_button.text == "Sign In / Up":
        logging.critical("ERROR: Not logged in correctly")
        return -1
    else:
        logging.info("success!")
        return 0


def clip_coupons(driver, headless_mode=False):
    """Navigate to offer page and collect coupon offers.

    First scrolls page to load more offers, will scroll 10 times or until no
    new clip buttons are exposed, whichever is later. Once done scrolling will
    start clipping found coupons with a 1 second pause between clicks to not
    present as a bot.

    Args:
        driver (webdriver): selenium webdriver session

    Returns:
        (coupons_clipped, len(coupons_found)) (tuple of integers): count of
            coupons clipped and coupons scanned for clipping

    """
    logging.info("starting coupon clipping")
    offer_url = "https://www.safeway.com/justforu/coupons-deals.html"

    logging.info(f"navigating to offers url: {offer_url}")
    driver.get(offer_url)

    time.sleep(3)

    # scroll page to load all offers
    keep_scrolling = True
    add_buttons_found = 0
    scrolls_remaining = 10

    # coupon discovery
    while keep_scrolling or scrolls_remaining > 0:

        scrolls_remaining -= 1

        # # uncomment this if requiring a literal scroll
        # driver.execute_script(
        #     "window.scrollTo(0, document.body.scrollHeight);"
        # )

        # scroll until the load more button goes away
        try:
            load_more_btn = driver.find_elements_by_class_name("load-more")[0]
            load_more_btn.click()
            time.sleep(5)

            # get add button count
            btn_class = "grid-coupon-clip-button"
            add_buttons = driver.find_elements_by_class_name(btn_class)
            add_buttons = [b for b in add_buttons if b.text.lower() == "add"]
            add_button_count = len(add_buttons)

            if add_button_count > add_buttons_found:
                add_buttons_found = add_button_count
            else:
                keep_scrolling = False

        except Exception:
            keep_scrolling = False

    # collect coupons
    coupons_found = driver.find_elements_by_class_name("grid-coupon-container")
    logging.info(f"found {len(coupons_found)} coupons.")

    coupons_clipped = 0

    # clipping coupons
    for idx, coupon in enumerate(coupons_found):

        # get add button
        add_button_class = "grid-coupon-btn"
        add_button = coupon.find_elements_by_class_name(add_button_class)[0]
        if add_button.text.lower() == "add":

            # get description
            description_class = "grid-coupon-description-text-title"
            description = coupon.find_elements_by_class_name(description_class)

            savings_class = "grid-coupon-heading-offer-price"
            savings = coupon.find_elements_by_class_name(savings_class)

            try:
                savings_text = savings[0].text
                savings_text = savings_text.decode("utf-8").strip()
                description_text = description[0].text
                description_text = description_text.decode("utf-8").strip()
                logging.info(f"\t[{idx+1:3} of {len(coupons_found):3}]\t{savings_text:20}\t{description_text}")
            except Exception:
                pass

            # click add button
            try:
                driver.execute_script("arguments[0].click();", add_button)
                coupons_clipped += 1
                time.sleep(1)
            except Exception:
                pass

    return (coupons_clipped, len(coupons_found))


def clip_counter(coupons_clipped, coupons_found):
    """Record to file the number of coupons clipped.

    Writes date lines to a file in the ./data/clipper_datafile_yyyyMM.csv
    format of the current year and month. Appends new line each time and
    creates a ./data/ directory if it does not already exist.

    Args:
        coupons_clipped (int): number of coupons clipped
        coupons_found (int): total number of coupons found

    """

    # name of this file
    this_file = os.path.splitext(os.path.basename(__file__))[0]
    log_datetag = datetime.today().strftime("%Y%m")

    # construct name of log file
    data_file = f"{this_file}_datafile_{log_datetag}.csv"

    # ensure logging directory exists
    logging.info("ensuring data directory exists")
    this_dir = os.path.dirname(os.path.realpath(__file__))
    data_dir = os.path.join(this_dir, "data")
    if not os.path.isdir(data_dir):
        os.makedirs(data_dir)

    data_filepath = os.path.join(data_dir, data_file)

    # append to datafile
    logging.info(f"appending data record to datefile {data_filepath}")

    log_datetime = datetime.today().strftime("%Y-%m-%d %H:%m:%S")
    data_line = f"{log_datetime},{coupons_clipped},{coupons_found}\n"

    new_file = not os.path.exists(data_filepath)

    with open(data_filepath, "a") as f:
        if new_file:
            f.write("datetime,coupons_clipped,coupons_found\n")
        f.write(data_line)


def clipper():
    """Primary function to clip coupons."""
    args = parse_arguments()

    logging.info("getting web driver")
    driver = get_webdriver(which_driver=args["which_driver"],
                           headless=args["headless_mode"])

    if driver == -1:
        logging.critical(f"Something went wrong initializing {args['which_driver']} webdriver... quitting.")
        return -1

    login = safeway_login(driver,
                          username=args["username"],
                          password=args["password"])
    if login == -1:
        logging.critical("Something went wrong logging in... quitting.")
        driver.quit()
        return -1

    _clipped, _found = clip_coupons(driver,
                                    headless_mode=args["headless_mode"])
    if _clipped == -1:
        logging.critical("Something went wrong clipping coupons... quitting.")
        driver.quit()
        return -1

    # record clip counter
    clip_counter(_clipped, _found)

    driver.quit()
    logging.info("complete")


if __name__ == "__main__":
    setup_logging()
    clipper()
