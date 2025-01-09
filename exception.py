# exception.py
import sys
from logger import logging


def error_message_detail(error_message, error_details: sys):
    _, _, exc_tb = sys.exc_info()  # Use sys.exc_info() instead
    file_name = exc_tb.tb_frame.f_code.co_filename
    error_message = f"Error occurred in script: {file_name} at line {exc_tb.tb_lineno} - {error_message}"
    return error_message


class CustomException(Exception):
    def __init__(self, error_message, error_details: sys):
        super().__init__(error_message)
        self.error_message = error_message_detail(error_message, error_details)

    def __str__(self):
        return self.error_message
