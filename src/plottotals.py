# system packages
from datetime import datetime
from typing   import Optional
import re

# local packages
from src.logger      import Logger
from src.plotutility import phase_start_time


class PlotTotals:
	'''
	Process plot totals at the end of the file.
	'''

	def __init__ (self, logger:Logger):
		self._logger = logger

		# parameters at the end of the log file
		self.working_gb:float = 0.0	# Approximate working space used (without final file): 269.308 GiB
		self.file_gb:float    = 0.0	# Final File size: 101.336 GiB
		self.total_time:float = 0.0	# Total time = 13508.459 seconds. CPU (133.870%) Sun Apr 25 20:44:18 2021
		self.copy_time:float  = 0.0	# Copy time = 371.657 seconds. CPU (21.260%) Sun Apr 25 20:50:30 2021
		self.end_time:Optional[datetime] = None

	def extract (self, data:str) -> bool:
		'''
		Extract the totals at the end of the file (working space, final file
		size, total time, and copy time). Return True if there was an error,
		otherwise False.

		Data looks like:

		Approximate working space used (without final file): 269.308 GiB
		Final File size: 101.336 GiB
		Total time = 13508.459 seconds. CPU (133.870%) Sun Apr 25 20:44:18 2021
		Copied final file from {temp.2.tmp} to {dest.2.tmp}
		Copy time = 371.657 seconds. CPU (21.260%) Sun Apr 25 20:50:30 2021
		Removed temp2 file {temp.2.tmp}
		Renamed final file from {dest.2.tmp} to {dest.plot}
		'''

		log_prefix = 'PlotTotals'

		line_1 = r'Approximate working space used \(without final file\): (\d+.\d+) GiB(.*)'
		line_2 = r'Final File size: (\d+.\d+) GiB(.*)'
		line_3 = r'Total time = (\d+.\d+) seconds(.*)'
		line_4 = r'Copy time = (\d+.\d+) seconds(.*)'
		pattern = line_1 + line_2 + line_3 + line_4

		results = re.search(pattern, data)
		if not results:
			self._logger.error(f'{log_prefix} failed to extract outer data')
			return True

		have:int = len(results.groups())
		need:int = 8
		if have != need:
			self._logger.error(f'{log_prefix} failed to match data, need {need} groups, have {have} groups')
			return True

		self.working_gb = float(results.group(1))
		self.file_gb    = float(results.group(3))
		self.total_time = float(results.group(5))
		self.copy_time  = float(results.group(7))
		self.end_time   = phase_start_time(self._logger, log_prefix, results.group(8))

		self._logger.debug(f'{log_prefix} working GB {self.working_gb}')
		self._logger.debug(f'{log_prefix} file GB {self.file_gb}')
		self._logger.debug(f'{log_prefix} total seconds {self.total_time}')
		self._logger.debug(f'{log_prefix} copy seconds {self.copy_time}')
		self._logger.debug(f'{log_prefix} end time {self.end_time}')

		return False
