# BBVA Plugin for [ofxstatement](https://github.com/kedder/ofxstatement/)

Parses BBVA xslx statement files to be used with GNU Cash or HomeBank.

## Installation

You can install the plugin as usual from pip or directly from the downloaded git

### `pip`

    pip3 install --user ofxstatement-bbva

### `setup.py`

    python3 setup.py install --user

## Usage
Download your transactions file from the official bank's site and then run

    ofxstatement convert -t bbva BBVA.xlsx BBVA.ofx


### Loading Historical data

BBVA website only allows to download the `xlsx` statements in for the last year,
however it's also possible to get the old statement files in PDF format and convert
these old per-quarter statements that are available from the archive.

A plugin is provided that uses `poppler-util`'s `pdftotext` to easily generate
machine parse-able data.

This is an experimental plugin, that may not always work but it can be used via:

    ofxstatement -d convert -t bbva-pdf ./dir-containing-all-pdfs BBVA-pdf.ofx
    ofxstatement -d convert -t bbva-pdf BBVA-20-Q2.pdf BBVA-pdf.ofx
