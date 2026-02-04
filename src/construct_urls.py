from src.login_selenium import PageNavigator
from src.logger import SingletonLogger
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.wait import WebDriverWait
import sys
import os
import pandas as pd

logger = SingletonLogger().get_logger()
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class ConstructUrls:
    """
    Manages interactions with the Baselinker inventory page.
    """
    INVENTORY_URL = "https://panel-d.baselinker.com/inventory_products"
    NUMBER_ID_CSV_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + "/data/csv/numer_id.csv"

    def read_product_ids_from_csv(self):
        try:
            df = pd.read_csv(self.NUMBER_ID_CSV_PATH)
            product_ids = df.iloc[:, 0].astype(str).values
            return product_ids, df
        except Exception as e:
            logger.error(f"Couldn't read csv file: {e}")
            raise

    def construct_products_urls(self, product_ids):
        try:
            product_urls = [f"{self.INVENTORY_URL}#product:{id}#tab:information" for id in product_ids]
            logger.debug("Successfully constructed all urls")
            return product_urls
        except Exception as e:
            logger.error(f"Couldn't construct products urls: {e}")
            raise

    def run(self):
        """
        Executes the sequence of actions on the inventory page.
        """
        product_ids, df = self.read_product_ids_from_csv()
        product_urls = self.construct_products_urls(product_ids)

        return product_urls, df 
    

        


