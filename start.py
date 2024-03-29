from flask import Flask, render_template_string, make_response
import sqlite3
from datetime import datetime
import csv
import io

app = Flask(__name__)

# Define HTML template with CSS for the table
html_template = """
<!DOCTYPE html>
<html>
<head>
    <title>Sensor Data</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        table { border-collapse: collapse; width: 60%; }
        th, td { text-align: left; padding: 8px; }
        tr:nth-child(even) { background-color: #f2f2f2; }
        th { background-color: #4CAF50; color: white; }
    </style>
</head>
<body>
    <h1>Data</h1>
    <a href="/download/csv" style="margin-bottom: 20px; display: inline-block; background-color: #4CAF50; color: white; padding: 10px; text-decoration: none; border-radius: 5px;">Download CSV</a>
    <table>
        <tr>
            <th>Timestamp</th>
            <th>Value</th>
        </tr>
        {% for row in data %}
        <tr>
            <td>{{ row[0] }}</td>
            <td>{{ row[1] }}</td>
        </tr>
        {% endfor %}
    </table>
</body>
</html>
"""

@app.route('/')
def show_data():
    # Connect to the SQLite database
    conn = sqlite3.connect('sensor_data.db')
    c = conn.cursor()
    
    # Query to select data from the table
    c.execute("SELECT timestamp, value FROM sensor_data ORDER BY timestamp DESC")
    data = c.fetchall()
    
    # Format the timestamp for each row to a more readable format
    formatted_data = [(datetime.strptime(row[0], '%Y-%m-%dT%H:%M:%S.%f').strftime('%B %d, %Y %H:%M:%S'), row[1]) for row in data]
    
    # Close the database connection
    conn.close()
    
    # Use the template with CSS to display the data
    return render_template_string(html_template, data=formatted_data)

@app.route('/download/csv')
def download_csv():
    # Connect to the SQLite database
    conn = sqlite3.connect('sensor_data.db')
    c = conn.cursor()

    # Query to select data
    c.execute("SELECT timestamp, value FROM sensor_data ORDER BY timestamp DESC")
    data = c.fetchall()
    
    # Close the database connection
    conn.close()

    # Create CSV in memory
    output = io.StringIO()
    writer = csv.writer(output, quoting=csv.QUOTE_NONNUMERIC)

    # Write header
    writer.writerow(['Timestamp', 'Value'])

    # Write data
    for row in data:
        writer.writerow(row)

    # Seek to start
    output.seek(0)
    
    # Create a response
    response = make_response(output.getvalue())
    response.headers["Content-Disposition"] = "attachment; filename=sensor_data.csv"
    response.headers["Content-type"] = "text/csv"
    return response

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=80)