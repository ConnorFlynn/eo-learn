# -*- coding: utf-8 -*-
#
# Configuration file for the Sphinx documentation builder.
#
# This file does only contain a selection of the most common options. For a
# full list see the documentation:
# http://www.sphinx-doc.org/en/master/config

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
import os
import shutil
import sys
from collections import defaultdict
from typing import Any, Dict, Optional

import sphinx.ext.autodoc

import eolearn.core
import eolearn.coregistration
import eolearn.features
import eolearn.geometry
import eolearn.io
import eolearn.mask
import eolearn.ml_tools
import eolearn.visualization  # noqa
from eolearn.core import EOTask

# -- Project information -----------------------------------------------------

# General information about the project.
project = "eo-learn"
copyright = "2018, eo-learn"
author = "Sinergise EO research team"
doc_title = "eo-learn Documentation"

# The version info for the project you're documenting, acts as replacement for
# |version| and |release|, also used in various other places throughout the
# built documents.
#
# The release is read from __init__ file and version is shortened release string.
with open(os.path.join(os.path.dirname(__file__), "../../setup.py")) as setup_file:
    for line in setup_file:
        if "version=" in line:
            release = line.split("=")[1].strip('", \n').strip("'")
            version = release.rsplit(".", 1)[0]

# -- General configuration ---------------------------------------------------

# If your documentation needs a minimal Sphinx version, state it here.
#
# needs_sphinx = '1.0'

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.doctest",
    "sphinx.ext.intersphinx",
    "sphinx.ext.autosummary",
    "sphinx.ext.viewcode",
    "nbsphinx",
    "sphinx_rtd_theme",
    "IPython.sphinxext.ipython_console_highlighting",
    "m2r2",
]

# Include typehints in descriptions
autodoc_typehints = "description"
autodoc_type_aliases = {
    "FeaturesSpecification": "eolearn.core.types.FeaturesSpecification",
    "SingleFeatureSpec": "eolearn.core.types.SingleFeatureSpec",
}

# Both the class’ and the __init__ method’s docstring are concatenated and inserted.
autoclass_content = "both"

# Content is in the same order as in module
autodoc_member_order = "bysource"

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# The suffix(es) of source filenames.
# You can specify multiple suffix as a list of string:
#
# source_suffix = ['.rst', '.md']
source_suffix = ".rst"

# The master toctree document.
master_doc = "index"

# The language for content autogenerated by Sphinx. Refer to documentation
# for a list of supported languages.
#
# This is also used if you do content translation via gettext catalogs.
# Usually you set "language" from the command line for these cases.
language = "en"

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path .
exclude_patterns = ["**.ipynb_checkpoints", "custom_reference*"]

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = "sphinx"

# If true, `todo` and `todoList` produce output, else they produce nothing.
todo_include_todos = True

# Mock imports that won't and don't have to be installed in ReadTheDocs environment
autodoc_mock_imports = [
    "ray",
    "geoviews",
    "hvplot",
    "pyepsg",
    "xarray",
]

# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = "sphinx_rtd_theme"

html_logo = "./figures/eo-learn-logo-white.png"

# Theme options are theme-specific and customize the look and feel of a theme
# further.  For a list of options available for each theme, see the
# documentation.
#
# html_theme_options = {}

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ["_static"]

# Custom sidebar templates, must be a dictionary that maps document names
# to template names.
#
# The default sidebars (for documents that don't match any pattern) are
# defined by theme itself.  Builtin themes are using these templates by
# default: ``['localtoc.html', 'relations.html', 'sourcelink.html',
# 'searchbox.html']``.
#
# html_sidebars = {}


# -- Options for HTMLHelp output ---------------------------------------------

# Output file base name for HTML help builder.
htmlhelp_basename = "eo-learndoc"
# show/hide links for source
html_show_sourcelink = False

# -- Options for LaTeX output ------------------------------------------------

latex_elements = {
    # The paper size ('letterpaper' or 'a4paper').
    #
    # 'papersize': 'letterpaper',
    # The font size ('10pt', '11pt' or '12pt').
    #
    # 'pointsize': '10pt',
    # Additional stuff for the LaTeX preamble.
    #
    # 'preamble': '',
    # Latex figure (float) alignment
    #
    # 'figure_align': 'htbp',
}

# Grouping the document tree into LaTeX files. List of tuples
# (source start file, target name, title,
#  author, documentclass [howto, manual, or own class]).
latex_documents = [
    (master_doc, "eo-learn.tex", doc_title, author, "manual"),
]


# -- Options for manual page output ------------------------------------------

# One entry per manual page. List of tuples
# (source start file, name, description, authors, manual section).
man_pages = [(master_doc, "eo-learn", doc_title, [author], 1)]


# -- Options for Texinfo output ----------------------------------------------

# Grouping the document tree into Texinfo files. List of tuples
# (source start file, target name, title, author,
#  dir menu entry, description, category)
texinfo_documents = [
    (master_doc, "eo-learn", doc_title, author, "eo-learn", "One line description of project.", "Miscellaneous"),
]

# -- Options for Epub output ----------------------------------------------

