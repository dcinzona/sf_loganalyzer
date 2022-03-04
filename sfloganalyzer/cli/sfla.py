import contextlib
import pdb
import sys
import traceback
import click
from click import ClickException

# import sfla
import sfloganalyzer
from .logger import get_tempfile_logger, init_logger
from ..utils.logging import tee_stdout_stderr
from .debug import set_debug_mode
from sfloganalyzer.graph import logviz
from .soqlparser import readLog

SUGGEST_ERROR_COMMAND = """Run this command for more information about debugging errors: sfla error --help"""

USAGE_ERRORS = (Exception, click.UsageError)


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
            # logger.error("ERROR")

        with set_debug_mode(debug):
            init_logger(debug=debug)
            # Hand CLI processing over to click, but handle exceptions
            try:
                cli(args[1:], standalone_mode=False)
            except click.Abort:  # Keyboard interrupt
                show_debug_info() if debug else print("\n[red bold]Aborted!")
            except ClickException as e:
                if "Missing argument 'LOGFILE'" in e.format_message():
                    sys.stderr.write(
                        "Missing logfile parameter.  Use 'sfla render [Options] [Logfile]'\n"
                    )
                else:
                    sys.stderr.write(f"{e}\n")
            except Exception as e:
                if debug:
                    show_debug_info()
                    pass
                else:
                    handle_exception(
                        e,
                        is_error_command,
                        tempfile_path,
                        debug,
                    )


def handle_exception(
    error,
    is_error_cmd,
    logfile_path,
    should_show_stacktraces=False,
):
    """Displays error of appropriate message back to user, prompts user to investigate further
    with `slfa error` commands, and writes the traceback to the latest logfile.
    """
    # error_console = Console(stderr=True)
    if isinstance(error, click.ClickException):
        sys.stderr.write(f"[red bold]Error: {error.format_message()}")
    else:
        sys.stderr.write(f"[red bold]Error: {error}")
    # Only suggest gist command if it wasn't run
    if not is_error_cmd:
        sys.stderr.write(f"[yellow]{SUGGEST_ERROR_COMMAND}")

    # This is None if we're handling an exception for a `cci error` command.
    if logfile_path:
        with open(logfile_path, "a") as log_file:
            traceback.print_exc(file=log_file)  # log stacktrace silently

    if should_show_stacktraces and not isinstance(error, USAGE_ERRORS):
        sys.stderr.write("\n== Stacktrace ==\n")
        traceback.print_exc()


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
