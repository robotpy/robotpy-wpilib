RobotPy documentation 
=====================

All of our documentation is built using Sphinx, and is hosted at
http://robotpy.readthedocs.org

You can learn more about how to write RST-formatted documetnation
at http://sphinx-doc.org/rest.html#rst-primer

Build your own copy of the docs
===============================

First, you need to install the software needed to build the docs. You can
install it by running the following command in this directory:

    pip3 install -r requirements.txt

If you are on OSX/Linux, you can build the docs using this command:

    make html

On Windows, you need to run this:

    make.bat html

Once this completes, you can open `_build/html/index.html` to view the docs!

