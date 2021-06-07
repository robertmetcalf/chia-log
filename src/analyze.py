# system packages
from __future__  import annotations
from datetime    import datetime
from statistics  import mean
from typing      import Dict, List, NamedTuple, Optional

# local packages
from src.config import Config
from src.plots  import Plots
class Range (NamedTuple):
	start:datetime
	end:datetime

class Analyze:
	'''
	Analyze the plots.
	'''

	def __init__ (self, config:Config) -> None:
		self._config = config

		self._plot_configs = PlotConfigurations()

		# key is yyyy-mm-dd, value is number of plots
		self._plots_per_day:Dict[str, int] = {}

		# key is yyyy-mm, value is number of plots
		self._plots_per_month:Dict[str, int] = {}

	def print (self, plots:Plots) -> None:
		self._print_configs();
		print()
		self._print_dates();
		print()
		self._print_overlap(plots);

		if self._config.is_csv:
			pass

		if self._config.is_json:
			pass

		if self._config.is_markdown:
			pass

	def process (self, plots:Plots) -> None:
		self._set_config(plots)		# group similar plots for analysis
		self._set_dates(plots)		# plot totals per day and month
		self._set_overlap(plots)	# number of overlaps for each plot

	def _set_config (self, plots:Plots) -> None:
		'''
		Append each plot to a PlotConfiguration() object. This groups similar
		plots together for analysis.
		'''

		for plot in plots.plots:
			# get the disk configuration that matches this plot
			plot_config = self._plot_configs.get_plot_config(plot.name)
			plot_config.increment_plot_count(plot.parameters.threads)
			plot_config.append(plot.parameters.threads, 1, plot.phase_1.total_time)
			plot_config.append(plot.parameters.threads, 2, plot.phase_2.total_time)
			plot_config.append(plot.parameters.threads, 3, plot.phase_3.total_time)
			plot_config.append(plot.parameters.threads, 4, plot.phase_4.total_time)
			plot_config.append(plot.parameters.threads, 5, plot.totals.total_time)

	def _set_dates (self, plots:Plots) -> None:
		'''Determine the number of plots processed per day.'''

		for plot in plots.plots:
			if not plot.end_date_yyyy_mm_dd:
				print(f'missing end date - file {plot.log_file}, index {plot.index}')
			else:
				if plot.end_date_yyyy_mm_dd not in self._plots_per_day:
					self._plots_per_day[plot.end_date_yyyy_mm_dd] = 0
				self._plots_per_day[plot.end_date_yyyy_mm_dd] += 1

				if plot.end_date_yyyy_mm not in self._plots_per_month:
					self._plots_per_month[plot.end_date_yyyy_mm] = 0
				self._plots_per_month[plot.end_date_yyyy_mm] += 1

	def _set_overlap (self, plots:Plots) -> None:
		'''Set the number of overlaps for each plot.'''

		range_source:Optional[Range] = None
		range_dest:Optional[Range]   = None

		for source in plots.plots:
			range_source = None
			range_dest   = None

			if source.phase_1.start_time and source.totals.end_time:
				range_source = Range(start=source.phase_1.start_time, end=source.totals.end_time)
				print(f'source start {range_source.start} end {range_source.end}')

			for dest in plots.plots:
				# don't compare a plot to itself
				if source.parameters.plot_id == dest.parameters.plot_id:
					continue

				if dest.phase_1.start_time and dest.totals.end_time:
					range_dest = Range(start=dest.phase_1.start_time, end=dest.totals.end_time)

				if range_source and range_dest:
					# the source ended before the destinaton started
					# src...src
					#           dest...dest
					if range_source.end < range_dest.start:
						continue
					# the destination ended before the source started
					#             src...src
					# dest...dest
					if range_dest.end < range_source.start:
						continue

					latest_start = max(range_source.start, range_dest.start)
					earliest_end = min(range_source.end, range_dest.end)
					#delta = (earliest_end - latest_start).seconds + 1
					delta = earliest_end - latest_start
					#overlap = max(0, delta)
					source.set_plot_overlap(source.parameters.plot_id, delta)

	def _print_configs (self) -> None:
		for index, plot_config in enumerate(self._plot_configs.plot_configs):
			if index:
				print()
			plot_config.print()

	def _print_dates (self) -> None:
		'''Print plots per month and plots per day.'''

		# plot totals per month
		total:int = 0
		for date in sorted(self._plots_per_month):
			count = self._plots_per_month[date]
			print(f'{date}    - {count:4}')
			total += count
		print(f'Total      - {total:4}')
		print()

		# plot totals per day
		total:int = 0
		for date in sorted(self._plots_per_day):
			count = self._plots_per_day[date]
			print(f'{date} - {count:4}')
			total += count
		print(f'Total      - {total:4}')

	def _print_overlap (self, plots:Plots) -> None:
		for plot in plots.plots:
			for plot_id, overlap in plot.overlap.items():
				print(f'plot id {plot_id}, elapsed {plot.elapsed_time} overlap {overlap}')


