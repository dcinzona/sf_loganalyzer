def test_NetworkX():
    import sfloganalyzer.graph.VizUtils.renderers.NetworkXRenderer as r
    import sfloganalyzer.options as options

    options.set(
        name="Test",
        logfile="test.log",
        format="svg",
        no_show=True,
        useloops=True,
        debug=True,
    )

    d = r.NetworkXRenderer()
    assert options.logfile == "test.log"

    assert options.doesnotexist is None

    d.processStack(["test"])
    assert d.operations == ["test"]
