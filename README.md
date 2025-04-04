# WaniKani Data Analysis Web Application

A web application that allows users to analyze their WaniKani learning progress by entering their API key.

## Setup

1. Clone this repository
2. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the application:
   ```bash
   python app.py
   ```
4. Open your browser and navigate to `http://localhost:5000`

## Features

- Enter your WaniKani API key to analyze your learning progress
- View level progression and review statistics
- Interactive charts and visualizations
- Secure API key handling

## Deployment

To deploy this application to a production environment:

1. Set up a production web server (e.g., Nginx)
2. Use Gunicorn as the WSGI server:
   ```bash
   gunicorn app:app
   ```
3. Configure your web server to proxy requests to Gunicorn

## Security Notes

- API keys are only used for the current session and are not stored
- All data processing happens server-side
- HTTPS is recommended for production deployment

## WordPress Integration

To integrate this with WordPress:

1. Host the Flask application on a separate server/subdomain
2. Use an iframe or embed the application in a WordPress page
3. Alternatively, create a WordPress plugin that communicates with the Flask backend
