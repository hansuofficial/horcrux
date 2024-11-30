import os
import json
import subprocess
from flask import Flask, request, jsonify

app = Flask(__name__)

def run_wine_arp(start_lat, start_lon, dest_lat, dest_lon):
    exe_path = "/app/code_smaller/QuadWeatherSouthPath/x64/Release/QuadWeatherSouthPath.exe"
    output_file = "/app/output/result.json"

    command = [
        "wine",
        exe_path,
        output_file,
        f"{start_lat:.6f}",
        f"{start_lon:.6f}",
        f"{dest_lat:.6f}",
        f"{dest_lon:.6f}",
    ]

    try:
        subprocess.run(command, check=True)
    except subprocess.CalledProcessError as e:
        return None, f"QuadWeatherSouthPath.exe exited with code {e.returncode}"
    except Exception as e:
        return None, f"Failed to execute QuadWeatherSouthPath.exe: {str(e)}"

    try:
        with open(output_file, "r") as f:
            result = json.load(f)
    except FileNotFoundError:
        return None, "Failed to read result file: File not found."
    except json.JSONDecodeError:
        return None, "Failed to parse JSON output from result file."

    try:
        os.remove(output_file)
    except Exception as e:
        return None, f"Failed to delete result file: {str(e)}"

    return result, None


# GET endpoint to calculate route
@app.route("/calc-route", methods=["GET"])
def calc_route_get():
    try:
        # Parse query parameters
        start_lat = float(request.args.get("start_lat", ""))
        start_lon = float(request.args.get("start_lon", ""))
        dest_lat = float(request.args.get("dest_lat", ""))
        dest_lon = float(request.args.get("dest_lon", ""))
    except ValueError:
        return jsonify({"error": "Invalid query parameters. Ensure all coordinates are valid floating-point numbers."}), 400

    # Run the external command
    result, error = run_wine_arp(start_lat, start_lon, dest_lat, dest_lon)
    if error:
        return jsonify({"error": error}), 500

    return jsonify(result), 200


# POST endpoint to calculate route
@app.route("/calc-route", methods=["POST"])
def calc_route_post():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid JSON body."}), 400

    try:
        # Parse JSON body
        start_lat = float(data.get("start_lat"))
        start_lon = float(data.get("start_lon"))
        dest_lat = float(data.get("dest_lat"))
        dest_lon = float(data.get("dest_lon"))
    except (ValueError, TypeError):
        return jsonify({"error": "Invalid JSON body. Ensure all coordinates are valid floating-point numbers."}), 400

    # Run the external command
    result, error = run_wine_arp(start_lat, start_lon, dest_lat, dest_lon)
    if error:
        return jsonify({"error": error}), 500

    return jsonify(result), 200


# Health check endpoint
@app.route("/healthz", methods=["GET"])
def healthz():
    return jsonify({"status": "healthy"}), 200


# Readiness check endpoint
@app.route("/readiness", methods=["GET"])
def readiness():
    return jsonify({"status": "ready"}), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
