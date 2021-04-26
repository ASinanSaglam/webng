
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
    argv = ['--debug']
    with weBNGTest(argv=argv) as app:
        app.run()
        assert app.debug is True


# Template test
def test_template():
    # test template without arguments
    os.chdir(tfold)
    with raises(SystemExit):
        argv = ['template', '-h']
        with weBNGTest(argv=argv) as app:
            app.run()
            assert app.exit_code == 0

    # test template with arguments
    os.chdir(tfold)
    fpath = os.path.join(tfold, "test.bngl")
    opath = os.path.join(tfold, "test_setup.yaml")
    argv = ['template', '-i', '{}'.format(fpath), '-o', '{}'.format(opath)]
    with weBNGTest(argv=argv) as app:
        app.run()
        assert os.path.isfile(opath)


# Setup test
def test_setup():
    # test command1 without arguments
    argv = ['setup']
    with raises(SystemExit):
        with weBNGTest(argv=argv) as app:
            app.run()
            assert app.exit_code == 0

    # test command1 with arguments
    os.chdir(tfold)
    fpath = os.path.join(tfold, "test_setup.yaml")
    opath = os.path.join(tfold, "test")
    argv = ['setup', '--opts', '{}'.format(fpath)]
    with weBNGTest(argv=argv) as app:
        app.run()
        assert os.path.isdir(opath)
    # clean up
    os.remove(fpath)
    shutil.rmtree(opath)


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
