#! /usr/bin/env python
# -*- coding: utf-8 -*-

from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
from netcdf4 import concatDimension, NcDataset
from uuid import uuid4
from pathlib2 import Path

if __name__ == "__main__":

    parser = ArgumentParser(
        formatter_class=ArgumentDefaultsHelpFormatter,
        description="Merge given datasets along the timeaxis.")
    parser.add_argument("outfile", type=str, help="outputfile")
    parser.add_argument("infiles", type=str, nargs="+", help="inputfiles")
    parser.add_argument(
        "--dim", type=str, default="time", help="name of the time dimension")
    parser.add_argument(
        "--dimvar", type=str, default="time",
        help="name of the time dimension variable")
    parser.add_argument(
        "-o", "--overwrite", action="store_true", default=False,
        help="overwrite outputfile if it already exists")

    args = parser.parse_args()

    if args.outfile in args.infiles and args.overwrite is False:
        raise TypeError(
            "Don't want to overwrite {:}. Set -o flag to force me".format(
                args.outfile))

    tmpfname = Path(args.outfile).parent / str(uuid4())
    fnames = args.infiles

    try:
        concatDimension(
            fnames, dim=args.dim, dimvar=args.dimvar,
            outfname=tmpfname, zlib=True)
  
        tmpfname.rename(args.outfile)
    finally:
        if tmpfname.is_file():
            tmpfname.unlink()
