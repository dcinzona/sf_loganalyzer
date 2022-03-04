import os
import pytest
from sfloganalyzer.cli.soqlparser import readLog


def test_ReadLog():
    logpath = os.path.join(os.path.dirname(__file__), "logs/test.log")
    reader = readLog(logpath)
    totalQueries = reader.run()
    assert totalQueries > 0


def test_InvalidLogFile():
    with pytest.raises(FileNotFoundError):
        readLog("test/test.log")
