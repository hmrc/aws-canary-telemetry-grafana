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

TIMEOUT_SECONDS = 10


async def main():
    url = GRAFANA_URL
    browser = syn_webdriver.Chrome()
    browser.set_viewport_size(1024, 768)

    # Set synthetics configuration
    synthetics_configuration.set_config(
        {
            "screenshot_on_step_start": False,
            "screenshot_on_step_success": True,
            "screenshot_on_step_failure": True,
        }
    )

    def navigate_to_page():
        browser.implicitly_wait(TIMEOUT_SECONDS)
        browser.get(url)

    def navigate_to_page_two():
        browser.implicitly_wait(TIMEOUT_SECONDS)
        browser.get(
            "https://grafana.internal-lab02.telemetry.tax.service.gov.uk/d/Telemetry_test_page/"
        )

    await syn_webdriver.execute_step("navigateToUrl", navigate_to_page)

    # Execute customer steps
    def customer_actions_1():
        logger.debug("Enter username")
        browser.find_element_by_xpath(
            '//*[@id="reactRoot"]/div/main/div[3]/div/div[2]/div/div/form/div[1]/div[2]/div/div/input'
        ).send_keys(GRAFANA_USERNAME)

    await syn_webdriver.execute_step("input", customer_actions_1)

    def customer_actions_2():
        logger.debug("Enter password")
        browser.find_element_by_xpath("//*[@id='current-password']").send_keys(
            GRAFANA_PASSWORD
        )

    await syn_webdriver.execute_step("input", customer_actions_2)

    def customer_actions_3():
        logger.debug("Click to login")
        browser.find_element_by_xpath(
            "/html/body/div[1]/div/main/div[3]/div/div[2]/div/div/form/button"
        ).click()

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
