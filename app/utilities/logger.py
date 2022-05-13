#!/usr/bin/env python3

import logging

from logging import Formatter, getLogger, StreamHandler
from console.colors import COLOR_NAME, BG_COLOR_NAME, set_color

class ColoredFormatter(Formatter):
	def format(self, record):
		message = record.getMessage()
		mapping = {
			'INFO': COLOR_NAME.CYAN,
			'WARNING': COLOR_NAME.YELLOW,
			'ERROR': COLOR_NAME.RED,
			'CRITICAL': BG_COLOR_NAME.RED,
			'DEBUG': COLOR_NAME.WHITE,
			'SUCCESS': COLOR_NAME.GREEN
		}
		return set_color('%s - %s - %s' % (self.formatTime(record, '%H:%M:%S'), record.levelname, message),
			mapping.get(record.levelname, 'white'))

logger = logging.getLogger(__name__)
handler = StreamHandler()
formatter = ColoredFormatter()
handler.setFormatter(formatter)
logger.addHandler(handler)

logging.SUCCESS = 25
logging.addLevelName(logging.SUCCESS, 'SUCCESS')
setattr(logger, 'success', lambda message, *args: logger._log(logging.SUCCESS, message, args))
logger.setLevel(logging.DEBUG)