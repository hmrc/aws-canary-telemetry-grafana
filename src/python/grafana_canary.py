import os

import boto3
from aws_synthetics.common import synthetics_configuration
from aws_synthetics.common import synthetics_logger as logger
from aws_synthetics.selenium import synthetics_webdriver as syn_webdriver


SSM_PARAM = "/secrets/grafana/admin_password"

client = boto3.client("ssm")
response = client.get_parameter(Name=SSM_PARAM, WithDecryption=True)


GRAFANA_USERNAME = "admin"
GRAFANA_PASSWORD = response.get("Parameter").get("Value")
GRAFANA_URL = os.getenv("GRAFANA_URL")
GRAFANA_DASHBOARD_URL = os.getenv("GRAFANA_DASHBOARD_URL")
SCREENSHOT_ON_STEP_START = os.getenv("SCREENSHOT_ON_STEP_START", False)
SCREENSHOT_ON_STEP_SUCCESS = os.getenv("SCREENSHOT_ON_STEP_SUCCESS", False)
SCREENSHOT_ON_STEP_FAILURE = os.getenv("SCREENSHOT_ON_STEP_FAILURE", True)

TIMEOUT_SECONDS = 10


async def main():
    url = GRAFANA_URL
    url_to_dashboard = GRAFANA_DASHBOARD_URL
    browser = syn_webdriver.Chrome()
    browser.set_viewport_size(1024, 768)

    selector_login_name = "//input[@placeholder='email or username']"
    selector_login_password = "//*[@id='current-password']"  # nosec B105
    selector_login_button = (
        "/html/body/div/div[1]/main/div/div[3]/div/div[2]/div/div/form/button"
    )

    # Set synthetics configuration
    synthetics_configuration.set_config(
        {
            "screenshot_on_step_start": bool(SCREENSHOT_ON_STEP_START),
            "screenshot_on_step_success": bool(SCREENSHOT_ON_STEP_SUCCESS),
            "screenshot_on_step_failure": bool(SCREENSHOT_ON_STEP_FAILURE),
        }
    )

    def navigate_to_page():
        browser.implicitly_wait(TIMEOUT_SECONDS)
        browser.get(url)

    def navigate_to_page_two():
        browser.implicitly_wait(TIMEOUT_SECONDS)
        browser.get(url_to_dashboard)

    await syn_webdriver.execute_step("navigateToUrl", navigate_to_page)

    # Execute customer steps
    def customer_actions_1():
        logger.debug("Enter username")
        browser.find_element_by_xpath(selector_login_name).send_keys(GRAFANA_USERNAME)

    await syn_webdriver.execute_step("input", customer_actions_1)

    def customer_actions_2():
        logger.debug("Enter password")
        browser.find_element_by_xpath(selector_login_password).send_keys(
            GRAFANA_PASSWORD
        )

    await syn_webdriver.execute_step("input", customer_actions_2)

    def customer_actions_3():
        logger.debug("Click to login")
        browser.find_element_by_xpath(selector_login_button).click()

    await syn_webdriver.execute_step("redirection", customer_actions_3)
    await syn_webdriver.execute_step("navigateToUrl", navigate_to_page_two)

    def customer_actions_4():
        browser.find_element_by_class_name("markdown-html")

    await syn_webdriver.execute_step("click", customer_actions_4)
    logger.info("Canary successfully executed")


async def handler(event, context):
    # user defined log statements using synthetics_logger
    logger.info(f'Selenium Python workflow canary with context: "{context}"')
    logger.info(f'Event received from CloudWatch: "{event}"')
    return await main()
