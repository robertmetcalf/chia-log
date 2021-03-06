# system packages
from datetime import datetime
from typing   import List, NamedTuple, Optional
import re

# local packages
from src.logger      import Logger
from src.plotutility import phase_start_time

class Phase3 (NamedTuple):
	table1:int			# compress table "from" (1 to 6)
	table2:int			# compress table "to"   (2 to 7)
	first_pass:float	# compress time in seconds
	second_pass:float	# compress time in seconds
	seconds:float		# total time in seconds


class PlotPhase3:
	'''
	Process a plot and extract the time for phase 3.
	'''

	def __init__ (self, logger:Logger, index:int) -> None:
		self._logger = logger
		self._index  = index

		self.start_time:Optional[datetime] = None
		self.total_time:float = 0.0

		self.table_time:List[Phase3] = []

	def extract (self, data:str) -> bool:
		'''Extract the time for phase 3. Return True if the extract was good, otherwise False.'''

		log_prefix = 'PlotPhase3'

		outer_begin  = r'Starting phase 3(.+)'
		outer_end    = r'Time for phase 3 = (\d+.\d+) seconds'
		pattern_outer = outer_begin + outer_end

		inner_head   = r'(.+?)Compressing tables (\d) and (\d)(.+?)'
		inner_first  = r'First computation pass time: (\d+.\d+) seconds(.+?)'
		inner_second = r'Second computation pass time: (\d+.\d+) seconds(.+?)'
		inner_total  = r'Total compress table time: (\d+.\d+) seconds'
		pattern_inner = inner_head + inner_first + inner_second + inner_total

		outer = re.search(pattern_outer, data)
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

		need = 9
		inner = re.findall(pattern_inner, body)
		for result in inner:
			have = len(result)
			if have != need:
				self._logger.error(f'{log_prefix} index {self._index} failed to match inner data, need {need} groups, have {have} groups')
				return False

			table_1 = int(result[1])
			table_2 = int(result[2])
			first_pass = float(result[4])
			second_pass = float(result[6])
			seconds  = float(result[8])
			ph = Phase3(table_1, table_2, first_pass, second_pass, seconds)
			self.table_time.append(ph)

			self._logger.debug(f'{log_prefix} index {self._index} compress tables {table_1} and {table_2} first {first_pass} second {second_pass} seconds {seconds}')

		self._logger.debug(f'{log_prefix} index {self._index} total seconds {self.total_time}')

		return True
