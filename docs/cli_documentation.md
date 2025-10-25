# CLI Documentation

## Overview

The PDF Price Search CLI provides a command-line interface for searching shipping prices and managing PDF data.

## Installation

```bash
pip install -e .
```

## Usage

### Basic Search

```bash
python -m src.presentation.cli search "2lb to zone 5"
```

### Interactive Mode

```bash
python -m src.presentation.cli
```

## Commands

### search

Search for shipping prices.

**Syntax**:
```bash
python -m src.presentation.cli search "<query>"
```

**Examples**:
```bash
# Basic search
python -m src.presentation.cli search "2lb to zone 5"

# With service name
python -m src.presentation.cli search "FedEx 2Day, 5lb, zone 8"

# Different query formats
python -m src.presentation.cli search "zone 3, 10 pounds"
python -m src.presentation.cli search "5 lbs zone 7"
```

### list

List all available shipping services.

**Syntax**:
```bash
python -m src.presentation.cli list
```

### load

Load PDF files from a directory.

**Syntax**:
```bash
python -m src.presentation.cli load <directory>
```

**Example**:
```bash
python -m src.presentation.cli load ./source
```

### help

Show help information.

**Syntax**:
```bash
python -m src.presentation.cli help
```

## Query Format

The CLI accepts natural language queries with the following components:

- **Weight**: `2lb`, `2 pounds`, `2lbs`, `2 lb`
- **Zone**: `zone 5`, `zone5`, `to zone 5`
- **Service** (optional): `FedEx 2Day`, `FedEx Ground`

**Valid Examples**:
- `"2lb to zone 5"`
- `"FedEx 2Day, 5 pounds, zone 8"`
- `"zone 3, 10 lbs"`
- `"5 lbs zone 7 FedEx Ground"`

## Output Format

### Search Results

```
Found price: $25.50 USD
Service: FedEx 2Day
Zone: 5
Weight: 3.0 lb
Source: fedex_rates.pdf
Search time: 15.2 ms
```

### List Results

```
Available Shipping Services:
1. FedEx 2Day
   Zones: 1-8
   Weight: 1.0-70.0 lb
   Source: fedex_rates.pdf

2. FedEx Standard Overnight
   Zones: 1-8
   Weight: 1.0-150.0 lb
   Source: fedex_rates.pdf

Total: 2 services
```

## Exit Codes

- `0`: Success
- `1`: General error
- `2`: Invalid query
- `3`: No results found
- `4`: File not found

## Environment Variables

- `PDF_SEARCH_DIR`: Default directory for PDF files
- `PDF_SEARCH_CACHE`: Enable/disable caching (true/false)

## Tips

1. **Use quotes** for queries with spaces
2. **Check available services** with `list` before searching
3. **Load PDFs first** if no results found
4. **Use tab completion** (if supported by your shell)
