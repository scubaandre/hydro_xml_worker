#!/bin/bash
mkdir -p /share/hydro_ottawa
chmod 777 /share/hydro_ottawa

echo "Starting Hydro Ottawa add-on v00.01.02..."
python3 /app/hydro_xml_worker.py