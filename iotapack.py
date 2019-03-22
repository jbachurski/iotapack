import argparse
import time
import os
import sys
import glob
import zipfile
import shutil
import traceback
from pathlib import Path

def trimcwd(p):
    return os.path.relpath(str(p), str(Path.cwd()))

def copy_file(src, dest):
    print(f"{trimcwd(src)} --> {trimcwd(dest)}")
    shutil.copy(str(src), str(dest))
    
def zipdir(path, ziph):
    for root, dirs, files in os.walk(path):
        for file in files:
            ziph.write(os.path.join(root, file))

def convert_crlf_to_lf(file):
    with file.open(mode="rb") as f:
        data = f.read()
    data = data.replace(b"\r\n", b"\n")
    with file.open(mode="wb") as f:
        f.write(data)

def main(name, model, lang, inputs, doc, cfg, add_sol, pdf_src=None, do_zip=False):
    start = time.time()
    
    model = Path.cwd() / Path(model)
    inputs = Path.cwd() / Path(inputs)
    doc = Path.cwd() / Path(doc)
    
    assert lang in ("py", "cpp")

    if lang == "py":
        model_caller = str(model)
    elif lang == "cpp":
        model_caller = str(model)[:-4] + (".exe" if sys.platform == "win32" else "")

    base = Path.cwd() / name
    
    shutil.rmtree(base, ignore_errors=True)
    while os.path.exists(str(base)):
        pass

    (base / "doc").mkdir(parents=True, exist_ok=True)
    copy_file(doc, base / "doc" / f"{name}zad.pdf")

    (base / "prog").mkdir(parents=True, exist_ok=True)
    copy_file(model, base / "prog" / f"{name}.{lang}")

    (base / "in").mkdir(parents=True, exist_ok=True)
    (base / "out").mkdir(parents=True, exist_ok=True)
    print("Looking for inputs", str(inputs / "*.in"))
    for file in glob.glob(str(inputs / "*.in")):
        file = Path(file)

        infile  = (base / "in"  / (f"{name}" + file.name))
        outfile = (base / "out" / (f"{name}" + file.name[:-3] + ".out"))

        copy_file(file, infile)

        print(f"$ {trimcwd(model_caller)} < {trimcwd(infile)} > {trimcwd(outfile)}")
        os.system(f"{model_caller} < {infile} > {outfile}")

        if sys.platform == "win32":
            convert_crlf_to_lf(infile)
            convert_crlf_to_lf(outfile)
    
    if cfg is not None:
        copy_file(Path(cfg), base / "config.yml")
    
    if add_sol is not None:
        for sol_f in add_sol:
            sol_f = Path(sol_f)
            copy_file(sol_f, base / "prog" / sol_f.name)
    
    if pdf_src is not None:
        pdf_src = Path.cwd() / Path(pdf_src)
        copy_file(pdf_src, base / "doc" / pdf_src.name)

    if do_zip:
        print("zip... ", end="", flush=True)
        zipdir(f"{name}", zipfile.ZipFile(f"{name}.zip", "w", zipfile.ZIP_DEFLATED))
        print("done")
    
    finish = time.time()
    print(f"[!] done in: {round(finish - start, 3)}s")
        
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("name", help="The name for the problem (the ID that is used in SIO2).")
    parser.add_argument("model", help="Relative directory to the model solution source.")
    parser.add_argument("lang", help="Either 'py' or 'cpp'. If 'cpp', then there must be a compiled version in the same directory.")
    parser.add_argument("inputs", help="The directory with .in input files.")
    parser.add_argument("doc", help="Problem statement file.")
    parser.add_argument("-c", "--cfg", default=None, help="The .yml config file")
    parser.add_argument("-a", "--addsol", action="append", help="Specify an additional solution (can be used multiple times)")
    parser.add_argument("-ps", "--pdfsrc", default=None, help="Embed the pdf source (probably a .tex file)")
    parser.add_argument("-z", "--zip", action="store_true", help="Flag that creates a zip file immediately after packing is done")
    
    args = parser.parse_args()
    main(args.name, args.model, args.lang, args.inputs, args.doc, args.cfg, args.addsol, args.pdfsrc, args.zip)
