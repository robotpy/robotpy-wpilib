
import argparse
import inspect

from pkg_resources import iter_entry_points

from .logconfig import configure_logging
import hal_impl


def _log_versions():
    import wpilib
    import hal
    import hal_impl
    
    import logging
    logger = logging.getLogger('wpilib')
    
    logger.info("WPILib version %s", wpilib.__version__)
    logger.info("HAL base version %s; %s platform version %s",
                hal.__version__,
                hal_impl.__halplatform__,
                hal_impl.__version__)
    if hasattr(hal_impl.version, "__hal_version__"):
        logger.info("HAL library version %s", hal_impl.version.__hal_version__)
    
    # should we just die here?
    if hal.__version__ != wpilib.__version__ and \
       hal.__version__ != hal_impl.__version__:
        logger.warn("Core component versions are not identical! This is not a supported configuration, and you may run into errors!")


class _CustomHelpAction(argparse.Action):

    def __init__(self,
                 option_strings,
                 dest=argparse.SUPPRESS,
                 default=argparse.SUPPRESS,
                 help=None):
        super(_CustomHelpAction, self).__init__(
            option_strings=option_strings,
            dest=dest,
            default=default,
            nargs=0,
            help=help)

    def __call__(self, parser, namespace, values, option_string=None):
        parser.print_help()
        parser.exit(1)  # argparse uses an exit code of zero by default
    
argparse._HelpAction = _CustomHelpAction
    
def run(robot_class, **kwargs):
    '''
        This function gets called in robot.py like so::
        
            if __name__ == '__main__':
                wpilib.run(MyRobot)
        
        This function loads available entry points, parses arguments, and
        sets things up specific to RobotPy so that the robot can run. This
        function is used whether the code is running on the RoboRIO or
        a simulation.
        
        :param robot_class: A class that inherits from :class:`.RobotBase`
        :param **kwargs: Keyword arguments that will be passed to the executed entry points
        :returns: This function should never return
    '''
    
    # sanity check
    if not hasattr(robot_class, 'main'):
        print("ERROR: run() must be passed a robot class that inherits from RobotBase (or IterativeBase/SampleBase)")
        exit(1)
    
    parser = argparse.ArgumentParser()
    subparser = parser.add_subparsers(dest='command', help="commands")
    subparser.required = True
    
    parser.add_argument('-v', '--verbose', action='store_true', default=False,
                        help="Enable debug logging")
    
    has_cmd = False
    
    for entry_point in iter_entry_points(group='robotpy', name=None):
        has_cmd = True
        cmd_class = entry_point.load()
        cmdparser = subparser.add_parser(entry_point.name, help=inspect.getdoc(cmd_class))
        obj = cmd_class(cmdparser)
        cmdparser.set_defaults(cmdobj=obj)
        
    if not has_cmd:
        parser.error("No entry points defined -- robot code can't do anything. Install packages to add entry points (see README)")
        exit(1)
    
    options = parser.parse_args()
    
    configure_logging(options.verbose)
    
    _log_versions()
    retval = options.cmdobj.run(options, robot_class, **kwargs)
    
    if retval is None:
        retval = 0
    elif retval is True:
        retval = 0
    elif retval is False:
        retval = 1
        
    exit(retval)

