#!/usr/bin/env python3
#
# This tool allows us to put metadata in each file noting the last git
# commit that the original java file was inspected at. Using this metadata,
# you can use the 'diff' command of the tool to easily see the changes
# that were made to the original file.
#
# Once you're satisified that our version of the file matches sufficiently
# enough, use the set-valid command to record the validation data.
#

import argparse
from contextlib import contextmanager
import inspect
import os
import posixpath
from os.path import abspath, basename, dirname, exists, join, normpath, relpath, splitext
import sys
import tempfile
import time

import sh


# Original files
orig_root = abspath(join(dirname(__file__), '..', '..', 'allwpilib', 'wpilibj', 'src'))

# Files that are being validated 
validation_root = abspath(join(dirname(__file__), '..', 'wpilib', 'wpilib')) 

exclude_commits_file = abspath(join(dirname(__file__), 'exclude_commits'))

invalid_hash = 'DOES_NOT_EXIST'

# git log option to exclude commits
def excluded_commits():
    exclude_commits = []
    
    if exists(exclude_commits_file):
        with open(exclude_commits_file) as fp:
            for line in fp:
                line = line.split()
                if line:
                    exclude_commits.append('commit %s' % line[0].strip())
                    
    
    return exclude_commits


def git_log(fname, rev_range=None):
    '''
        Executes git log for a particular file, excluding particular commits that aren't
        particularly useful to see
    '''
    
    if rev_range:
        endl = (rev_range, fname)
        end = '%s %s' % (rev_range, fname)
    else:
        endl = (fname,)
        end = fname
    
    tname = None
    excluded = excluded_commits()
    
    if len(excluded) == 0:
        os.system('git log --follow -p %s' % end)
    else:
        # read all the commits in, filtering out the excluded commits
        try:
            # grep -z isn't portable, so do it in python
            pycontents = inspect.cleandoc("""
                commits = ['%s']
                
                import sys
                for t in sys.stdin.read().split('\\0'):
                    for c in commits:
                        if c in t:
                            break
                    else:
                        sys.stdout.write(t)
            """) % ("','".join(excluded))
            
            with tempfile.NamedTemporaryFile(mode='w', delete=False) as fp:
                tname = fp.name
                fp.write(pycontents)
            
            cmd = "git log --follow -p -z --color %s | python3 %s | tr -d '\\000' | less -FRX" % (end, tname)
            os.system(cmd)
            
        finally:
            if tname is not None:
                os.unlink(tname)
            pass

@contextmanager
def chdir(path):
    orig_path = os.getcwd()
    os.chdir(path)
    yield
    os.chdir(orig_path)


def get_fname(root, fname):
    if exists(fname):
        return abspath(fname)
    
    fname = join(root, fname)
    if exists(fname):
        return abspath(fname)
    
    raise OSError('%s does not exist' % fname)

def find_suggestions(fname):
    fname = splitext(basename(fname))[0].lower()
    
    for root, _, files in os.walk(orig_root):
        for f in files:
            if splitext(f)[0].lower() == fname:
                yield relpath(join(root, f), orig_root)

def choose_suggestion(fname):
    suggestions = list(find_suggestions(fname))
    if suggestions:
        print("Suggestions:")
        for i, s in enumerate(suggestions):
            print(" ", i, s)
        
        v = input("Use? [0-%s,n] " % i)
        if v != 'n':
            return suggestions[int(v)]

class ValidationInfo:
    
    @staticmethod
    def from_line(py_fname, line):
        line = line.strip()
        if line.startswith('# novalidate'):
            return ValidationInfo(novalidate=True)
        
        s = line.split()
        if len(s) != 6:
            raise ValueError("Invalid validation line: %s" % line)
        
        return ValidationInfo(date=s[2],
                              initials=s[3],
                              hash=s[4],
                              orig_fname=s[5],
                              py_fname=py_fname)
    
    @staticmethod
    def from_now(initials, orig_fname):
        v = ValidationInfo(date=time.strftime('%Y-%m-%d'),
                           initials=initials,
                           orig_fname=posixpath.normpath(orig_fname))
        
        v.hash = v.orig_hash
        return v
    
    def __init__(self, **kwargs):
        self.novalidate = kwargs.get('novalidate', False)
        self.date = kwargs.get('date')
        self.initials = kwargs.get('initials')
        self.hash = kwargs.get('hash')
        self.orig_fname = kwargs.get('orig_fname')
        self.py_fname = kwargs.get('py_fname')
        
    
    @property
    def orig_hash(self):
        if not hasattr(self, '_orig_hash'):
            with chdir(orig_root):
                fpath = normpath(self.orig_fname)
                if not exists(fpath):
                    self._orig_hash = invalid_hash
                else:
                    self._orig_hash = str(sh.git('log', '-n1', '--pretty=%h', fpath, _tty_out=False)).strip()
        
        return self._orig_hash
    
    @property
    def line(self):
        if self.novalidate:
            return '# novalidate\n'
        else:
            return '# validated: %(date)s %(initials)s %(hash)s %(orig_fname)s\n' % self.__dict__
    
    def __repr__(self):
        return '<ValidationInfo: %s>' % self.line.strip()

