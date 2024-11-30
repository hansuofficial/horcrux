#!/bin/bash

unzip /app/files/code_smaller.zip -d /app/
# cd /app/code_smaller/QuadWeatherSouthPath/QuadWeatherSouthPath
# wine /app/code_smaller/QuadWeatherSouthPath/x64/Release/QuadWeatherSouthPath.exe  /app/output/result.json 34.944210 127.827940 34.720719 128.580744

python3 /app/app.py
# exec /bin/bash

