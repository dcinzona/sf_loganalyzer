import pytest
from sfloganalyzer.cli.soqlparser import readLog


def test_ReadLog():
    reader = readLog("examples/gmt.log")
    totalQueries = reader.run()
    assert totalQueries > 0


def test_InvalidLogFile():
    with pytest.raises(FileNotFoundError):
        readLog("test/test.log")
