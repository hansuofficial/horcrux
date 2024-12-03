import os
import json
import subprocess
import uuid
from flask import Flask, request, jsonify

app = Flask(__name__)

def run_wine_arp(start_lat, start_lon, dest_lat, dest_lon):
    exe_path = "/app/code_smaller/QuadWeatherSouthPath/x64/Release/QuadWeatherSouthPath.exe"
    working_dir = "/app/code_smaller/QuadWeatherSouthPath/QuadWeatherSouthPath"

    unique_id = uuid.uuid4()
    output_file = f"/app/output/result_{unique_id}.json"

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
        subprocess.run(command, check=True, cwd=working_dir)
    except subprocess.CalledProcessError as e:
        if e.returncode == 10:
            return jsonify({"error": f"Wrong number of argumenets passed to QuadWeatherSouthPath.exe"}), 500
        elif e.returncode == 11:
            return jsonify({"error": f"Given coordinates outside of service area"}), 500
        elif e.returncode == 12:
            return jsonify({"error": f"Could not open a file for writing json output (list of coordinates)"}), 500
        elif e.returncode == 13:
            return jsonify({"error": f"Invalid parameters. Check the data type"}), 500
        elif e.returncode == 14:
            return jsonify({"error": f"Unknown internal error from QuadWeatherSouthPath.exe"}), 500
        else:
            return jsonify({"error": f"Unknown error from wine. Error code: {e.returncode}"}), 500
    except Exception as e:
        return None, f"Failed to execute QuadWeatherSouthPath.exe: {str(e)}"

    try:
        with open(output_file, "r") as f:
            result = json.load(f)
    except FileNotFoundError:
        return jsonify({"error": f"Wine exited successfully but cannot find the output file: {output_file}"}), 500
    except json.JSONDecodeError:
         return jsonify({"error": f"Error while decoding json from {output_file}"}), 500

    try:
        os.remove(output_file)
    except Exception as e:
        jsonify({"error": f"Could not delete the temporary output file: {str(e)}"}), 500

    transformed_result = transform_coordinates(result)

    return jsonify(transformed_result), 200

def transform_coordinates(result):
    """
    Transforms the keys 'lat' and 'lon' in the result JSON to 'latitude' and 'longitude'.
    
    Args:
        result (list of dict): A list of dictionaries with 'lat' and 'lon' keys.

    Returns:
        list of dict: Transformed list with 'latitude' and 'longitude' keys.
    """
    transformed = []
    for entry in result:
        transformed.append({
            "latitude": entry.get("lat"),
            "longitude": entry.get("lon")
        })
    return transformed


@app.route("/calc-route", methods=["GET"])
def calc_route_get():
    try:
        start_lat = float(request.args.get("start_lat", ""))
        start_lon = float(request.args.get("start_lon", ""))
        dest_lat = float(request.args.get("dest_lat", ""))
        dest_lon = float(request.args.get("dest_lon", ""))
    except ValueError:
        return jsonify({"error": "Invalid query parameters. Ensure all coordinates are valid floating-point numbers."}), 400

    return run_wine_arp(start_lat, start_lon, dest_lat, dest_lon)


@app.route("/calc-route", methods=["POST"])
def calc_route_post():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid JSON body."}), 400

    try:
        start_lat = float(data.get("start_lat"))
        start_lon = float(data.get("start_lon"))
        dest_lat = float(data.get("dest_lat"))
        dest_lon = float(data.get("dest_lon"))
    except (ValueError, TypeError):
        return jsonify({"error": "Invalid JSON body. Ensure all coordinates are valid floating-point numbers."}), 400
    
    return run_wine_arp(start_lat, start_lon, dest_lat, dest_lon)


@app.route("/health", methods=["GET"])
def healthz():
    return jsonify({"status": "healthy"}), 200


@app.route("/readiness", methods=["GET"])
def readiness():
    return jsonify({"status": "ready"}), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
