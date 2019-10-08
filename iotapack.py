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

def get_ext(filename):
    return os.path.splitext(filename)[1][1:]

def wait_while(condition, timeout=5):
    start = time.time()
    while condition() and time.time() - start < timeout:
        pass
    if condition():
        raise ValueError(f"Condition '{condition}' timed out")

def main(name, model, lang, inputs, doc, cfg=None, add_sol=None, pdf_src=None, checker=None, outputs=False, do_zip=False, fullcleanup=False):
    start = time.time()
    cleanup = []

    model = Path.cwd() / Path(model)
    inputs = Path.cwd() / Path(inputs)

    force_doc_ext = None
    if get_ext(doc) == "html":
        _doc = doc
        doc = f"{name}doc.tmp.html.zip"
        with zipfile.ZipFile(doc, mode='w') as doczip:
            doczip.write(_doc, arcname="index.html")
        cleanup.append(doc)
        force_doc_ext = "html.zip"
    elif get_ext(doc) == "zip":
        force_doc_ext = "html.zip"

    doc = Path.cwd() / Path(doc)

    assert lang in ("py", "cpp")

    if lang == "py":
        model_caller = str(model)
    elif lang == "cpp":
        model_caller = str(model)[:-4] + (".exe" if sys.platform == "win32" else "")

    base = Path.cwd() / name

    shutil.rmtree(base, ignore_errors=True)
    wait_while(lambda: os.path.exists(str(base)))

    (base / "doc").mkdir(parents=True, exist_ok=True)
    copy_file(doc, base / "doc" / f"{name}zad.{force_doc_ext if force_doc_ext else get_ext(doc)}")

    (base / "prog").mkdir(parents=True, exist_ok=True)
    copy_file(model, base / "prog" / f"{name}.{lang}")

    (base / "in").mkdir(parents=True, exist_ok=True)
    (base / "out").mkdir(parents=True, exist_ok=True)

    if os.path.isdir(inputs):
        print("Looking for inputs", str(inputs / "*.in"))
        for file in sorted(glob.glob(str(inputs / "*.in"))):
            file = Path(file)

            infile  = (base / "in"  / (f"{name}" + file.name))
            copy_file(file, infile)

            if outputs:
                outfile = (base / "out" / (f"{name}" + file.name[:-3] + ".out"))
                print(f"$ {trimcwd(model_caller)} < {trimcwd(infile)} > {trimcwd(outfile)}")
                os.system(f"'{model_caller}' < '{infile}' > '{outfile}'")

                if sys.platform == "win32":
                    convert_crlf_to_lf(infile)
                    convert_crlf_to_lf(outfile)
    else:
        copy_file(inputs, base / "prog" / f"{name}ingen.{get_ext(inputs)}")

    if cfg is not None:
        copy_file(Path(cfg), base / "config.yml")

    if add_sol is not None:
        for sol_f in add_sol:
            sol_f = Path(sol_f)
            copy_file(sol_f, base / "prog" / sol_f.name)

    if pdf_src is not None:
        pdf_src = Path.cwd() / Path(pdf_src)
        copy_file(pdf_src, base / "doc" / pdf_src.name)

    if checker is not None:
        checker = Path.cwd() / Path(checker)
        copy_file(checker, base / "prog" / f"{name}chk.{get_ext(str(checker))}")

    if do_zip:
        print("Zipping... ", end="", flush=True)
        with zipfile.ZipFile(f"{name}.zip", "w", zipfile.ZIP_DEFLATED) as arc:
            arc.writestr(zipfile.ZipInfo(f"{name}/doc/"), "")
            arc.writestr(zipfile.ZipInfo(f"{name}/prog/"), "")
            arc.writestr(zipfile.ZipInfo(f"{name}/in/"), "")
            arc.writestr(zipfile.ZipInfo(f"{name}/out/"), "")
            zipdir(f"{name}", arc)
        print("done")

    finish = time.time()

    if cleanup:
        print("Cleaning up...")
        for file in cleanup:
            print(f"## {file}")
            os.remove(file)
    
    if fullcleanup:
        print("Cleaning up build directory...")
        shutil.rmtree(base, ignore_errors=True)

    print(f"[!] done in: {round(finish - start, 3)}s")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog="iotapack")
    parser.add_argument("name", help="The name for the problem (the ID that is used in SIO2).")
    parser.add_argument("model", help="Relative directory to the model solution source.")
    parser.add_argument("lang", help="Either 'py' or 'cpp'. If 'cpp', then there must be a compiled version in the same directory if outputs are generated.")
    parser.add_argument("inputs", help="The directory with .in input files or a cpp/py program for generating them.")
    parser.add_argument("doc", help="Problem statement file.")
    parser.add_argument("-c", "--cfg", default=None, help="The .yml config file")
    parser.add_argument("-a", "--addsol", action="append", help="Specify an additional solution (can be used multiple times)")
    parser.add_argument("-s", "--pdfsrc", default=None, help="Embed the text source (probably a .tex file)")
    parser.add_argument("-k", "--checker", default=None, help="Checker program, for checking the correctness of results")
    parser.add_argument("-o", "--outputs", action="store_true", help="Generate the outputs and embed them in the problem package.")
    parser.add_argument("-z", "--zip", action="store_true", help="Flag that creates a zip file immediately after packing is done")
    parser.add_argument("-f", "--fullcleanup", action="store_true", help="Remove the package directory after building (useful when zipping)")

    args = parser.parse_args()
    main(args.name, args.model, args.lang, args.inputs, args.doc, args.cfg, args.addsol, args.pdfsrc, args.checker, args.outputs, args.zip, args.fullcleanup)
