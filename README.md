# iotapack

`iotapack` is a simple tool for compiling SIO2 problem packages.

*Note: **all** paths are assumed to be relative to the current working directory.*

Requires Python 3.

Supports usage of input generation scripts, custom checkers and and HTML problem text.

Use `iotapack --help` for to get help.

positional arguments:
- `name`: The name for the problem (the ID that is used in SIO2).
- `model`: Relative directory to the model solution source.
- `lang`: Either 'py' or 'cpp'. If 'cpp', then there must be a compiled version in the same directory.
- `inputs`: The directory with .in input files or a cpp/py program for generating them.
- `doc`: Problem statement file.

optional arguments:
- `-h, --help`: show this help message and exit
- `-c CFG, --cfg CFG`: The .yml config file
- `-a ADDSOL, --addsol ADDSOL`: Specify an additional solution (can be used multiple times)
- `-ps PDFSRC, --pdfsrc PDFSRC`: Embed the pdf source (probably a .tex file)
- `-k CHECKER, --checker CHECKER`: Checker program, for checking the correctness of results
- `-z, --zip`: Flag that creates a zip file immediately after packing is done
