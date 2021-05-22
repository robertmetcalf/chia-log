# system packages
from __future__ import annotations
from statistics import mean
from typing     import Dict, List

# local packages
from src.config import Config
from src.plot   import Plot

class Analyze:
	'''
	Analyze the plots.
	'''

	def __init__ (self, config:Config) -> None:
		self._config = config

	def set_config (self, plots:List[Plot]) -> None:
		'''Set the configuration for each plot.'''

		plot_configs = PlotConfigurations()

		for plot in plots:
			# get the disk configuration that matches this plot
			plot_config = plot_configs.get_plot_config(plot.name)
			plot_config.increment_plot_count(plot.parameters.threads)
			plot_config.append(plot.parameters.threads, 1, plot.phase_1.total_time)
			plot_config.append(plot.parameters.threads, 2, plot.phase_2.total_time)
			plot_config.append(plot.parameters.threads, 3, plot.phase_3.total_time)
			plot_config.append(plot.parameters.threads, 4, plot.phase_4.total_time)
			plot_config.append(plot.parameters.threads, 5, plot.totals.total_time)

		for index, plot_config in enumerate(plot_configs.plot_configs):
			if index:
				print()
			plot_config.print()

	def set_dates (self, plots:List[Plot]) -> None:
		'''Set the number of plots processed per day.'''

		plot_days:Dict[str, int] = {}
		plot_months:Dict[str, int] = {}

		for plot in plots:
			if not plot.end_date_yyyy_mm_dd:
				print(f'missing end date - file {plot.log_file}, index {plot.index}')
			else:
				if plot.end_date_yyyy_mm_dd not in plot_days:
					plot_days[plot.end_date_yyyy_mm_dd] = 0
				plot_days[plot.end_date_yyyy_mm_dd] += 1

				if plot.end_date_yyyy_mm not in plot_months:
					plot_months[plot.end_date_yyyy_mm] = 0
				plot_months[plot.end_date_yyyy_mm] += 1

		total:int = 0
		for date in sorted(plot_months):
			count = plot_months[date]
			print(f'{date}    - {count:4}')
			total += count
		print(f'Total      - {total:4}')
		print()

		total:int = 0
		for date in sorted(plot_days):
			count = plot_days[date]
			print(f'{date} - {count:4}')
			total += count
		print(f'Total      - {total:4}')

	def print (self) -> None:
		if self._config.is_csv:
			pass

		if self._config.is_json:
			pass

		if self._config.is_markdown:
			pass

class PlotConfigurations:
	'''
	Manages all plot configurations, as found in the chia-log.yaml file.
	'''

	def __init__ (self) -> None:
		self._plot_configs:Dict[str, PlotConfiguration] = {}

	@property
	def plot_configs (self) -> List[PlotConfiguration]:
		return [plot_config for plot_config in self._plot_configs.values()]

	def get_plot_config (self, name:str) -> PlotConfiguration:
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

		# thread count, phase 1 - 5, list of values (seconds for each phase)
		self.rows:Dict[int, Dict[int, List[float]]] = {}

		# number of plots with this configuration; key is threads, value is plot count
		self._plot_count:Dict[int, int] = {}

	def append (self, threads:int, phase:int, value:float) -> None:
		if threads not in self.rows:
			self.rows[threads] = {}
		if phase not in self.rows[threads]:
			self.rows[threads][phase] = []
		self.rows[threads][phase].append(value)

	def avg (self, threads:int, phase:int) -> int:
		return int(mean(self.rows[threads][phase]))

	def increment_plot_count (self, threads:int) -> None:
		if threads not in self._plot_count:
			self._plot_count[threads] = 0
		self._plot_count[threads] += 1

	def print (self) -> None:
		print(f'Disk - {self.name}')
		for threads in self.rows:
			print(f'  threads {threads} count {self._plot_count[threads]:4} p1 {self.avg(threads, 1):6,} p2 {self.avg(threads, 2):6,} p3 {self.avg(threads, 3):6,} p4 {self.avg(threads, 4):6,} tot {self.avg(threads, 5):6,}')
