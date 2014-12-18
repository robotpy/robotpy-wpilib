#!/usr/bin/env python3
#
# This is a simple (ha!) installer program that is designed to be used to
# deploy RobotPy to a roborio via SSH
#
# It is intended to work on Windows, OSX, and Linux.
#


import argparse
import configparser
import hashlib
import inspect
import os
from os.path import abspath, basename, dirname, exists, isdir, join
import shutil
import subprocess
import sys

from collections import OrderedDict
from distutils.version import LooseVersion
from urllib.request import urlopen, urlretrieve

try:
    import pip
except ImportError:
    print("ERROR: pip must be installed for the installer to work!")
    exit(1)
    
is_windows = hasattr(sys, 'getwindowsversion')




def md5sum(fname):
    md5 = hashlib.md5()
    with open(fname, 'rb') as fp:
        buf = fp.read(65536)
        while len(buf) > 0:
            md5.update(buf)
            buf = fp.read(65536)
    return md5.hexdigest()


class OpkgError(Exception):
    pass

class OpkgRepo(object):
    '''Simplistic OPkg Manager'''
    
    def __init__(self, feedurl, arch, opkg_cache):
        self.pkgs = {}
        
        self.feedurl = feedurl
        self.opkg_cache = opkg_cache
        self.db_fname = join(opkg_cache, 'Packages')
        self.arch = arch
        
        if not exists(self.opkg_cache):
            os.makedirs(self.opkg_cache)
        
        if exists(self.db_fname):
            with open(self.db_fname, 'r') as fp:
                self._read_pkgs(fp.readlines())
        
    def update_packages(self):
        pkgurl = self.feedurl + '/Packages'
        r = urlopen(pkgurl)
        self._read_pkgs(line.decode('utf-8').strip() for line in r.readlines())
        self.save()
    
    def _read_pkgs(self, lines):
    
        # dictionary of lists of packages sorted by version
        pkg = OrderedDict()
    
        for line in lines:
            line = line.strip()
            if len(line) == 0:
                self._add_pkg(pkg)
                pkg = OrderedDict()
            else:
                k, v = [i.strip() for i in line.split(':', 1)]
                if k == 'Version':
                    v = LooseVersion(v)
                pkg[k] = v            
             
        self._add_pkg(pkg)
            
        # Finally, make sure all the packages are sorted by version
        for pkglist in self.pkgs.values():
            pkglist.sort(key=lambda p: p['Version'])
    
    def _add_pkg(self, pkg):
        if len(pkg) == 0 or pkg.get('Architecture', None) != self.arch:
            return
        
        # Only retain one version of a package
        pkgs = self.pkgs.setdefault(pkg['Package'], [])
        for old_pkg in pkgs:
            if old_pkg['Version'] == pkg['Version']:
                old_pkg.clear()
                old_pkg.update(pkg)
                break
        else:
            pkgs.append(pkg)
    
    def get_pkginfo(self, name):
        return self.pkgs[name][-1]
        
    def _get_pkg_fname(self, pkg):
        return join(self.opkg_cache, basename(pkg['Filename']))
        
    def get_cached_pkg(self, name):
        '''Returns the filename of a cached package'''
        pkg = self.get_pkginfo(name)
        fname = self._get_pkg_fname(pkg)
        
        if not exists(fname):
            raise OpkgError('Cached package for %s does not exist' % name)
        
        if not md5sum(fname) == pkg['MD5Sum']:
            raise OpkgError('Cached package for %s md5sum does not match' % name)
        
        return fname
        
    def download(self, name):
        
        pkg = self.get_pkginfo(name)
        fname = self._get_pkg_fname(pkg)
        
        # Only download it if necessary
        if not exists(fname) or not md5sum(fname) == pkg['MD5Sum']:
        
            # Get it
            print(pkg['Filename'])
            
            def _reporthook(count, blocksize, totalsize):
                percent = int(count*blocksize*100/totalsize)
                sys.stdout.write("\r%02d%%" % percent)
                sys.stdout.flush()
            
            urlretrieve('%s/%s' % (self.feedurl, pkg['Filename']),
                        fname, _reporthook)
        
        # Validate it
        if md5sum(fname) != pkg['MD5Sum']:
            raise OpkgError('Downloaded package for %s md5sum does not match' % name)
        
        return fname
        
    def save(self):
        with open(self.db_fname, 'w') as fp:
            for pkglist in self.pkgs.values():
                for pkg in pkglist:
                    for kv in pkg.items():
                        fp.write('%s: %s\n' % kv)
                    fp.write('\n')
    
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
    
    # opkg feed
    opkg_feed = 'http://www.tortall.net/~robotpy/feeds/2014/'
    opkg_arch = 'armv7a-vfp-neon'
    
    commands = [
        'install-robotpy',
        'download-robotpy',
        'install',
        'download'
    ]

    def __init__(self):
        
        if not exists(self.pip_cache):
            os.makedirs(self.pip_cache)
        
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
        
            # plink has a -pw argument we can use, instead of trying to hack it
            pw_args = [ '-pw', self.password ]
        
        scp_args = [cmd]
        
        if not isinstance(src, str):
            scp_args.extend(src)
        else:
            if isdir(src):
                scp_args.append('-r')
            scp_args.append(src)
        
        scp_args.append('%s@%s:%s' % (self.username, self.hostname, dst))
        
        return subprocess.call(scp_args)
    
    def _poor_sync(self, src, dst):
        
        # Poor man's implementation of rsync. Why? Well..
        # -> Windows may not have rsync
        # -> The roborio does not have it by default (required on client and server side)
        # -> The cache may gather a lot of files, no sense copying all of them
        
        if isdir(src):
            files = os.listdir(src)
        else:
            files = [basename(src)]
            src = dirname(src)
        
        local_files = {}
        
        for file in files:
            hash = md5sum(join(src, file))
            local_files[file] = hash
        
        lines = self._ssh('[ ! -d %s ] || md5sum %s/*' % (dst, dst), get_output=True)
        
        # once you get it, compare them
        for line in lines:
            md5 = line[:32]
            fname = basename(line[32:].strip())
            
            # Discard matching files
            if fname in local_files and local_files[fname] == md5:
                del local_files[fname]
        
        # Finally, copy the remaining files over
        # -> TODO: going to have command line issues if there are too many files.. 
        if len(local_files) != 0:
            local_files = [join(src, file) for file in local_files.keys()]
            self._scp(local_files)
            
            
    def _get_opkg(self):
        return OpkgRepo(self.opkg_feed, self.opkg_arch, self.opkg_cache)
    
    #
    # Commands
    #

    def _create_rpy_options(self, options):
        # Construct an appropriate line to install
        options.requirement = []
        options.packages = ['wpilib',
                            'robotpy-hal-base',
                            'robotpy-hal-roborio']

        if options.basever is not None:
            options.packages = ['%s==%s' % (pkg, options.basever) for pkg in options.packages]

        if not options.no_tools:
            options.packages.append('robotpy-wpilib-utilities')

        return options
    
    def install_robotpy_opts(self, parser):
        parser.add_argument('--basever', default=None,
                            help='Install a specific version of WPILib et al')
        parser.add_argument('--no-tools', action='store_true', default=False,
                            help="Don't install robotpy-wpilib-utilities")
    
    def install_robotpy(self, options):
        '''
            This will copy the appropriate RobotPy components to the robot, and install
            them. If the components are already installed on the robot, then they will
            be reinstalled.
        '''
        
        opkg = self._get_opkg()
        
        try:
            fname = opkg.get_cached_pkg('python3')
        except OpkgError as e:
            raise ArgError(e)
        
        # TODO: add to list of things to install..
        
        return self.install(self._create_rpy_options(options))
    
    # These share the same options
    download_robotpy_opts = install_robotpy_opts
    
    def download_robotpy(self, options):
        '''
            This will update the cached RobotPy packages to the newest versions available.
        '''
        
        opkg = self._get_opkg()
        opkg.update_packages()
        opkg.download('python3')
        
        return self.download(self._create_rpy_options(options))
    
    
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
        # .. this is inefficient
        print("Copying over the pip cache...")
        retval = self._scp(self.pip_cache, '')
        
        print("Running installation...")
        cmd = "/usr/local/bin/pip3 install --no-index --find-links=pip_cache -U "
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
