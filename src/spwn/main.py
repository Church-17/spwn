import os
from spwn.args import Args
from spwn.config import Config
from spwn.file_manage import recognize_exe, recognize_libs
from spwn.exe import Exe
from spwn.libc import Libc
from spwn.interactions import Interactions
from spwn.template import Template

def main():

	# Parse args and config
	args = Args()
	config = Config(args)

	# List files of cwd
	cwd_files = os.listdir()

	# Recognize exe
	exe_path = recognize_exe(cwd_files)
	if exe_path:
		os.chmod(exe_path, 0o755)
		exe = Exe(exe_path)
	else:
		exe = None

	# Recognize libs
	if (not exe) or (not exe.statically_linked):
		cwd_libs = recognize_libs(cwd_files)

		# Recognize libc
		libc = Libc(cwd_libs["libc"]) if "libc" in cwd_libs else None
		if libc:
			# Download libc source
			if config.download_libc_source: libc.download_source()

			print()

	if exe:
		# Describe
		exe.describe()
		exe.check_functions(config.check_functions)

		# Patch exe (checking exe.statically_linked, libc and cwd_libs are not unbound)
		if config.patch_path and (not exe.statically_linked): exe.patch(config.patch_path, cwd_libs, libc)

		# Analyze
		if config.seccomp: exe.seccomp()
		if config.yara_rules: exe.yara(config.yara_rules)
		if config.cwe: exe.cwe()
		print()

	if config.template_file:

		# Interactions
		interactions = Interactions(config.pwntube_variable, config.tab) if config.interactions else None
		
		# Create script
		template = Template(config.template_file)
		template.create_script(config.script_basename, args.remote, exe, libc, interactions)

