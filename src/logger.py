class Logger:
	def __init__ (self, verbose:int):
		self._verbose:int = verbose

	def error (self, t:str) -> None:
		'''Errors are always printed'''

		print(f'Error: {t}')

	def warn (self, t:str) -> None:
		'''Warnings are the minimum level of logging'''

		if self._verbose >= 1:
			print(f'Warn: {t}')

	def info (self, t:str) -> None:
		'''Info is the 2nd level of logging'''

		if self._verbose >= 2:
			print(f'Info: {t}')

	def debug (self, t:str) -> None:
		'''Debug is the most verbose level of logging'''

		if self._verbose == 3:
			print(f'Debug: {t}')
