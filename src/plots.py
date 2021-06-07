# system packages
from pathlib  import Path
from typing   import List
import re

# local packages
from src.config import Config
from src.plot   import Plot


class Plots:
	'''
	Process plots in log files. A log file may contain more than one plot entry.
	'''

	def __init__ (self, config:Config) -> None:
		self._config = config

		self._files:List[Path] = []		# files that were processed
		self._plots:List[Plot] = []		# a single plot extracted from a log file
		self._plot_ids:List[str] = []	# plot id's are used to check for duplicates

	@property
	def files (self) -> List[Path]:
		'''Return a list of files processed, each element is a Path() object.'''

		return self._files

	@property
	def plots (self) -> List[Plot]:
		'''Return a list of Plot() objects.'''

		return self._plots

	def extract (self, log_file_path:Path) -> None:
		'''Extract one or more plots from a log file.'''

		# define the output from a single plot; a log file may contain more than
		# one plot
		plot_begin = r'Starting plotting progress (.+?)'
		plot_end   = r'Renamed final file'
		pattern = plot_begin + plot_end

		if log_file_path in self._files:
			return

		with open(log_file_path, 'r') as f:
			log_data = f.read()
			data_replace = log_data.replace('\n', ' ')

			plots = re.findall(pattern, data_replace)
			self._config.logger.debug(f'number of  plots {len(plots)}')

			# process each plot in the log file
			for index, result in enumerate(plots, 1):
				self._config.logger.debug(f'results len {len(result)}')

				plot = Plot(self._config, log_file_path, index)
				if plot.extract(result):
					plot_id = plot.parameters.plot_id
					if plot_id not in self._plot_ids:
						self._plots.append(plot)
						self._plot_ids.append(plot_id)

			self._files.append(log_file_path)

	def post_process (self) -> None:
		'''Post-process each plot and add more information.'''

		for plot in self._plots:
			plot.set_plot_configuration()	# group plots by disks/SSDs used
			plot.set_plot_date()			# plot yyyy-mm and yyyy-mm-dd and
			plot.set_plot_time()			# start, end, and elapsed time

			'''
			from datetime    import datetime
			from collections import namedtuple
			Range = namedtuple('Range', ['start', 'end'])

			r1 = Range(start=datetime(2012, 1, 15), end=datetime(2012, 5, 10))
			r2 = Range(start=datetime(2012, 3, 20), end=datetime(2012, 9, 15))
			latest_start = max(r1.start, r2.start)
			earliest_end = min(r1.end, r2.end)
			delta = (earliest_end - latest_start).seconds + 1
			overlap = max(0, delta)
			'''

	def sort_by_start_time (self) -> List[Plot]:
		'''
		Return all Plot() objects sorted by the start time. Duplicate start
		times look at the final end time as a secondary sort.
		'''

		return []
