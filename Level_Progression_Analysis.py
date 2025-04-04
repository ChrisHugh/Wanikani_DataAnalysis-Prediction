import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
from datetime import datetime
import json
import numpy as np

def clean_for_json(value):
    """Convert NaN, infinite, or invalid JSON values to None"""
    if pd.isna(value) or (isinstance(value, float) and not np.isfinite(value)):
        return None
    return value

def generate_level_progression_html():
    """Generate visualization data and save standalone HTML"""
    try:
        # Create Analysis Images directory if it doesn't exist
        os.makedirs('Analysis Images', exist_ok=True)

        # Load data
        level_progressions = pd.read_csv('data/curated/curated_level_progressions_20250404_131342.csv')
        print("Successfully loaded level progressions data")
        print(f"Data shape: {level_progressions.shape}")
        print(f"Columns: {level_progressions.columns.tolist()}")

        level_progressions['Time Spent'] = pd.to_datetime(level_progressions['passed_at']) - pd.to_datetime(level_progressions['started_at'])

        # Convert time spent to days
        level_progressions['Time Spent'] = level_progressions['Time Spent'].dt.days
        print(f"Time spent range: {level_progressions['Time Spent'].min()} to {level_progressions['Time Spent'].max()} days")
        print(f"Processed {len(level_progressions)} level progressions")

        # Create color gradient based on time spent
        mean_time = level_progressions['Time Spent'].mean()
        print(f"Mean time per level: {mean_time:.2f} days")
        colors = []
        for time in level_progressions['Time Spent']:
            if pd.isna(time):
                colors.append('rgb(200, 200, 200)')  # Gray for NaN values
            elif time < mean_time * 0.75:  # Fast (light blue)
                colors.append('rgb(173, 216, 230)')  # Light blue
            elif time < mean_time * 1.25:  # Medium (reddish pink)
                colors.append('rgb(255, 105, 180)')  # Hot pink
            else:  # Long (medium purple)
                colors.append('rgb(147, 112, 219)')  # Medium purple

        # Clean data for JSON serialization
        x_values = [clean_for_json(x) for x in level_progressions['level'].tolist()]
        y_values = [clean_for_json(y) for y in level_progressions['Time Spent'].tolist()]
        text_values = [clean_for_json(t) if pd.notna(t) else 'No data' 
                      for t in level_progressions['Time Spent'].round(1).tolist()]

        # Create the trace data
        trace = {
            'type': 'bar',
            'x': x_values,
            'y': y_values,
            'marker': {'color': colors},
            'text': text_values,
            'textposition': 'auto',
            'name': 'Time Spent (days)'
        }

        # Create the layout
        layout = {
            'title': 'Level Progression vs Time Spent',
            'xaxis': {'title': 'Level', 'tickmode': 'linear', 'tick0': 1, 'dtick': 1},
            'yaxis': {'title': 'Time Spent (Days)', 'tickmode': 'linear', 'tick0': 0, 'dtick': 5},
            'showlegend': False,
            'template': 'plotly_white',
            'height': 600,
            'width': 800
        }

        # Create the figure for saving HTML
        fig = go.Figure(data=[go.Bar(**trace)], layout=layout)

        # Save standalone HTML file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        html_path = os.path.join('Analysis Images', f'level_progression_{timestamp}.html')
        fig.write_html(html_path, include_plotlyjs=True, full_html=True)
        print(f"Successfully saved HTML to: {html_path}")
        
        # Create the plot data for web display
        plot_data = {
            'data': [trace],
            'layout': layout
        }
        
        # Verify JSON serialization
        try:
            json.dumps(plot_data)
            print("Successfully verified JSON serialization")
        except Exception as e:
            print(f"JSON serialization error: {str(e)}")
            raise
        
        return plot_data

    except Exception as e:
        print(f"An error occurred: {str(e)}")
        import traceback
        print("Full traceback:")
        print(traceback.format_exc())
        return {'error': str(e)}

if __name__ == "__main__":
    plot_data = generate_level_progression_html()
    print(json.dumps(plot_data, indent=2))





