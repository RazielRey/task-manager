"""
Setup configuration for Task CLI
Used to package and install the CLI tool
"""

from setuptools import setup, find_packages
from task_cli.version import __version__

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="task-cli",
    version=__version__,
    author="Your Name",
    author_email="your.email@example.com",
    description="Command-line interface for Task Management API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/task-manager-devops",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=[
        "click>=8.1.7",
        "requests>=2.31.0",
        "tabulate>=0.9.0",
        "colorama>=0.4.6",
    ],
    entry_points={
        "console_scripts": [
            "task=task_cli.cli:cli",
        ],
    },
)