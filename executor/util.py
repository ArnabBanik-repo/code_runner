import base64
import logging
from datetime import datetime
from time import strftime


def create_logger(logger_name: str) -> logging.Logger:
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.DEBUG)
    stream_handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    stream_handler.setFormatter(formatter)
    file_handler = logging.FileHandler(f'logs/{logger_name}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')
    file_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)
    logger.addHandler(file_handler)
    return logger

def decode_base64(encoded_str: bytes) -> str:
    decoded_bytes = base64.b64decode(encoded_str)
    return decoded_bytes.decode('utf-8')

def encode_base64(raw_str: str) -> bytes:
    raw_bytes = raw_str.encode('utf-8')
    encoded_bytes = base64.b64encode(raw_bytes)
    return encoded_bytes