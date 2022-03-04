import contextlib
import io
import os
import sfloganalyzer.cli.sfla as sfla


def test_Logviz_Errors():
    # assert "Missing logfile parameter" in captured.out
    with contextlib.redirect_stderr(io.StringIO()) as stderr:
        sfla.main(["sfla", "render"])
        consoleOut = stderr.getvalue()
        assert "Missing logfile parameter" in consoleOut
    with contextlib.redirect_stderr(io.StringIO()) as stderr:
        sfla.main(["sfla", "render", "test.log"])
        consoleOut = stderr.getvalue()
        assert "Path 'test.log' does not exist" in consoleOut


def test_Logviz_Run():
    # assert "Missing logfile parameter" in captured.out
    with contextlib.redirect_stdout(io.StringIO()) as stdout:
        logpath = os.path.join(os.path.dirname(__file__), "logs/test.log")
        sfla.main(["sfla", "render", "--no-show", logpath])
        consoleOut = stdout.getvalue()
        assert "reader operations processed" in consoleOut
