"""
Run via command line: python3 readlog.py [logfile] [optional:outputfilecsv]
Requires Python 3.6 or higher
"""
import sys
import traceback
import click

import sfloganalyzer.options as options
import sfloganalyzer.parser.logfileReader as logfileReader
from .VizUtils.renderers.GraphVizRenderer import GraphVizRenderer as Renderer

# import sfloganalyzer.graph.VizUtils.renderers.NetworkXRenderer as NetworkXRenderer


class logviz:
    reader = None

    def __init__(self, *args, **kwargs) -> None:
        self.useloops = options.useloops
        pass

    def run(self, *args, **kwargs):
        self.reader = logfileReader.reader(**kwargs)
        self.reader.read()
        self.renderer = Renderer(*args, **kwargs)
        self.renderer.processStack(self.reader.operations)
        print(f"\n{len(self.reader.operations)} reader operations processed")
        if not kwargs.get("no_show", False):
            print("...Loading file in default system viewer")
            self.renderer.g.view()
        else:
            print("...Skipping system viewer")
            print("Graphviz file saved to: " + self.renderer.g.filepath)
            print(
                f"{str(kwargs.get('format')).upper()} file saved to: {self.renderer.g.filepath}.{str(kwargs.get('format'))}"
            )


@click.command(name="render", help="Visualize log data.")
@click.argument("logfile", required=True, type=click.Path(exists=True))
@click.option(
    "-e",
    "--engine",
    default="dot",
    help="Graphviz engine",
    show_default=True,
    type=click.Choice(
        ["dot", "neato", "twopi", "circo", "fdp", "sfdp", "patchwork", "osage"]
    ),
)
@click.option(
    "-f",
    "--format",
    default="svg",
    help="Output format [svg, pdf, png]",
    show_default=True,
    type=click.Choice(["svg", "pdf", "png", "dot"]),
)
@click.option(
    "-8",
    "--useloops",
    default=True,
    help="Use loops for duplicate nodes.\nNodes are only rendered once",
    show_default=True,
)
@click.option(
    "-r",
    "--rankdir",
    default="TB",
    help='The direction the nodes "travel": [TB, BT, LR, RL]',
    show_default=True,
    type=click.Choice(["TB", "BT", "LR", "RL"], case_sensitive=False),
)
@click.option(
    "-E",
    "--exclude",
    help="Types of operations to exclude from the graph.  Never exclude errors / exceptions.\n",
    show_default=True,
    multiple=True,
    type=click.Choice(
        ["apex", "trigger", "flow", "callout", "dml", "soql", "system", "validation"],
        case_sensitive=False,
    ),
)
@click.option(
    "--no-show",
    default=False,
    is_flag=True,
    help="Don't show the graph in the default system viewer",
)
@click.option(
    "--strict",
    default=False,
    is_flag=True,
    help="Will only render a single edge per node regardless of loop-backs",
    show_default=True,
)
@click.option(
    "-S",
    "--stop-on-exception",
    default=False,
    is_flag=True,
    help="Stops processing additional operations after first exception",
    show_default=True,
)
@click.option(
    "-R",
    "--redact",
    default=False,
    is_flag=True,
    help="Strips out operation names and uses event types instead",
    show_default=True,
)
@click.option("--debug", default=False, is_flag=True, help="Debug mode")
def run(*args, **kwargs):
    options.setOptions(**kwargs)
    if options.debug:
        pass
    try:
        runner = logviz()
        runner.run(*args, **kwargs)
    except Exception as e:
        print(f"\n== Error ==\n{e}\n")
        traceback.print_exc()
        print(f"\nLast Line: {runner.reader.lineCount}")
        for line in reversed(runner.reader.logReversed[0:2]):
            print(line)
        sys.exit(1)
