import sys
from proj_whisper.logger.logger import logging

def get_error_message(error_message, detail:sys):
    _,_,exc_tb = detail.exc_info()
    file_name = exc_tb.tb_frame.f_code.co_filename
    line_number = exc_tb.tb_lineno
    error_message = f"Error occurred in script: {file_name} at line number: {line_number} with error message: {error_message}"
    return error_message

class CustomException(Exception):
    def __init__(self, error_message, detail:sys):
        super().__init__(error_message)
        self.error_message = get_error_message(error_message, detail)
        logging.error(self.error_message)
    def __str__(self):
        return self.error_message