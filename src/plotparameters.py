# system packages
from typing import Tuple
import re

# local packages
from src.logger import Logger


class PlotParameters:
	'''
	Process plot parameters at the top of each plot log.
	'''

	def __init__ (self, logger:Logger, index:int) -> None:
		self._logger = logger
		self._index  = index

		# parameters at the top of the log file
		self.temp_dir_1:str  = ''		# into temporary dirs: /media/temp001 and /media/temp002
		self.temp_dir_2:str  = ''		# into temporary dirs: /media/temp001 and /media/temp002
		self.plot_id:str     = ''		# ID: c259696a3a94a3b9302ec95d24a5763d9e1125f6ac5ff68f7aca1790501986e9
		self.plot_size:int   = 0		# Plot size is: 32
		self.buffer_size:int = 0		# Buffer size is: 4096MiB
		self.buckets:int     = 0		# Using 128 buckets
		self.threads:int     = 0		# Using 4 threads of stripe size 65536
		self.stripe_size:int = 0		# Using 4 threads of stripe size 65536

	@property
	def temp_dirs (self) -> Tuple[str, str]:
		return self.temp_dir_1, self.temp_dir_2

	def extract (self, data:str) -> bool:
		'''
		Extract the parameters (plot size, buffer size, buckets, threads, and
		stripe size). Return True if the extract was good, otherwise False.

		Data looks like:

		into temporary dirs: /media/temp and /media/temp
		ID: c259696a3a94a3b9302ec95d24a5763d9e1125f6ac5ff68f7aca1790501986e9
		Plot size is: 32
		Buffer size is: 4096MiB
		Using 128 buckets
		Using 4 threads of stripe size 65536
		'''

		log_prefix = 'PlotParameters'
		line_1 = r'into temporary dirs: (.+) and (.+) '
		line_2 = r'ID: (\w+) '
		line_3 = r'Plot size is: (\d+) '
		line_4 = r'Buffer size is: (\d+)MiB '
		line_5 = r'Using (\d+) buckets '
		line_6 = r'Using (\d+) threads of stripe size (\d+)'
		pattern = line_1 + line_2 + line_3 + line_4 + line_5 + line_6

		results = re.search(pattern, data)
		if not results:
			self._logger.error(f'{log_prefix} index {self._index} failed to extract data')
			return False

		have:int = len(results.groups())
		need:int = 8
		if have != need:
			self._logger.error(f'{log_prefix} index {self._index} failed to match data, need {need} groups, have {have} groups')
			return False

		self.temp_dir_1  = str(results.group(1))
		self.temp_dir_2  = str(results.group(2))
		self.plot_id     = str(results.group(3))
		self.plot_size   = int(results.group(4))
		self.buffer_size = int(results.group(5))
		self.buckets     = int(results.group(6))
		self.threads     = int(results.group(7))
		self.stripe_size = int(results.group(8))

		self._logger.debug(f'{log_prefix} index {self._index} res {results.groups()}')

		return True
