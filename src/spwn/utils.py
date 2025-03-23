import subprocess
from pwn import log, context, options
from pwnlib.log import Progress, Logger

log_silent = context.silent


def ask(prompt: str, can_skip: bool = True) -> str:
	while True:
		received = input(f" [?] {prompt} > ")
		if received or can_skip: return received
		log.warning("Can't skip")


def choose(prompt: str, opts: list, default: int | None = None) -> int:
	assert opts
	if len(opts) == 1: return 0
	return options(prompt, list(map(str, opts)), default)


def run_command(args: list | str, progress_log: Progress | Logger = log, **kwargs) -> str | None:
	"""Run a command, logging out failures msg in the progress or in the log"""
	
	assert args
	cmd = args.split(" ")[0] if isinstance(args, str) else args[0]

	# Try executing command
	try:
		return subprocess.check_output(args, stderr=subprocess.DEVNULL, text=True, **kwargs)

	# Handle command not found
	except FileNotFoundError as err:
		progress_log.failure(f"To execute this please install {cmd}")

	# Handle interrupt
	except KeyboardInterrupt as err:
		progress_log.failure(f"{cmd} interrupted")

	# Handle errors
	except subprocess.CalledProcessError as err:
		progress_log.failure(f"{cmd} failed")
		log.debug(err)
		log.debug(err.stderr)

	# Handle timeout
	except subprocess.TimeoutExpired as err:
		log.debug(f"{cmd} timeout")
		return ""

	return None
