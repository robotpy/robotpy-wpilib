#!/usr/bin/env python3
#
# (C) 2014-2015 Dustin Spicuzza. Distributed under MIT license.
#
# This is a simple (ha!) installer program that is designed to be used to
# deploy RobotPy to a roborio via SSH
#
# It is intended to work on Windows, OSX, and Linux.
#
# For now, let's try to keep this to a single file so that it can be moved
# around easily without having to think about it too hard and worry about
# path issues. Reconsider this once we get to 4000+ lines of code... :p
#
# NOTE: This file is used in robotpy-wpilib and in pyfrc, please keep the two
# copies in sync!
#


import argparse
import configparser
import getpass
import hashlib
import inspect
import os
import socket
import string
from os.path import abspath, basename, dirname, exists, isdir, join, relpath
import shutil
import subprocess
import sys
import tempfile

from collections import OrderedDict
from distutils.version import LooseVersion
from functools import reduce as _reduce
from urllib.request import urlretrieve


is_windows = hasattr(sys, 'getwindowsversion')


def md5sum(fname):
    md5 = hashlib.md5()
    with open(fname, 'rb') as fp:
        buf = fp.read(65536)
        while len(buf) > 0:
            md5.update(buf)
            buf = fp.read(65536)
    return md5.hexdigest()

def _urlretrieve(url, fname):
    # Get it
    print("Downloading", url)
    
    def _reporthook(count, blocksize, totalsize):
        percent = min(int(count*blocksize*100/totalsize), 100)
        sys.stdout.write("\r%02d%%" % percent)
        sys.stdout.flush()
    
    urlretrieve(url, fname, _reporthook)
    sys.stdout.write('\n')

class OpkgError(Exception):
    pass

