# Smartphone Commander

A versatile command-line tool for managing Android devices via ADB (Android Debug Bridge) and extracting mobile network operator (MNO) data.

## Overview

This repository contains various tools designed to:

1. Control Android devices remotely via ADB commands
2. Extract and process mobile network operator (MNO) data
3. Analyze frequency spectrum allocation for mobile operators

## 📱 Android Device Management

The `smartphone-cli.py` script provides a simple command-line interface to manage Android devices:

### Features

- Toggle airplane mode on/off
- Reboot devices
- Support for multiple connected devices

### Usage

```bash
# Toggle airplane mode on/offss
python smartphone-cli.py -a [--id DEVICE_ID]

# Reboot a device
python smartphone-cli.py -r [--id DEVICE_ID]

# Display help
python smartphone-cli.py -h
```

If no device ID is specified, the tool will automatically use the first connected device.

## 📡 Mobile Network Operator (MNO) Data Tools

The `mno_extraction` directory contains tools for extracting and processing mobile network operator data:

### Features

- Extract MNO data from HTML sources
- Parse and structure operator information by country
- Extract spectrum band allocations from various sources
- Merge and enhance MNO data with spectrum information

### Tools

#### 1. Data Extraction

from: https://en.wikipedia.org/wiki/List_of_mobile_network_operators_in_Europe 

```bash
# Extract MNO data from HTML to JSON
cd mno_extraction
python extract_mno_data.py
```

#### 2. Spectrum Data Integration

from: https://lteitaly.it/spectrum.php 

```bash
# Merge spectrum data with MNO information
cd mno_extraction
python merge_mno_spectrum.py
```

#### 3. Data Enhancement

```bash
# Further enhance and organize the merged data
cd mno_extraction
python enhance_mno_spectrum.py
```

## Requirements

- Python 3.6+
- ADB (Android Debug Bridge) installed and in PATH
- Required Python packages:
  - BeautifulSoup4
  - argparse
  - subprocess

## Installation

1. Clone this repository:
```bash
git clone https://github.com/yourusername/smartphone-commander.git
cd smartphone-commander
```

2. Install required Python packages:
```bash
pip install -r requirements.txt
```

3. Ensure ADB is installed and accessible in your PATH.

## Data Format

### MNO Data Structure

The extracted MNO data includes:
- Country information
- Operator details
- MCC/MNC codes
- Network types and technologies

### Spectrum Data Structure

The spectrum data includes:
- Band information (GSM, UMTS, LTE, 5G NR)
- Bandwidth allocations
- Technology deployments
- Frequency ranges

## License

This project is open source and available under the MIT License.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
