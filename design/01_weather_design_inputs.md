# 01 — Weather design inputs

Project: Boeing National Aeromodelling Competition 2026-27, IIT Madras zone, Aerial Firefighting Challenge (1000 mL water payload).
Date of study: 2026-11-21.

## 1. Scope

This file gives the weather conditions for two sites:

| Site | Month | Role |
|---|---|---|
| Bengaluru | December | Test flights before the competition |
| Chennai (IIT Madras) | January | Zonal competition |

The user confirmed the site roles on 2026-11-21. The rulebook does not give the zonal date or the flight hours.

## 2. Sources and method

| Item | Value |
|---|---|
| Station data (primary for wind, temperature, rain) | METAR reports from the Iowa Environmental Mesonet archive: VOMM (Chennai airport, about 8 km from IIT Madras), VOBG (Bengaluru HAL airport, in the city), VOBL (Bengaluru Kempegowda airport, 30 km north) |
| Model data (primary for pressure and air density) | Open-Meteo historical archive, default reanalysis blend, hourly. Points: 12.97 N 77.59 E (Bengaluru, model elevation 914 m) and 12.99 N 80.23 E (IIT Madras, model elevation 16 m) |
| Period | 11 seasons: Bengaluru December 2015 to 2025; Chennai January 2016 to 2026 |
| Day window | 08:00 to 17:00 IST, unless the table shows the hour |
| Wind height | All wind values are at 10 m above ground. Launch and landing occur at about 2 m (see section 5) |
| Air density | Humid-air equation of state from temperature, relative humidity and surface pressure. Density altitude from the ISA model |
| Scripts | `design/weather_scripts/download.sh` (raw data), `model_stats.py`, `metar_stats.py` (statistics) |

Data checks:
- The station mean winds and the model mean winds agree within about 0.5 m/s.
- The model gust values are not usable as design values. The model gives a median gust of 8 to 9 m/s for a mean wind of 4 m/s (gust factor 2.3).
- The stations report a gust in only 1.5 % (VOMM) and 0.4 % (VOBL) of daytime reports. A METAR gives a gust only when it is about 10 kt (5 m/s) above the mean wind. Thus smaller gusts occur but do not show in the reports.
- All day, the model shows rain on 18 to 19 % of days, and the stations show any rain or drizzle report on 16 to 18 % of days. These agree.
- In 08:00 to 17:00, the model shows rain on 21 to 22 % of days, but the stations show it on only 10 to 13 % of days. The station value is primary.
- VOBG and VOBL contain a small number of bad wind values (above 40 m/s). The statistics below do not use maximum values from these stations.

## 3. Summary table — design values

| Parameter | Bengaluru, December | Chennai, January |
|---|---|---|
| Field elevation | 890 to 915 m | about 10 m |
| Temperature, 14:00 mean | 26.5 °C | 29.5 °C |
| Daily maximum, mean / 95th percentile | 27 °C / 29 °C | 30 °C / 32 °C |
| Daily minimum, mean / 5th percentile | 17 °C / 13 °C | 22.5 °C / 20 °C |
| Relative humidity, 08:00 / 14:00 | 87 to 95 % / 51 to 54 % | 86 % / 60 % |
| Surface pressure, afternoon | 912 hPa | 1010 hPa |
| Air density, daytime mean | 1.063 kg/m³ | 1.164 kg/m³ |
| Air density, design value (low, hot afternoon) | **1.05 kg/m³** | **1.15 kg/m³** |
| Density altitude, design value | about 1600 m | about 650 m |
| Kinematic viscosity, afternoon | 1.75 × 10⁻⁵ m²/s | 1.61 × 10⁻⁵ m²/s |
| Mean wind at 10 m, 12:00 to 16:00 | 3.3 to 3.8 m/s | 4.1 to 4.7 m/s |
| 90th percentile wind at 10 m, afternoon | 5.1 to 5.7 m/s | 6.2 m/s |
| 99th percentile wind at 10 m, afternoon | 7.2 m/s | 7.7 m/s |
| Design gust at 10 m *(interp.)* | 8 to 9 m/s | 9 to 10 m/s |
| Main wind direction, afternoon | East (57 %), north-east (23 %) | East (48 %), north-east (39 %) |
| Days with any rain or drizzle report in 08:00 to 17:00 | 13 % (about 4 days in the month) | 10 % (about 3 days in the month) |
| Days with thunder | 1 % or less | 1 % |

