# JSHarvester

A tool for collecting and downloading JavaScript files to support Javascript recon during bug hunting/pentesting.

## Overview

JSHarvester is designed for bug hunters, and pentesters who need to:
- Identify and collect all JavaScript files from target domains
- Filter out common libraries to focus on custom code
- Gather resources for detecting sensitive information like endpoints, API keys, and credentials

## Installation

### Prerequisites


```bash
# Go tools
go install github.com/projectdiscovery/urlfinder/cmd/urlfinder@latest
go install github.com/projectdiscovery/httpx/cmd/httpx@latest
go install github.com/projectdiscovery/katana/cmd/katana@latest
go install github.com/tomnomnom/anew@latest
go install github.com/s0md3v/uro@latest

# Python requirements
pip install requests
```


### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yee-yore/jsharvester.git
   ```

2. Navigate to the directory:
   ```bash
   cd jsharvester
   ```

3. Make the script executable (Unix-based systems):
   ```bash
   chmod +x jsharvester.py
   ```

## Usage

### Basic Usage

Collect JavaScript URLs from a domain:

```bash
python jsharvester.py -d example.com
```

This will save all discovered JavaScript URLs to `example.com_js.txt`.

### Download JavaScript Files

Collect and download JavaScript files:

```bash
python jsharvester.py -d example.com -jd
```

This will:
1. Save JavaScript URLs to `example.com_js.txt`
2. Download all JavaScript files to a directory named `example.com`



### Command-line Options

```
-d, --domain DOMAIN       Target domain (required)
-o, --output PATH         Output file path (default: {domain}_js.txt)
-jd, --download           Download JavaScript files to {domain} directory
```

## How It Works

JSHarvester performs the following steps:

1. **URL Collection**:
   - `urlfinder`: crawls javascript urls passively
   - `katana`: crawls javascript urls actively
   - `anew`: merges results and removes duplicates 

2. **Filtering**:
   - `httpx`: verifies live URLs 
   - Filters for files with `.js` extension
   - `uro`: optimizes URLs 
   - Excludes common JavaScript libraries like jQuery

3. **Download** (optional):
   - Downloads each JavaScript file
   - Preserves original filenames

## Bug Hunting and Penetration Testing Applications

JavaScript files collected with JSHarvester can be used with the following tools to discover security vulnerabilities:

- **jsleak** https://github.com/byt3hx/jsleak
- **nuclei** https://github.com/projectdiscovery/nuclei