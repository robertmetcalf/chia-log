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

	def __init__ (self, config:Config):
		self._config = config

	def process (self, plots:List[Plot]) -> None:
		# for each mount type
		disks = Disks()

		for plot in plots:
			disk = disks.get_disk(plot.disk)
			disk.inc_plot_count()
			disk.append(1, plot.phase_1.total_time)
			disk.append(2, plot.phase_2.total_time)
			disk.append(3, plot.phase_3.total_time)
			disk.append(4, plot.phase_4.total_time)
			disk.append(5, plot.totals.total_time)

		for disk in disks.disks:
			print(f'Disk - {disk.comment} count {disk.plot_count}')
			for phase in range(1, 6):
				print(f'p{phase} {disk.avg(phase)}')

		# find the total time, in seconds, for each phase

	def print (self) -> None:
		pass

class Disks:
	'''
	Manages individual disks, as found in the chia-log.yaml file.
	'''

	def __init__ (self):
		self._disks:Dict[str, Disk] = {}

	@property
	def disks (self) -> List[Disk]:
		return [disk for disk in self._disks.values()]

	def get_disk (self, comment:str) -> Disk:
		if comment not in self._disks:
			self._disks[comment] = Disk(comment)

		return self._disks[comment]


class Disk:
	'''
	Manage an individual disk configuration.
	'''

	def __init__ (self, comment:str) -> None:
		self.comment = comment
		self.phases:Dict[int, List[float]] = {}
		self._plot_count = 0

		for phase in range(1, 6):
			self.phases[phase] = []

	@property
	def plot_count (self) -> int:
		return self._plot_count

	def append (self, phase:int, value:float) -> None:
		self.phases[phase].append(value)

	def avg (self, phase:int) -> int:
		return int(mean(self.phases[phase]))

	def inc_plot_count (self) -> None:
		self._plot_count += 1