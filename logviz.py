"""
Run via command line: python3 readlog.py [logfile] [optional:outputfilecsv]
Requires Python 3.6 or higher
"""
import sys,traceback
import click

from logfileReader import reader
from vizutils.renderer import renderer


class logviz:
    reader=None

    def __init__(self, *args, **kwargs) -> None:
        self.useloops = False
        pass

    def run(self,*args, **kwargs):
        print(kwargs)
        self.reader = reader(kwargs['logfile'])
        self.reader.read()
        self.renderer = renderer(*args, **kwargs)
        self.renderer.processStack(self.reader.operations)
        print(f'\n{len(self.reader.operations)} reader operations processed')
        print(f'...Loading file in default system viewer')
        if(kwargs.get('no-show', False) == False):
            self.renderer.g.view()
        

@click.command()
@click.argument('logfile', required=True, type=click.Path(exists=True))
@click.option('-e','--engine', default='dot', help='Graphviz engine' , show_default=True, type=click.Choice(['dot','neato','twopi','circo','fdp','sfdp','patchwork','osage']))
@click.option('-f','--format', default='svg', help='Output format [svg, pdf, png]' , show_default=True, type=click.Choice(['svg','pdf','png']))
@click.option('-8','--useloops', default=True, help='Use loops for duplicate nodes.\nNodes are only rendered once' , show_default=True)
@click.option('-o','--outputfile', help='Output file')
@click.option('--no-show', default=False, is_flag=True, help='Don\'t show the graph in the default system viewer')
@click.option('--strict', default=True, help='Will only render a single edge regardless of loop-backs' , show_default=True)
@click.option('-r','--rankdir', default='TB', help='The direction the nodes "travel": [TB, BT, LR, RL]', show_default=True)
def run(*args, **kwargs):
    runner = logviz()
    try:
        runner.run(*args, **kwargs)
        #runner.run(logfile, format, engine, useloops, outputfile, rankdir)
    except Exception as e:
        print(f"\n== Error ==\n{e}\n")
        traceback.print_exc()
        print(f"Last Line: {runner.reader.lineCount}")
        for line in runner.reader.logReversed[-2:]:
            print(line)
        sys.exit(1)


if __name__ == "__main__":
    run(obj={})