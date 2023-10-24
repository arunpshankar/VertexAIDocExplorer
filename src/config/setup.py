import yaml
import os 

def load_config(config_path: str) -> dict:
    """
    Load the YAML configuration from the given path.

    Args:
    - config_path (str): Path to the YAML configuration file.

    Returns:
    - dict: Loaded configuration data.
    """
    with open(config_path, 'r') as file:
        return yaml.safe_load(file)


def set_google_credentials(credentials_path: str) -> None:
    """
    Set the Google application credentials environment variable.

    Args:
    - credentials_path (str): Path to the Google credentials file.
    """
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentials_path