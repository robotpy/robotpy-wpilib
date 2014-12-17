#!/usr/bin/env python3

import argparse
import configparser
import inspect
import os
from os.path import abspath, dirname, exists, isdir, join
import shutil
import subprocess
import sys


try:
    import pip
except ImportError:
    print("ERROR: pip must be installed for the installer to work!")
    exit(1)
    
is_windows = hasattr(sys, 'getwindowsversion')

    
class ArgError(Exception):
    pass

class RobotpyInstaller(object):

    cfg = abspath(join(dirname(__file__), '.installer_config'))

    pip_cache = abspath(join(dirname(__file__), 'pip_cache'))
    opkg_cache = abspath(join(dirname(__file__), 'opkg_cache'))
    
    win_bins = abspath(join(dirname(__file__), 'win32'))
    
    # Defaults, actual values come from config file
    username = 'admin'
    password = ''
    hostname = ''
    
    commands = [
        'install-robotpy',
        'download-robotpy',
        'install',
        'download'
    ]

    def __init__(self):
        
        if not exists(self.pip_cache):
            os.makedirs(self.pip_cache)
        
        if not exists(self.opkg_cache):
            os.makedirs(self.opkg_cache)
        
        if not exists(self.cfg):
            self._do_config()
            
        config = configparser.ConfigParser()
        config.read(self.cfg)
        
        try:
            self.username = config['auth'].get('username', self.username)
            self.password = config['auth'].get('password', self.password)
            self.hostname = config['auth']['hostname']
        except KeyError as e:
            raise ArgError("Error reading %s; delete it and try again" % self.cfg)
    
    def _do_config(self):
        
        print("Robot setup (hit enter for default value):")
        hostname = ''
        while hostname == '':
            hostname = input('Robot hostname (like roborio-XXX.local, or an IP address): ')
        
        username = input('Username [%s]: ' % self.username)
        password = input('Password [%s]: ' % self.password)
        
        config = configparser.ConfigParser()
        config['auth'] = {}
        
        if username != '' and username != self.username:
            config['auth']['username'] = username
        if password != '' and password != self.password:
            config['auth']['username'] = password
            
        config['auth']['hostname'] = hostname
        
        with open(self.cfg, 'w') as fp:
            config.write(fp)
            
    
    #
    # This sucks. We should be using paramiko here... 
    #
    
    def _ssh(self, *args):
    
        # Check for requirements
        cmd = shutil.which('ssh')
        if cmd is None:
            if is_windows:
                cmd = join(self.win_bins, 'plink.exe')
            else:
                raise ArgError("Cannot find ssh executable")
        
        return subprocess.call([cmd, '%s@%s' % (self.username, self.hostname)]
                               + list(args))
        
            
    def _scp(self, src, dst):
        
        # Check for requirements
        cmd = shutil.which('scp')
        if cmd is None:
            if is_windows:
                cmd = join(self.win_bins, 'pscp.exe')
            else:
                raise ArgError("Cannot find ssh executable")
        
        scp_args = [cmd]
        
        if isdir(src):
            scp_args.append('-r')
        
        scp_args.append(src)
        scp_args.append('%s@%s:%s' % (self.username, self.hostname, dst))
        
        return subprocess.call(scp_args)
    
    #
    # Commands
    #
    
    def install_robotpy_opts(self, parser):
        #parser.add_argument()
        pass
    
    def install_robotpy(self, options):
        '''
            This will copy the appropriate RobotPy components to the robot, and install
            them. If the components are already installed on the robot, then they will
            be reinstalled.
        '''
        
        # Construct an appropriate line to install
        
        raise NotImplementedError()
    
    def download_robotpy_opts(self, parser):
        pass
    
    def download_robotpy(self, options):
        '''
            This will update the cached RobotPy packages to the newest versions available.
        '''
        
        # TODO: What is required to download the opkg files?
        
        raise NotImplementedError()
    
    
    def download_opts(self, parser):
        parser.add_argument('packages', nargs='*',
                            help="Packages to download")
        parser.add_argument('-r', '--requirement', action='append', default=[],
                            help='Install from the given requirements file. This option can be used multiple times.')
        parser.add_argument('--pre', action='store_true', default=False, 
                            help="Include pre-release and development versions.")
    
    def download(self, options):
        '''
            Specify python package(s) to download, and store them in the cache
        '''
        
        if len(options.requirement) == 0 and len(options.packages) == 0:
            raise ArgError("You must give at least one requirement to install")
        
        # Use pip install --download to put packages into the cache
        pip_args = ['install',
                    '--download',
                    self.pip_cache]
        
        for r in options.requirement:
            pip_args.extend(['-r', r])
            
        pip_args.extend(options.packages)
    
        return pip.main(pip_args)
    
    # These share the same options
    install_opts = download_opts
    
    def install(self, options):
        '''
            Copies python packages over to the roboRIO, and installs them. If the
            package already has been installed, it will be reinstalled.
        '''
        
        if len(options.requirement) == 0 and len(options.packages) == 0:
            raise ArgError("You must give at least one requirement to install")
        
        # TODO
        # Deal with requirements.txt files specially, because we have to 
        # copy the file over.
        
        # copy them to the cache with a unique name, and delete them later?
        if len(options.requirement) != 0:
            raise NotImplementedError()
        
        # copy the pip cache over
        print("Copying over the pip cache...")
        retval = self._scp(self.pip_cache, '')
        
        print("Running installation...")
        cmd = "/usr/local/bin/pip3 install --no-index --find-links=pip_cache "
        cmd += ' '.join(options.packages)
    
        self._ssh(cmd)
        
        print("Done.")

def main(args=None):

    if args is None:
        args = sys.argv[1:]

    try:
        installer = RobotpyInstaller()
    except ArgError as e:
        print("ERROR: %s" % e)
        return 1
    
    # argparse boilerplate... 
    parser = argparse.ArgumentParser()
    subparser = parser.add_subparsers(dest='command', help="Commands")
    subparser.required = True
    
    # Setup various options
    for command in installer.commands:
        fn = getattr(installer, command.replace('-', '_'))
        opt_fn = getattr(installer, command.replace('-', '_') + '_opts')
        cmdparser = subparser.add_parser(command, help=inspect.getdoc(fn))
        opt_fn(cmdparser)
        cmdparser.set_defaults(cmdobj=fn)
        
    options = parser.parse_args(args)

    try:
        retval = options.cmdobj(options)
    except ArgError as e:
        parser.error(str(e))
        retval = 1
    
    if retval is None:
        retval = 0
    elif retval is True:
        retval = 0
    elif retval is False:
        retval = 1
        
    return retval


if __name__ == '__main__':

    retval = main()    
    exit(retval)
