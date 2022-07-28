import re

from setuptools import setup

# Requirements
requirements = []
with open("requirements.txt") as f:
    requirements = f.read().splitlines()

# Version Info
version = ""
with open("discord/__init__.py") as f:

    search = re.search(r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]', f.read(), re.MULTILINE)

    if search is not None:
        version = search.group(1)

    else:
        raise RuntimeError("Could not grab version string")

if not version:
    raise RuntimeError("version is not set")

if version.endswith(("a", "b", "rc")):
    # append version identifier based on commit count
    try:
        import subprocess

        p = subprocess.Popen(
            ["git", "rev-list", "--count", "HEAD"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        out, err = p.communicate()
        if out:
            version += out.decode("utf-8").strip()
        p = subprocess.Popen(
            ["git", "rev-parse", "--short", "HEAD"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        out, err = p.communicate()
        if out:
            version += f"+g{out.decode('utf-8').strip()}"
    except Exception:
        pass

# README
readme = ""
with open("README.rst") as f:
    readme = f.read()

# Extra Requirements
# Ex: pip install py-cord[voice] or [speed]
extras_require = {
    "voice": ["PyNaCl>=1.3.0,<1.6"],
    "docs": [
        "sphinx==4.5.0",
        "sphinxcontrib_trio==1.1.2",
        "sphinxcontrib-websupport",
        "myst-parser",
    ],
    "speed": [
        "orjson>=3.5.4",
        "aiodns>=1.1",
        "Brotlipy",
        "cchardet",
    ],
}

# Folders And Such Included
packages = [
    "discord",
    "discord.types",
    "discord.sinks",
    "discord.ui",
    "discord.webhook",
    "discord.commands",
    "discord.ext.commands",
    "discord.ext.tasks",
    "discord.ext.pages",
    "discord.ext.bridge",
]


setup(
    name="py-cord",
    author="Pycord Development",
    url="https://pycord.dev/github",
    project_urls={
        "Website": "https://pycord.dev",
        "Documentation": "https://docs.pycord.dev/en/master/",
        "Issue tracker": "https://github.com/Pycord-Development/pycord/issues",
    },
    version=version,
    packages=packages,
    license="MIT",
    description="A Python wrapper for the Discord API",
    long_description=readme,
    long_description_content_type="text/x-rst",
    include_package_data=True,
    install_requires=requirements,
    extras_require=extras_require,
    python_requires=">=3.8.0",
    classifiers=[
        "Development Status :: 4 - Beta",
        "License :: OSI Approved :: MIT License",
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: Internet",
        "Topic :: Software Development :: Libraries",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Utilities",
        "Typing :: Typed",
    ],
    test_suite="tests",  # Test Folder For Workflows
)
