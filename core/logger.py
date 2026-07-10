"""
PersianTranscriber Logger
Version: 0.1.0
"""

import logging
import os
from datetime import datetime

import config


def get_logger():
    os.makedirs(config.DEFAULT_LOG_FOLDER, exist_ok=True)

    log_file = os.path.join(
        config.DEFAULT_LOG_FOLDER,
        f"app_{datetime.now().strftime('%Y%m%d')}.log"
    )

    logging.basicConfig(
        filename=log_file,
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s"
    )

    return logging.getLogger("PersianTranscriber")
