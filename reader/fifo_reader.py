import os
import struct

from util import create_logger

LOGGER = create_logger("FIFOReader")

def read_messages(fifo_path):
    LOGGER.info("Starting to read messages from FIFO: %s", fifo_path)
    if not os.path.exists(fifo_path):
        raise FileNotFoundError(f"FIFO path {fifo_path} does not exist.")

    with open(fifo_path, "rb") as fifo:
        while True:
            length_bytes = fifo.read(4)
            while not length_bytes:
                LOGGER.debug("No data available, waiting for messages...")
                pass

            if len(length_bytes) < 4:
                raise RuntimeError("Incomplete length prefix")

            message_length = struct.unpack('!I', length_bytes)[0]
            LOGGER.debug("Message length: %d", message_length)

            message_bytes = fifo.read(message_length)
            if not message_bytes:
                raise RuntimeError("Expected to read %d bytes but got none.", message_length)

            while len(message_bytes) < message_length:
                LOGGER.debug("Partial message read, reading remaining bytes...")
                more_bytes = fifo.read(message_length - len(message_bytes))
                if not more_bytes:
                    raise RuntimeError("Incomplete message read")
                message_bytes += more_bytes

            message = message_bytes.decode('utf-8')
            try:
                language, code_block = message.split("|", 1)
            except ValueError:
                raise RuntimeError(f"Invalid message format: {message}")

            yield int(language), code_block