# modify a single file
def set_info(fname, info):
    '''
        Writes the magic to the first line that starts with # validated
        or # novalidate. If no such line exists, write to the first line
        of the file
    '''
    
    with open(fname, 'r') as fin, \
         tempfile.NamedTemporaryFile(dir=dirname(fname), mode='w', delete=False) as fout:
        
        found = False
        written = False
        
        # search for the line first
        for line in fin:
            if line.startswith('# validated') or \
               line.startswith('# novalidate'):
                found = True
                break
        
        fin.seek(0)
        
        # Now rewrite the file
        for line in fin:
            if not written:
                if not found:
                    fout.write(info.line)
                    written = True
                    
                elif line.startswith('# validated') or \
                   line.startswith('# novalidate'):
                    line = info.line
                    written = True
            
            fout.write(line)
            
    os.replace(fout.name, fname)

def get_info(fname):
    with open(normpath(fname)) as fp:
        for line in fp:
            if line.startswith('# validated') or \
               line.startswith('# novalidate'):
                return ValidationInfo.from_line(fname, line)

#
# Actions
#

def action_show(args):
    '''
        Show status of all files
    '''
    
    counts = {'good': 0, 'outdated': 0, 'unknown': 0}
    
    if hasattr(args, 'filename') and args.filename is not None:
        _action_show(get_fname(validation_root, args.filename), counts)
    else:
        for root, _, files in os.walk(validation_root):
            for f in sorted(files):
                if not f.endswith('.py') or f == '__init__.py':
                    continue
                
                fname = join(root, f)
                _action_show(fname, counts)
    
    print()
    print("%(good)s OK, %(outdated)s out of date, %(unknown)s unknown" % (counts))

def _action_show(fname, counts):
    

    info = get_info(fname)
    path = relpath(fname, validation_root)
    
    if info is None:
        status = '-- '
        counts['unknown'] += 1
    elif info.novalidate:
        status = 'OK '
        counts['good'] += 1
    else:
        if info.hash == info.orig_hash:
            status = 'OK '
            counts['good'] += 1
        elif info.orig_hash == invalid_hash:
            status = 'ERR'
            counts['unknown'] += 1
        else:
            status = "OLD"
            path += ' (%s..%s)' % (info.hash, info.orig_hash)
            counts['outdated'] += 1
    
    print('%s: %s' % (status, path))
    

def action_diff(args):
    
    info = get_info(get_fname(validation_root, args.filename))
    if info is None:
        raise OSError("No validation information found for %s" % args.filename)
    
    if info.orig_hash == invalid_hash:
        update_src(info)
    
    with chdir(orig_root): 
        git_log(normpath(info.orig_fname),
                '%s..%s' % (info.hash, info.orig_hash))
    
    if info.orig_hash != info.hash:
        print()
        if input("Validate file? [y/n]").lower() in ['y', 'yes']:
            args.orig_fname = None
            action_validate(args)
        

def action_validate(args):

    fname = get_fname(validation_root, args.filename)

    initials = args.initials
    if not initials:
        name = sh.git('config', 'user.name', _tty_out=False).strip()
        initials = ''.join(n[0] for n in name.split())
        
    if not initials:
        raise ValueError("Specify --initials or execute 'git config user.name Something'")
    
    orig_fname = args.orig_fname
    if not orig_fname:
        info = get_info(fname)
        if info is not None:
            orig_fname = info.orig_fname
    
    # if there's no orig_filename specified, then raise an error
    if not orig_fname:
        orig_fname = choose_suggestion(fname)
        if not orig_fname:
            raise ValueError("Error: must specify original filename")
    
    info = ValidationInfo.from_now(initials, orig_fname)
    
    # write the information to the file
    set_info(fname, info)
    
    print(fname)
    print(info.line)
    
def action_novalidate(args):
    fname = get_fname(validation_root, args.filename)
    info = ValidationInfo(novalidate=True)
    set_info(fname, info)
    
    print(fname)
    print(info.line)


def action_show_log(args):
    '''Shows logs of file in original root'''
    fname = choose_suggestion(args.filename)
    if fname:
       with chdir(orig_root):
           git_log(fname)

def update_src(info):
    print(info.orig_fname, "no longer exists, choose another?")
    info.orig_fname = choose_suggestion(relpath(info.py_fname, validation_root))
    if info.orig_fname is not None:
        set_info(info.py_fname, info)
        if hasattr(info, '_orig_hash'):
            delattr(info, '_orig_hash')

def action_update_src(args):
    '''Update the source of a file if it's renamed'''
    fname = get_fname(validation_root, args.filename)
    info = get_info(fname)
    if info is None:
        print(fname, "not validated, no source to update")
    elif info.orig_hash != invalid_hash:
        print("Update not required for", fname)
    else:
        update_src(info)
        
             

if __name__ == '__main__':
    
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest='action')
    
    sp = subparsers.add_parser('diff')
    sp.add_argument('filename')
    sp.add_argument('--initials', default=None)
    
    sp = subparsers.add_parser('show')
    sp.add_argument('filename', nargs='?')
    
    sp = subparsers.add_parser('set-valid')
    sp.add_argument('filename')
    sp.add_argument('orig_fname', nargs='?')
    sp.add_argument('--initials', default=None)
    
    sp = subparsers.add_parser('set-novalidate')
    sp.add_argument('filename')
    
    sp = subparsers.add_parser('show-log')
    sp.add_argument('filename')
    
    sp = subparsers.add_parser('update-src')
    sp.add_argument('filename')

    args = parser.parse_args()
    
    if args.action in [None, 'show']:
        action_show(args)
        
    elif args.action == 'diff':
        action_diff(args)
        
    elif args.action == 'set-valid':
        action_validate(args)
        
    elif args.action == 'set-novalidate':
        action_novalidate(args)
        
    elif args.action == 'show-log':
        action_show_log(args)
        
    elif args.action == 'update-src':
        action_update_src(args)
        
    else:
        parser.error("Invalid action %s" % args.action)
