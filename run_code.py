import sys
import os
import re
from dotenv import load_dotenv
from pydantic import BaseModel

from src.login_selenium import PracujLogin
from src.construct_urls import ConstructUrls
from src.description import ChangeDescription

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Constants
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
SUBDIRS = ["cookies", "csv"]
NUMBER_ID_RES_CSV_PATH = os.path.join(DATA_DIR, "csv", "numer_id_recorded.csv")


def create_data_directories():
    """Checks for the existence of the data directory and its subdirectories,
    and creates them if they don't exist."""
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)

    for subdir in SUBDIRS:
        subdir_path = os.path.join(DATA_DIR, subdir)
        if not os.path.exists(subdir_path):
            os.makedirs(subdir_path)


class WorkflowConfig(BaseModel):
    email: str
    password: str
    username: str = "main"
    headless: bool = True
    browser: str = "firefox"


class Workflow:
    def __init__(self, config: WorkflowConfig):
        self.config = config

    def _login(self):
        return PracujLogin(
            email=self.config.email,
            password=self.config.password,
            username=self.config.username,
            headless=self.config.headless,
            browser=self.config.browser,
        ).login()

    def _process_products(self, driver, wait, product_urls, df):
        for url in product_urls:
            ChangeDescription(driver=driver, wait=wait, url=url).run()
            product_id = (
                match.group(1) if (match := re.search(r"product:(\d+)", url)) else None
            )
            if product_id:
                df.loc[int(product_id), "poprawione"] = product_id

    def run(self):
        create_data_directories()
        df = None
        try:
            driver, wait = self._login()
            product_urls, df = ConstructUrls().run()
            df.set_index("NR ID Katalog Antoni", inplace=True)
            self._process_products(driver, wait, product_urls, df)
        finally:
            if df is not None:
                df.to_csv(NUMBER_ID_RES_CSV_PATH, index=True)


def main():
    load_dotenv()
    email = os.getenv("EMAIL")
    password = os.getenv("PASSWORD")

    if not email or not password:
        raise ValueError("EMAIL and PASSWORD environment variables must be set.")

    config = WorkflowConfig(email=email, password=password, headless=False)
    Workflow(config).run()


if __name__ == "__main__":
    main()


        
