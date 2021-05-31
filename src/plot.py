# system packages
from pathlib import Path

# local packages
from src.config         import Config
from src.plotparameters import PlotParameters
from src.plotphase1     import PlotPhase1
from src.plotphase2     import PlotPhase2
from src.plotphase3     import PlotPhase3
from src.plotphase4     import PlotPhase4
from src.plottotals     import PlotTotals


class Plot:
	'''
	Process a plot.
	'''

	def __init__ (self, config:Config, log_file:Path, index:int) -> None:
		self._config = config

		logger = config.logger

		self.log_file = log_file
		self.index = index

		# extracted from the log file
		self.parameters = PlotParameters(logger, index)
		self.phase_1    = PlotPhase1(logger, index)
		self.phase_2    = PlotPhase2(logger, index)
		self.phase_3    = PlotPhase3(logger, index)
		self.phase_4    = PlotPhase4(logger, index)
		self.totals     = PlotTotals(logger, index)

		# determined after the log file is processed
		self.name:str = ''					# plot name configurations for categorizing plot types
		self.end_date_yyyy_mm_dd:str = ''	# end date yyyy-mm-dd
		self.end_date_yyyy_mm:str = ''		# end date yyyy-mm

	def extract (self, data:str) -> bool:
		'''
		Extract a plot. Return True if the extract was good, otherwise False.
		'''

		if not self.parameters.extract(data):
			return False

		if not self.phase_1.extract(data):
			return False

		if not self.phase_2.extract(data):
			return False

		if not self.phase_3.extract(data):
			return False

		if not self.phase_4.extract(data):
			return False

		if not self.totals.extract(data):
			return False

		return True

	def set_plot_configuration (self) -> None:
		'''
		Determine the plot configuration based on the "temp" and "dest"
		directory settings.
		'''

		log_prefix = 'Plot'

		# get the dest and temp directories for this plot
		dest_dir = str(self.totals.dest_dir)
		temp_dir_1, temp_dir_2 = self.parameters.temp_dirs	# at the top of the log file

		# match the dest and temp directories to a "mount" entry in the config file
		found:bool = False
		for plot_config in self._config.plot_configurations:
			if dest_dir in plot_config['dest']:
				if temp_dir_1 in plot_config['temp'] and temp_dir_2 in plot_config['temp']:
					self.name = plot_config['name']
					found = True
					break

		if not found:
			self._config.logger.error(f'{log_prefix} plot config not found, temp-1 {temp_dir_1}, temp-2 {temp_dir_2}, dest {dest_dir}')

	def set_plot_date (self) -> None:
		'''
		Set the date this plot completed, which is used to determine the number
		of plots per day and month. Use the end date in the "totals" section.
		'''

		et = self.totals.end_time
		if et:
			self.end_date_yyyy_mm_dd = f'{et.year:04}-{et.month:02}-{et.day:02}'
			self.end_date_yyyy_mm = f'{et.year:04}-{et.month:02}'
