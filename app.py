"""
PersianTranscriber
Main Application
"""

import config
from core.logger import get_logger


def main():
    logger = get_logger()

    logger.info("Application started")

    print("=" * 40)
    print(config.APP_NAME)
    print("Version:", config.VERSION)
    print("Language:", config.LANGUAGE)
    print("Output:", config.DEFAULT_OUTPUT_FOLDER)
    print("Core initialized successfully")
    print("=" * 40)

    logger.info("Application initialized successfully")


if __name__ == "__main__":
    main()
