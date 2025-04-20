# BRFSS Health Data API

This Flask API serves cleaned data from the CDC's Behavioral Risk Factor Surveillance System (BRFSS).

## Base URL

http://192.3.36.156:5000

## Endpoint

### `/data`

Returns JSON data.

**Optional query parameters:**

- `limit` (int): number of records to fetch (default: 1000)
- `year` (int): filter by year
- `topic` (string): filter by topic keyword

**Example:**

```
/data?limit=5000&year=2023&topic=Depression
```

## Usage in Python

```python
import pandas as pd
df = pd.read_json("http://192.3.36.156:5000/data?year=2023&topic=Obesity")
df.to_csv("brfss.csv", index=False)
```

## Source

Data from CDC BRFSS: https://www.cdc.gov/brfss/
