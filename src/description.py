import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import functools
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

from src.logger import SingletonLogger
from src.login_selenium import PageNavigator
from src.ai_implementation import ProductDescriptionGenerator
from src.ai_implementation import GeneratedDescription
import time 
from selenium.common.exceptions import ElementNotInteractableException

logger = SingletonLogger().get_logger()


def log_exceptions(func):
    """A decorator that wraps a function in a try-except block and logs exceptions."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            result = func(*args, **kwargs)
            logger.debug(f"Successfully executed '{func.__name__}'.")
            return result
        except Exception as e:
            logger.error(f"Error executing '{func.__name__}': {e}")
            raise
    return wrapper


class ChangeDescription:
    """
    Manages interactions with the product description page.

    This class encapsulates Selenium-based actions to automate the process of
    updating product descriptions with AI-generated content.
    """

    class Locators:
        """
        Defines locators for web elements on the product page.
        """
        OPEN_DESCRIPTION_SECTION = (By.CSS_SELECTOR, "div.panel-group:nth-child(2) > div:nth-child(1) > div:nth-child(1)")
        MAIN_DESCRIPTION_TEXTAREA = (By.ID, "txt|-2|db|0|pl")
        SECOND_DESCRIPTION_TEXTAREA = (By.ID, "txt|-3|db|0|pl")
        SAVE_CHANGES_BUTTON = (By.CSS_SELECTOR, "button.footer_control:nth-child(9)")

    def __init__(self, driver: WebDriver, wait: WebDriverWait, url: str):
        """
        Initializes the ProductPage with a WebDriver, WebDriverWait, and a URL.
        """
        self.driver = driver
        self.wait = wait
        self.url = url

    @log_exceptions
    def open_description_section(self):
        """Opens the description editing section on the page."""
        button = self.wait.until(EC.element_to_be_clickable(self.Locators.OPEN_DESCRIPTION_SECTION))
        self.driver.execute_script("arguments[0].click()", button)

    def get_main_description(self) -> str:
        """
        Retrieves the text from the main description field.
        """
        try:
            description_field = self.wait.until(EC.presence_of_element_located(self.Locators.MAIN_DESCRIPTION_TEXTAREA))
            logger.debug("Scrolled into view ")
            description_text = description_field.get_attribute('value')
            print(description_text)
            time.sleep(1)
            description_field.clear()
            logger.debug("Cleared text")
            logger.debug(f"Successfully extracted description")
            return description_text
        except ElementNotInteractableException as e:
            description_field = self.wait.until(EC.presence_of_element_located(self.Locators.MAIN_DESCRIPTION_TEXTAREA))
            logger.debug("Scrolled into view ")
            description_text = description_field.get_attribute('value')
            print(description_text)
            time.sleep(2)
            description_field.clear()
            logger.debug("Cleared text")
            logger.debug(f"Successfully extracted description")
            return description_text 


    @log_exceptions
    def clear_second_description(self):
        """Clears the text from the second description field."""
        sec_description_field = self.wait.until(EC.presence_of_element_located(self.Locators.SECOND_DESCRIPTION_TEXTAREA))
        sec_description_field.location_once_scrolled_into_view
        sec_description_field.clear()

    @log_exceptions
    def get_generated_response(self, description: str) -> GeneratedDescription:
        """
        Generates a new product description using the AI implementation.
        """
        return ProductDescriptionGenerator(description=description).generate()

    @log_exceptions
    def paste_main_description(self, main_description: str):
        """
        Pastes the provided text into the main description field.
        """
        description_field = self.wait.until(EC.presence_of_element_located(self.Locators.MAIN_DESCRIPTION_TEXTAREA))
        description_field.send_keys(main_description)

    @log_exceptions
    def paste_second_description(self, second_description: str):
        """
        Pastes the provided text into the second description field.
        """
        description_field = self.wait.until(EC.presence_of_element_located(self.Locators.SECOND_DESCRIPTION_TEXTAREA))
        description_field.send_keys(second_description)

    @log_exceptions
    def click_save_changes_button(self):
        """Clicks the 'Save Changes' button."""
        save_button = self.wait.until(EC.element_to_be_clickable(self.Locators.SAVE_CHANGES_BUTTON))
        save_button.click()

    def run(self):
        """
        Executes the full workflow for updating a product description.
        """
        PageNavigator(self.driver, self.wait).navigate_to(self.url)
        self.open_description_section()
        original_description = self.get_main_description()
        self.clear_second_description()
        
        generated_content = self.get_generated_response(original_description)
        
        self.paste_main_description(generated_content.description)
        self.paste_second_description(generated_content.benefits)
        self.click_save_changes_button()