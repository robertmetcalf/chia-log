# system packages
from pathlib import Path
from typing  import List

# third party packages

# local packages
from src.config  import Config
from src.logfile import LogFile


class Analyze:
	'''
	'''

	def __init__ (self):
		self._log_file_paths:List[Path] = []	# path to each log file
		self._log_files:List[LogFile] = []		# processed log files

	@property
	def log_files (self) -> int:
		return len(self._log_files)

	def log_file (self, log_file_path:Path) -> None:
		if log_file_path not in self._log_file_paths:
			lf = LogFile()
			lf.log_file(log_file_path)
			self._log_files.append(lf)

	def print (self, config:Config) -> None:
		pass
