FROM python:3.11-alpine3.18

LABEL \
  io.hass.name="Hydro Ottawa Scraper" \
  io.hass.version="0.1.9-2" \
  io.hass.type="addon"

RUN apk add --no-cache bash \
    && pip install --no-cache-dir requests pyppeteer

ENV PYTHONUNBUFFERED=1

WORKDIR /app
COPY hydro_xml_worker.py .
COPY run.sh .
RUN chmod a+x run.sh

CMD [ "/bin/bash", "/app/run.sh" ]
