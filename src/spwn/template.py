from pathlib import Path
import re
from spwn.placeholders import *
from spwn.utils import log
from spwn.file_manage import fix_if_exist
from spwn.exe import Exe
from spwn.libc import Libc
from spwn.interactions import Interactions


def create_script(
		template: Path,
		script: Path,
		remote: str | None = None,
		exe: Exe | None = None,
		libc: Libc | None = None,
		interactions: Interactions | None = None,
	) -> None:

	# Check template file
	if not template.is_file():
		log.failure("Template file doesn't exists. A new script will not be created")
		return

	# Read template file
	template_content = template.read_text()

	# Search of tabs before interactions
	match = re.search(rf"([ \t]*){INTERACTIONS}", template_content)
	tab_interactions_placeholder: str = match.group(1) if match else ""

	# Handle host and port from remote
	host, port = remote.split(":", 1) if remote and ":" in remote else (None, None)

	# Replace placeholders
	new_content = (template_content
		.replace(REMOTE, (remote or "REMOTE"))
		.replace(HOST, (host or "HOST"))
		.replace(PORT, (port or "PORT"))
		.replace(EXE_BASENAME, (exe.path.name if exe else "EXE_BASENAME"))
		.replace(EXE_RELPATH, (str(exe.path.relative_to(Path.cwd(), walk_up=True)) if exe else "EXE_RELPATH"))
		.replace(EXE_ABSPATH, (str(exe.path.resolve()) if exe else "EXE_ABSPATH"))
		.replace(EXE_DEBUG_BASENAME, (exe.debug_path.name if exe else "EXE_DEBUG_BASENAME"))
		.replace(EXE_DEBUG_RELPATH, (str(exe.debug_path.relative_to(Path.cwd(), walk_up=True)) if exe else "EXE_DEBUG_RELPATH"))
		.replace(EXE_DEBUG_ABSPATH, (str(exe.debug_path.resolve()) if exe else "EXE_DEBUG_ABSPATH"))
		.replace(LIBC_BASENAME, (libc.path.name if libc else "LIBC_BASENAME"))
		.replace(LIBC_RELPATH, (str(libc.path.relative_to(Path.cwd(), walk_up=True)) if libc else "LIBC_RELPATH"))
		.replace(LIBC_ABSPATH, (str(libc.path.resolve()) if libc else "LIBC_ABSPATH"))
		.replace(LIBC_DEBUG_BASENAME, (libc.debug_path.name if libc else "LIBC_DEBUG_BASENAME"))
		.replace(LIBC_DEBUG_RELPATH, (str(libc.debug_path.relative_to(Path.cwd(), walk_up=True)) if libc else "LIBC_DEBUG_RELPATH"))
		.replace(LIBC_DEBUG_ABSPATH, (str(libc.debug_path.resolve()) if libc else "LIBC_DEBUG_ABSPATH"))
		.replace(LIBC_ID, (libc.libc_id if libc and libc.libc_id else "LIBC_ID"))
		.replace(LIBC_VERSION, (libc.libc_version if libc and libc.libc_version else "LIBC_VERSION"))
		.replace(INTERACTIONS, (interactions.dump(tab_interactions_placeholder) if interactions else ""))
	)

	# Write new script
	script = fix_if_exist(Path(str(script).replace(EXE_BASENAME, (exe.path.name if exe else ""))))
	script.write_text(new_content)
	log.success(f"Script \'{script}\' created")
