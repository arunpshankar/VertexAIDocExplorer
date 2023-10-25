from src.config.logging import logger
from typing import Dict
from typing import Any
import subprocess
import yaml
import os

class Config:
    def __init__(self, config_path: str = "config/config.yaml"):
        self.config = self._load_config(config_path)
        self.PROJECT_ID = self.config['project_id']
        self.DATA_STORE_ID = self.config['datastore_id']
        self.set_google_credentials(self.config['credentials_json'])

    @staticmethod
    def _load_config(config_path: str) -> Dict[str, Any]:
        """
        Load the YAML configuration from the given path.

        Args:
        - config_path (str): Path to the YAML configuration file.

        Returns:
        - dict: Loaded configuration data.
        """
        with open(config_path, 'r') as file:
            return yaml.safe_load(file)

    @staticmethod
    def set_google_credentials(credentials_path: str) -> None:
        """
        Set the Google application credentials environment variable.

        Args:
        - credentials_path (str): Path to the Google credentials file.
        """
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentials_path

    @staticmethod
    def get_access_token() -> str:
        """
        Fetch an access token for authentication.

        Returns:
        - str: The fetched access token.
        """
        logger.info("Fetching access token...")
        cmd = ["gcloud", "auth", "print-access-token"]
        token = subprocess.check_output(cmd).decode('utf-8').strip()
        logger.info("Access token obtained successfully.")
        return token


config = Config()
access_token = config.get_access_token()