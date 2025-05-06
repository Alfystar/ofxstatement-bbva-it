#!/usr/bin/python3
"""Setup
"""
from distutils.core import setup
from setuptools import find_packages

VERSION = "0.4"

with open("README.md", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="ofxstatement-bbva",
    version=VERSION,
    author="Marco Trevisan",
    author_email="mail@3v1n0.net",
    url="https://github.com/3v1n0/ofxstatement-bbva",
    description=("BBVA plugin for ofxstatement"),
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="GPLv3",
    keywords=[
        "ofx",
        "banking",
        "statement",
        "bbva",
        "banco",
        "Banco" "Bilbao" "Vizcaya" "Argentaria",
    ],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Programming Language :: Python :: 3",
        "Natural Language :: English",
        "Topic :: Office/Business :: Financial :: Accounting",
        "Topic :: Utilities",
        "Environment :: Console",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
    ],
    packages=find_packages("src"),
    package_dir={"": "src"},
    namespace_packages=["ofxstatement", "ofxstatement.plugins"],
    entry_points={
        "ofxstatement": [
            "bbva = ofxstatement.plugins.bbva:BBVAPlugin",
            "bbva-pdf = ofxstatement.plugins.bbva_pdf:BBVAPdfPlugin",
        ],
    },
    install_requires=["ofxstatement", "openpyxl"],
    include_package_data=True,
    zip_safe=True,
)
