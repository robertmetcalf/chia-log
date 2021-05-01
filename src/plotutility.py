# system packages
from datetime import datetime
from typing   import Optional
import re

# local packages
from src.logger import Logger


def phase_start_time (logger:Logger, log_prefix:str, data:str) -> Optional[datetime]:
	'''Get the start time for a given phase and return a time stamp'''

	# dates look like: Sun Apr 25 16:59:09 2021
	expression = r'... (\w{3}) (\w{3}) (\d+) (\d+):(\d+):(\d+) (\d+)'

	res = re.search(expression, data[:250])
	if res:
		month  = res.group(2)
		day    = res.group(3)
		hour   = res.group(4)
		minute = res.group(5)
		second = res.group(6)
		year   = res.group(7)

		date_string:str = f'{year}-{month}-{day} {hour}:{minute}:{second}'
		date_format:str = '%Y-%b-%d %H:%M:%S'
		dt = datetime.strptime(date_string, date_format)

		logger.debug(f'{log_prefix} start time {dt}')

		return dt

	return None
