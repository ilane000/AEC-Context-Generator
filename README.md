# AEC Context Generator - Automation Pipeline

AEC Context Generator is a desktop Python application (built with tkinter) that automates the acquisition of 3D building site contexts.

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
