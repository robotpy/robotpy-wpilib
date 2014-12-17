#!/usr/bin/env python3
'''
    A custom documentation generator because sphinx-apidoc doesn't quite do
    what I want it to. The autosummary thing is really close to what I want.
    However, the documentation for how to use it is lacking.
    
    This is designed to generate docs for our flat import structure in a
    manner that is friendly to the readthedocs theme.
'''

import os
import sys
import inspect
import shutil

from os.path import abspath, join, dirname, exists

import sphinx.apidoc

mod_doc = '''
%(header)s

.. automodule:: %(module)s
    :members:

.. autosummary::
    %(cls_names)s

.. toctree::
    :hidden:
    
    %(cls_files)s

'''

cls_doc = '''
%(header)s

.. automodule:: %(clsmodname)s
    :members:
    :undoc-members:
    :show-inheritance:
'''

def heading(name, c):
    return '%s\n%s' % (name, c*len(name))


def gen_package(mod):
    
    name = mod.__name__
    
    docdir = abspath(join(dirname(__file__), name))
    pkgrst = abspath(join(dirname(__file__), '%s.rst' % name))
    
    if exists(docdir):
        shutil.rmtree(docdir)
        
    os.mkdir(docdir)
    
    classes = []
    
    for clsname, cls in inspect.getmembers(mod, inspect.isclass):
        
        clsmodname = cls.__module__
        with open(join(docdir, '%s.rst' % clsname), 'w') as fp:
            fp.write(cls_doc % {
                'modname': name,
                'header':  heading(clsname, '-'),
                'clsname': clsname,
                'clsmodname': clsmodname
            })
        
        classes.append((clsmodname, clsname))

    classes = sorted(classes)

    # Create toctree
    with open(pkgrst, 'w') as fp:
        
        cls_names = ['%s.%s' % (clsmodule, clsname) for clsmodule, clsname in classes]
        cls_files = ['%s/%s' % (name, clsname) for clsmodule, clsname in classes]
    
        fp.write(mod_doc % {
            'header': heading(name + ' Package', '='),
            'module': name,
            'cls_names': '\n    '.join(cls_names),
            'cls_files': '\n    '.join(cls_files)
        })

def main():
    
    sys.path.insert(0, abspath(join(dirname(__file__), '..', 'wpilib')))
    sys.path.insert(0, abspath(join(dirname(__file__), '..', 'hal-base')))
    sys.path.insert(0, abspath(join(dirname(__file__), '..', 'hal-sim')))
    
    import wpilib
    import wpilib.buttons
    import wpilib.command
    import wpilib.interfaces
    
    gen_package(wpilib)
    gen_package(wpilib.buttons)
    gen_package(wpilib.command)
    gen_package(wpilib.interfaces)
    


if __name__ == '__main__':
    main()
