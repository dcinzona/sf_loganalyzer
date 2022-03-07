def test_NetworkX():
    import sfloganalyzer.graph.VizUtils.renderers.NetworkXRenderer as r

    d = r.Renderer(
        **{
            "name": "Test",
            "logfile": "test.log",
            "format": "svg",
            "no_show": True,
            "useloops": True,
        }
    )
    assert d.options.logfile == "test.log"

    d.processStack(["test"])
    assert d.operations == ["test"]
