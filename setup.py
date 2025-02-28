from setuptools import setup, find_packages

__version__ = "0.1.0"

setup(
    name="opentips",
    version=__version__,
    author="sargeairraid@gmail.com",
    description="Automated assistant that provides coding tips as you work",
    packages=find_packages(),
    install_requires=[
        "aider-chat~=0.75.1",
        "aiohttp~=3.11.11",
        "jsonrpcserver~=5.0.9",
        "litellm~=1.61.9",
        "colorama~=0.4.6",
        "charset-normalizer~=3.4.1",
        "unidiff~=0.7.5",
    ],
    entry_points={
        "console_scripts": [
            "opentips=opentips.cli.main:main",
            "opentips-client=opentips.cli.client:main",
        ],
    },
    extras_require={
        "dev": [
            "flake8~=7.1.1",
            "pytest~=8.3.4",
            "pytest-asyncio~=0.25.3",
            "python-semantic-release~=9.21.0",
            "pytest-cov~=4.1.0",
            "build~=1.2.2",
            "twine~=6.1.0",
        ],
    },
    python_requires=">=3.11",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Programming Language :: Python :: 3.11",
    ],
)
