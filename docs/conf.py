#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# Imports
#

import sys
import os
from os.path import abspath, dirname

# Project must be built+installed to generate docs
import wpilib

# -- RTD configuration ------------------------------------------------

# on_rtd is whether we are on readthedocs.org, this line of code grabbed from docs.readthedocs.org
on_rtd = os.environ.get("READTHEDOCS", None) == "True"

# This is used for linking and such so we link to the thing we're building
rtd_version = os.environ.get("READTHEDOCS_VERSION", "latest")
if rtd_version not in ["stable", "latest"]:
    rtd_version = "stable"

# -- General configuration ------------------------------------------------


# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.intersphinx",
    "sphinx.ext.viewcode",
    "robotpy_sphinx.all",
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# The suffix of source filenames.
source_suffix = ".rst"

# The master toctree document.
master_doc = "index"

# General information about the project.
project = "RobotPy WPILib"
copyright = "2014-2020, RobotPy development team"

# The version info for the project you're documenting, acts as replacement for
# |version| and |release|, also used in various other places throughout the
# built documents.
#
# The short X.Y version.
version = ".".join(wpilib.__version__.split(".")[:2])
# The full version, including alpha/beta/rc tags.
release = wpilib.__version__

autoclass_content = "both"

intersphinx_mapping = {
    "networktables": (
        f"https://pynetworktables.readthedocs.io/en/{rtd_version}/",
        None,
    ),
    "wpimath": (
        f"https://robotpy.readthedocs.io/projects/wpimath/en/{rtd_version}/",
        None,
    ),
}

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
exclude_patterns = ["_build"]

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = "sphinx"

# -- Options for HTML output ----------------------------------------------

if not on_rtd:  # only import and set the theme if we're building docs locally
    import sphinx_rtd_theme

    html_theme = "sphinx_rtd_theme"
    html_theme_path = [sphinx_rtd_theme.get_html_theme_path()]
else:
    html_theme = "default"

# Output file base name for HTML help builder.
htmlhelp_basename = "RobotPyWPILibdoc"


# -- Options for LaTeX output ---------------------------------------------

latex_elements = {}

# Grouping the document tree into LaTeX files. List of tuples
# (source start file, target name, title,
#  author, documentclass [howto, manual, or own class]).
latex_documents = [
    (
        "index",
        "RobotPyWPILib.tex",
        "RobotPy WPILib Documentation",
        "RobotPy development team",
        "manual",
    )
]

# -- Options for Texinfo output -------------------------------------------

# Grouping the document tree into Texinfo files. List of tuples
# (source start file, target name, title, author,
#  dir menu entry, description, category)
texinfo_documents = [
    (
        "index",
        "RobotPyWPILib",
        "RobotPy WPILib Documentation",
        "RobotPy development team",
        "RobotPyWPILib",
        "One line description of project.",
        "Miscellaneous",
    )
]

# -- Options for Epub output ----------------------------------------------

# Bibliographic Dublin Core info.
epub_title = "RobotPy WPILib"
epub_author = "RobotPy development team"
epub_publisher = "RobotPy development team"
epub_copyright = "2014, RobotPy development team"

# A list of files that should not be packed into the epub file.
epub_exclude_files = ["search.html"]

# -- Custom Document processing ----------------------------------------------

from robotpy_sphinx.regen import gen_package
from robotpy_sphinx.sidebar import generate_sidebar

generate_sidebar(
    globals(),
    "wpilib",
    "https://raw.githubusercontent.com/robotpy/docs-sidebar/master/sidebar.toml",
)

root = abspath(dirname(__file__))

gen_package(root, "wpilib", exclude=["wpi_*"])
gen_package(root, "wpilib.drive")
gen_package(root, "wpilib.interfaces")
gen_package(root, "wpilib.simulation")
