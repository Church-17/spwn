# Spwn

This repository started as a translation of
[pwninit](https://github.com/io12/pwninit). It has been created because I
love the utilities provided by pwninit, but I'm too lazy to learn Rust and
I wanted to customize it, so I rewrote it in python (and added
some more features).

## Features
 * Auto detect files (binary, libc, loader)
 * Get loader from libc version (if missing)
 * Unstrip the libc with `pwn.libcdb.unstrip_libc`
 * Set binary and loader executable
 * Set runpath and interpreter for the debug binary
 * Generate a basic script from a template
 * Interactively generate functions to interact with the binary
 * Print basic info about the files:
   * `file`
   * `checksec`
   * libc version
   * potentially vulnerable functions
   * cryptographic constants
   * seccomp rules
 * Launch decompiler
 * Launch custom user-provided commands

## Usage
```
spwn [inter|i|-i] [help|h|-h] [ionly|io|-io]
	- inter:
	    Interactively create interaction functions
	- help:
	    Print this message
	- ionly:
		Create the interaction functions, without doing any analysis
```

If the files have weird namings (such as the libc name not starting with
libc), the autodetection will fail and fall in the manual selection,
the best fix for this is to rename the files.

To understand how the interactions creation works, I suggest to just try
it out. It should be pretty straight forward, but if you want to pwn
as fast as possible, you cannot waste any time :)

## Installation
Non python tools:
```bash
sudo apt update
sudo apt install patchelf elfutils ruby-dev
sudo gem install seccomp-tools
```
Main package:
```
pip install git+https://github.com/MarcoMeinardi/spwn
```
You might need to add `~/.local/bin/spwn` to your `$PATH`

## Customization
This tool is written because I wanted to customize `pwninit` as much
as possible. If you want to customize your own `spwn` you can:
 - Clone this repo
 - Modify whatever you want
 - In the repository's root directory: `pip install -U .`

or directly modify the files in:
`~/.local/lib/python3.{version}/site-packages/spwn`

Note that `default-template.py` is copied only on the first installation,
thus, if you want to modify the template, you have to edit the
`template.py` file, specified in the configs.

## Configurations
You can configure some stuffs in the config file. It's default location
is `~/.config/spwn/config.json`. In the same directory you can also find
`template.py`, the template of the script generated by `spwn`, which
you can modify to your liking.

### Template
The template path can be directly edited in the config file, however,
if you want to change the location of the config file, you have to
edit the source code. The variable is `CONFIG_PATH` in `spwn.py`.
It's location should be
`~/.local/lib/python3.{python-version}/site-packages/spwn/spwn.py`.
Note that if you reinstall or update `spwn`,
this variable will be overwritten.

### Custom commands
For the pre and post analysis commands, they are in the form
`[command, timeout]`. The `command` should contain the `"{binary}"` or
`"{debug_binary}"` string in order to be formatted with the correct
executable path. You should use `debug_binary` only if your command
will run the binary. If you set `timeout` to `false`, the program gets
run with `subprocess.Popen`, thus the analysis will go on while
running it and the process will go on after `spwn` will have
terminated. This might be used, for example, to launch the decompiler.
If you want to run the program without a timeout (discouraged) you
can set it to `null`. A couple of examples are:
```
["command {binary}", 1]
["command {debug_binary} < /dev/null", false]
```

### Custom script
You can even run whole python scripts, all you have to do is to specify
their path in the `preanalysis_scripts` or `postanalysis_scripts`. If
you just provide the file name, it will be searched in the config
directory. The scripts must contain a `main` function that takes one
parameter: `files`. This parameter is a `FileManager` object and its
structure is as follows:
```python
class FileManager:
    # Three `Binary` objects
    self.binary
    self.libc    # Can be None
    self.loader  # Can be None
    # libc and loader have their own type that are a subclass of `Binary`
    self.other_binaries  # (all the other files) list of relative paths

class Binary:
    self.name  # relative path to the original binary
    self.debug_name  # relative path to the debug binary, if there is none it is equal to `self.name`
    self.pwnfile  # `pwn.ELF` object
```
For example:
```python
def main(files):
    print(f"The binary is {files.binary.name}")
```

### Decompiler
For the decompilers commands, the syntax is the same of the pre and
post analysis commands. I created an apposite config, rather than
putting it in a pre analysis command, because I use IDA freeware
and it can decompile only x86-64 binaries, so I have to use another
decompiler for other architectures. If you want to use always the
same decompiler, leave `idafree_command` empty and if you don't want
to launch any decompiler, just leave both configs empty. If you wish
to modify the conditions to select the decompiler, you will have to
modify the `open_decompiler` function in `analyzer.py`.

---
If you have any question or feature request, feel free to ask
[here](https://github.com/MarcoMeinardi/spwn/issues).
