#!/bin/bash
# simplified run.sh for v0.00.08
mkdir -p /share/hydro_ottawa
chmod 777 /share/hydro_ottawa

echo "Launching Hydro Ottawa Scraper v00.01.00..."
python3 /app/hydro_xml_worker.py