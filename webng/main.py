
import cement
from cement.core.exc import CaughtSignal
from .core.exc import weBNGError
from .controllers.base import Base
from .core.bng_to_we import BNGL_TO_WE
from .core.weTemplater import weTemplater

# configuration defaults
CONFIG = cement.init_defaults('webng')
CONFIG['webng']['foo'] = 'bar'

class weBNGBase(cement.Controller):
    '''
    webng is a simple command line tool to simplify WESTPA simulations of
    BioNetGen models. It can generate a template options file and using the 
    options file you can generate a WESTPA folder ready to run using the model
    file given. 

    Subcommands
    -------
    setup
        creates a WESTPA folder ready to run form a given options YAML file
    template
        generates a simple template YAML file to pass to setup subcommand
    '''

    class Meta:
        label = "webng"
        description = "webng"
        help = "webng"

    # This overwrites the default behavior
    @cement.ex(
            help="Sets up a WESTPA simulation folder from an options YAML file. "
                  + "Run \"webng template -h\" for more information.",
            arguments=[
                (["--opts"],{"help":"Options YAML file (required)." + 
                                       "Run \"webng template -h\" for more information.",
                                   "default": None,
                                   "type": str,
                                   "required": True})
            ]
    )
    def setup(self):
        '''
        This sub command sets up a WESTPA folder from a given options YAML file. 

        See \"webng template -h\" for more information on the options YAML file.
        '''
        args = self.app.pargs
        BNGL_TO_WE(args).run()
    
    @cement.ex(
            help="Writes a template options file for a WESTPA simulation using a BNGL model.",
            arguments=[
                (["-i", "--input"],{"help":"The bngl model to write the template for." +
                                      "If not model name is given, a template for \"model.bngl\" will be written",
                                   "default": "model.bngl",
                                   "type": str,
                                   "required": False}),
                (["-o", "--output"],{"help":"The name for the options file (default: opts.yaml)",
                                   "default": "opts.yaml",
                                   "type": str,
                                   "required": False})
            ]
    )
    def template(self):
        '''
        This sub command is used to write a template options file 
        '''
        args = self.app.pargs
        weTemplater(args).run()



class weBNG(cement.App):
    """weBNG primary application."""

    class Meta:
        label = 'webng'
        description = "A command line tool to setup WESTPA simulations from BNGL models."
        help = "weBNG"

        # configuration defaults
        config_defaults = CONFIG

        # call sys.exit() on close
        exit_on_close = True

        # load additional framework extensions
        extensions = [
            'yaml',
            'colorlog',
            'jinja2',
        ]

        # configuration handler
        config_handler = 'yaml'

        # configuration file suffix
        config_file_suffix = '.yml'

        # set the log handler
        log_handler = 'colorlog'

        # set the output handler
        output_handler = 'jinja2'

        # register handlers
        handlers = [
            weBNGBase
        ]

class weBNGTest(cement.TestApp,weBNG):
    """A sub-class of weBNG that is better suited for testing."""

    class Meta:
        label = 'webng'


def main():
    with weBNG() as app:
        try:
            app.run()

        except AssertionError as e:
            print('AssertionError > %s' % e.args[0])
            app.exit_code = 1

            if app.debug is True:
                import traceback
                traceback.print_exc()

        except weBNGError as e:
            print('weBNGError > %s' % e.args[0])
            app.exit_code = 1

            if app.debug is True:
                import traceback
                traceback.print_exc()

        except CaughtSignal as e:
            # Default Cement signals are SIGINT and SIGTERM, exit 0 (non-error)
            print('\n%s' % e)
            app.exit_code = 0


if __name__ == '__main__':
    main()
