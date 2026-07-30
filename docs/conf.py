import os
import sys
from importlib.metadata import version as get_version

old_changelog = os.path.join(os.path.dirname(__file__), "..", "CHANGELOG.md")
new_changelog = os.path.join(os.path.dirname(__file__), "changelog.md")

with open(old_changelog, encoding="utf-8") as f:
    changelog_lines = f.readlines()

# Inject relative documentation links
for i, line in enumerate(changelog_lines):
    if line.startswith("[version guarantees]: "):
        changelog_lines[i] = "[version guarantees]: version_guarantees.rst\n"
        break

CHANGELOG_TEXT = "".join(changelog_lines) + """
## Older Versions

A changelog for versions prior to v2.0 can be found [here](old_changelog.rst).
"""


# Only write if it's changed to avoid recompiling the docs
def write_new():
    with open(new_changelog, "w", encoding="utf-8") as fw:
        fw.write(CHANGELOG_TEXT)


try:
    c_file = open(new_changelog, encoding="utf-8")
except FileNotFoundError:
    write_new()
else:
    if c_file.read() != CHANGELOG_TEXT:
        write_new()
    c_file.close()

sys.path.insert(0, os.path.abspath(".."))
sys.path.append(os.path.abspath("extensions"))

# -- General configuration ------------------------------------------------

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosectionlabel",
    "sphinx.ext.autosummary",
    "sphinx.ext.extlinks",
    "sphinx.ext.intersphinx",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
    "sphinx.ext.duration",
    "sphinxcontrib_trio",
    "exception_hierarchy",
    "attributetable",
    "resourcelinks",
    "nitpick_file_ignorer",
    "myst_parser",
    "sphinx_copybutton",
    "sphinxext.opengraph",
    "sphinx_autodoc_typehints",
]

always_document_param_types = True
toc_object_entries_show_parents = "hide"
autosectionlabel_prefix_document = True

ogp_site_url = "https://pycord.dev/"
ogp_image = "https://pycord.dev/static/img/logo.png"

autodoc_member_order = "bysource"
autodoc_typehints = "signature"

# Disable overload signature injection to keep docs concise. See https://github.com/Pycord-Development/pycord/pull/3124
typehints_document_overloads = False
# maybe consider this? # TODO(Paillat-dev): Consider this
# napoleon_attr_annotations = False

extlinks = {
    "issue": ("https://github.com/Pycord-Development/pycord/issues/%s", "GH-%s"),
    "dpy-issue": ("https://github.com/Rapptz/discord.py/issues/%s", "GH-%s"),
}

intersphinx_mapping = {
    "py": ("https://docs.python.org/3", None),
    "aio": ("https://docs.aiohttp.org/en/stable/", None),
    "req": ("https://requests.readthedocs.io/en/latest/", None),
}

rst_prolog = """
.. |coro| replace:: This function is a |coroutine_link|_.
.. |maybecoro| replace:: This function *could be a* |coroutine_link|_.
.. |coroutine_link| replace:: *coroutine*
.. _coroutine_link: https://docs.python.org/3/library/asyncio-task.html#coroutine
.. |gateway| replace:: |gateway_link|_
.. |gateway_link| replace:: *gateway*
.. _gateway_link: https://docs.discord.com/developers/events/gateway-events
"""

templates_path = ["_templates"]

source_suffix = {
    ".rst": "restructuredtext",  # Used For The Other Docs
    ".md": "markdown",  # Used ONLY In the Guide For Faster Making Time
}

master_doc = "index"

project = "Pycord"
copyright = "2015-2021, Rapptz & 2021-present, Pycord Development"

# The full version, including alpha/beta/rc tags.
release = get_version("py-cord")

# The short X.Y version.
version = ".".join(release.split(".")[:2])

# This assumes a tag is available for final releases
branch = (
    "master"
    if "a" in version or "b" in version or "rc" in version or "dev" in release
    else f"v{release}"
)

html_title = f"{project} v{version} Documentation"

language = "en"

gettext_compact = False
gettext_uuid = True
locale_dirs = ["locales/"]

exclude_patterns = ["_build", "node_modules", "build", "locales"]

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = "friendly"

# Nitpicky mode options
nitpick_ignore_files = [
    "migrating_to_v1",
    "whats_new",
    "old_changelog",
]

# -- Options for HTML output ----------------------------------------------

html_theme = "furo"

html_context = {
    "discord_invite": "https://pycord.dev/discord",
    "discord_extensions": [
        ("discord.ext.commands", "ext/commands"),
        ("discord.ext.tasks", "ext/tasks"),
        ("discord.ext.pages", "ext/pages"),
        ("discord.ext.bridge", "ext/bridge"),
    ],
}

resource_links = {
    "discord": "https://pycord.dev/discord",
    "issues": "https://github.com/Pycord-Development/pycord/issues",
    "discussions": "https://github.com/Pycord-Development/pycord/discussions",
    "examples": f"https://github.com/Pycord-Development/pycord/tree/{branch}/examples",
    "guide": "https://guide.pycord.dev/",
}

