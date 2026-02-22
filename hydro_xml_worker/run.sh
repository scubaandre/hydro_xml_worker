#!/bin/bash
mkdir -p /share/hydro_ottawa
chmod 777 /share/hydro_ottawa

echo "Starting Hydro Ottawa Scraper add-on..."
python3 /app/hydro_xml_worker.py