# system packages
from datetime import datetime
from typing   import List, NamedTuple, Optional
import re

# local packages
from src.logger      import Logger
from src.plotutility import phase_start_time

class Phase2 (NamedTuple):
	table:int		# compute table number (7 to 2)
	seconds:float	# compute time


class PlotPhase2:
	'''
	Process a plot and extract the time for phase 2.
	'''

	def __init__ (self, logger:Logger, index:int) -> None:
		self._logger = logger
		self._index  = index

		self.start_time:Optional[datetime] = None
		self.total_time:float = 0.0

		self.table_time:List[Phase2] = []

	def extract (self, data:str) -> bool:
		'''Extract the time for phase 2. Return True if the extract was good, otherwise False.'''

		log_prefix = 'PlotPhase2'

		outer_begin = r'Starting phase 2(.+)'
		outer_end   = r'Time for phase 2 = (\d+.\d+) seconds'
		inner_begin = r'(.+?)Backpropagating on table (\d)(.+?)'
		inner_end   = r'time =  (\d+.\d+) seconds'

		outer = re.search(outer_begin + outer_end, data)
		if not outer:
			self._logger.error(f'{log_prefix} index {self._index} failed to extract outer data')
			return False

		have:int = len(outer.groups())
		need:int = 2
		if have != need:
			self._logger.error(f'{log_prefix} index {self._index} failed to match outer data, need {need} groups, have {have} groups')
			return False

		body = outer.group(1)
		self.start_time = phase_start_time(self._logger, log_prefix, self._index, body)
		self.total_time = float(outer.group(2))

		need = 4
		inner = re.findall(inner_begin + inner_end, body)
		for result in inner:
			have = len(result)
			if have != need:
				self._logger.error(f'{log_prefix} index {self._index} failed to match inner data, need {need} groups, have {have} groups')
				return False

			table = int(result[1])
			seconds = float(result[3])
			ph = Phase2(table, seconds)
			self.table_time.append(ph)
			self._logger.debug(f'{log_prefix} index {self._index} table {table} seconds {seconds}')

		self._logger.debug(f'{log_prefix} index {self._index} total seconds {self.total_time}')

		return True
