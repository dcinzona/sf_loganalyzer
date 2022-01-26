import sys, os, re, traceback


class reader:

    def __init__(self, logfile):
        self.logfile = logfile
        self.logReversed = []
        self.lineCount = 0
        self.operations = []
        self.logpath = os.path.abspath(logfile)
        self.filename = os.path.basename(self.logpath)
        self.inputfileDir = os.path.dirname(os.path.abspath(self.logpath))
