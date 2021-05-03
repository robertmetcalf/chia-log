# system packages
from pathlib  import Path
from typing   import List
import re

# local packages
from src.config import Config
from src.plot   import Plot


class LogFiles:
	'''
	Process each log file. A log file may contain more than one plot entry.
	'''

	def __init__ (self, config:Config):
		self._config = config

		self._files:List[Path] = []		# files that were processed
		self._plots:List[Plot] = []		# a single plot in a log file

	@property
	def files (self) -> List[Path]:
		return self._files

	@property
	def plots (self) -> List[Plot]:
		return self._plots

	def extract (self, log_file_path:Path) -> None:
		'''Extract one or more plots from a log file.'''

		outer_begin = r'Starting plotting progress (.+?)'
		outer_end   = r'Renamed final file'
		pattern = outer_begin + outer_end

		if log_file_path in self._files:
			return

		with open(log_file_path, 'r') as f:
			data = f.read()
			data_replace = data.replace('\n', ' ')

			outer = re.findall(pattern, data_replace)
			self._config.logger.debug(f'number of  plots {len(outer)}')
			for results in outer:
				self._config.logger.debug(f'results len {len(results)}')
				plot = Plot(self._config)
				if not plot.extract(results):
					self._plots.append(plot)

			self._files.append(log_file_path)
