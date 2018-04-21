# Author: Pietro Caragiulo
# Rev: 20180414.1
# Usage: python .\makeHspice.py -i .\netlist -top topcell
# Usage for Developer: python .\makeHspice.py -v -i .\netlist -top topcell
# This script will create a SPICE file with name netlist.new

import argparse
import logging
import re
import sys

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--verbose", action="store_true",
                        help="Show debugging info.")
    parser.add_argument("-i", "--inputfiles", nargs=1,
                        help="Parameters inserted from source to destination.", required=True)
    parser.add_argument("-top", "--topcell", nargs=1,
                        help="Top Cell Name.", required=True)

    args = parser.parse_args()

    if args.verbose:
        myloglevel = logging.DEBUG
    else:
        myloglevel = logging.INFO

    # set logging based on args
    logging.basicConfig(
        format='%(asctime)s %(levelname)s %(message)s', level=myloglevel)

    sfile = args.inputfiles[0]
    top = args.topcell[0]

    # openfiles
    try:
        srcfile = open(sfile, 'r')
    except IOError as e:
        logging.error("[%s] cannot be opened!", sfile)
        logging.error(e)
        sys.exit(1)
    logging.debug("[%s] opened for reading", sfile)

    # create new file for merging
    try:
        newfile = open(sfile + '.new', 'w')
    except IOError as e:
        logging.error("[%s] cannot be opened!", sfile + '.new')
        logging.error(e)
        sys.exit(1)
    logging.debug("[%s] opened for writing", sfile + '.new')

    # read file content and store it as a list
    srcfile_content = srcfile.read().splitlines()

    # substitutions
    commentNextENDS = False
    commentSUBCKT = '*.SUBCKT ' + top
    for i, line in enumerate(srcfile_content):
        logging.debug("[%d] [%s]", i, line)

        # line = re.sub('old', 'new', line)
        line = re.sub(r'.PARAM', r'*.PARAM', line)
        line = re.sub(r'W=([^\s]+)', r"W='\1'", line)
        line = re.sub(r'L=([^\s]+)', r"L='\1'", line)
        line = re.sub(r'm=([^\s]+)', r"m='\1'", line)

        # handle the topcell
        line = re.sub('.SUBCKT ' + top, commentSUBCKT, line)
        if commentNextENDS == False:
            regexp = re.compile('\*.SUBCKT')
            if regexp.search(line):
                commentNextENDS = True
        if commentNextENDS:
            line = re.sub(r'.ENDS', r'*.ENDS', line)

        # finally create new file
        newfile.write(line + '\n')

    srcfile.close()
    newfile.close()
    logging.debug("closing files")
    logging.info("Results stored in " + sfile + ".new")

if __name__ == "__main__":
    main()
