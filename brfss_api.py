from flask import Flask, request, jsonify
import pandas as pd
import requests

app = Flask(__name__)
CDC_API_URL = "https://data.cdc.gov/resource/dttw-5yxu.json"

# --- Helper: Fetch and clean BRFSS data from CDC API ---
def fetch_cleaned_brfss(limit=1000):
    params = {"$limit": limit}
    response = requests.get(CDC_API_URL, params=params)

    if response.status_code != 200:
        raise Exception(f"CDC API error: {response.status_code}")

    brfss_df = pd.DataFrame(response.json())

    # Keep relevant columns
    keep_cols = [
        'year', 'locationabbr', 'locationdesc', 'class', 'topic', 'question',
        'response', 'break_out', 'break_out_category', 'sample_size',
        'data_value', 'confidence_limit_low', 'confidence_limit_high',
        'data_value_unit', 'data_value_type', 'geolocation'
    ]
    df = brfss_df[keep_cols].copy()

    # Rename for clarity
    df.rename(columns={
        'locationabbr': 'state_abbr',
        'locationdesc': 'state',
        'class': 'category',
        'break_out': 'demographic_group',
        'break_out_category': 'demographic_category',
        'data_value': 'value',
        'confidence_limit_low': 'ci_low',
        'confidence_limit_high': 'ci_high',
        'data_value_unit': 'unit',
        'data_value_type': 'value_type'
    }, inplace=True)

    # Convert to numeric
    for col in ['year', 'sample_size', 'value', 'ci_low', 'ci_high']:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    # Drop rows missing important info
    df.dropna(subset=['year', 'state', 'question', 'value'], inplace=True)

    # Normalize text fields
    text_cols = [
        'state_abbr', 'state', 'category', 'topic',
        'question', 'response', 'demographic_group', 'demographic_category'
    ]
    for col in text_cols:
        df[col] = df[col].str.strip().str.title()

    return df


# --- API Endpoint: /data ---
@app.route('/data', methods=['GET'])
def get_data():
    try:
        # Query parameters
        limit = request.args.get('limit', default=1000, type=int)
        year = request.args.get('year', type=int)
        topic = request.args.get('topic', type=str)

        # Fetch & clean
        df = fetch_cleaned_brfss(limit)

        # Apply filters if provided
        if year:
            df = df[df['year'] == year]
        if topic:
            df = df[df['topic'].str.contains(topic, case=False, na=False)]

        return df.to_json(orient='records')

    except Exception as e:
        return jsonify({'error': str(e)}), 500


# --- API Root ---
@app.route('/')
def home():
    return {
        "message": "Welcome to the BRFSS Health Data API",
        "usage": {
            "/data": {
                "description": "Get cleaned health data from the CDC BRFSS dataset",
                "parameters": {
                    "limit": "Number of records to fetch (default: 1000, no max)",
                    "year": "Filter by year (e.g. 2023)",
                    "topic": "Filter by topic keyword (e.g. Depression)"
                },
                "example": "/data?limit=5000&year=2023&topic=Smoking"
            }
        }
    }


# --- Run Server ---
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
