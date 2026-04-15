"""Convert the GEM Global-Integrated-Power xlsx into a compact JSON file
the website can load. Aggregates units to plant level (one marker per plant)."""

import json
import math
from collections import defaultdict
from pathlib import Path

import openpyxl

ROOT = Path(__file__).resolve().parents[2]
XLSX = ROOT / "data" / "Global-Integrated-Power-March-2026-II.xlsx"
OUT = ROOT / "GEM-map" / "data" / "plants.json"

WANTED = {
    "Type": "type",
    "Country/area": "country",
    "Region": "region",
    "Plant / Project name": "name",
    "Capacity (MW)": "capacity",
    "Status": "status",
    "Start year": "year",
    "Fuel (combustion only)": "fuel",
    "Owner(s)": "owner",
    "Latitude": "lat",
    "Longitude": "lon",
    "GEM location ID": "loc_id",
    "GEM.Wiki URL": "url",
    "Subnational unit (state, province)": "state",
    "City": "city",
}


def main():
    wb = openpyxl.load_workbook(XLSX, read_only=True, data_only=True)
    ws = wb["Power facilities"]
    rows = ws.iter_rows(values_only=True)
    header = next(rows)
    idx = {h: i for i, h in enumerate(header)}

    plants = {}  # key = (loc_id) -> aggregated plant
    skipped = 0
    total = 0

    for r in rows:
        total += 1
        get = lambda col: r[idx[col]] if col in idx else None
        lat = get("Latitude")
        lon = get("Longitude")
        if lat is None or lon is None:
            skipped += 1
            continue
        try:
            lat = float(lat)
            lon = float(lon)
        except (TypeError, ValueError):
            skipped += 1
            continue
        if math.isnan(lat) or math.isnan(lon):
            skipped += 1
            continue

        loc_id = get("GEM location ID") or f"{get('Plant / Project name')}|{lat:.4f}|{lon:.4f}"
        cap = get("Capacity (MW)") or 0
        try:
            cap = float(cap)
        except (TypeError, ValueError):
            cap = 0

        if loc_id not in plants:
            plants[loc_id] = {
                "n": get("Plant / Project name") or "Unnamed",
                "t": get("Type") or "unknown",
                "c": get("Country/area") or "",
                "s": get("Subnational unit (state, province)") or "",
                "ci": get("City") or "",
                "lat": round(lat, 5),
                "lon": round(lon, 5),
                "cap": 0.0,
                "u": 0,  # unit count
                "st": defaultdict(float),  # status -> capacity
                "yr": None,
                "ow": get("Owner(s)") or "",
                "url": get("GEM.Wiki URL") or "",
                "fu": set(),
            }
        p = plants[loc_id]
        p["cap"] += cap
        p["u"] += 1
        status = (get("Status") or "unknown").lower()
        p["st"][status] += cap
        yr = get("Start year")
        try:
            yr = int(yr)
            if p["yr"] is None or yr < p["yr"]:
                p["yr"] = yr
        except (TypeError, ValueError):
            pass
        fuel = get("Fuel (combustion only)")
        if fuel:
            p["fu"].add(str(fuel).split(":")[0].strip())

    # Use parallel arrays (columnar) + dictionary-encoded categoricals
    # to keep the JSON file small enough to ship to a browser.
    types = []
    countries = []
    statuses = []
    type_idx = {}
    country_idx = {}
    status_idx = {}

    def enc(value, lookup, table):
        if value not in lookup:
            lookup[value] = len(table)
            table.append(value)
        return lookup[value]

    rows_out = []
    for p in plants.values():
        status = max(p["st"].items(), key=lambda x: x[1])[0] if p["st"] else "unknown"
        rows_out.append([
            p["n"],
            enc(p["t"], type_idx, types),
            enc(p["c"], country_idx, countries),
            enc(status, status_idx, statuses),
            p["lat"],
            p["lon"],
            round(p["cap"], 1),
            p["yr"] if p["yr"] is not None else 0,
            p["u"],
            p["s"],
            p["ci"],
            p["ow"][:160],
            p["url"],
        ])

    payload = {
        "schema": ["n", "t", "c", "st", "lat", "lon", "cap", "yr", "u", "s", "ci", "ow", "url"],
        "types": types,
        "countries": countries,
        "statuses": statuses,
        "rows": rows_out,
    }

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT, "w") as f:
        json.dump(payload, f, separators=(",", ":"))

    print(f"Total unit rows: {total}")
    print(f"Skipped (no coords): {skipped}")
    print(f"Aggregated plants: {len(rows_out)}")
    print(f"Wrote: {OUT} ({OUT.stat().st_size/1e6:.1f} MB)")


if __name__ == "__main__":
    main()
