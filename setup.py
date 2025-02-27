from setuptools import setup, find_packages

__version__ = "1.0.0"

# Base configuration that doesn't require cx_Freeze
kwargs = {
    "name": "opentips",
    "version": __version__,
    "author": "sgtairraid@gmail.com",
    "description": "Automated assistant that provides coding tips as you work",
    "packages": find_packages(),
    "install_requires": [
        "aider-chat~=0.74.1",
        "aiohttp~=3.11.11",
        "jsonrpcserver~=5.0.9",
        "litellm~=1.59.8",
        "colorama~=0.4.6",
        "charset-normalizer~=3.4.1",
        "unidiff~=0.7.5",
    ],
    "entry_points": {
        "console_scripts": [
            "opentips=opentips.cli.main:main",
            "opentips-client=opentips.cli.client:main",
        ],
    },
    "extras_require": {
        "dev": [
            "flake8~=7.1.1",
            "pytest~=8.3.4",
            "pytest-asyncio~=0.25.3",
            "python-semantic-release~=9.21.0",
            "pytest-cov~=4.1.0",
            "build~=1.2.2",
            "twine~=6.1.0",
        ],
        "exe": [
            "cx_Freeze~=7.2.9",
        ],
    },
    "python_requires": ">=3.11",
    "classifiers": [
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Programming Language :: Python :: 3.11",
    ],
}

# Add cx_Freeze-specific configuration if available
try:
    from cx_Freeze import setup, Executable
except ImportError:
    import sys

    if "build" in sys.argv:
        sys.exit(
            "Error: cx_Freeze is required for building executables.\n"
            "Please install it with: pip install '.[exe]'"
        )

build_options = {
    "packages": find_packages(),
    "excludes": [
        "pytest",
        "flake8",
        "twine",
        "build",
        "semantic_release",
    ],
    "includes": [pkg.split("~=")[0].strip() for pkg in kwargs["install_requires"]]
}

kwargs.update(
    {
        "options": {"build_exe": build_options},
        "executables": [
            Executable("opentips/cli/main.py", base="console", target_name="opentips")
        ],
    }
)

setup(**kwargs)