# Bibliographic Dublin Core info.
epub_title = project
epub_author = author
epub_publisher = author
epub_copyright = copyright

# The unique identifier of the text. This can be a ISBN number
# or the project homepage.
#
# epub_identifier = ''

# A unique identification for the text.
#
# epub_uid = ''

# A list of files that should not be packed into the epub file.
epub_exclude_files = ["search.html"]

# Example configuration for intersphinx: refer to the Python standard library.
intersphinx_mapping = {"https://docs.python.org/3.8/": None}


# -- Custom settings ----------------------------------------------

# When Sphinx documents class signature it prioritizes __new__ method over __init__ method. The following hack puts
# EOTask.__new__ method the the blacklist so that __init__ method signature will be taken instead. This seems the
# cleanest way even though a private object is accessed.
sphinx.ext.autodoc._CLASS_NEW_BLACKLIST.append("{0.__module__}.{0.__qualname__}".format(EOTask.__new__))


EXAMPLES_FOLDER = "./examples"
MARKDOWNS_FOLDER = "./markdowns"


def copy_documentation_examples(source_folder, target_folder):
    """Makes sure to copy only notebooks that are actually included in the documentation"""
    files_to_include = ["core/images/eopatch.png"]

    for rst_file in ["examples.rst", "index.rst"]:
        with open(rst_file, "r") as fp:
            content = fp.read()

        for line in content.split("\n"):
            line = line.strip(" \t")
            if line.startswith("examples/"):
                files_to_include.append(line.split("/", 1)[1])

    for file in files_to_include:
        source_path = os.path.join(source_folder, file)
        target_path = os.path.join(target_folder, file)
        os.makedirs(os.path.dirname(target_path), exist_ok=True)
        shutil.copyfile(source_path, target_path)


# copy examples
shutil.rmtree(EXAMPLES_FOLDER, ignore_errors=True)
copy_documentation_examples("../../examples", EXAMPLES_FOLDER)


shutil.rmtree(MARKDOWNS_FOLDER, ignore_errors=True)
os.mkdir(MARKDOWNS_FOLDER)
shutil.copyfile("../../CONTRIBUTING.md", os.path.join(MARKDOWNS_FOLDER, "CONTRIBUTING.md"))


def process_readme():
    """Function which will process README.md file and divide it into INTRO.md and INSTALL.md, which will be used in
    documentation
    """
    with open("../../README.md", "r") as file:
        readme = file.read()

    readme = readme.replace("# eo-learn", "# Introduction").replace("docs/source/", "")
    readme = readme.replace("[`", "[").replace("`]", "]").replace("docs/source/", "")
    readme = readme.replace("**`", "**").replace("`**", "**")

    chapters = [[]]
    for line in readme.split("\n"):
        if line.strip().startswith("## "):
            chapters.append([])
        if line.startswith("<img"):
            line = "<p></p>"

        chapters[-1].append(line)

    chapters = ["\n".join(chapter) for chapter in chapters]

    intro = "\n".join(
        [
            chapter
            for chapter in chapters
            if not (chapter.startswith("## Install") or chapter.startswith("## Documentation"))
        ]
    )
    install = "\n".join([chapter for chapter in chapters if chapter.startswith("## Install")])

    intro = intro.replace("./CONTRIBUTING.md", "contribute.html")

    with open(os.path.join(MARKDOWNS_FOLDER, "INTRO.md"), "w") as file:
        file.write(intro)
    with open(os.path.join(MARKDOWNS_FOLDER, "INSTALL.md"), "w") as file:
        file.write(install)


process_readme()


# Create a list of all EOTasks
def get_subclasses(cls):
    direct_subclasses = cls.__subclasses__()
    nested_subclasses = [s for c in direct_subclasses for s in get_subclasses(c)]

    return list(set(direct_subclasses).union(nested_subclasses))


EOTASKS_PATH = "eotasks"

with open(f"{EOTASKS_PATH}.rst", "w") as f:
    f.write("EOTasks\n")
    f.write("=======\n")
    f.write("\n")

    eopackage_tasks = {}

    for eotask_cls in get_subclasses(EOTask):
        eopackage = eotask_cls.__module__.split(".")[1]
        eotask = eotask_cls.__module__ + "." + eotask_cls.__name__

        if eopackage not in eopackage_tasks:
            eopackage_tasks[eopackage] = []

        eopackage_tasks[eopackage].append(eotask)

    for eopackage in sorted(eopackage_tasks.keys()):
        f.write(eopackage + "\n")
        f.write("-" * len(eopackage) + "\n")
        f.write("\n")

        f.write(".. currentmodule:: eolearn." + eopackage + "\n")
        f.write(".. autosummary::\n")
        f.write("\t:nosignatures:\n")
        f.write("\n")

        eotasks = eopackage_tasks[eopackage]
        eotasks.sort()

        for eotask in eotasks:
            # tilde is used to show only the class name without the module
            f.write("\t~" + eotask + "\n")

        f.write("\n")


# Auto-generate documentation pages
current_dir = os.path.abspath(os.path.dirname(__file__))
reference_dir = os.path.join(current_dir, "reference")
custom_reference_dir = os.path.join(current_dir, "custom_reference")
custom_reference_files = {filename.rsplit(".", 1)[0] for filename in os.listdir(custom_reference_dir)}

