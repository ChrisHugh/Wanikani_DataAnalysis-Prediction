import pandas as pd
import json
import os
from datetime import datetime

class WaniKaniDataProcessor:
    def __init__(self):
        self.raw_data_dir = "data/raw"
        self.processed_data_dir = "data/processed"
        self.curated_data_dir = "data/curated"
        if not os.path.exists(self.curated_data_dir):
            os.makedirs(self.curated_data_dir)

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
        # Load the JSON file
        filepath = os.path.join(self.raw_data_dir, filename)
        data = self.load_json_file(filepath)
        
        # Expand the data
        expanded_df = self.expand_data_column(data)
        
        # Save processed data
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_filename = f"curated_{filename.replace('.json', '')}_{timestamp}.csv"
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
    processor = WaniKaniDataProcessor()
    processor.process_all_files() 