Design gust *(interp.)*: the 90th percentile mean wind multiplied by a gust factor of 1.5. This factor is typical for open grass terrain. The few VOMM gust reports have a median of 10.3 m/s and a maximum of 11.8 m/s. These agree with the upper end of the range.

## 4. Diurnal profile (station data, 10 m wind)

### Chennai (VOMM), January

| Hour IST | Temp °C | RH % | Mean wind m/s | 90th pct wind m/s | Calm % |
|---|---|---|---|---|---|
| 07 | 23.1 | 89 | 1.2 | 2.1 | 27 |
| 08 | 24.6 | 86 | 1.5 | 2.6 | 19 |
| 09 | 26.4 | 79 | 2.3 | 4.1 | 8 |
| 10 | 27.9 | 70 | 3.2 | 5.1 | 3 |
| 11 | 28.9 | 65 | 3.7 | 5.7 | 1 |
| 12 | 29.4 | 62 | 4.1 | 6.2 | 1 |
| 13 | 29.6 | 60 | 4.4 | 6.2 | 0 |
| 14 | 29.5 | 60 | 4.6 | 6.2 | 0 |
| 15 | 29.2 | 61 | 4.7 | 6.2 | 0 |
| 16 | 28.7 | 63 | 4.5 | 6.2 | 0 |
| 17 | 27.8 | 67 | 4.3 | 5.7 | 0 |

Wind direction, Chennai:
- 08:00 to 11:00: north-east 33 %, north 21 %, east 18 %, north-west and west 21 % (light land breeze), variable 8 %.
- 12:00 to 17:00: east 48 %, north-east 39 %, south-east 7 %. The sea breeze makes the afternoon wind steady from the east.

### Bengaluru (VOBL / VOBG), December

| Hour IST | Temp °C | RH % | Mean wind m/s | 90th pct wind m/s |
|---|---|---|---|---|
| 07 | 17 to 18.5 | 92 to 98 | 2.0 | 3.6 |
| 08 | 19 to 20 | 87 to 95 | 2.5 | 4.1 |
| 09 | 21 | 79 to 86 | 3.1 | 4.6 to 5.1 |
| 10 | 22.5 | 71 | 3.5 | 5.1 |
| 12 | 25 | 57 to 59 | 3.4 to 3.8 | 5.1 to 5.7 |
| 14 | 26.3 | 51 to 54 | 3.3 to 3.7 | 5.1 |
| 16 | 26 | 53 | 3.2 to 3.6 | 4.6 to 5.1 |
| 17 | 25 | 57 | 3.0 to 3.5 | 4.1 to 5.1 |

Wind direction, Bengaluru: east about 60 %, north-east about 22 %, south-east about 10 %, all day. The direction is very constant.

## 5. Wind at launch and landing height

The wind at 2 m is less than the wind at 10 m. For open grass (roughness length 0.03 m), the log law gives V(2 m) = 0.72 × V(10 m) *(interp.)*.

| | Bengaluru | Chennai |
|---|---|---|
| Afternoon mean wind at 2 m | 2.5 m/s | 3.2 m/s |
| Afternoon 90th percentile wind at 2 m | 3.9 m/s | 4.5 m/s |

At the flight height of 10 to 30 m, use the 10 m values or slightly more.

## 6. Design implications (environment only)

### 6.1 Air density: Bengaluru air is about 9 % thinner

The density ratio is 1.164 / 1.063 = 1.095. For the same aircraft and the same load:
- Stall speed and flight speed are about 4.6 % higher in Bengaluru (speed ∝ 1/√ρ).
- Power required in level flight is about 4.6 % higher in Bengaluru.
- Static thrust of the propeller is about 6 to 9 % lower in Bengaluru. The exact value depends on how much the motor speed increases in the thinner air.
- At the same speed, the Reynolds number is about 8 % lower in Bengaluru.

Result: an aircraft that flies well with 1000 mL in Bengaluru has more margin in Chennai. Bengaluru is the more severe case for lift, take-off and climb.

