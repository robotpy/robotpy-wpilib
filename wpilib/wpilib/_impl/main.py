
import argparse
import inspect

from pkg_resources import iter_entry_points

from .logconfig import configure_logging

def run(robot_class):
    '''
        This function gets called in robot.py like so::
        
            if __name__ == '__main__':
                wpilib.run(MyRobot)
        
        This function loads available entry points, parses arguments, and
        sets things up specific to RobotPy so that the robot can run. This
        function is used whether the code is running on the RoboRIO or
        a simulation.
        
        :param robot_class: A class that inherits from :class:`.RobotBase`
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
    
    retval = options.cmdobj.run(options, robot_class)
    
    if retval is None:
        retval = 0
    elif retval is True:
        retval = 0
    elif retval is False:
        retval = 1
        
    exit(retval)

