# Spwn

This repository started as a fork of [the original spwn](https://github.com/MarcoMeinardi/spwn). It was a good tools for initialize a PWN challenge, but I wanted more customization, and since it had not been maintained for a couple of years, I started to look into the code to give more freedom to the user. In the end, I ended up completely refactoring the code and adding some useful features.

## Features
- Auto detect files (binary, libc, loader)
- Print basic info about the files:
  - `checksec`
  - libc version
  - potentially vulnerable functions
  - cryptographic constants
  - seccomp rules
  - CWEs
- Download and unstrip the libs and the loader related to the libc
- Download the libc source code
- Download loader from libc version (if missing)
- Set binary and loader executable
- Set runpath and interpreter for the debug binary
- Interactively generate functions to interact with the binary
- Generate a basic script from a template
- Launch custom user-provided commands

## Usage
```
spwn [-h] [-i] [-so] [-io] [-nd] [--config] [{inter,i,ionly,io,nd,nodecomp,config} ...] [template]

options:
  -h, --help       show this help message and exit
  -i, --inter      Interactively create interaction functions
  -so, --sonly     Create the interaction script without analyzing the binary
  -io, --ionly     Create the interaction functions, without doing any analysis
  -nd, --nodecomp  Don't open the decompiler
  --config         Setup configs and quit
```

If the files have weird names (such as the libc name not starting with
"libc"), the autodetection will fail and fall in the manual selection,
the best fix for this is to rename the files.

To understand how the interactions creation works, I suggest to just try
it out. It should be pretty straight forward, but if you want to pwn
as fast as possible, you cannot waste any time :)

## Installation
Non python tools:
```bash
sudo apt update
sudo apt install patchelf elfutils ruby-dev
# Or the equivalent for you package manager
sudo gem install seccomp-tools  # Might not need `sudo`
```
To install [cwe_checker](https://github.com/fkie-cad/cwe_checker)
follow the instructions in their repository.

Main package:
```
pip install spwn
```
You might need to add `~/.local/bin/` to your `$PATH`

## Files layout
Files in the current working directory don't get modified. If there is
any library, the `debug_dir` directory gets created, all the `ELF`s get
copied there and the binary in that folder is modified to set the run
path and the interpreter. Everything is set relative to the current
working directory, thus, even if the files you want to work with are in
`./{debug_dir}/`, you should run everything from the current working directory.
If there is only one binary, no `debug_dir` gets created, because there is no
need to modify it.

## Customization
This tool is written because I wanted to customize `pwninit` as much
as possible. If you want to customize your own `spwn` you can:
 - Clone this repo
 - Modify whatever you want
 - In the repository's root directory: `pip install -U .`

or directly modify the files in:
`~/.local/lib/python3.{version}/site-packages/spwn`

Note that the default configurations and templates, gets written
only if they are not already present (or updated if some fields
are missing), so, if you want to customize those, you have to
modify the files as specified in the configurations section.

## Configurations
You can configure some stuffs in the `config.json` file. Configuration
gets written in `~/.config/spwn/` in the first run of `spwn` or by
calling `spwn --setup`. In the same directory you will also find
`template.py`, the template of the script generated by `spwn`, which
you can modify to your liking.

This is the default `config.json` file:
```json
{
    "debug_dir": "debug_dir",
    "script_file": "a.py",
    "pwn_process": "r",
    "tab": "\t",
    "template_file": "~/.config/spwn/template.py",
    "custom_template_prefix": "template_",
    "suppress_warnings": false,
    "yara_rules": "~/.config/spwn/findcrypt3.rules",
    "preanalysis_commands": [],
    "postanalysis_commands": [],
    "preanalysis_scripts": [],
    "postanalysis_scripts": [],
    "idafree_command": "",
    "decompiler_command": ""
}
```

### Multiple templates
You can have multiple templates and select which one to use from command
line. You have to place your templates in the same directory of the base
template (`template_file`), and name it
`{custom_template_prefix}{name}.py`. To use it, you just have to specify
`name` in the command line (`spwn {name}`).

The whole file will be treated as a format string, so, be careful to put
double curly brackets if they don't have to be treated as format
specifiers (`my_set = {{1, 2, 3}}`). The actual format specifiers (which
you have to place in single curly brackets) are: `{binary}`, `{libc}`,
`{debug_dir}` and `{interactions}`.

### Suppress warnings
If set to `true`, don't show warning messages for non installed non-vital
dependencies.

### Custom commands
The pre and post analysis commands, are in the form `[command, timeout]`.
`command` is a list of strings and should contain the `"{binary}"` or
`"{debug_binary}"` string in order to be formatted with the correct
executable path. You should use `debug_binary` only in the post analysis
and if your command will run the binary. If you set `timeout` to `false`,
the program gets run with `subprocess.Popen`, thus the analysis will go
on while running it and the process will go on after `spwn` will have
terminated. This might be used, for example, to run the ROP-gadgets
search in the background. If you want to run the program without a
timeout (discouraged) you can set it to `null`. A couple of examples are:
```
["one_gadget {binary}", 1]
["ropr -njs {debug_binary} > gadgets", false]
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
    # libc and loader have their own type that are a subclasses of `Binary`
    self.other_binaries  # list of relative paths

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
post analysis commands. I created a special config, rather than
putting it in a pre analysis command, because I use IDA freeware
and it can decompile only x86/x86_64 binaries, so I have to use another
decompiler for other architectures (I have created this feature
before the custom scripts thing, but since the decompiler is
something that you will almost always launch, I left it to make
it easier to use). If you want to use always the same decompiler,
leave `idafree_command` empty and if you don't want to launch any
decompiler, just leave both configs empty. If you wish to modify
the conditions to select the decompiler, you can either modify
the `open_decompiler` function in `analyzer.py` or create a
custom script.

---
If you have any question or feature request, feel free to ask
[here](https://github.com/MarcoMeinardi/spwn/issues).