class PlotConfigurations:
	'''
	Manages all plot configurations, as found in the chia-log.yaml file.
	'''

	def __init__ (self) -> None:
		# key is name such as "temp is a single SSD", value is a PlotConfiguration()
		self._plot_configs:Dict[str, PlotConfiguration] = {}

	@property
	def plot_configs (self) -> List[PlotConfiguration]:
		return [plot_config for plot_config in self._plot_configs.values()]

	def get_plot_config (self, name:str) -> PlotConfiguration:
		'''
		Return an existing PlotConfiguration() or create a new one based on the
		config name, which was created in plot.set_plot_configuration(). The
		names are found in chia-log.yaml and example is "temp is a single SSD".
		'''

		if name not in self._plot_configs:
			self._plot_configs[name] = PlotConfiguration(name)

		return self._plot_configs[name]

class PlotConfiguration:
	'''
	Manage an individual plot configuration. A configuration is the
	"plotConfigurations.name" in the chia-log.yaml file. A configuration has
	one or more "rows." A row consists of the number of threads (plots create -r
	parameter) and values for each phase. Phases are 1-4 and the 5th phase is
	the totals section in the log file.
	'''

	def __init__ (self, name:str) -> None:
		self.name = name

		# key is thread count, value is a dictionary of phases (1 - 5) and a
		# list of values (seconds) for each phase
		self._rows:Dict[int, Dict[int, List[float]]] = {}

		# number of plots with this configuration; key is threads, value is plot count
		self._plot_count:Dict[int, int] = {}

	def append (self, threads:int, phase:int, value:float) -> None:
		if threads not in self._rows:
			self._rows[threads] = {}
		if phase not in self._rows[threads]:
			self._rows[threads][phase] = []
		self._rows[threads][phase].append(value)

	def avg (self, threads:int, phase:int) -> int:
		return int(mean(self._rows[threads][phase]))

	def increment_plot_count (self, threads:int) -> None:
		if threads not in self._plot_count:
			self._plot_count[threads] = 0
		self._plot_count[threads] += 1

	def print (self) -> None:
		print(f'Disk - {self.name}')
		for threads in sorted(self._rows.keys()):
			print(f'  threads {threads} plots {self._plot_count[threads]:4} p1 {self.avg(threads, 1):6,} p2 {self.avg(threads, 2):6,} p3 {self.avg(threads, 3):6,} p4 {self.avg(threads, 4):6,} tot {self.avg(threads, 5):6,}')

	def sort_by_threads (self) -> Dict[int, Dict[int, List[float]]]:
		'''
		Return self._rows sorted by the key, which is the number of threads.
		'''

		new_rows:Dict[int, Dict[int, List[float]]] = {}

		for thread_count in sorted(self._rows.keys()):
			new_rows[thread_count] = self._rows[thread_count]

		return new_rows
