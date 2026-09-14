# AEC CONTEXT GENERATOR

An experimental Python utility built to bypass manual CAD drafting by automating architectural site data collection. Queries spatial API endpoints to instantly parse, project, and generate a layered 3D context model from a single location input.

## Features
- **Geocoding:** Queries the French BAN API for Lambert 93 (EPSG:2154) coordinates.
- **Site Acquisition:** Automatically extracts footprint boundaries via OSM (Overpass API).
- **3D Extrusion:** Uses `shapely` and `ezdxf` to generate 3D DXF files from footprints and building height tags.

## Requirements
```bash
pip install requests shapely pyproj ezdxf
```

## Usage
Run `aec-context-gen-main.py`. Enter the target address, acquisition radius, and default height, then click *Acquire & Process Site*. The script outputs a DXF file ready for import into Rhino, SketchUp, or Blender.