class OpkgRepo(object):
    '''Simplistic OPkg Manager'''
    
    sys_packages = ['libc6']
    
    def __init__(self, opkg_cache, arch):
        self.feeds = []
        self.opkg_cache = opkg_cache
        self.arch = arch
        if not exists(self.opkg_cache):
            os.makedirs(self.opkg_cache)
        self.pkg_dbs = join(self.opkg_cache, 'Packages')
        if not exists(self.pkg_dbs):
            os.makedirs(self.pkg_dbs)

    def add_feed(self, url):
        # Snippet from https://gist.github.com/seanh/93666
        valid_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)
        safe_url = ''.join(c for c in url if c in valid_chars)
        safe_url = safe_url.replace(' ','_')
        feed = {
            "url": url,
            "db_fname": join(self.pkg_dbs, safe_url),
            "pkgs": OrderedDict()
        }
        if exists(feed["db_fname"]):
            self.load_package_db(feed)
        self.feeds.append(feed)
        
    def update_packages(self):
        for feed in self.feeds:
            pkgurl = feed["url"] + '/Packages'
            _urlretrieve(pkgurl, feed['db_fname'])
            self.load_package_db(feed)

    def load_package_db(self, feed):
    
        # dictionary of lists of packages sorted by version
        pkg = OrderedDict()
        with open(feed["db_fname"], 'r') as fp:
            for line in fp.readlines():
                line = line.strip()
                if len(line) == 0:
                    self._add_pkg(pkg, feed)
                    pkg = OrderedDict()
                else:
                    if ":" in line:
                        k, v = [i.strip() for i in line.split(':', 1)]
                        if k == 'Version':
                            v = LooseVersion(v)
                        pkg[k] = v
             
        self._add_pkg(pkg, feed)
            
        # Finally, make sure all the packages are sorted by version
        for pkglist in feed["pkgs"].values():
            pkglist.sort(key=lambda p: p['Version'])
    
    def _add_pkg(self, pkg, feed):
        if len(pkg) == 0 or pkg.get('Architecture', None) != self.arch:
            return
        # Add download url and fname
        if 'Filename' in pkg:
            pkg['url'] = "/".join((feed["url"], pkg['Filename']))
        
        # Only retain one version of a package
        pkgs = feed["pkgs"].setdefault(pkg['Package'], [])
        for old_pkg in pkgs:
            if old_pkg['Version'] == pkg['Version']:
                old_pkg.clear()
                old_pkg.update(pkg)
                break
        else:
            pkgs.append(pkg)
    
    def get_pkginfo(self, name):
        for feed in self.feeds:
            if name in feed["pkgs"]:
                return feed["pkgs"][name][-1]
        raise OpkgError("Package '%s' is not in the package list (have you downloaded it yet?)" % name)
        
    def _get_pkg_fname(self, pkg):
        return join(self.opkg_cache, basename(pkg['Filename']))
        
    def _get_pkg_deps(self, name):
        info = self.get_pkginfo(name)
        if "Depends" in info:
            return set([dep for dep in [dep.strip().split(" ", 1)[0] for dep in info["Depends"].split(",")] if dep not in self.sys_packages])
        return set()
        
    def get_cached_pkg(self, name):
        '''Returns the pkg, filename of a cached package'''
        pkg = self.get_pkginfo(name)
        fname = self._get_pkg_fname(pkg)
        
        if not exists(fname):
            raise OpkgError("Package '%s' has not been downloaded into the cache" % name)
        
        if not md5sum(fname) == pkg['MD5Sum']:
            raise OpkgError('Cached package for %s md5sum does not match' % name)
        
        return pkg, fname

    def resolve_pkg_deps(self, packages):
        '''Given a list of package(s) desired to be installed, topologically
           sorts them by dependencies and returns an ordered list of packages'''
          
        pkgs = {}
        packages = packages[:]
        
        for pkg in packages:
            if pkg in pkgs:
                continue
            deps =  self._get_pkg_deps(pkg)
            pkgs[pkg] = deps
            packages.extend(deps)
        
        retval = []
        for results in self._toposort(pkgs):
            retval.extend(results)
            
        return retval

    def _toposort(self, data):
        # Copied from https://bitbucket.org/ericvsmith/toposort/src/25b5894c4229cb888f77cf0c077c05e2464446ac/toposort.py?at=default
        # -> Apache 2.0 license, Copyright 2014 True Blade Systems, Inc.
        
        # Special case empty input.
        if len(data) == 0:
            return

        # Copy the input so as to leave it unmodified.
        data = data.copy()

        # Ignore self dependencies.
        for k, v in data.items():
            v.discard(k)
        # Find all items that don't depend on anything.
        extra_items_in_deps = _reduce(set.union, data.values()) - set(data.keys())
        # Add empty dependences where needed.
        data.update({item:set() for item in extra_items_in_deps})
        while True:
            ordered = set(item for item, dep in data.items() if len(dep) == 0)
            if not ordered:
                break
            yield ordered
            data = {item: (dep - ordered)
                    for item, dep in data.items()
                        if item not in ordered}
        if len(data) != 0:
            raise ValueError('Cyclic dependencies exist among these items: {}'.format(', '.join(repr(x) for x in data.items())))
    
    def download(self, name):
        
        pkg = self.get_pkginfo(name)
        fname = self._get_pkg_fname(pkg)
        
        # Only download it if necessary
        if not exists(fname) or not md5sum(fname) == pkg['MD5Sum']:
            _urlretrieve(pkg['url'], fname)
        # Validate it
        if md5sum(fname) != pkg['MD5Sum']:
            raise OpkgError('Downloaded package for %s md5sum does not match' % name)
        
        return fname

def ssh_exec_pass(password, args, capture_output=False, suppress_known_hosts=False):
    '''
        Wrapper around openssh that allows you to send a password to
        ssh/sftp/scp et al similar to sshpass. *nix only, tested on linux
        and OSX.
        
        Not super robust, but works well enough for most purposes. Typical
        usage might be::
        
            ssh_exec_pass('p@ssw0rd', ['ssh', 'root@1.2.3.4', 'echo hi!'])
        
        :param args: A list of args. arg[0] must be the command to run.
        :param capture_output: If True, suppresses output to stdout and stores
                               it in a buffer that is returned
        :returns: (retval, output)
    '''

    import pty, select
    
    # create pipe for stdout
    stdout_fd, w1_fd = os.pipe()
    stderr_fd, w2_fd = os.pipe()
    
    pid, pty_fd = pty.fork()
    if not pid:
        # in child
        os.close(stdout_fd)
        os.close(stderr_fd)
        os.dup2(w1_fd, 1)    # replace stdout on child
        os.dup2(w2_fd, 2)    # replace stderr on child
        os.close(w1_fd)
        os.close(w2_fd)
        
        os.execv(args[0], args)
    
    os.close(w1_fd)
    os.close(w2_fd)
    
    output = bytearray()
    rd_fds = [stdout_fd, stderr_fd, pty_fd]
    
    def _read(fd):
        if fd not in rd_ready:
            return 
        try:
            data = os.read(fd, 1024)
        except IOError:
            data = None
        if not data:
            rd_fds.remove(fd) # EOF
            
        return data
    
    # Read data, etc
    try:
        while rd_fds:
            
            rd_ready, _, _ = select.select(rd_fds, [], [], 0.04)
            
            if rd_ready:
                
                # Deal with prompts from pty
                data = _read(pty_fd)
                if data is not None:
                    if b'assword:' in data:
                        os.write(pty_fd, bytes(password + '\n', 'utf-8'))
                    elif b're you sure you want to continue connecting' in data:
                        os.write(pty_fd, b'yes\n')
                    
                
                # Deal with stdout
                data = _read(stdout_fd)
                if data is not None:
                    if capture_output:
                        output.extend(data)
                    else:
                        sys.stdout.write(data.decode('utf-8', 'ignore'))
                        
                data = _read(stderr_fd)
                if data is not None:
                    if not suppress_known_hosts or b'Warning: Permanently added' not in data:
                        sys.stderr.write(data.decode('utf-8', 'ignore'))
    finally:
        os.close(pty_fd)
        
    pid, retval = os.waitpid(pid, 0)
    retval = (retval & 0xff00) >> 8
    return retval, output

