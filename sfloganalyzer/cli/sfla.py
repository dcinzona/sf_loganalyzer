import contextlib
import pdb
import sys
import traceback
import click

# import sfla
import sfloganalyzer
from .logger import get_tempfile_logger, init_logger
from ..utils.logging import tee_stdout_stderr
from .debug import set_debug_mode
from sfloganalyzer.graph import logviz
from .soqlparser import readLog


def main(args=None):
    """Main SF Log Analyzer CLI entry point.
    This runs as the first step in processing any CLI command.
    This wraps the `click` library in order to do some initialization and centralized error handling.
    """
    with contextlib.ExitStack() as stack:
        args = args or sys.argv

        debug = "--debug" in args
        if debug:
            # args.remove("--debug")
            pass

        is_error_command = len(args) > 2 and args[1] == "error"
        tempfile_path = None
        if not is_error_command:
            logger, tempfile_path = get_tempfile_logger()
            stack.enter_context(tee_stdout_stderr(args, logger, tempfile_path))

        with set_debug_mode(debug):
            try:
                pass
            except Exception as e:
                print(f"\n== Error ==\n{e}\n")
                sys.exit(1)

            init_logger(debug=debug)
            # Hand CLI processing over to click, but handle exceptions
            try:
                cli(args[1:], standalone_mode=False)
            except click.Abort:  # Keyboard interrupt
                show_debug_info() if debug else print("\n[red bold]Aborted!")
                sys.exit(1)
            except Exception as e:
                if debug:
                    show_debug_info()
                else:
                    print(f"\n== Error ==\n{e}\n")
                    sys.exit(1)
                sys.exit(1)


def show_debug_info():
    """Displays the traceback and opens pdb"""
    traceback.print_exc()
    pdb.post_mortem()


def show_version_info():
    print(f"SFLogAnalyzer version: {sfloganalyzer.__version__} ({sys.argv[0]})")
    print(f"Python version: {sys.version.split()[0]} ({sys.executable})")
    print()


@click.group("main", help="")
@click.version_option(show_version_info, message="")
def cli():
    """Top-level `click` command group."""


@cli.command(name="version", help="Print the current version of CumulusCI")
def version():
    show_version_info()


@cli.command(name="soql", help="Visualize log data.")
@click.argument("logfile", required=True, type=click.Path(exists=True))
def soql(logfile):
    """Visualize log data."""
    readLog(logfile).run()


cli.add_command(logviz.run)
