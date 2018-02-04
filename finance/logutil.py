import logging

def setup_logging():
    # Create root logger
    logger = logging.getLogger('')
    logger.setLevel(logging.DEBUG)

    # Create stream handler
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)

    # Create formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)

    # Add the handler to the rool logger
    logger.addHandler(ch)

    return logger
