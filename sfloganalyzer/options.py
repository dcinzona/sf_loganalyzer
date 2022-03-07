class options:
    """Every module should import this if it has to access options defined by the command line
    example: `import sfloganalyzer.options as options`
    """

    logfile: str = None
    debug: bool = False
    useloops: bool = False
    engine: str = "dot"
    format: str = "svg"
    no_show: bool = False
    strict: bool = False
    exclude: list[str] = []
    rankdir: str = "TB"
    stop_on_exception: bool = False
    redact: bool = False

    def __init__(self, **kwargs):
        global logfile, debug, useloops, engine, format, no_show, strict, exclude, rankdir, stop_on_exception, redact
        logfile = kwargs.get("logfile", None)
        debug = kwargs.get("debug", False)
        useloops = kwargs.get("useloops", False)
        engine = kwargs.get("engine", "dot")
        format = kwargs.get("format", "svg")
        no_show = kwargs.get("no_show", False)
        strict = kwargs.get("strict", False)
        exclude = kwargs.get("exclude", [])
        rankdir = kwargs.get("rankdir", "TB")
        stop_on_exception = kwargs.get("stop_on_exception", False)
        redact = kwargs.get("redact", False)


def setOptions(**kwargs):
    global options
    options = options(**kwargs)
