# JSHarvester

A tool for collecting and downloading JavaScript files to support Javascript recon during bug hunting/pentesting.

## Overview

JSHarvester is designed for bug hunters, and pentesters who need to:
- Identify and collect all JavaScript files from target domains
- Filter out common libraries to focus on custom code
- Gather resources for detecting sensitive information like endpoints, API keys, and credentials

## Dependencies
- urx
- urlfinder
- waymore
- uro
- httpx

## Basic Usage
```bash
chmod +x JSHarvester.sh
./JSHarvester.sh example.com
```

## Bug Hunting and Penetration Testing Applications

JavaScript files collected with JSHarvester can be used with the following tools to discover security vulnerabilities:

- **jsleak** https://github.com/byt3hx/jsleak
- **nuclei** https://github.com/projectdiscovery/nuclei