base_colors = {
    "white": "#ffffff",
    "grey-1": "#f9f9fa",
    "grey-1-8": "rgba(249, 249, 250, 0.8)",
    "grey-2": "#ededf0",
    "grey-3": "#d7d7db",
    "grey-4": "#b1b1b3",
    "grey-5": "#2a2a2b",
    "grey-6": "#4a4a4f",
    "grey-7": "#2a2a2b",
    "grey-8": "#1e1e1f",
    "black": "#0c0c0d",
    "blue-1": "#3399ff",
    "blue-2": "#0a84ff",
    "blue-3": "#0060df",
    "blue-4": "#003eaa",
    "blue-5": "#002275",
    "blue-6": "#000f40",
    "blurple": "#5865F2",
}

html_theme_options = {
    "source_repository": "https://github.com/Pycord-Development/pycord",
    "source_branch": "master",
    "source_directory": "docs/",
    "light_css_variables": {
        # Theme
        # "color-brand-primary": "#5865f2",
        "font-stack": "'Outfit', sans-serif",
        # Custom
        **base_colors,
        "attribute-table-title": "var(--grey-6)",
        "attribute-table-entry-border": "var(--grey-3)",
        "attribute-table-entry-text": "var(--grey-5)",
        "attribute-table-entry-hover-border": "var(--blue-2)",
        "attribute-table-entry-hover-background": "var(--grey-2)",
        "attribute-table-entry-hover-text": "var(--blue-2)",
        "attribute-table-badge": "var(--grey-7)",
        "light-snake-display": "unset",
        "dark-snake-display": "none",
    },
    "dark_css_variables": {
        # Theme
        # "color-foreground-primary": "#fff",
        # "color-brand-primary": "#5865f2",
        # "color-background-primary": "#17181a",
        # "color-background-secondary": "#1a1c1e",
        # "color-background-hover": "#33373a",
        # Custom
        "attribute-table-title": "var(--grey-3)",
        "attribute-table-entry-border": "var(--grey-5)",
        "attribute-table-entry-text": "var(--grey-3)",
        "attribute-table-entry-hover-border": "var(--blue-1)",
        "attribute-table-entry-hover-background": "var(--grey-6)",
        "attribute-table-entry-hover-text": "var(--blue-1)",
        "attribute-table-badge": "var(--grey-4)",
        "light-snake-display": "none",
        "dark-snake-display": "unset",
    },
}

html_logo = "./images/pycord_logo.png"
html_favicon = "./images/pycord.ico"

html_static_path = ["_static"]
html_css_files = ["css/custom.css"]
html_js_files = ["js/custom.js"]

html_sidebars = {
    "**": [
        "sidebar/brand.html",
        "sidebar/search.html",
        "sidebar/scroll-start.html",
        "sidebar/navigation.html",
        "sidebar/ethical-ads.html",
        "sidebar/width-selector.html",
        "sidebar/scroll-end.html",
        "sidebar/variant-selector.html",
    ]
}

html_search_language = "en"

htmlhelp_basename = "pycorddoc"

# -- Options for LaTeX output ---------------------------------------------

latex_documents = [
    ("index", "Pycord.tex", "Pycord Documentation", "Pycord Development", "manual"),
]

# -- Options for manual page output ---------------------------------------

man_pages = [("index", "Pycord", "Pycord Documentation", ["Pycord Development"], 1)]

# -- Options for Texinfo output -------------------------------------------

texinfo_documents = [
    (
        "index",
        "Pycord",
        "Pycord Documentation",
        "Pycord Development",
        "Pycord",
        "An async Discord API wrapper for Python.",
        "Miscellaneous",
    ),
]

linkcheck_ignore = [
    r"https://docs.discord.com/developers/.*#",
    r"https://support(?:-dev)?.discord.com/hc/en-us/articles/.*",
    r"https://dis.gd/contact",
    r"https://guide.pycord.dev/",
    r"https://guide.pycord.dev/.*",
    r"https://pycord.dev/",
    r"https://pycord.dev/.*",
    r"https://packages.debian.org/.*",
    r"https://github.com/Pycord-Development/pycord/issues/new\?template=bug_report.yml",
    r"https://discord.com/developers/.*",
]

linkcheck_exclude_documents = [
    r".*/migrating_to_v1.*",
    r".*/migrating_to_v2.*",
    r".*/old_changelog.*",
    r"migrating_to_v1.*",
    r"migrating_to_v2.*",
    r"old_changelog.*",
]

linkcheck_anchors_ignore_for_url = [r"https://github.com/Delitefully/DiscordLists"]

modindex_common_prefix = ["discord."]
suppress_warnings = ["autosectionlabel.*"]
myst_enable_extensions = [
    "amsmath",
    "attrs_inline",
    "colon_fence",
    "deflist",
    "dollarmath",
    "fieldlist",
    "html_admonition",
    "html_image",
    "linkify",
    "replacements",
    "smartquotes",
    "strikethrough",
    "substitution",
    "tasklist",
]
myst_links_external_new_tab = True
