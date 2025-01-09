import logging
import os
from datetime import datetime

# Correcting the file path construction
LOG_FILE = f"{datetime.now().strftime('%m_%d_%Y_%H_%M_%S')}.log"
log_dir = os.path.join(os.getcwd(), "logs")  # Directory path for logs
os.makedirs(log_dir, exist_ok=True)  # Ensure the logs directory exists

LOG_FILE_PATH = os.path.join(log_dir, LOG_FILE)  # Full path to the log file

# Configure logging
logging.basicConfig(
    filename=LOG_FILE_PATH,
    format="[ %(asctime)s ] %(lineno)d %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

# Example logging to test
logger = logging.getLogger(__name__)
logger.info("Logger is working correctly!")
