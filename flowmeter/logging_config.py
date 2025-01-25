import logging

def setup_logger(name, module):
    logger = logging.getLogger(name)
    logger.propagate = False
    
    if not logger.hasHandlers():
        logger.setLevel(logging.DEBUG)

        console_handler = logging.StreamHandler()
        console_formatter = logging.Formatter(f'{module}: %(asctime)s - %(levelname)s - %(message)s')
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)

        file_handler = logging.FileHandler('flowmeter.log', encoding='utf-8')
        file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)

    return logger