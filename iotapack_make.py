import argparse
import zipfile
import os

def main():
    base = os.path.dirname(os.path.realpath(__file__))
    with zipfile.ZipFile(os.path.join(base, "template.zip")) as archive:
        archive.extractall(".")

if __name__ == "__main__":
    main()
