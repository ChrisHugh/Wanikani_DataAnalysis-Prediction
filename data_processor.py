import pandas as pd
import json
import os
import shutil
from datetime import datetime, timedelta

class WaniKaniDataProcessor:
    def __init__(self, cache_duration_hours=168):  # 1 week cache
        self.raw_data_dir = "data/raw"
        self.processed_data_dir = "data/processed"
        self.curated_data_dir = "data/curated"
        self.archive_dir = "data/archive"
        self.cache_duration = timedelta(hours=cache_duration_hours)
        
        # Create directories if they don't exist
        os.makedirs(self.curated_data_dir, exist_ok=True)
        os.makedirs(self.archive_dir, exist_ok=True)

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
        
        # Extract timestamp from filename (format: curated_XXXX_YYYYMMDD_HHMMSS)
        filename = os.path.basename(filepath)
        timestamp_str = filename.split('_')[-2] + '_' + filename.split('_')[-1].split('.')[0]
        file_time = datetime.strptime(timestamp_str, "%Y%m%d_%H%M%S")
        
        # Check if file is older than cache duration
        return datetime.now() - file_time < self.cache_duration

    def _archive_old_files(self, prefix):
        """Archive files older than cache duration for a given prefix"""
        current_time = datetime.now()
        
        # Get all files with the given prefix
        files = [f for f in os.listdir(self.curated_data_dir) if f.startswith(prefix)]
        for file in files:
            filepath = os.path.join(self.curated_data_dir, file)
            # Extract timestamp (format: curated_XXXX_YYYYMMDD_HHMMSS)
            timestamp_str = file.split('_')[-2] + '_' + file.split('_')[-1].split('.')[0]
            file_time = datetime.strptime(timestamp_str, "%Y%m%d_%H%M%S")
            
            if current_time - file_time >= self.cache_duration:
                # Create archive subdirectory if it doesn't exist
                archive_subdir = os.path.join(self.archive_dir, prefix)
                os.makedirs(archive_subdir, exist_ok=True)
                
                # Move file to archive
                shutil.move(filepath, os.path.join(archive_subdir, file))
                print(f"Archived {file} to {archive_subdir}")

    def load_json_file(self, filepath):
        """Load JSON file and return as list of dictionaries"""
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)

    def expand_data_column(self, data_list):
        """Expand the nested 'data' column into separate columns"""
        # Convert to DataFrame
        df = pd.DataFrame(data_list)
        
        # Extract the 'data' column
        data_df = pd.json_normalize(df['data'])
        
        # Drop the original 'data' column
        df = df.drop('data', axis=1)
        
        # Combine the original columns with the expanded data columns
        result_df = pd.concat([df, data_df], axis=1)
        
        return result_df

    def process_file(self, filename):
        """Process a single JSON file and save both raw and processed versions"""
        # Check for cached curated file
        prefix = f"curated_{filename.replace('.json', '')}"
        latest_curated = self._get_latest_file(self.curated_data_dir, prefix)
        
        if self._is_cache_valid(latest_curated):
            print(f"Using cached curated data for {filename}")
            return pd.read_csv(latest_curated)
        
        # Load the JSON file
        filepath = os.path.join(self.raw_data_dir, filename)
        data = self.load_json_file(filepath)
        
        # Expand the data
        expanded_df = self.expand_data_column(data)
        
        # Archive old files before saving new ones
        self._archive_old_files(prefix)
        
        # Save processed data
        output_filename = f"{prefix}.csv"
        output_path = os.path.join(self.curated_data_dir, output_filename)
        
        expanded_df.to_csv(output_path, index=False)
        print(f"Processed data saved to: {output_path}")
        
        return expanded_df

    def process_all_files(self):
        """Process all JSON files in the raw data directory"""
        for filename in os.listdir(self.raw_data_dir):
            if filename.endswith('.json'):
                print(f"Processing {filename}...")
                self.process_file(filename)

if __name__ == "__main__":
    processor = WaniKaniDataProcessor(cache_duration_hours=168)  # 1 week cache
    processor.process_all_files() 