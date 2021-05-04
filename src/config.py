# system packages
from pathlib import Path
from typing  import Any, Dict, List
import pprint

# third party packages
import yaml

# local packages
from src.logger import Logger


class Config:
	def __init__ (self):
		# CLI options
		self._option_config:str  = ''			# --config file
		self._option_file:str    = ''			# --file to process
		self._option_output:str  = ''			# --output format
		self._option_verbose:int = 0 			# --verbose logging

		# directories section
		self._log_directories:List[Path] = []	# a list of log directories

		# files section
		self._patterns:List[str]         = []	# log file patterns to look for

		# is the configuration valid
		self._valid:bool = False
		self._logger = Logger()

	@property
	def file (self) -> str:
		return self._option_file

	@property
	def log_directories (self) -> List[Path]:
		'''Log path directories to analyze'''

		return self._log_directories

	@property
	def logger (self) -> Logger:
		return self._logger

	@property
	def patterns (self) -> List[str]:
		return self._patterns

	@property
	def valid (self) -> bool:
		'''Is the configuration valid (True) or not (False)'''

		return self._valid

	@property
	def verbose (self) -> int:
		return self._option_verbose

	def cli_options ( self, option_config:str, option_file:str, option_output:str, option_verbose:int) -> None:
		self._option_config:str  = option_config	# --config file
		self._option_file:str    = option_file		# --file to process
		self._option_output:str  = option_output	# --output format
		self._option_verbose:int = option_verbose 	# --verbose logging

		# validate the configuration file and command-line arguments
		valid_con = self._validate_config()
		valid_cli = self._validate_cli()
		self._valid = valid_con and valid_cli

		self._logger.set_log_level(self._option_verbose)

	def _validate_config (self) -> bool:
		'''Validate the configuration file'''

		cfg:Dict[str, Any] = {}

		# read the configuration file
		config_file = Path(self._option_config).resolve()
		if not config_file.exists():
			print(f'Error: config file does not exist ({config_file})')
			return False

		with open(config_file, 'r') as yaml_file:
			try:
				cfg = yaml.load(yaml_file, Loader=yaml.SafeLoader)
			except yaml.YAMLError as e:
				if hasattr(e, 'problem_mark'):
					mark = getattr(e, 'problem_mark')
					print(f'Error: in config file, yaml error, line {mark.line + 1}, column {mark.column + 1}')
					return False

		# the "directories" section
		if cfg and 'directories' in cfg:
			directories:Dict[str, Any] = cfg['directories']

			if directories and 'logs' in directories:
				logs:List[str] = directories['logs']

				if logs:
					for log in logs:
						log_path = Path(log).resolve()
						if log_path.exists():
							self._log_directories.append(log_path)
						else:
							print(f'Error: in config file, log directory does not exist -> {log}')

		if not self._log_directories:
			print(f'Error: in config file, no valid log directories found')
			return False

		# the "files" section
		if cfg and 'files' in cfg:
			files:Dict[str, Any] = cfg['files']

			if files and 'patterns' in files:
				patterns:List[str] = files['patterns']

				if patterns:
					for pattern in patterns:
						self._patterns.append(pattern)

		# the "logging" section
		if cfg and 'logging' in cfg:
			logging:Dict[str, Any] = cfg['logging']

			if logging and 'level' in logging:
				level:str = logging['level'].lower()

				levels = ['error', 'warn', 'info', 'debug']
				if level in levels:
					# set the verbose level only it it's not already set
					if self._option_verbose == 0:
						self._option_verbose = levels.index(level)

		# the "plots" section
		if cfg and 'plots' in cfg:
			plots:List[Any] = cfg['plots']

			for plot in plots:
				pass

		pp = pprint.PrettyPrinter(indent=4)
		pp.pprint(cfg)

		return True

	def _validate_cli (self) -> bool:
		'''Validate the CLI arguments'''

		valid = True

		# --config - validate the config file
		if self._option_config:
			p = Path(self._option_config).resolve()
			if not p.exists():
				print(f'Error: config file does not exist ({self._option_config})')
				valid = False

		# --file - validate if a specified file exists
		if self._option_file:
			p = Path(self._option_file).resolve()
			if not p.exists():
				print(f'Error: file does not exist ({self._option_file})')
				valid = False

		# --output - validate the output type (csv, json, md, or markdown)
		if self._option_output:
			valid_output = ['csv', 'json', 'markdown', 'md']
			if self._option_output.lower() not in valid_output:
				print(f'Error: output type not valid ({self._option_output})')
				valid = False

		# --verbose - validate the number of verbose flags
		if self._option_verbose > 3:
			print(f'Error: three (3) verbose flags is the limit, you specified {self._option_verbose}')
			valid = False

		return valid
