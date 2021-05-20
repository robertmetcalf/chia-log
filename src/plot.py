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
		self.parameters = PlotParameters(logger)
		self.phase_1    = PlotPhase1(logger)
		self.phase_2    = PlotPhase2(logger)
		self.phase_3    = PlotPhase3(logger)
		self.phase_4    = PlotPhase4(logger)
		self.totals     = PlotTotals(logger)

		# determined after the log file is processed
		self.name:str = ''			# plot configurations for categorizing plot types
		self.end_date:str = ''		# end date yyyy-mm-dd

	def extract (self, data:str) -> bool:
		'''
		Extract a plot. Return True if there was an error, otherwise False.
		'''

		if self.parameters.extract(data):
			return True

		if self.phase_1.extract(data):
			return True

		if self.phase_2.extract(data):
			return True

		if self.phase_3.extract(data):
			return True

		if self.phase_4.extract(data):
			return True

		if self.totals.extract(data):
			return True

		return False

	def post_process (self) -> None:
		'''
		Post-process each plot and add more information.
		'''

		self._set_plot_type()
		self._set_plot_date()

	def _set_plot_type (self) -> None:
		'''
		Determine the plot type based on the "temp" and "dest" directory settings.
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

	def _set_plot_date (self) -> None:
		'''
		Set the date this plot completed, which is used to determine the number
		of plots per day.
		'''

		et = self.totals.end_time
		if et:
			self.end_date = f'{et.year:04}-{et.month:02}-{et.day:02}'
