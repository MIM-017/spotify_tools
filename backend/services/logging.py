import logging

def setup_module_logger(module_name, logging_level=logging.INFO) -> logging.Logger:
    """Sets up the logger for the module"""

    logger = logging.getLogger(module_name)
    logger.setLevel(logging_level)

    formatter = logging.Formatter(
        '{module} - {asctime} - {levelname} - {message}', style="{", datefmt='%Y-%m-%d %H:%M:%S')

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # file_handler = logging.FileHandler("logs.txt", mode='w', encoding='utf-8')
    # file_handler.setFormatter(formatter)
    # logger.addHandler(file_handler)

    return logger