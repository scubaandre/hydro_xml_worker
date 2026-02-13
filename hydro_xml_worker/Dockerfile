FROM python:3.11-alpine3.18

LABEL \
  io.hass.name="Hydro Ottawa Scraper" \
  io.hass.version="00.01.03" \
  io.hass.type="addon"

RUN apk add --no-cache bash curl \
    && pip install --no-cache-dir requests pyppeteer

# Ensures logs are sent to the console immediately
ENV PYTHONUNBUFFERED=1

WORKDIR /app
COPY hydro_xml_worker.py .
COPY run.sh .
RUN chmod a+x run.sh

CMD [ "/bin/bash", "/app/run.sh" ]