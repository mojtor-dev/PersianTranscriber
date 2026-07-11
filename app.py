"""
PersianTranscriber
Main Application
"""

import config
from core.logger import AppLogger


def main():
    logger = AppLogger()

    logger.write("Application started")

    print("=" * 40)
    print(config.APP_NAME)
    print("Version:", config.VERSION)
    print("Language:", config.LANGUAGE)
    print("Output:", config.DEFAULT_OUTPUT_FOLDER)
    print("Core initialized successfully")
    print("=" * 40)

    logger.write("Application initialized successfully")


if __name__ == "__main__":
    main()
