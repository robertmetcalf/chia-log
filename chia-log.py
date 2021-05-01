#!/usr/bin/env python

# system packages
from pathlib import Path
import argparse

# third party packages

# local packages
#from src.analyze  import Analyze
from src.config   import Config
from src.logfiles import LogFiles


class Main:
	'''
	This is the "main" driver for chia-log.py.
	'''

	def __init__ (self, config:Config):
		self._config = config

	def run (self) -> None:
		# Process log files; a log file may contain more than one plot entry.
		# For example, the user ran "chia plots create -n 8 > log.txt", which
		# creates 8 plots and re-directs the output to one log file.
		log_files = LogFiles(self._config)

		if self._config.file:
			# process a single file
			file = Path(self._config.file).resolve()
			log_files.extract(file)

		else:
			# process each log file directory (in the config file)
			for log_directory in self._config.log_directories:
				# look for log files that match a pattern (*.log, etc.)
				for pattern in self._config.patterns:
					files = log_directory.glob(f'**/{pattern}')
					if files:
						for file in sorted(files):
							self._config.logger.debug(f'files - {file}')
							log_files.extract(file)

		print(f'Processed {len(log_files.files)} files containing {len(log_files.plots)} plots')


		#print(f'Debug: analyze {analyze.log_files} files')

		#analyze = Analyze()

		#analyze.print(config)


if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='Process chia log files.')
	parser.add_argument('-c', '--config', type=str, default='chia-log.yaml', help='configuration file')
	parser.add_argument('-f', '--file', type=str, default='', help='process a specific file')
	parser.add_argument('-o', '--output', type=str, default='csv', help='output format (csv, json, or markdown)')
	parser.add_argument('-v', '--verbose', action='count', default=0, help='')
	args = parser.parse_args()

	config = Config(args.config, args.file, args.output, args.verbose)
	if config.valid:
		main = Main(config)
		main.run()
