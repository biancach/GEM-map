# GEM Power Map

Interactive map of every power plant in the **Global Energy Monitor — Global Integrated Power Tracker** (March 2026 release).

## Run it

The page loads `data/plants.json`, so you need a local web server (a `file://` open won't work because of `fetch`):

```bash
cd GEM-map
python3 -m http.server 8000
# then open http://localhost:8000
```

## Rebuild data from the spreadsheet

```bash
python3 GEM-map/scripts/convert.py
```

Reads `../data/Global-Integrated-Power-March-2026-II.xlsx`, aggregates ~182k unit rows into ~145k plant-level points, and writes a columnar / dictionary-encoded JSON to `GEM-map/data/plants.json` (~24 MB; ~4 MB gzipped). Serve gzipped if your host supports it.

## Features

- 🗺️ Clustered global map (Leaflet + MarkerCluster, dark Carto basemap)
- 🎨 Markers colored & sized by fuel type and capacity (MW)
- 🔎 **Search by plant name** — instant substring match against all 145k plants
- 📍 **Power plants near me** — uses browser geolocation, draws a 75 km radius and lists the closest 25 plants sorted by distance
- 🌍 **Search by place** — type any city/country/address (Nominatim geocoder) and the map flies there with a 75 km radius
- 🎚️ Filter by fuel type, status (operating / construction / retired / etc.), and minimum capacity
- 🎲 **Surprise me** — fly to a random plant from the current filter set
- 📊 Live stats: number of plants & total capacity matching the current filters
- 🔗 Click any marker for owner, start year, unit count and a direct link to its **GEM.wiki** page

## Possible next features

- Heatmap layer toggle (capacity-weighted)
- Time slider showing build-out by start year
- Country leaderboards (top N coal/solar/etc. by GW)
- CSV download of the current viewport
- Compare-mode: pick two countries side-by-side
