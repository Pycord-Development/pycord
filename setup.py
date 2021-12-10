import re
from setuptools import setup

requirements = []
with open("requirements.txt") as f:
    requirements = f.read().splitlines()

version = ""
with open("discord/__init__.py") as f:

    search = re.search(r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]', f.read(), re.MULTILINE)

    if search is not None:
        version = search.group(1)

    else:
        raise RuntimeError("Could not grab version string")

if not version:
    raise RuntimeError('version is not set')

if version.endswith(('a', 'b', 'rc')):
    # append version identifier based on commit count
    try:
        import subprocess

        p = subprocess.Popen(["git", "rev-list", "--count", "HEAD"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = p.communicate()
        if out:
            version += out.decode("utf-8").strip()
        p = subprocess.Popen(["git", "rev-parse", "--short", "HEAD"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = p.communicate()
        if out:
            version += "+g" + out.decode("utf-8").strip()
    except Exception:
        pass

readme = ""
with open("README.rst") as f:
    readme = f.read()

extras_require = {
    "voice": ["PyNaCl>=1.3.0,<1.5"],
    "docs": [
        "sphinx==4.3.1",
        "sphinxcontrib_trio==1.1.2",
        "sphinxcontrib-websupport",
    ],
    "speed": [
        "orjson>=3.5.4",
        "aiodns>=1.1",
        "Brotlipy",
        "cchardet",
    ],
}

packages = [
    "discord",
    "discord.types",
    "discord.ui",
    "discord.webhook",
    "discord.commands",
    "discord.ext.commands",
    "discord.ext.tasks",
]


setup(
    name="py-cord",
    author="Pycord Development",
    url="https://github.com/Pycord-Development/pycord",
    project_urls={
        "Documentation": "https://pycord.readthedocs.io/en/latest/",
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
        "Development Status :: 3 - Alpha",
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
    test_suite="tests",
)
