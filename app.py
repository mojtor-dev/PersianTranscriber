"""
PersianTranscriber
Main Application
"""

import config


def main():
    print("=" * 40)
    print(config.APP_NAME)
    print("Version:", config.VERSION)
    print("Language:", config.LANGUAGE)
    print("Output:", config.DEFAULT_OUTPUT_FOLDER)
    print("Core initialized successfully")
    print("=" * 40)


if __name__ == "__main__":
    main()
