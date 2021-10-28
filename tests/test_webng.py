import os, shutil
from pytest import raises
from webng.main import weBNGTest

tfold = os.path.dirname(__file__)


def test_webng():
    # test webng without any subcommands or arguments
    with weBNGTest() as app:
        app.run()
        assert app.exit_code == 0


def test_webng_debug():
    # test that debug mode is functional
    argv = ["--debug"]
    with weBNGTest(argv=argv) as app:
        app.run()
        assert app.debug is True


# Template test
def test_template():
    # test template without arguments
    os.chdir(tfold)
    with raises(SystemExit):
        argv = ["template", "-h"]
        with weBNGTest(argv=argv) as app:
            app.run()
            assert app.exit_code == 0

    # test template with arguments
    os.chdir(tfold)
    fpath = os.path.join(tfold, "test.bngl")
    opath = os.path.join(tfold, "test_setup.yaml")
    argv = ["template", "-i", "{}".format(fpath), "-o", "{}".format(opath)]
    with weBNGTest(argv=argv) as app:
        app.run()
        assert os.path.isfile(opath)


# Setup test
def test_setup():
    # test command1 without arguments
    argv = ["setup", "-h"]
    with raises(SystemExit):
        with weBNGTest(argv=argv) as app:
            app.run()
            assert app.exit_code == 0

    # test command1 with arguments
    os.chdir(tfold)
    fpath = os.path.join(tfold, "test_setup.yaml")
    opath = os.path.join(tfold, "test")
    # adjust iteration count
    import yaml
    with open(fpath, 'r') as f:
        opts_yaml = yaml.load(f)
    opts_yaml['sampling_options']['max_iter'] = 5
    with open(fpath, 'w') as f:
        yaml.dump(opts_yaml, f)
    argv = ["setup", "--opts", "{}".format(fpath)]
    with weBNGTest(argv=argv) as app:
        app.run()
        assert os.path.isdir(opath)


def test_simrun():
    fpath = os.path.join(tfold, "test")
    os.chdir(fpath)
    import subprocess

    rc = subprocess.run(["./init.sh"])
    assert rc.returncode == 0
    rc = subprocess.run(["w_run", "--serial"])
    assert rc.returncode == 0
    # clean up
    os.remove(os.path.join(tfold, "test_setup.yaml"))
    shutil.rmtree(os.path.join(tfold, "test"))


# TODO: Write tests for each analysis

# Average test
# def test_avg_analysis():
#     # test command1 without arguments
#     argv = ['analysis']
#     with weBNGTest(argv=argv) as app:
#         app.run()

#     # test command1 with arguments
#     argv = ['analysis --opts {}'.format("test_average.yaml")]
#     with weBNGTest(argv=argv) as app:
#         app.run()

# Evolution test
# def test_evo_analysis():
#     # test command1 without arguments
#     argv = ['analysis']
#     with weBNGTest(argv=argv) as app:
#         app.run()

#     # test command1 with arguments
#     argv = ['analysis --opts {}'.format("test_evolution.yaml")]
#     with weBNGTest(argv=argv) as app:
#         app.run()
