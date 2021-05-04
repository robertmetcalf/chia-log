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

	def __init__ (self, config:Config):
		self._config = config

		logger = config.logger

		# extracted from the log file
		self.parameters = PlotParameters(logger)
		self.phase_1    = PlotPhase1(logger)
		self.phase_2    = PlotPhase2(logger)
		self.phase_3    = PlotPhase3(logger)
		self.phase_4    = PlotPhase4(logger)
		self.totals     = PlotTotals(logger)

		# determined after the log file is processed
		self.disk:str = ''		# disk configurations for categorizing plot types

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

	def _set_plot_type (self) -> None:
		'''
		Determine the plot type based on the "temp" and "dest" directory settings.
		'''

		# get the temp and dest directories for this plot
		dest_dir = str(self.totals.dest_dir)
		temp_dir_1, temp_dir_2 = self.parameters.temp_dirs	# at the top of the log file

		# match the dest and temp directories to a "mount" entry in the config file
		for disk in self._config.disks:
			if dest_dir in disk['dest']:
				if temp_dir_1 in disk['temp'] and temp_dir_2 in disk['temp']:
					self.disk = disk['comment']
					break
