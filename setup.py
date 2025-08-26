"""Project setup and configuration."""
from setuptools import setup, find_packages

setup(
    name="second-brain",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "requests>=2.31.0",
        "pandas>=2.0.0",
        "openpyxl>=3.1.2",
    ],
    python_requires=">=3.11",
    author="Marcelo Wizenberg",
    description="A personal knowledge management system",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/celowiz/second-brain",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.11",
    ],
)
