#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

setup(
    name='ofxstatement-bbva',
    version='0.5.0',
    author='Marco Trevisan, ea_enel',
    author_email='mail@3v1n0.net',
    url='https://github.com/3v1n0/ofxstatement-bbva.git',
    description='BBVA plugin for ofxstatement with multi-language support (Italian/Spanish)',
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type='text/markdown',
    license='GPLv3',
    keywords=[
        'ofx',
        'ofxstatement',
        'bbva',
        'banco',
        'banking',
        'statement',
        'multi-language',
        'Banco', 'Bilbao', 'Vizcaya', 'Argentaria'
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Programming Language :: Python :: 3',
        'Natural Language :: English',
        'Natural Language :: Italian',
        'Natural Language :: Spanish',
        'Topic :: Office/Business :: Financial :: Accounting',
        'Topic :: Utilities',
        'Environment :: Console',
        'Operating System :: OS Independent',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
    ],
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    entry_points={
        'ofxstatement': [
            'bbva = ofxstatement_bbva:BBVAPlugin',
            'bbva-pdf = ofxstatement_bbva:BBVAPdfPlugin',
        ]
    },
    install_requires=['ofxstatement', 'openpyxl'],
    include_package_data=True,
    zip_safe=True
)
