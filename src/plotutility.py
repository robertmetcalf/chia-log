# system packages
from datetime import datetime
from typing   import Optional
import re

# local packages
from src.logger import Logger


def phase_start_time (logger:Logger, log_prefix:str, index:int, data:str) -> Optional[datetime]:
	'''Get the start time for a given phase and return a time stamp'''

	# dates look like:
	#   Sun Apr 25 16:59:09 2021
	#   Sat May  1 03:10:43 2021
	#   1   2  3 4 5  6  7  8 <- group
	expression = r'... (\w{3}) (\w{3})(\s{1,2})(\d+) (\d+):(\d+):(\d+) (\d+)'

	res = re.search(expression, data[:250])
	if not res:
		logger.error(f'{log_prefix} index {index} failed to extract date')
		return None

	have:int = len(res.groups())
	need:int = 8
	if have != need:
		logger.error(f'{log_prefix} index {index} failed to match date, need {need} groups, have {have} groups')
		return None

	month  = res.group(2)
	day    = res.group(4)
	hour   = res.group(5)
	minute = res.group(6)
	second = res.group(7)
	year   = res.group(8)

	date_string:str = f'{year}-{month}-{day} {hour}:{minute}:{second}'
	date_format:str = '%Y-%b-%d %H:%M:%S'
	dt = datetime.strptime(date_string, date_format)

	logger.debug(f'{log_prefix} index {index} start time {dt}')

	return dt
