from flask import Flask, render_template, request, jsonify, session, Response
import os
from data_fetcher import WaniKaniDataFetcher
from data_processor import WaniKaniDataProcessor
from Level_Progression_Analysis import generate_level_progression_html
import pandas as pd
from datetime import datetime
import json
import requests

app = Flask(__name__)
app.secret_key = os.urandom(24)  # For session management

def validate_api_key(api_key):
    """Validate the WaniKani API key by making a test request"""
    try:
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Wanikani-Revision': '20170710'
        }
        print(f"\nTesting API key validation...")
        response = requests.get('https://api.wanikani.com/v2/user', headers=headers)
        print(f"API validation response status: {response.status_code}")
        
        if response.status_code != 200:
            print(f"API validation failed. Response: {response.text}")
            return False
            
        print("API key validation successful")
        return True
        
    except Exception as e:
        print(f"Error during API key validation: {str(e)}")
        return False

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    api_key = request.form.get('api_key')
    if not api_key:
        print("No API key provided")
        return jsonify({'error': 'API key is required'}), 400
    
    print(f"\nReceived analyze request with API key: {api_key[:5]}...")
    
    try:
        # Validate the API key first
        if not validate_api_key(api_key):
            return jsonify({'error': 'Invalid API key or unable to connect to WaniKani. Please check your API key and try again.'}), 401

        # Set the API key in environment
        os.environ['WANIKANI_API_KEY'] = api_key
        
        # Fetch and process data
        try:
            fetcher = WaniKaniDataFetcher()
            fetcher.fetch_all_data()
        except Exception as e:
            print(f"Error in data fetching: {str(e)}")
            return jsonify({'error': f'Error fetching data: {str(e)}'}), 500

        try:
            processor = WaniKaniDataProcessor()
            processor.process_all_files()
        except Exception as e:
            print(f"Error in data processing: {str(e)}")
            return jsonify({'error': f'Error processing data: {str(e)}'}), 500

        # Generate the level progression visualization
        try:
            visualization_data = generate_level_progression_html()
            print("\nVisualization data from generate_level_progression_html:")
            print(json.dumps(visualization_data, indent=2))
            
            if isinstance(visualization_data, dict) and 'error' in visualization_data:
                return jsonify({'error': f'Error generating visualization: {visualization_data["error"]}'}), 500
                
            # Verify the data structure
            if not isinstance(visualization_data, dict) or 'data' not in visualization_data or 'layout' not in visualization_data:
                print("Invalid visualization data structure")
                print(f"Type: {type(visualization_data)}")
                print(f"Keys: {visualization_data.keys() if isinstance(visualization_data, dict) else 'not a dict'}")
                return jsonify({'error': 'Invalid visualization data structure'}), 500
                
            response_data = {
                'visualization': visualization_data,
                'message': 'Analysis complete!'
            }
            
            print("\nFinal response data:")
            print(json.dumps(response_data, indent=2))
            
            return jsonify(response_data)
            
        except Exception as e:
            print(f"Error in visualization generation: {str(e)}")
            import traceback
            print(traceback.format_exc())
            return jsonify({'error': f'Error generating visualization: {str(e)}'}), 500
        
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        import traceback
        print(traceback.format_exc())
        return jsonify({'error': f'An unexpected error occurred: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True) 