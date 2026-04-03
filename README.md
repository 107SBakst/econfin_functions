# econfin_functions

A Python package for economic and financial data functions, providing easy access to various economic data sources.

## Installation

```bash
pip install econfin_functions
```

Or install directly from GitHub:

```bash
pip install git+https://github.com/107SBakst/econfin_functions.git
```

## Features

### Israel Central Bureau of Statistics (CBS) API

Access time series data from Israel's Central Bureau of Statistics through their official API.

## Quick Start

```python
from econfin_functions import il_cbs_api

# Fetch Israeli population data (series 3763) for recent years
data_df, meta_df = il_cbs_api(
    series_id=3763,
    startPeriod='2020-01',
    endPeriod='2024-12',
    format_type='json'
)

print("Data:")
print(data_df.head())
print("\nMetadata:")
print(meta_df.head())
```

## API Reference

### `il_cbs_api()`

Fetch time series data and metadata from Israel's Central Bureau of Statistics API.

#### Parameters

- **series_id** (str or int): The CBS series ID (e.g., '3763' for population data)
- **startPeriod** (str, optional): Start period in YYYY-MM format (e.g., '2020-01')
- **endPeriod** (str, optional): End period in YYYY-MM format (e.g., '2024-12')  
- **format_type** (str, default 'json'): Response format - 'json' or 'xml'
- **download** (bool, default False): Whether to download data (True) or just fetch (False)
- **lang** (str, default 'en'): Language - 'en' for English, 'he' for Hebrew

#### Returns

A tuple of two pandas DataFrames:
1. **Data DataFrame**: Time series data with columns:
   - `TimePeriod`: Time period (converted to datetime when possible)
   - `Value`: Data values
   - `series_id`: Reference to the series ID

2. **Metadata DataFrame**: Series metadata with columns:
   - `id`: Series ID
   - `time_unit`: Time unit (e.g., "Month")
   - `data_type`: Data type (e.g., "Original Data")
   - `unit`: Measurement unit (e.g., "Thousands")
   - `precision`: Data precision
   - `last_update`: Last update date
   - `level1-4`: Hierarchical categorization
   - `series_name`: Series name
   - `series_id`: Reference to the series ID

## Examples

### Basic Usage

```python
from econfin_functions import il_cbs_api

# Get population data with default settings
data, metadata = il_cbs_api(3763)
```

### Specify Time Range

```python
# Get data for specific time period
data, metadata = il_cbs_api(
    series_id=3763,
    startPeriod='2023-01',
    endPeriod='2024-12'
)
```

### XML Format

```python
# Use XML format instead of JSON
data, metadata = il_cbs_api(
    series_id=3763,
    format_type='xml',
    startPeriod='2024-01'
)
```

### Hebrew Language

```python
# Get data in Hebrew
data, metadata = il_cbs_api(
    series_id=3763,
    lang='he'
)
```

### Working with the Data

```python
import matplotlib.pyplot as plt

# Fetch and plot population data
data, meta = il_cbs_api(3763, startPeriod='2020-01')

# Basic info
print(f"Series: {meta['series_name'].iloc[0]}")
print(f"Unit: {meta['unit'].iloc[0]}")
print(f"Data points: {len(data)}")

# Plot the data
plt.figure(figsize=(12, 6))
plt.plot(data['TimePeriod'], data['Value'])
plt.title(f"{meta['series_name'].iloc[0]} - {meta['unit'].iloc[0]}")
plt.xlabel('Time Period')
plt.ylabel(f"Value ({meta['unit'].iloc[0]})")
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()

# Summary statistics
print(f"Latest value: {data['Value'].iloc[0]:,.1f}")
print(f"Average: {data['Value'].mean():,.1f}")
print(f"Min: {data['Value'].min():,.1f}")
print(f"Max: {data['Value'].max():,.1f}")
```

## Finding Series IDs

To find CBS series IDs, visit the [Israel CBS website](https://www.cbs.gov.il/en) and navigate to their data tables. The series ID is typically shown in the URL or table metadata.

Some common series IDs:
- `3763`: Total population  
- `3764`: Jewish population
- `3765`: Arab population

## Requirements

- Python 3.8+
- pandas >= 1.5.0
- requests >= 2.28.0
- lxml >= 4.9.0 (for XML processing)

## Error Handling

The function includes comprehensive error handling:

```python
try:
    data, metadata = il_cbs_api('invalid_series')
except RuntimeError as e:
    print(f"API Error: {e}")
except ValueError as e:
    print(f"Parameter Error: {e}")
```

## Contributing

This package is designed to be extensible. Future additions may include:
- Additional Israeli data sources
- International economic data APIs  
- R function equivalents
- Advanced data processing utilities

## License

MIT License - see LICENSE file for details.

## Author

Samuel Bakst - [107sbakst@gmail.com](mailto:107sbakst@gmail.com)

## Links

- [GitHub Repository](https://github.com/107SBakst/econfin_functions)
- [Israel CBS API Documentation](https://www.cbs.gov.il/)
- [Report Issues](https://github.com/107SBakst/econfin_functions/issues)

---

*Note: This package is not officially affiliated with Israel's Central Bureau of Statistics. Please respect their API usage guidelines and terms of service.*