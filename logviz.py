"""
Run via command line: python3 readlog.py [logfile] [optional:outputfilecsv]
Requires Python 3.6 or higher
"""
import os,sys,re,traceback

from logfileReader import reader


class logviz:
    reader=None
    def run(self):
        self.reader = reader(sys.argv[1])
        self.reader.read()


if __name__ == "__main__":
    if(len(sys.argv) != 2 and len(sys.argv) != 3):
        print("Usage: logviz.py <logfile> [optional:outputfile]")
        sys.exit()
    runner = logviz()
    try:
        runner.run()
    except Exception as e:
        print(f"\n== Error ==\n{e}\n")
        traceback.print_exc()
        print(f"\nLast Line: {runner.reader.lineCount}\n {runner.reader.logReversed[1]}\n {runner.reader.logReversed[0]}")
        sys.exit(1)