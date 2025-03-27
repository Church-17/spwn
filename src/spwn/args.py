class Args:
	def __init__(self) -> None:

		args = self.parse_args()

		self.remote: str | None		= args["remote"]
		self.interactions: bool		= args["interactions"]
		self.template: str | None	= args["template"]
		self.only: bool				= args["only"]
		self.libc_source: bool		= args["libc_source"]
		self.patch: str | None		= args["patch"]
		self.seccomp: bool			= args["seccomp"]
		self.yara: str | None		= args["yara"]
		self.cwe: bool				= args["cwe"]

	def parse_args(self) -> dict[str]:
		"""Parse the arguments given to the command into a dict"""

		import argparse
		parser = argparse.ArgumentParser(
			prog="spwn",
			description="spwn is a tool to quickly start a pwn challenge",
		)
		parser.add_argument(
			"-r", "--remote",
			help="Specify the host:port",
		)
		parser.add_argument(
			"-i", "--interactions",
			help="Create the interactions",
			action="store_true",
		)
		parser.add_argument(
			"-t", "--template",
			help="Create the script from the template",
		)
		parser.add_argument(
			"-o", "--only",
			help="Do only the actions specified in args",
			action="store_true",
		)
		parser.add_argument(
			"--libc-source",
			help="Donwload the libc source",
			action="store_true",
		)
		parser.add_argument(
			"--patch",
			help="Patch the executable with the specified path",
		)
		parser.add_argument(
			"--seccomp",
			help="Check seccomp",
			action="store_true",
		)
		parser.add_argument(
			"--yara",
			help="Check for given Yara rules",
		)
		parser.add_argument(
			"--cwe",
			help="Check for CWEs",
			action="store_true",
		)
		return parser.parse_args().__dict__
