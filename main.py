import os
import sys
import json
import threading

from reader import fifo_reader as reader
from executor.processors import code_runner as runner
from util import create_logger

SAMPLE_USER_ID = "arnab_banik"
LOGGER = create_logger("CodeRunnerMain")

def get_config_path() -> str:
    if os.name == "nt":
        return "queue_config_win.json"
    else:
        return "queue_config_linux.json"

def load_config() -> dict:
    config_path = get_config_path()
    LOGGER.info("Loading configuration from %s", config_path)

    with open(config_path, "r") as f:
        config = json.load(f)

    if "reader_fifo_path" not in config:
        raise KeyError("Configuration must include 'reader_fifo_path'")

    if "writer_fifo_path" not in config:
        raise KeyError("Configuration must include 'writer_fifo_path'")

    return config

def read_and_run() -> None:
    fifo_path = global_config["reader_fifo_path"]
    try:
        for language, code_block in reader.read_messages(fifo_path):
            try:
                output = runner.run(language, code_block, SAMPLE_USER_ID)
                print(f"Output:\n{output}")
            except Exception as e:
                print(f"Error executing code: {e}", file=sys.stderr)
    except Exception as e:
        LOGGER.error("Error reading from FIFO: %s", e)
        sys.exit(1)

def main() -> None:
    reader_thread = threading.Thread(target=read_and_run)
    reader_thread.start()
    reader_thread.join()

if __name__ == "__main__":
    global_config = load_config()
    main()
