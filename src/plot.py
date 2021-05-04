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

		self.parameters = PlotParameters(logger)
		self.phase_1    = PlotPhase1(logger)
		self.phase_2    = PlotPhase2(logger)
		self.phase_3    = PlotPhase3(logger)
		self.phase_4    = PlotPhase4(logger)
		self.totals     = PlotTotals(logger)

	def extract (self, data:str) -> bool:
		'''Extract a plot. Return True if there was an error, otherwise False.'''

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
		# post-process each plot and add more information

		temp_dirs = self.parameters.temp_dirs
		dest_dir = self.totals.dest_dir