class Error(Exception):
    pass
  
class ArgError(Error):
    pass

class SshExecError(Error):
    def __init__(self, msg, retval):
        super().__init__(msg)
        self.retval = retval

# Arguments to pass to SSH to allow a man in the middle attack
mitm_args = ['-oStrictHostKeyChecking=no', '-oUserKnownHostsFile=/dev/null']

def ssh_from_cfg(cfg_filename, username, password, hostname=None, allow_mitm=False, no_resolve=False):
    
    dirty = True
    cfg = configparser.ConfigParser()
    cfg.setdefault('auth', {})
    
    if exists(cfg_filename):
        cfg.read(cfg_filename)
        dirty = False
        
    if hostname is not None:
        dirty = True
        cfg['auth']['hostname'] = hostname
   
    hostname = cfg['auth'].get('hostname')
    
    if not hostname:
        dirty = True
        
        print("Robot setup (hit enter for default value):")
        while not hostname:
            hostname = input('Robot hostname (like roborio-XXX-frc.local, or an IP address): ')

        cfg['auth']['hostname'] = hostname

    if dirty:
        with open(cfg_filename, 'w') as fp:
            cfg.write(fp)
            
    
    
    if not no_resolve:
        try:
            print("Looking up hostname", hostname, '...')
            # addrs = [(family, socktype, proto, canonname, sockaddr)]
            addrs = socket.getaddrinfo(hostname, None)
        except socket.gaierror as e:
            raise Error("Could not find robot at %s" % hostname) from e

        # Sort the address by family.
        # Lucky for us, the family type is the first element of the tuple, and it's an enumerated type with
        # AF_INET=2 (IPv4) and AF_INET6=23 (IPv6), so sorting them will provide us with the AF_INET address first.
        addrs.sort()
            
        # pick the first address that is sock_stream
        # AF_INET sockaddr tuple:  (address, port)
        # AF_INET6 sockaddr tuple: (address, port, flow info, scope id)
        for _, socktype, _, _, sockaddr in addrs:
            if socktype == socket.SOCK_STREAM:
                ip = sockaddr[0] # The address if the first tuple element for both AF_INET and AF_INET6
                print("-> Found %s at %s" % (hostname, ip))
                print()
                hostname = ip
                break 
    
    print("Connecting to robot via SSH at", hostname)
    
    return SshController(hostname, username, password,
                         allow_mitm)


def ensure_win_bins():
    '''Makes sure the right Windows binaries are present'''
    
    if not is_windows:
        return
        
    _win_bins = abspath(join(dirname(__file__), 'win32'))
    _plink_url = 'http://the.earth.li/~sgtatham/putty/latest/x86/plink.exe'
    _psftp_url = 'http://the.earth.li/~sgtatham/putty/latest/x86/psftp.exe'
    
    if not exists(_win_bins):
        os.mkdir(_win_bins)
        
    psftp = join(_win_bins, 'psftp.exe')
    plink = join(_win_bins, 'plink.exe')
        
    if not exists(psftp):
        _urlretrieve(_psftp_url, psftp)
    
    if not exists(plink):
        _urlretrieve(_plink_url, plink)

    return _win_bins

