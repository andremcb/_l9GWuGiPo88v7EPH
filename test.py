import os
import re
import unittest

import selenium
from selenium import webdriver
from selenium.webdriver import DesiredCapabilities
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class TestAcceptanceStripe(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(TestAcceptanceStripe, self).__init__(*args, **kwargs)
        with open("order.html", "r") as file_descriptor:
            self.dom_str = file_descriptor.read()

    def test_acceptance_stripe_public_key_has_been_set(self):
        """Check if Stripe key was defined."""
        pattern = re.compile(r"Stripe\('pk_test_\w{24}'\);", re.I | re.M)
        res = re.search(pattern, self.dom_str)
        self.assertTrue(res.group())

    def test_acceptance_stripe_script_has_been_inserted(self):
        """Check if Stripe script was inserted."""
        pattern = re.compile(
            r'<script src="https://js.stripe.com/v3"></script>', re.I | re.M
        )
        res = re.search(pattern, self.dom_str)
        self.assertTrue(res.group())

    def test_acceptance_checkout_button_was_instantiated(self):
        """Check if checkout button was captured."""
        pattern = re.compile(
            r"document.getElementById\('checkout-button-sku_\w{14}'\);", re.I | re.M
        )
        res = re.search(pattern, self.dom_str)
        self.assertTrue(res.group())

    def test_acceptance_sku_item_defined_on_checkout(self):
        """Check if checkout button was captured."""
        pattern = re.compile(
            r"items: \[\{sku: 'sku_\w{14}', quantity: \d{1}\}\]", re.I | re.M
        )
        res = re.search(pattern, self.dom_str)
        self.assertTrue(res.group())

    # Check if redirectToCheckout function call is present
    def test_acceptance_redirect_to_checkout(self):
        pattern = re.compile(r"stripe.redirectToCheckout", re.I | re.M)
        res = re.search(pattern, self.dom_str)
        self.assertTrue(res.group())

    # Check if successUrl redirects to order_success.html
    def test_acceptance_success_url(self):
        pattern = re.compile(
            r"successUrl: \'(http|https)://(.*)/order_success.html\?session_id=\{CHECKOUT_SESSION_ID\}\'",
            re.I | re.M,
        )
        res = re.search(pattern, self.dom_str)
        self.assertTrue(res.group())

    # Check if cancelUrl redirects to order.html
    def test_acceptance_cancel_url(self):
        pattern = re.compile(
            r"cancelUrl: \'(http|https)://(.*)/order.html\'", re.I | re.M
        )
        res = re.search(pattern, self.dom_str)
        self.assertTrue(res.group())


class AssessmentTestCases(unittest.TestCase):
    def setUp(self):

        with open("order.html", "r") as file_descriptor:
            self.dom_str = file_descriptor.read()

        CHROMEDRIVER_PATH = '/usr/local/bin/chromedriver'
        WINDOW_SIZE = "1920,1080"

        options = selenium.webdriver.ChromeOptions()
        options.headless = True
        options.add_argument("--window-size=%s" % WINDOW_SIZE)

        self.driver = webdriver.Chrome(
            executable_path=CHROMEDRIVER_PATH,
            options=options
        )

    def _get_button_id(self):
        pattern = re.compile(
            r"\('checkout-button-sku_\w{14}'\);", re.I | re.M
        )
        res = re.search(pattern, self.dom_str)
        return res.group().split("'")[1]

    def _get_url(self):
        pattern = re.compile(
            r"cancelUrl: \'(http|https)://(.*)/order.html\'", re.I | re.M
        )
        res = re.search(pattern, self.dom_str)
        return ":".join(res.group().split(": ")[1:]).strip("'")

    def test_assessment_successful_payment_on_the_checkout_page_redirects_to_order_html(
        self
    ):
        self.driver.get('http://localhost:8000/order.html')
        elem = self.driver.find_element_by_id('checkout-button-sku_Fg6RQOAN2Tu58m')
        elem.click()

        wait = WebDriverWait(self.driver, 20)

        email_elem = wait.until(EC.presence_of_element_located((By.ID, "email")))

        cardnum_elem = self.driver.find_element_by_id("cardNumber")
        cardexp_elem = self.driver.find_element_by_id("cardExpiry")
        cardcvc_elem = self.driver.find_element_by_id("cardCvc")
        cardname_elem = self.driver.find_element_by_id("billingName")

        email_elem.send_keys("assessment@test.com.br")
        cardnum_elem.send_keys("4242424242424242")
        cardexp_elem.send_keys("0439")
        cardcvc_elem.send_keys("424")
        cardname_elem.send_keys("Selenium Test WebDriver")

        confirm_elem = self.driver.find_element_by_xpath("//button[@type='submit']")
        confirm_elem.click()

        session_id_elem = wait.until(
            EC.presence_of_element_located((By.ID, "sessionId"))
        )
        self.assertIn("order_success.html", self.driver.current_url)
        self.assertTrue(session_id_elem.text)

    def tearDown(self):
        self.driver.close()


if __name__ == "__main__":
    unittest.main()
