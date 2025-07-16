import logging

formatter = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s - "
    "File: %(filename)s - Line: %(lineno)d - Function: %(funcName)s",
)

email_file_handler = logging.FileHandler("logs/email_logs.log")
email_logger = logging.getLogger("email_logger")

# File handler for logging to a file
email_file_handler.setFormatter(formatter)

# Add the handler to the logger
email_logger.addHandler(email_file_handler)