### 6.2 Thrust-to-weight limit (T/W ≤ 1.5, rule 2)

The organizers measure T/W at the venue in Chennai *(interp.: the method of measurement is not in the rulebook)*. The denser air in Chennai gives about 6 to 9 % more static thrust than in Bengaluru.
- If T/W is 1.50 when measured in Bengaluru, it can be about 1.60 to 1.64 in Chennai.
- The organizers then add ballast below the CG. This ballast adds mass to the aircraft in flight. The rulebook does not say if the ballast counts in the empty weight, which is the divisor of the score.
- Keep T/W at 1.37 or less when you measure it in Bengaluru. Measure it again in Chennai before the inspection.

### 6.3 Wind

- The aircraft must fly with control in a mean wind of 6 m/s and gusts to 10 m/s at 10 m. This covers about 90 % of afternoon hours in Chennai.
- The loaded flight speed must be sufficiently high for flight into this wind. The aircraft must return to the landing zone in the 3 min window.
- The release zone is about 40 m from the take-off and landing zone. The organizers can move it for the wind direction.
- The wind comes from the east or north-east in about 80 to 90 % of afternoon hours in both cities. The crosswind on take-off and landing depends on the arena layout, which is not known.
- In Chennai, the wind at 08:00 to 09:00 is much lower: mean 1.5 to 2.3 m/s, calm 8 to 19 % of the time. A hand launch in calm air needs more launch speed or more thrust.
- The flight schedule is not under the control of the team. The design must work at the windiest hour (14:00 to 16:00).

### 6.4 Temperature and sun

- The design temperature is 32 °C in the shade (Chennai, 95th percentile).
- An aircraft in direct sun gets much hotter than the air *(interp.: often 45 to 60 °C on dark surfaces)*. Foam, hot glue and heat-shrink film can soften. Keep the aircraft and the batteries in the shade between flights.
- LiPo batteries work well at 22 to 32 °C. No heater or extra cooling is necessary for this temperature range.
- Water at 28 to 30 °C has a density of about 996 kg/m³. Thus 1000 mL of water has a mass of about 996 g, not 1000 g.

### 6.5 Humidity and rain

- Morning relative humidity is 86 to 98 %. Dew can form on the aircraft before 09:00. Balsa and paper parts can absorb moisture and become heavier. Weigh the aircraft in the same condition each time.
- Rain occurs in the daytime on about 10 to 13 % of days. Thunderstorms are rare.
- The aircraft carries water and releases it in flight. Seal the electronics against water from the payload. This seal also gives protection against light rain.
- Late north-east monsoon systems can still bring heavy rain in early December to Bengaluru and in early January to Chennai *(interp.)*. Plan spare days for test flights.
- The station reports show more rain days from 2020 to 2026 than from 2016 to 2019. A change in the method of the reports can be part of this difference.

## 7. Key checks

These values are the environmental inputs for the sizing step. The sizing step and the verification must use them.

1. Design air density for performance (lift, take-off, climb): **1.05 kg/m³** (Bengaluru afternoon).
2. Design air density for the venue (Chennai afternoon): **1.15 kg/m³**. Use 1.164 kg/m³ for a mean value.
3. Static thrust in Chennai is about 1.06 to 1.09 times the static thrust in Bengaluru. Keep T/W ≤ 1.37 when measured in Bengaluru.
4. Design wind at 10 m: mean 6 m/s, gust 10 m/s. Wind at 2 m: 0.72 × the 10 m value.
5. Wind direction for the layout: east to north-east in both cities.
6. Design ambient temperature: 32 °C maximum, 13 °C minimum (Bengaluru early morning).
7. Water payload mass: about 996 g for 1000 mL at 28 to 30 °C.
8. Kinematic viscosity for Reynolds number: 1.75 × 10⁻⁵ m²/s (Bengaluru), 1.61 × 10⁻⁵ m²/s (Chennai).

## 8. Open items

1. Find the zonal date and the flight hours from the IIT Madras (Shaastra) page when it is published.
2. Find how the organizers measure T/W (static thrust on a scale, battery state, propeller).
3. Find if the T/W ballast counts in the empty weight for the score. Ask the organizers.
