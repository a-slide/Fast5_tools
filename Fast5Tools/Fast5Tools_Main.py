  #!/usr/bin/env python3
# -*- coding: utf-8 -*-

#~~~~~~~~~~~~~~IMPORTS~~~~~~~~~~~~~~#
# Standard library imports
import argparse
import sys

# Local imports
from Fast5Tools import __version__ as package_version
from Fast5Tools import __name__ as package_name
from Fast5Tools.Fast5_db import Fast5_db
from Fast5Tools.make_fast5_db import make_fast5_db
from Fast5Tools.Helper_fun import stderr_print

#~~~~~~~~~~~~~~TOP LEVEL ENTRY POINT~~~~~~~~~~~~~~#
def main ():
    # Simple triage function
    try:
        args = sys.argv
        if len(args) == 1:
            raise ValueError ("Error: Missing command\n")
        if args[1] == "make_db":
            make_db ()
        elif args[1] == "bam_to_db":
            bam_to_db ()
        elif args[1] == "eventalign_to_db":
            eventalign_to_db ()
        elif args[1] in ["-v", "--version"]:
            stderr_print ("{} v{}\n".format(package_name, package_version))
        elif args[1] in ["-h", "--help"]:
            raise ValueError ("Fast5Tools help\n")
        else:
            raise ValueError ("Error: Invalid command '{}'\n".format(args[1]))

    except ValueError as E:
        stderr_print (E)
        stderr_print ("Usage: Fast5Tools [command] [options]\n")
        stderr_print ("Valid command:\n\t-v/--version\n\tmake_db\n\tbam_to_db\n\teventalign_to_db\n")
        stderr_print ("For help on given command, type Fast5Tools [command] -h\n")
        sys.exit()

#~~~~~~~~~~~~~~SUBPROGRAMS~~~~~~~~~~~~~~#
def make_db ():
    # Define parser object
    parser = argparse.ArgumentParser(description="fast5_parse read all fast5 files in a directory recursively, extract raw signal, metadata and Albacore basecalling values (if available).\
    The fast5 objects generated are stored in a HDF5 database")
    parser.prog = "Fast5Tools fast5_parse"

    # Define arguments
    parser.add_argument("subprogram")
    parser.add_argument("-f", "--fast5_dir", required=True, help="Path to the folder containing Fast5 files")
    parser.add_argument("-d", "--db_fn", required=True, help="Path to the output database file")
    parser.add_argument("--basecall_id", default='Basecall_1D_000', help="Name of the analysis group in the fast5 file containing the basecalling information (default = 'Basecall_1D_000')")
    parser.add_argument("--signal_normalization", default="zscore", help="Index of the read in the Raw (default = 'zscore')")
    parser.add_argument("-t", "--threads", default=2, type=int, help="Total number of threads (default = 2)")
    parser.add_argument("--max_fast5", default=0 , type=int , help = "Maximum number of file to try to parse. 0 to deactivate (default = 0)")
    parser.add_argument("--basecall_required", default=False, action='store_true', help = "If true skip fast5 files without basecall")
    parser.add_argument("--verbose", default=False, action='store_true', help="If given will be more chatty (default = False)")

    # Parse Arguments
    a = parser.parse_args()

    # Run command
    f = make_fast5_db(
        fast5_dir = a.fast5_dir,
        db_fn = a.db_fn,
        basecall_id = a.basecall_id,
        signal_normalization=a.signal_normalization,
        threads = a.threads,
        max_fast5 = a.max_fast5,
        basecall_required = a.basecall_required,
        verbose = a.verbose)

def bam_to_db ():
    # Define parser object
    parser = argparse.ArgumentParser(description="Add Bam alignmnent to am existing fast5 database")
    parser.prog = "Fast5Tools add_bam_alignment"

    # Define arguments
    parser.add_argument("subprogram")
    parser.add_argument("-d", "--db_fn", required=True, help="Path to the output database file")
    parser.add_argument("-a", "--alignment_fn", required=True, help="Path to a BAM or SAM file containing all aligned reads (does not need to be sorted, filtered or indexed)")
    parser.add_argument("--analysis_name", help="sufix name for the aligment analysis. Will through an error if a same name is already in the db (default = '')")
    parser.add_argument("--only_primary", default=False, action='store_true', help="Only select primary alignments (default = False)")
    parser.add_argument("--verbose", default=False, action='store_true', help="If given will be more chatty (default = False)")

    # Parse Argumentss
    a = parser.parse_args()

    # Run command
    with Fast5_db (db_fn=a.db_fn, verbose=a.verbose) as f:
        f.bam_to_db ( fn = a.alignment_fn, analysis_name = a.analysis_name, only_primary = a.only_primary, verbose=a.verbose)

def eventalign_to_db ():
    # Define parser object
    parser = argparse.ArgumentParser(description="Add Nanopolish Eventalign data to am existing fast5 database. \
    The input file must be generated by nanopolish eventalign (--print-read-names' and '--signal-index' options) \
    In addition the files has to be collapsed by kmers using NanopolishComp Eventalign_collapse")
    parser.prog = "Fast5Tools add_nanopolish_eventalign"

    # Define arguments
    parser.add_argument("subprogram")
    parser.add_argument("-d", "--db_fn", required=True, help="Path to the output database file")
    parser.add_argument("-e", "--eventalign_fn", required=True, help="Path to a tsv file output generated by nanopolish eventalign")
    parser.add_argument("--analysis_name", help="Name of the analysis in the fast5 file database, Overwrite previous analysis if a same name is already in the db (default = 'Nanopolish_eventalign')")
    parser.add_argument("--verbose", default=False, action='store_true', help="If given will be more chatty (default = False)")

    # Parse Arguments
    a = parser.parse_args()

    # Run command
    with Fast5_db (db_fn=a.db_fn, verbose=a.verbose) as f:
        f.eventalign_to_db ( fn=a.eventalign_fn, analysis_name=a.analysis_name, verbose=a.verbose)
