import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Load data
level_progressions = pd.read_csv('data\curated\curated_level_progressions_20250320_141329_20250320_143544.csv')

level_progressions['Time Spent'] = pd.to_datetime(level_progressions['passed_at']) - pd.to_datetime(level_progressions['started_at'])

# Convert time spent to days
level_progressions['Time Spent'] = level_progressions['Time Spent'].dt.days

# Create color gradient based on time spent
mean_time = level_progressions['Time Spent'].mean()
colors = []
for time in level_progressions['Time Spent']:
    if time < mean_time * 0.75:  # Fast (light blue)
        colors.append('rgb(173, 216, 230)')  # Light blue
    elif time < mean_time * 1.25:  # Medium (reddish pink)
        colors.append('rgb(255, 105, 180)')  # Hot pink
    else:  # Long (medium purple)
        colors.append('rgb(147, 112, 219)')  # Medium purple

# Create the plot using graph_objects for more control
fig = go.Figure(data=[
    go.Bar(
        x=level_progressions['level'],
        y=level_progressions['Time Spent'],
        marker_color=colors,
        text=level_progressions['Time Spent'].round(1),  # Add value labels
        textposition='auto',
        name='Time Spent (days)'
    )
])

# Update layout
fig.update_layout(
    title='Level Progression vs Time Spent',
    xaxis_title='Level',
    yaxis_title='Time Spent (Days)',
    showlegend=False,
    template='plotly_white'
)

# Update axes
fig.update_xaxes(tickmode='linear', tick0=1, dtick=1)
fig.update_yaxes(tickmode='linear', tick0=0, dtick=5)

fig.show()






