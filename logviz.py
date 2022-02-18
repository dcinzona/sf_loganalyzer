"""
Run via command line: python3 readlog.py [logfile] [optional:outputfilecsv]
Requires Python 3.6 or higher
"""
import os,sys,re,traceback

from logfileReader import reader
from vizutils.renderer import renderer


class logviz:
    reader=None
    def run(self):
        if(len(sys.argv) < 2):
            print('Usage: python3 logviz.py [logfile] [optional format:pdf,png,svg]')
            exit()
        logfile = sys.argv[1]
        fileFormat = None
        if(len(sys.argv) > 2):
            fileFormat = sys.argv[2]
        self.reader = reader(logfile)
        self.reader.read()
        self.renderer = renderer(filename=logfile, fileformat=fileFormat)
        self.renderer.processStack(self.reader.operations)
        print(f'\n{len(self.reader.operations)} reader operations found')


if __name__ == "__main__":
    if(len(sys.argv) != 2 and len(sys.argv) != 3):
        print('Usage: python3 logviz.py [logfile] [optional format:pdf,png,svg]')
        sys.exit()
    runner = logviz()
    try:
        runner.run()
    except Exception as e:
        print(f"\n== Error ==\n{e}\n")
        traceback.print_exc()
        print(f"Last Line: {runner.reader.lineCount}")
        for line in runner.reader.logReversed[-2:]:
            print(line)
        sys.exit(1)