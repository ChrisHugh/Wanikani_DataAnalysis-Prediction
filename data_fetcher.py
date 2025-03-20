import os
import json
import pandas as pd
from datetime import datetime, timedelta
import requests
from config import WANIKANI_API_KEY

class WaniKaniDataFetcher:
    def __init__(self, cache_duration_hours=24):
        self.base_url = "https://api.wanikani.com/v2"
        self.headers = {
            "Authorization": f"Bearer {WANIKANI_API_KEY}",
            "Wanikani-Revision": "20170710"
        }
        self.raw_data_dir = "data/raw"
        self.processed_data_dir = "data/processed"
        self.cache_duration = timedelta(hours=cache_duration_hours)
        
        # Create directories if they don't exist
        os.makedirs(self.raw_data_dir, exist_ok=True)
        os.makedirs(self.processed_data_dir, exist_ok=True)

    def _get_latest_file(self, directory, prefix):
        """Get the most recent file for a given endpoint"""
        files = [f for f in os.listdir(directory) if f.startswith(prefix)]
        if not files:
            return None
        
        # Sort by timestamp in filename (newest first)
        latest_file = sorted(files, reverse=True)[0]
        return os.path.join(directory, latest_file)

    def _is_cache_valid(self, filepath):
        """Check if the cached file is still valid"""
        if not filepath or not os.path.exists(filepath):
            return False
        
        # Extract timestamp from filename
        filename = os.path.basename(filepath)
        timestamp_str = filename.split('_')[-1].split('.')[0]
        file_time = datetime.strptime(timestamp_str, "%Y%m%d_%H%M%S")
        
        # Check if file is older than cache duration
        return datetime.now() - file_time < self.cache_duration

    def fetch_endpoint(self, endpoint, params=None, force_refresh=False):
        """Fetch data from a WaniKani endpoint with pagination handling"""
        url = f"{self.base_url}/{endpoint}"
        all_data = []
        
        while url:
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            data = response.json()
            
            all_data.extend(data['data'])
            url = data.get('pages', {}).get('next_url')
            
        return all_data

    def save_raw_data(self, data, endpoint):
        """Save raw JSON data with timestamp"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{endpoint}_{timestamp}.json"
        filepath = os.path.join(self.raw_data_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return filepath

    def fetch_and_save(self, endpoint, params=None, force_refresh=False):
        """Fetch data and save it both as raw JSON and processed CSV"""
        # Check for cached data
        latest_raw = self._get_latest_file(self.raw_data_dir, f"{endpoint}_")
        latest_csv = self._get_latest_file(self.processed_data_dir, f"{endpoint}_")
        
        if not force_refresh and self._is_cache_valid(latest_raw):
            print(f"Using cached data for {endpoint}")
            with open(latest_raw, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return data
        
        print(f"Fetching {endpoint}...")
        data = self.fetch_endpoint(endpoint, params)
        
        # Save raw data
        raw_filepath = self.save_raw_data(data, endpoint)
        print(f"Saved raw data to {raw_filepath}")
        
        # Convert to DataFrame and save as CSV
        df = pd.DataFrame(data)
        if not df.empty:
            csv_filename = f"{endpoint}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            csv_filepath = os.path.join(self.processed_data_dir, csv_filename)
            df.to_csv(csv_filepath, index=False)
            print(f"Saved processed data to {csv_filepath}")
        
        return data

    def fetch_all_data(self, force_refresh=False):
        """Fetch all relevant WaniKani data"""
        endpoints = [
            'user',
            'subjects',
            'assignments',
            'reviews',
            'level_progressions',
            'review_statistics',
            'spaced_repetition_systems'
        ]
        
        for endpoint in endpoints:
            try:
                self.fetch_and_save(endpoint, force_refresh=force_refresh)
            except Exception as e:
                print(f"Error fetching {endpoint}: {str(e)}")

if __name__ == "__main__":
    fetcher = WaniKaniDataFetcher(cache_duration_hours=24)  # Cache for 24 hours
    fetcher.fetch_all_data() 