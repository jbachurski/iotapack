# iotapack

`iotapack` is a simple tool for compiling SIO2 problem packages.

Use `iotapack --help` for to get help.

positional arguments:
  `name`                  The name for the problem (the ID that is used in
                        SIO2).
  `model`                 Relative directory to the model solution source.
  `lang`                  Either 'py' or 'cpp'. If 'cpp', then there must be a
                        compiled version in the same directory.
  `inputs`                The directory with .in input files.
  `doc`                   Problem statement file.

optional arguments:
  `-h, --help`            show this help message and exit
  `-c CFG, --cfg CFG`     The .yml config file
  `-a ADDSOL, --addsol ADDSOL`
                        Specify an additional solution (can be used multiple
                        times)
  `-ps PDFSRC, --pdfsrc PDFSRC`
                        Embed the pdf source (probably a .tex file)
  `-z, --zip`             Flag that creates a zip file immediately after packing
                        is done
