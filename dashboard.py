import socket
import threading
import time
from flask import Flask, render_template, jsonify
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import io
import base64

app = Flask(__name__)

# Global variables to store metrics
metrics_data = {
    "cpu": [],
    "timestamps": []
}

# Start time for x-axis in seconds
start_time = time.time()

def update_metrics(cpu_usage):
    """
    Update the metrics data with new CPU usage and timestamp.
    """
    metrics_data["cpu"].append(cpu_usage)
    metrics_data["timestamps"].append(time.time() - start_time)

def collect_metrics():
    """
    Function to simulate receiving metrics (replace with real UDP reception).
    This is just a placeholder for actual UDP message handling.
    """
    while True:
        time.sleep(5)  # Simulate receiving metrics every 5 seconds
        cpu_usage = 50  # Placeholder for actual CPU usage metric
        update_metrics(cpu_usage)


@app.route('/')
def index():
    """
    Render the main dashboard page.
    """
    return render_template('index.html')


@app.route('/metrics')
def get_metrics():
    """
    Return the latest metrics as JSON.
    """
    return jsonify(metrics_data)


def plot_metrics():
    """
    Function to generate a real-time plot of CPU usage.
    """
    fig, ax = plt.subplots()
    ax.set_title('CPU Usage Over Time')
    ax.set_xlabel('Time (s)')
    ax.set_ylabel('CPU Usage (%)')

    def animate(i):
        ax.clear()
        ax.plot(metrics_data["timestamps"], metrics_data["cpu"], label="CPU Usage")
        ax.set_xlim(left=max(0, time.time() - start_time - 60), right=time.time() - start_time)  # Show last 60s of data
        ax.set_ylim(0, 100)
        ax.set_title('CPU Usage Over Time')
        ax.set_xlabel('Time (s)')
        ax.set_ylabel('CPU Usage (%)')
        ax.legend()

    ani = FuncAnimation(fig, animate, interval=1000)

    # Save plot to a PNG image in memory and encode it as base64
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    img = base64.b64encode(buf.read()).decode('utf-8')
    buf.close()
    return img


@app.route('/plot')
def plot():
    """
    Route to return the plot image in base64 format.
    """
    img = plot_metrics()
    return f"<img src='data:image/png;base64,{img}'>"


if __name__ == '__main__':
    # Start the thread to collect metrics
    metrics_thread = threading.Thread(target=collect_metrics)
    metrics_thread.daemon = True
    metrics_thread.start()

    # Run the Flask app
    app.run(debug=True, host='0.0.0.0')