class SshController(object):
    '''
        Use this to transfer files and execute commands on a RoboRIO in a
        cross platform manner
    '''
   
    def __init__(self, hostname, username, password, allow_mitm=False):
        self.username = username
        self.password = password
        self._allow_mitm = allow_mitm
        self.hostname = hostname
    
    @property
    def win_bins(self):
        if not hasattr(self, '_win_bins'):
            self._win_bins = ensure_win_bins()
        return self._win_bins
        
    #
    # This sucks. We should be using paramiko here... but we cannot
    #
    
    def ssh(self, *args, get_output=False):
    
        ssh_args = ['%s@%s' % (self.username, self.hostname)] + list(args)
    
        # Check for requirements
        if is_windows:
            cmd = join(self.win_bins, 'plink.exe')
            
            # plink has a -pw argument we can use, which is nice
            ssh_args = [cmd, '-pw', self.password ] + ssh_args
            
            try:
                if get_output:
                    return subprocess.check_output(ssh_args, universal_newlines=True)
                else:
                    subprocess.check_call(ssh_args)
            except subprocess.CalledProcessError as e:
                raise SshExecError(e, e.returncode)
            
        else:
            cmd = shutil.which('ssh')
            if cmd is None:
                raise Error("Cannot find ssh executable!")
            
            if self._allow_mitm:
                ssh_args = mitm_args + ssh_args
            
            ssh_args = [cmd] + ssh_args
            
            retval, output = ssh_exec_pass(self.password, ssh_args, get_output,
                                           suppress_known_hosts=self._allow_mitm)
            if retval != 0:
                raise SshExecError('Command %s returned non-zero error status %s' % (' '.join(ssh_args), retval),
                                   retval)
            return output.decode('utf-8')
        
    
    def sftp(self, src, dst, mkdir=True):
        '''
            src can be a single file, list of files, or directory
            dst is always a directory, for simplicity
        '''
         
        # Create the batch file
        # - psftp cares about the destination file to be exact
        # - sftp will accept a directory
         
        bfp, bfname = tempfile.mkstemp(text=True)
        try:
            with os.fdopen(bfp, 'w') as fp:
                
                if isinstance(src, str):
                    if isdir(src):
                        rdst = "%s/%s" % (dst, basename(src))
                        if mkdir:
                            fp.write('mkdir "%s"\n' % rdst)
                        
                        if is_windows:
                            fp.write('put -r "%s" "%s/%s"\n' % (src, dst, basename(src)))
                        else:
                            # Some versions of OpenSSH work fine. Some don't. Will
                            # have to do this the hard way instead...
                            # ... https://bugzilla.mindrot.org/show_bug.cgi?id=2150
                            
                            first = True
                            for d, _, files in os.walk(src):
                                if first:
                                    rd = rdst
                                    first = False
                                else:
                                    rd = join(rdst, relpath(d, src))
                                    fp.write('mkdir "%s"\n' % rd)
                                
                                for f in files:
                                    lf = join(d, f)
                                    rf = join(rd, f)
                                    fp.write('put "%s" "%s"\n' % (lf, rf))
                    else:
                        if mkdir:
                            fp.write('mkdir "%s"\n' % dst)
                        
                        fp.write('put "%s" "%s/%s"\n' % (src, dst, basename(src)))
                else:
                    if mkdir:
                        fp.write('mkdir "%s"\n' % dst)
                    
                    for f in src:
                        fp.write('put "%s" "%s/%s"\n' % (f, dst, basename(f)))
            
            sftp_args =['-b', bfname,
                        '%s@%s' % (self.username, self.hostname)]
            
            
            if is_windows:
                cmd = join(self.win_bins, 'psftp.exe')
                
                # psftp has a -pw argument we can use, which is nice
                sftp_args = [ cmd, '-pw', self.password ] + sftp_args
                
                try:
                    subprocess.check_call(sftp_args)
                except subprocess.CalledProcessError as e:
                    raise SshExecError(e, e.returncode)
                
            else:
                cmd = shutil.which('sftp')
                if cmd is None:
                    raise Error("Cannot find sftp executable!")
                
                if self._allow_mitm:
                    sftp_args = mitm_args + sftp_args
                
                # Must disable BatchMode, else password interaction doesn't work
                sftp_args = [cmd, '-oBatchMode=no'] + sftp_args
                
                retval, _ = ssh_exec_pass(self.password, sftp_args,
                                          suppress_known_hosts=self._allow_mitm)
                if retval != 0:
                    raise SshExecError('Command %s returned non-zero error status %s' % (sftp_args, retval),
                                       retval)
            
        finally:
            try:
                os.unlink(bfname)
            except:
                pass
    
    def poor_sync(self, src, dst):
        '''
            :param src: Local file, list of files, or directory to sync
            :param dst: Remote directory to copy file to
            
            .. warning:: if you use a list of files, they cannot have the same
                         filename!
        '''
        
        # Poor man's implementation of rsync. Why? Well..
        # -> Windows may not have rsync
        # -> The roborio does not have it by default (required on client and server side)
        # -> The cache may gather a lot of files, no sense copying all of them
        
        # files is a list of {fname: full_fname}
        
        if not isinstance(src, str):
            files = {basename(f): f for f in src}
            md5sum_cmd = 'md5sum %s 2> /dev/null' % ' '.join(['%s/%s' % (dst, f) for f in files.keys()])
        elif isdir(src):
            files = {f: join(src, f) for f in os.listdir(src)}
            md5sum_cmd = 'md5sum %s/* 2> /dev/null' % (dst)
        else:
            files = {basename(src), src}
            md5sum_cmd = 'md5sum %s/%s 2> /dev/null' % (dst, basename(src))
        
        local_files = {}
        
        for fname, full_fname in files.items():
            fhash = md5sum(full_fname)
            local_files[fname] = fhash
        
        # Hack to determine if the directory actually exists, so that 
        # we create it before putting the files over (necessary because
        # sftp doesn't behave predictably in a cross platform manner 
        # when mkdir fails)
        mkdir = False
        ssh_cmd = md5sum_cmd + '; [ -d "%s" ]; echo $?' % dst
        
        lines = self.ssh(ssh_cmd, get_output=True)
        
        # once you get it, compare them
        for line in lines.split('\n'):
            if len(line) == 1:
                mkdir = (line == '1')
                continue
            md5 = line[:32]
            fname = basename(line[32:].strip())
            
            # Discard matching files
            if fname in local_files and local_files[fname] == md5:
                del local_files[fname]
        
        # Finally, copy the remaining files over
        if len(local_files) != 0:
            local_files = [files[file] for file in local_files.keys()]
            self.sftp(local_files, dst, mkdir=mkdir)


