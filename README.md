# Airplane Mode

Enable/disable wifi, bluetooth, and background applications.

**NOTE:**

- only supports macOS
- requires Python 3.10 (type annotations, configparser extensions)

# Installation and Usage

## Installation

This requires the `blueutil` program to manage the system's bluetooth.

```bash
brew install blueutil
pip install .
```

## Usage

```sh
$ airplanemode --help
usage: airplanemode [-h] [--version] {status} ...

positional arguments:
  {status}

options:
  -h, --help  show this help message and exit
  --version   show program's version number and exit
```

# Contributing

```sh
# Create Python virtual environment
python -m venv .venv
# Activate Python virtual environment
. .venv/bin/activate
# Install package for local development
python script/setup.py
# Build the package for distribution
python script/build.py
# Format all files
python script/fmt.py
# Run tests (including formatters and linters)
python script/test.py
```
