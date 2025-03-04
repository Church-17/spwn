from spwn.exe import Exe
from spwn.libc import Libc
from spwn.loader import Loader
from spwn.utils import run_command, ask
from pwn import options
import os
import shutil

def recognize_binaries(
		dirpath: str,
		exe_path: str | None = None,
		libc_path: str | None = None,
		loader_path: str | None = None,
	) -> tuple[Exe | None, Libc | None, Loader | None]:
	"""Recognize the executable, libc and loader from a directory. 'None' means to search for that element, an empty string to not search"""
	
	# If there are not all of them, recognize them from file
	if (exe_path is None) or (libc_path is None) or (loader_path is None):

		# Get all possible exes, libcs and loaders
		exes: list[str] = []
		libcs: list[str] = []
		loaders: list[str] = []
		for file in os.listdir(dirpath):
			file = os.path.join(dirpath, file)
			if (exe_path is None) and Exe.check_filetype(file):
				exes.append(file)
			if (libc_path is None) and Libc.check_filetype(file):
				libcs.append(file)
			if (loader_path is None) and Loader.check_filetype(file):
				loaders.append(file)

		# Select binaries
		if exes: exe_path = exes[(options("Select executable:", exes) if len(exes) > 1 else 0)]
		if libcs: libc_path = libcs[(options("Select libc:", libcs) if len(libcs) > 1 else 0)]
		if loaders: loader_path = loaders[(options("Select loader:", loaders) if len(loaders) > 1 else 0)]

	# Create binaries objects
	exe = Exe(exe_path) if exe_path else None
	libc = Libc(libc_path) if libc_path else None
	loader = Loader(loader_path) if loader_path else None

	return (exe, libc, loader)


def create_debug_dir(
		debug_dir: str,
		libs_path: str | None = None,
		exe: Exe | None = None,
		libc: Libc | None = None,
		loader: Loader | None = None,
	) -> tuple[str]:
	"""Create debug dir, populate it, update debug paths"""

	# Check if debug dir exists, in case ask for a new name
	while os.path.exists(debug_dir):
		new_name = ask(f"{debug_dir} already exists: type another name or leave empty to overwrite")
		if new_name:
			debug_dir = new_name
		else:
			shutil.rmtree(debug_dir)
			break

	# Create debug dir
	os.mkdir(debug_dir)

	# If libs are been downloaded...
	if libs_path:

		# Copy the libs requested by the exe from libs path to debug dir (if not exe, copy all of them)
		libs_to_copy = set(os.listdir(libs_path))
		if exe:
			libs_to_copy = libs_to_copy & {os.path.basename(lib) for lib in exe.libs}
		for lib in libs_to_copy:
			shutil.copy2(os.path.join(libs_path, lib), debug_dir)

			# From the copied libs, identify libc and loader, and update their debug path
			filepath = os.path.join(debug_dir, lib)
			if libc and Libc.check_filetype(filepath):
				libc.debug_path = filepath
			elif loader and Loader.check_filetype(filepath):
				loader.debug_path = filepath

	# If download libs failed, fall back to the cwd

	elif exe:
		# Copy the libc and the loader from cwd, with the names requested by the exe
		for lib in exe.libs:
			filepath = os.path.join(debug_dir, lib)
			if Libc.check_filetype(lib):
				shutil.copy2(libc.path, filepath)
				libc.debug_path = filepath
			elif loader and Loader.check_filetype(lib):
				shutil.copy2(loader.path, filepath)
				loader.debug_path = filepath

	# Return the actual debug dir
	return debug_dir