class RobotpyInstaller(object):
    '''
        Logic for installing RobotPy
    '''
    
    cfg_filename = abspath(join(dirname(__file__), '.installer_config'))
    
    pip_cache = abspath(join(dirname(__file__), 'pip_cache'))
    opkg_cache = abspath(join(dirname(__file__), 'opkg_cache'))
    
    # opkg feed
    opkg_arch = 'cortexa9-vfpv3'
    
    commands = [
        'install-robotpy',
        'download-robotpy',
        'install',
        'download',
        'install-pip',
        'download-pip',
        'install-opkg',
        'download-opkg'
    ]

    def __init__(self):
        
        if not exists(self.pip_cache):
            os.makedirs(self.pip_cache)
        
        self._ctrl = None
        self._hostname = None
        self.remote_commands = []

    def _get_opkg(self):
        opkg = OpkgRepo(self.opkg_cache, self.opkg_arch)
        opkg.add_feed('http://www.tortall.net/~robotpy/feeds/2016')
        opkg.add_feed("http://download.ni.com/ni-linux-rt/feeds/2015/arm/ipk/cortexa9-vfpv3")
        return opkg

    def set_hostname(self, hostname):
        if self._ctrl is not None:
            raise ValueError("internal error: too late")
        self._hostname = hostname

    @property
    def ctrl(self):
        if self._ctrl is None:
            self._ctrl = ssh_from_cfg(self.cfg_filename,
                                      username='admin', password='',
                                      hostname=self._hostname,
                                      allow_mitm=True)
        return self._ctrl

    def execute_remote(self):
        if len(self.remote_commands) > 0:
            self.ctrl.ssh(" && ".join(self.remote_commands))

    #
    # Commands
    #

    #
    # RobotPy install commands
    #

    def _create_rpy_pip_options(self, options):
        # Construct an appropriate line to install
        options.requirement = []
        options.packages = ['wpilib',
                            'robotpy-hal-base',
                            'robotpy-hal-roborio']
        options.upgrade = True
        
        options.force_reinstall = False
        options.ignore_installed = False
        options.no_deps = False
        
        if options.basever is not None:
            options.packages = ['%s==%s' % (pkg, options.basever) for pkg in options.packages]

        # Versioning for these packages are separate
        options.packages.append('pynivision')

        if not options.no_tools:
            options.packages.append('robotpy-wpilib-utilities')

        return options

    def _create_rpy_opkg_options(self, options):
        # Construct an appropriate line to install
        options.requirement = []
        options.packages = ['python3']
        options.upgrade = True

        options.force_reinstall = False
        options.ignore_installed = False

        return options

    def install_robotpy_opts(self, parser):
        parser.add_argument('--basever', default=None,
                            help='Install a specific version of WPILib et al')
        parser.add_argument('--no-tools', action='store_true', default=False,
                            help="Don't install robotpy-wpilib-utilities")
        parser.add_argument('--pre', action='store_true', default=False, 
                            help="Include pre-release and development versions.")
    
    def install_robotpy(self, options):
        '''
            This will copy the appropriate RobotPy components to the robot, and install
            them. If the components are already installed on the robot, then they will
            be reinstalled.
        '''
        opkg_options = self._create_rpy_opkg_options(options)
        self.install_opkg(opkg_options)

        # We always add --pre to install-robotpy, in case the user downloaded
        # a prerelease version. Never add --pre without user intervention
        # for download-robotpy, however
        pip_options = self._create_rpy_pip_options(options)
        pip_options.pre = True
        return self.install_pip(pip_options)

    # These share the same options
    download_robotpy_opts = install_robotpy_opts

    def download_robotpy(self, options):
        '''
            This will update the cached RobotPy packages to the newest versions available.
        '''

        self.download_opkg(self._create_rpy_opkg_options(options))

        return self.download_pip(self._create_rpy_pip_options(options))

    #
    # OPKG install commands
    #

    def download_opkg_opts(self, parser):
        parser.add_argument('packages', nargs='*',
                            help="Packages to download")
        parser.add_argument('--force-reinstall', action='store_true', default=False,
                            help='When upgrading, reinstall all packages even if they are already up-to-date.')
    install_opkg_opts = download_opkg_opts

    def download_opkg(self, options):
        """
            Specify opkg package(s) to download, and store them in the cache
        """
        
        # Don't leave windows users stranded
        ensure_win_bins()
        
        opkg = self._get_opkg()
        opkg.update_packages()
        package_list = opkg.resolve_pkg_deps(options.packages)
        for package in package_list:
            opkg.download(package)

    def install_opkg(self, options):
        opkg = self._get_opkg()

        # Write out the install script
        # -> we use a script because opkg doesn't have a good mechanism
        #    to only install a package if it's not already installed
        opkg_script_fname = join(self.opkg_cache, 'install_opkg.sh')
        opkg_script = ""
        opkg_files = []
        package_list = opkg.resolve_pkg_deps(options.packages)
        
        for package in package_list:
            try:
                pkg, fname = opkg.get_cached_pkg(package)
            except OpkgError as e:
                raise Error(e)

            opkg_script_bit = inspect.cleandoc('''
                set -e
                if ! opkg list-installed | grep -F '%(name)s - %(version)s'; then
                    opkg install %(options)s opkg_cache/%(fname)s
                else
                    echo "%(name)s already installed, continuing..."
                fi
            ''')

            opkg_script_bit %= {
                'fname': basename(fname),
                'name': pkg['Package'],
                'version': pkg['Version'],
                'options': "--force-reinstall" if options.force_reinstall else ""
            }
            opkg_script += "\n" + opkg_script_bit
            opkg_files.append(fname)

        with open(opkg_script_fname, 'w', newline='\n') as fp:
            fp.write(opkg_script)
        opkg_files.append(opkg_script_fname)

        print("Copying over the opkg cache...")
        self.ctrl.poor_sync(opkg_files, 'opkg_cache')
        self.remote_commands.append('bash opkg_cache/install_opkg.sh')

    #
    # Pip install commands
    #

    def download_pip_opts(self, parser):
        parser.add_argument('packages', nargs='*',
                            help="Packages to download/install, may be a local file")
        parser.add_argument('-r', '--requirement', action='append', default=[],
                            help='Install from the given requirements file. This option can be used multiple times.')
        parser.add_argument('--pre', action='store_true', default=False, 
                            help="Include pre-release and development versions.")
        
        # Various pip arguments
        parser.add_argument('-U', '--upgrade', action='store_true', default=False,
                            help="Upgrade packages (ignored when downloading, always downloads new packages)")
        
        parser.add_argument('--force-reinstall', action='store_true', default=False,
                            help='When upgrading, reinstall all packages even if they are already up-to-date.')
        parser.add_argument('-I', '--ignore-installed', action='store_true', default=False,
                            help='Ignore the installed packages (reinstalling instead).')
        
        parser.add_argument('--no-deps', action='store_true', default=False,
                            help="Don't install package dependencies.")
    
    def _process_pip_args(self, options):
        pip_args = []
        if options.pre:
            pip_args.append('--pre')
        if options.upgrade:
            pip_args.append('--upgrade')
        if options.force_reinstall:
            pip_args.append('--force-reinstall')
        if options.ignore_installed:
            pip_args.append('--ignore-installed')
        if options.no_deps:
            pip_args.append('--no-deps')
        
        return pip_args
    
    def download_pip(self, options):
        '''
            Specify python package(s) to download, and store them in the cache
        '''
        
        ensure_win_bins()
        
        try:
            import pip
        except ImportError:
            raise Error("ERROR: pip must be installed to download python packages")
        
        if len(options.requirement) == 0 and len(options.packages) == 0:
            raise ArgError("You must give at least one requirement to install")
        
        # Use pip install --download to put packages into the cache
        pip_args = ['install',
                    '--download',
                    self.pip_cache]
        
        pip_args.extend(self._process_pip_args(options))
        
        for r in options.requirement:
            pip_args.extend(['-r', r])
            
        pip_args.extend(options.packages)
    
        return pip.main(pip_args)
    
    # These share the same options
    install_pip_opts = download_pip_opts
    
    def install_pip(self, options):
        '''
            Copies python packages over to the roboRIO, and installs them. If the
            package already has been installed, it will not be upgraded. Use -U to
            upgrade a package.
        '''
        
        if len(options.requirement) == 0 and len(options.packages) == 0:
            raise ArgError("You must give at least one requirement to install")
        
        # TODO
        # Deal with requirements.txt files specially, because we have to 
        # copy the file over.
        
        # copy them to the cache with a unique name, and delete them later?
        if len(options.requirement) != 0:
            raise NotImplementedError()
        
        cmd = "/usr/local/bin/pip3 install --no-index --find-links=pip_cache "
        cmd_args = []

        # Is the user asking to install a file?
        if len(options.packages) == 1 and exists(options.packages[0]):
            pkg = options.packages[0]
            self.ctrl.sftp(pkg, 'pip_cache', mkdir=False)
            cmd_args = ['pip_cache/' + basename(pkg)]
        else:
            # copy the pip cache over
            # .. this is inefficient
            print("Copying over the pip cache...")
            self.ctrl.poor_sync(self.pip_cache, 'pip_cache')

            print("Running installation...")
            cmd_args = options.packages
        
        cmd += ' '.join(self._process_pip_args(options) + cmd_args)
        self.remote_commands.append(cmd)
        
        print("Done.")

    # Backwards-compatibility aliases
    install_opts = install_pip_opts
    install = install_pip
    download_opts = download_pip_opts
    download = download_pip

def main(args=None):

    if args is None:
        args = sys.argv[1:]

    try:
        installer = RobotpyInstaller()
    except Error as e:
        print("ERROR: %s" % e)
        return 1
    
    # argparse boilerplate... 
    parser = argparse.ArgumentParser()
    subparser = parser.add_subparsers(dest='command', help="Commands")
    subparser.required = True
    
    # shared options
    shared = argparse.ArgumentParser(add_help=False)
    shared.add_argument('--robot', default=None, help='Specify the robot hostname')
    
    # Setup various options
    for command in installer.commands:
        fn = getattr(installer, command.replace('-', '_'))
        opt_fn = getattr(installer, command.replace('-', '_') + '_opts')
        cmdparser = subparser.add_parser(command, help=inspect.getdoc(fn),
                                         parents=[shared])
        opt_fn(cmdparser)
        cmdparser.set_defaults(cmdobj=fn)
    
    options = parser.parse_args(args)
    if options.robot:
        installer.set_hostname(options.robot)

    try:
        retval = options.cmdobj(options)
        installer.execute_remote()
    except ArgError as e:
        parser.error(str(e))
        retval = 1
    except Error as e:
        sys.stderr.write(str(e) + '\n')
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
