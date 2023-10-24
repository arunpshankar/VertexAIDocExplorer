import logging
import os

def setup_logger(log_filename="app.log", log_dir="logs"):
    # Ensure the logging directory exists
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    # Define the log file path
    log_filepath = os.path.join(log_dir, log_filename)

    # Define the logging configuration
    logging.basicConfig(
        level=logging.INFO,  # Log level: DEBUG, INFO, WARNING, ERROR, CRITICAL
        format="%(asctime)s [%(levelname)s]: %(message)s",  # Format of the log message
        handlers=[
            logging.StreamHandler(),  # Log to console
            logging.FileHandler(log_filepath)  # Log to file
        ]
    )

    # Return the configured logger
    return logging.getLogger()
