# system packages
from datetime import datetime
from pathlib  import Path
from typing   import Optional
import re

# local packages
from src.logger      import Logger
from src.plotutility import phase_start_time


class PlotTotals:
	'''
	Process plot totals at the end of the file.
	'''

	def __init__ (self, logger:Logger, index:int) -> None:
		self._logger = logger
		self._index  = index

		# parameters at the end of the log file
		self.working_gb:float = 0.0		# Approximate working space used (without final file): 269.308 GiB
		self.file_gb:float    = 0.0		# Final File size: 101.336 GiB
		self.total_time:float = 0.0		# Total time = 13508.459 seconds. CPU (133.870%) Sun Apr 25 20:44:18 2021
		self.temp_path:str    = ''		# Copied final file from "/temp2/name.plot.2.tmp" to "/dest/name.plot.2.tmp"
		self.dest_path:str    = ''		# Copied final file from "/temp2/name.plot.2.tmp" to "/dest/name.plot.2.tmp"
		self.copy_secs:float  = 0.0		# Copy time = 371.657 seconds. CPU (21.260%) Sun Apr 25 20:50:30 2021
		self.end_time:Optional[datetime] = None

	@property
	def dest_dir (self) -> Path:
		return Path(self.dest_path).parent

	def extract (self, data:str) -> bool:
		'''
		Extract the totals at the end of the file (working space, final file
		size, total time, and copy time). Return True if the extract was good,
		otherwise False.

		Data looks like:

		Approximate working space used (without final file): 269.308 GiB
		Final File size: 101.336 GiB
		Total time = 13508.459 seconds. CPU (133.870%) Sun Apr 25 20:44:18 2021
		Copied final file from "/temp2/name.plot.2.tmp" to "/dest/name.plot.2.tmp"
		Copy time = 371.657 seconds. CPU (21.260%) Sun Apr 25 20:50:30 2021
		Removed temp2 file "/temp/name.plot.2.tmp"? 1
		Renamed final file from "/dest/name.plot.2.tmp" to "/dest/name.plot"
		'''

		log_prefix = 'PlotTotals'

		line_1 = r'Approximate working space used \(without final file\): (\d+.\d+) GiB(.*)'
		line_2 = r'Final File size: (\d+.\d+) GiB(.*)'
		line_3 = r'Total time = (\d+.\d+) seconds(.*)'
		line_4 = r'Copied final file from "(.*)" to "(.*)" '
		line_5 = r'Copy time = (\d+.\d+) seconds(.*)'
		pattern = line_1 + line_2 + line_3 + line_4 + line_5

		results = re.search(pattern, data)
		if not results:
			self._logger.error(f'{log_prefix} index {self._index} failed to extract outer data')
			return False

		have:int = len(results.groups())
		need:int = 10
		if have != need:
			self._logger.error(f'{log_prefix} index {self._index} failed to match data, need {need} groups, have {have} groups')
			return False

		self.working_gb = float(results.group(1))
		self.file_gb    = float(results.group(3))
		self.total_time = float(results.group(5))
		self.temp_path  = str(results.group(7))
		self.dest_path  = str(results.group(8))
		self.copy_secs  = float(results.group(9))
		self.end_time   = phase_start_time(self._logger, log_prefix, self._index, results.group(10))

		self._logger.debug(f'{log_prefix} index {self._index} working GB {self.working_gb}')
		self._logger.debug(f'{log_prefix} index {self._index} file GB {self.file_gb}')
		self._logger.debug(f'{log_prefix} index {self._index} total seconds {self.total_time}')
		self._logger.debug(f'{log_prefix} index {self._index} copy seconds {self.copy_secs}')
		self._logger.debug(f'{log_prefix} index {self._index} end time {self.end_time}')
		self._logger.debug(f'{log_prefix} index {self._index} temp path {self.temp_path}')
		self._logger.debug(f'{log_prefix} index {self._index} dest path {self.dest_path}')

		return True
