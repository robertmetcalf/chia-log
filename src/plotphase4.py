# system packages
from datetime import datetime
from typing   import Optional
import re

# local packages
from src.logger      import Logger
from src.plotutility import phase_start_time


class PlotPhase4:
	'''
	Process a plot and extract the time for phase 4.
	'''

	def __init__ (self, logger:Logger, index:int) -> None:
		self._logger = logger
		self._index  = index

		self.start_time:Optional[datetime] = None
		self.total_time:float = 0.0

	def extract (self, data:str) -> bool:
		'''Extract the time for phase 4. Return True if the extract was good, otherwise False.'''

		log_prefix = 'PlotPhase4'

		outer_begin = r'Starting phase 4(.+)'
		outer_end   = r'Time for phase 4 = (\d+.\d+) seconds'
		pattern = outer_begin + outer_end

		outer = re.search(pattern, data)
		if not outer:
			self._logger.error(f'{log_prefix} failed to extract outer data')
			return False

		have:int = len(outer.groups())
		need:int = 2
		if have != need:
			self._logger.error(f'{log_prefix} index {self._index} failed to match outer data, need {need} groups, have {have} groups')
			return False

		body = outer.group(1)
		self.start_time = phase_start_time(self._logger, log_prefix, self._index, body)
		self.total_time = float(outer.group(2))

		self._logger.debug(f'{log_prefix} index {self._index} total seconds {self.total_time}')

		return True
