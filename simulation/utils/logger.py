import logging

class ContextLoggerAdapter(logging.LoggerAdapter):
    def process(self, msg, kwargs):
        return f"Id: {self.extra['tracking_id']}: {msg}", kwargs

def setup_logger(tracking_id):
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)

    # Use the tracking_id to create a unique log filename.
    filename = f"log/{tracking_id}-simulate.log"
    file_handler = logging.FileHandler(filename, mode='w')
    file_handler.setLevel(logging.DEBUG)

    # console_handler = logging.StreamHandler()
    # console_handler.setLevel(logging.DEBUG)

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(message)s')
    file_handler.setFormatter(formatter)
    # console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    # logger.addHandler(console_handler)

    return logger
