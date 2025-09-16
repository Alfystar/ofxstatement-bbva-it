# BBVA Plugin for [ofxstatement](https://github.com/kedder/ofxstatement/)

This plugin parses BBVA Excel statement files with multi-language support (Italian and Spanish) to be used with GNU Cash, HomeBank, or other financial software.

## Installation

You can install the plugin as usual from pip or directly from the downloaded source

### pip
```bash
pip3 install --user ofxstatement-bbva
```

### From source
```bash
git clone https://github.com/3v1n0/ofxstatement-bbva.git
cd ofxstatement-bbva
python3 -m venv .venv
source .venv/bin/activate  # Activates virtual environment
pip install -r requirements.txt
pip install build
python3 -m build --sdist --wheel
pip install dist/ofxstatement_bbva-<version>.tar.gz # replace <version> with the version number inside setup.py
```

> **Note**: The above commands install the package in a virtual environment (`.venv`). To install system-wide instead, skip the venv creation and activation steps, and optionally add `--user` flag to install for the current user only.

## Configuration

You have to configure some parameters in your local environment to allow the conversion.

To edit the config file, run this command:

```bash
$ ofxstatement edit-config
```

It opens a text editor with the current configuration.

Now add the plugin configuration. Here are examples for different languages:

### Spanish Configuration (Default)
```ini
[bbva-spain]
plugin = bbva
language = es
default_account = bbva-user1
```

### Italian Configuration
```ini
[bbva-italy]
plugin = bbva
language = it
default_account = bbva-user2
```

### Configuration Parameters

- `plugin`: Must be set to `bbva`
- `language`: Supported languages are `it` (Italian) and `es` (Spanish). If not specified or an unsupported language is used, defaults to Spanish (`es`)
- `default_account`: Code insert inside the `.ofx` file at the tag `ACCTID`. Used inside the financial software to auto detect which Accaunt nead to be update. Es: in Home bank is the `Account number` in the `Account Manager` window. 

> **Note**: You can have multiple configurations with different names, just add new sections (`[bbva-ConfName]`)with the same structure and change the section name.

## Usage

Download your transactions file from the official BBVA website and then run:

```bash
$ ofxstatement convert -t <bbva-conf> BBVA.xlsx BBVA.ofx
```

Replace `bbva-conf` with the configuration name you chose in your config file.

> **Note**: The Excel file of the transactions is downloaded from the BBVA website using a Browser (for now is not possible from APP).
> You can find the download button from `Home`⇥`Bank account`⇥`Transaction zone`.
> Select the date range and download the file in Excel format (.xlsx).

### Supported File Formats

The plugin currently supports Excel files (.xlsx) in this language:
- Spanish
- Italian

### Loading Historical Data

BBVA website only allows downloading Excel statements for the last year. However, it's also possible to get old statement files in PDF format and convert these using the experimental PDF plugin:

```bash
$ ofxstatement -d convert -t bbva-pdf ./dir-containing-all-pdfs BBVA-pdf.ofx
$ ofxstatement -d convert -t bbva-pdf BBVA-20-Q2.pdf BBVA-pdf.ofx
```

**Note**: The PDF plugin is experimental and uses `poppler-util`'s `pdftotext` to generate machine-parseable data.

### Add Alias

To simplify the use of the plugin, we strongly recommend adding an alias to your system (if in a Linux/macOS environment) by adding this alias to your `~/.bash_aliases`:

> **Note**: This alias uses configuration name `bbva-conf`. If you use another name, change it in the alias.

```bash
$ printf '\n# BBVA Excel convert to OFX format\nalias ofxBBVA="ofxstatement convert -t bbva-conf"\n' >> ~/.bash_aliases
```

After that, reload your terminal (close and reopen) and the usage becomes:

```bash
$ ofxBBVA BBVA.xlsx BBVA.ofx
```

**Note**: If after reload the alias is not loading, go to your `~/.bashrc` and check if the following lines are present. If not, add them at the end:

```bash
# Alias definitions.
# You may want to put all your additions into a separate file like
# ~/.bash_aliases, instead of adding them here directly.
# See /usr/share/doc/bash-doc/examples in the bash-doc package.

if [ -f ~/.bash_aliases ]; then
    . ~/.bash_aliases
fi
```

## How to use OFX file after conversion

The `ofx` format stands for '*Open Financial Exchange*'. It can be used to transfer your accounting records from one database to another.
This repository allows you to convert the records that **BBVA** shares via Excel into this *open source* format.
Once you have the `ofx` file, you can use any program to manage your finances.
Among the many available, a non-exhaustive list of open source products is:

- [HomeBank](http://homebank.free.fr/en/index.php), continuously updated program, available on desktop platforms, with many useful features and active community support. **100% compatibility**
  
  To use automatic account mapping, open the `*.ofx` file and search for `<BANKID>` or `<ACCTID>`, then use one of these populated values during import.

- [GnuCash](https://www.gnucash.org/), professional accounting software with double-entry bookkeeping
- [KMyMoney](https://kmymoney.org/), personal finance manager for KDE

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. When contributing:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the GNU General Public License v3 (GPLv3) - see the LICENSE file for details.