repository_dir = os.path.join(current_dir, "..", "..")
modules = ["core", "coregistration", "features", "geometry", "io", "mask", "ml_tools", "visualization"]

APIDOC_OPTIONS = ["--module-first", "--separate", "--no-toc", "--templatedir", os.path.join(current_dir, "_templates")]
APIDOC_EXCLUDE = defaultdict(list, {"core": ["graph.py", "eodata_io.py", "eodata_merge.py"]})

shutil.rmtree(reference_dir, ignore_errors=True)
shutil.copytree(custom_reference_dir, reference_dir)


def run_apidoc(_):
    from sphinx.ext.apidoc import main

    sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
    for module in modules:
        module_dir = os.path.join(current_dir, "..", "..", module)

        exclude = [os.path.join(module_dir, "eolearn", module, filename) for filename in APIDOC_EXCLUDE[module]]
        exclude.extend([os.path.join(module_dir, "setup.py"), os.path.join(module_dir, "eolearn", "tests")])

        main(["-e", "-o", reference_dir, module_dir, *exclude, *APIDOC_OPTIONS])


def configure_github_link(_app: Any, pagename: str, _templatename: Any, context: Dict[str, Any], _doctree: Any) -> None:
    """Because some pages are auto-generated and some are copied from their original location the link "Edit on GitHub"
    of a page is wrong. This function computes a custom link for such pages and saves it to a custom meta parameter
    `github_url` which is then picked up by `sphinx_rtd_theme`.

    Resources to understand the implementation:
    - https://www.sphinx-doc.org/en/master/extdev/appapi.html#event-html-page-context
    - https://dev.readthedocs.io/en/latest/design/theme-context.html
    - https://sphinx-rtd-theme.readthedocs.io/en/latest/configuring.html?highlight=github_url#file-wide-metadata
    - https://github.com/readthedocs/sphinx_rtd_theme/blob/1.0.0/sphinx_rtd_theme/breadcrumbs.html#L35
    """
    # ReadTheDocs automatically sets the following parameters but for local testing we set them manually:
    show_link = context.get("display_github")
    context["display_github"] = True if show_link is None else show_link
    context["github_user"] = context.get("github_user") or "sentinel-hub"
    context["github_repo"] = context.get("github_repo") or "eo-learn"
    context["github_version"] = context.get("github_version") or "develop"
    context["conf_py_path"] = context.get("conf_py_path") or "/docs/source/"

    if pagename.startswith("examples/"):
        github_url = create_github_url(context, conf_py_path="/")

    elif pagename.startswith("reference/"):
        filename = pagename.split("/", 1)[1]

        if filename in custom_reference_files:
            github_url = create_github_url(context, pagename=f"custom_reference/{filename}")
        else:
            subpackage = filename.split(".")[1]
            filename = filename.replace(".", "/")
            filename = f"{subpackage}/{filename}"

            full_path = os.path.join(repository_dir, f"{filename}.py")
            is_module = os.path.exists(full_path)

            github_url = create_github_url(
                context,
                theme_vcs_pageview_mode="blob" if is_module else "tree",
                conf_py_path="/",
                pagename=filename,
                page_source_suffix=".py" if is_module else "",
            )

    elif pagename == EOTASKS_PATH:
        # This page is auto-generated in conf.py
        github_url = create_github_url(context, pagename="conf", page_source_suffix=".py")

    else:
        return

    context["meta"] = context.get("meta") or {}
    context["meta"]["github_url"] = github_url


def create_github_url(
    context: Dict[str, Any],
    theme_vcs_pageview_mode: Optional[str] = None,
    conf_py_path: Optional[str] = None,
    pagename: Optional[str] = None,
    page_source_suffix: Optional[str] = None,
) -> str:
    """Creates a GitHub URL from context in exactly the same way as in
    https://github.com/readthedocs/sphinx_rtd_theme/blob/1.0.0/sphinx_rtd_theme/breadcrumbs.html#L39

    The function allows URL customization by overwriting certain parameters.
    """
    github_host = context.get("github_host") or "github.com"
    github_user = context.get("github_user", "")
    github_repo = context.get("github_repo", "")
    theme_vcs_pageview_mode = theme_vcs_pageview_mode or context.get("theme_vcs_pageview_mode") or "blob"
    github_version = context.get("github_version", "")
    conf_py_path = conf_py_path or context.get("conf_py_path", "")
    pagename = pagename or context.get("pagename", "")
    page_source_suffix = context.get("page_source_suffix", "") if page_source_suffix is None else page_source_suffix
    return (
        f"https://{github_host}/{github_user}/{github_repo}/{theme_vcs_pageview_mode}/"
        f"{github_version}{conf_py_path}{pagename}{page_source_suffix}"
    )


def setup(app):
    app.connect("builder-inited", run_apidoc)
    app.connect("html-page-context", configure_github_link)
    app.connect("autodoc-process-docstring", sphinx.ext.autodoc.between("Credits:", what=["module"], exclude=True))
