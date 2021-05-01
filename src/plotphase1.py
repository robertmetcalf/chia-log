# system packages
from datetime import datetime
from typing   import List, NamedTuple, Optional
import re

# local packages
from src.logger      import Logger
from src.plotutility import phase_start_time

class Phase1 (NamedTuple):
	table:int		# compute table number (1 to 7)
	seconds:float	# compute time


class PlotPhase1:
	'''
	Process a plot and extract the time for phase 1.
	'''

	def __init__ (self, logger:Logger):
		self._logger = logger

		self.start_time:Optional[datetime] = None
		self.total_time:float = 0.0

		self.table_time:List[Phase1] = []

	def extract (self, data:str) -> None:
		'''Extract the time for phase 1'''

		log_prefix = 'PlotPhase1'

		outer_begin = r'Starting phase 1(.+)'
		outer_end   = r'Time for phase 1 = (\d+.\d+) seconds'
		inner_begin = r'(.+?)Computing table (\d)(.+?)'
		inner_end   = r'time: (\d+.\d+) seconds'

		outer = re.search(outer_begin + outer_end, data)
		if not outer:
			self._logger.error(f'{log_prefix} failed to extract outer data')
			return

		have:int = len(outer.groups())
		need:int = 2
		if have != need:
			self._logger.error(f'{log_prefix} failed to match outer data, need {need} groups, have {have} groups')
			return

		body = outer.group(1)

		self.start_time = phase_start_time(self._logger, log_prefix, body)
		self.total_time = float(outer.group(2))

		need = 4
		inner = re.findall(inner_begin + inner_end, body)
		for result in inner:
			have = len(result)
			if have != need:
				self._logger.error(f'{log_prefix} failed to match inner data, need {need} groups, have {have} groups')
				continue

			table = int(result[1])
			seconds = float(result[3])
			ph = Phase1(table, seconds)
			self.table_time.append(ph)
			self._logger.debug(f'{log_prefix} table {table} seconds {seconds}')

		self._logger.debug(f'{log_prefix} total seconds {self.total_time}')
