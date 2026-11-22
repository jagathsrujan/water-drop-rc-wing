#!/bin/sh
# Download the raw data that model_stats.py and metar_stats.py read. Run from the folder that holds the scripts' input files.
V="temperature_2m,relative_humidity_2m,dew_point_2m,surface_pressure,wind_speed_10m,wind_gusts_10m,wind_direction_10m,precipitation"
curl -s "https://archive-api.open-meteo.com/v1/archive?latitude=12.97&longitude=77.59&start_date=2015-12-01&end_date=2025-12-31&hourly=$V&timezone=Asia%2FKolkata&wind_speed_unit=ms" -o blr.json
curl -s "https://archive-api.open-meteo.com/v1/archive?latitude=12.99&longitude=80.23&start_date=2016-01-01&end_date=2026-01-31&hourly=$V&timezone=Asia%2FKolkata&wind_speed_unit=ms" -o maa.json
for s in VOMM VOBG VOBL; do
  curl -s "https://mesonet.agron.iastate.edu/cgi-bin/request/asos.py?station=$s&data=tmpf&data=relh&data=drct&data=sknt&data=gust&data=alti&data=p01m&data=wxcodes&year1=2015&month1=12&day1=1&year2=2026&month2=2&day2=1&tz=Asia%2FKolkata&format=onlycomma&latlon=no&missing=M&trace=T&direct=no&report_type=3&report_type=4" -o $s.csv
done
