import os
import json
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import requests
import math

try:
    from shapely.geometry import Polygon, MultiPolygon
    import pyproj
    from pyproj import Transformer
    import ezdxf
    HAS_DEPS = True
except ImportError:
    HAS_DEPS = False

class AECContextGeneratorApp(tk.Tk):
    def __init__(self):
        super().__init__()
        
        self.title("AEC CONTEXT GENERATOR // v1.0.0-alpha")
        self.geometry("680x520")
        self.configure(bg="#111111")
        
        # Style Configuration
        self.style = ttk.Style()
        self.style.theme_use("clam")
        
        # Configure dark theme colors
        self.style.configure("TLabel", background="#111111", foreground="#CCCCCC", font=("Courier", 10))
        self.style.configure("TButton", background="#222222", foreground="#FFFFFF", bordercolor="#444444", font=("Courier", 10, "bold"))
        self.style.map("TButton", background=[("active", "#333333")], foreground=[("active", "#00FF00")])
        self.style.configure("TFrame", background="#111111")
        self.style.configure("TEntry", fieldbackground="#222222", foreground="#FFFFFF", bordercolor="#444444", insertcolor="#FFFFFF")
        
        # Title Header
        title_frame = tk.Frame(self, bg="#111111", bd=0)
        title_frame.pack(fill="x", padx=20, pady=15)
        
        title_lbl = tk.Label(title_frame, text="SYS:LOGIC // AEC_CONTEXT_GENERATOR", bg="#111111", fg="#00FF00", font=("Courier", 12, "bold"))
        title_lbl.pack(anchor="w")
        
        desc_lbl = tk.Label(title_frame, text="Automated 3D Site Acquisition Pipeline // Lambert 93 (EPSG:2154)", bg="#111111", fg="#888888", font=("Courier", 9))
        desc_lbl.pack(anchor="w")
        
        # Main Layout container
        main_frame = ttk.Frame(self)
        main_frame.pack(fill="both", expand=True, padx=20, pady=5)
        
        # Inputs Frame
        inputs_frame = tk.LabelFrame(main_frame, text=" acquisition parameters ", bg="#111111", fg="#00FF00", font=("Courier", 9), bd=1, relief="solid")
        inputs_frame.pack(fill="x", padx=5, pady=5, ipady=8)
        
        # Row 1: Target Location Address
        tk.Label(inputs_frame, text="LOCATION ADDRESS:", bg="#111111", fg="#CCCCCC", font=("Courier", 9)).grid(row=0, column=0, padx=10, pady=8, sticky="w")
        self.address_entry = tk.Entry(inputs_frame, bg="#222222", fg="#FFFFFF", insertbackground="white", font=("Courier", 10), bd=1, relief="solid")
        self.address_entry.grid(row=0, column=1, columnspan=3, padx=10, pady=8, sticky="ew")
        self.address_entry.insert(0, "8 Rue de l'Archipel, Lyon, France")
        
        # Row 2: Boundary Radius and Building Height
        tk.Label(inputs_frame, text="RADIUS (METERS):", bg="#111111", fg="#CCCCCC", font=("Courier", 9)).grid(row=1, column=0, padx=10, pady=8, sticky="w")
        self.radius_entry = tk.Entry(inputs_frame, bg="#222222", fg="#FFFFFF", insertbackground="white", font=("Courier", 10), bd=1, relief="solid", width=12)
        self.radius_entry.grid(row=1, column=1, padx=10, pady=8, sticky="w")
        self.radius_entry.insert(0, "150")
        
        tk.Label(inputs_frame, text="DEFAULT HEIGHT (M):", bg="#111111", fg="#CCCCCC", font=("Courier", 9)).grid(row=1, column=2, padx=10, pady=8, sticky="w")
        self.height_entry = tk.Entry(inputs_frame, bg="#222222", fg="#FFFFFF", insertbackground="white", font=("Courier", 10), bd=1, relief="solid", width=12)
        self.height_entry.grid(row=1, column=3, padx=10, pady=8, sticky="w")
        self.height_entry.insert(0, "12")
        
        inputs_frame.columnconfigure(1, weight=1)
        inputs_frame.columnconfigure(3, weight=1)
        
        # Action Buttons
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill="x", padx=5, pady=10)
        
        self.acquire_btn = ttk.Button(btn_frame, text="[ ACQUIRE & PROCESS SITE ]", command=self.run_pipeline)
        self.acquire_btn.pack(side="left", padx=5, expand=True, fill="x")
        
        # Log Console
        console_lbl = tk.Label(main_frame, text="SYSTEM LOGGER // LOG OUTPUT", bg="#111111", fg="#888888", font=("Courier", 9))
        console_lbl.pack(anchor="w", padx=5, pady=(10, 2))
        
        self.log_widget = scrolledtext.ScrolledText(main_frame, bg="#080808", fg="#00FF00", insertbackground="white", font=("Courier", 9), bd=1, relief="solid")
        self.log_widget.pack(fill="both", expand=True, padx=5, pady=5)
        
        self.log("SYS:INIT // Pipeline initialization sequence completed.")
        if not HAS_DEPS:
            self.log("WARNING: Optional dependencies (shapely, pyproj, ezdxf) are missing.")
            self.log("Install them via: pip install -r requirements.txt")
            self.log("The pipeline will simulate shape export using mock geometry if run.")
            
    def log(self, text):
        self.log_widget.insert(tk.END, f"{text}\n")
        self.log_widget.see(tk.END)
        
    def run_pipeline(self):
        self.acquire_btn.config(state="disabled")
        self.log("\n=================== START PIPELINE ===================")
        
        address = self.address_entry.get().strip()
        try:
            radius = float(self.radius_entry.get())
            default_height = float(self.height_entry.get())
        except ValueError:
            self.log("ERROR: Radius and Height must be numeric values.")
            self.acquire_btn.config(state="normal")
            return
            
        self.log(f"SYS:GEOCODE // Querying BAN API for: '{address}'")
        
        # 1. Geocoding via French BAN API
        try:
            r = requests.get(f"https://api-adresse.data.gouv.fr/search/?q={requests.utils.quote(address)}&limit=1", timeout=10)
            if r.status_code != 200:
                self.log(f"BAN API Error: HTTP {r.status_code}")
                self.acquire_btn.config(state="normal")
                return
            
            data = r.json()
            if not data.get("features"):
                self.log("BAN API: No coordinates found for target address.")
                self.acquire_btn.config(state="normal")
                return
                
            feature = data["features"][0]
            lon, lat = feature["geometry"]["coordinates"]
            label = feature["properties"]["label"]
            self.log(f"BAN SUCCESS // Found: {label}")
            self.log(f"BAN COORDS  // Lon: {lon:.6f}, Lat: {lat:.6f} (WGS84)")
            
        except Exception as e:
            self.log(f"CONNECTION ERROR // BAN API: {e}")
            self.acquire_btn.config(state="normal")
            return
            
        # 2. Coordinate Transformation Setup
        center_x, center_y = lon, lat
        if HAS_DEPS:
            try:
                # Transform center to Lambert 93 (EPSG:2154)
                wgs84_to_l93 = Transformer.from_crs("EPSG:4326", "EPSG:2154", always_xy=True)
                center_x, center_y = wgs84_to_l93.transform(lon, lat)
                self.log(f"PROJ:EPSG2154 // Transformed to Lambert 93 (X: {center_x:.2f}, Y: {center_y:.2f})")
            except Exception as e:
                self.log(f"PROJ ERROR // EPSG:2154 conversion failed: {e}")
                
        # 3. Calculate Bounding Box in coordinates
        # Approximate degrees per meter for bounding box query
        deg_lat = radius / 111111.0
        deg_lon = radius / (111111.0 * math.cos(math.radians(lat)))
        
        south = lat - deg_lat
        north = lat + deg_lat
        west = lon - deg_lon
        east = lon + deg_lon
        
        self.log(f"SYS:OSM_QUERY // Requesting building footprints in bounding box...")
        self.log(f"SYS:BBOX // S:{south:.5f} W:{west:.5f} N:{north:.5f} E:{east:.5f}")
        
        # 4. Query Overpass API (OSM) for Buildings
        overpass_url = "https://overpass-api.de/api/interpreter"
        query = f"""
        [out:json][timeout:15];
        (
          way["building"]({south:.6f},{west:.6f},{north:.6f},{east:.6f});
          relation["building"]({south:.6f},{west:.6f},{north:.6f},{east:.6f});
        );
        out body;
        >;
        out skel qt;
        """
        
        try:
            r = requests.post(overpass_url, data={"data": query}, timeout=15)
            if r.status_code != 200:
                self.log(f"OSM Error: HTTP {r.status_code}")
                self.acquire_btn.config(state="normal")
                return
                
            osm_data = r.json()
            elements = osm_data.get("elements", [])
            ways = [e for e in elements if e["type"] == "way"]
            nodes = {{n["id"]: (n["lon"], n["lat"]) for n in elements if n["type"] == "node"}}
            
            self.log(f"OSM SUCCESS // Retreived {len(ways)} building geometries.")
            
        except Exception as e:
            self.log(f"CONNECTION ERROR // OSM Overpass: {e}")
            self.acquire_btn.config(state="normal")
            return
            
        # 5. Export to DXF
        out_filename = "site_context_output.dxf"
        self.log(f"SYS:DXF_EXPORT // Writing layers into '{out_filename}'...")
        
        if HAS_DEPS:
            try:
                doc = ezdxf.new("R2010")
                msp = doc.modelspace()
                
                # Setup transformation
                wgs84_to_l93 = Transformer.from_crs("EPSG:4326", "EPSG:2154", always_xy=True)
                
                processed_count = 0
                for way in ways:
                    way_nodes = way.get("nodes", [])
                    if len(way_nodes) < 3:
                        continue
                    
                    # Convert nodes to coordinates
                    poly_coords = []
                    valid_nodes = True
                    for node_id in way_nodes:
                        if node_id in nodes:
                            n_lon, n_lat = nodes[node_id]
                            # Convert to Lambert 93 and relative to center
                            lx, ly = wgs84_to_l93.transform(n_lon, n_lat)
                            rx = lx - center_x
                            ry = ly - center_y
                            poly_coords.append((rx, ry))
                        else:
                            valid_nodes = False
                            break
                            
                    if not valid_nodes or len(poly_coords) < 3:
                        continue
                        
                    # Extract building height if available, else default
                    tags = way.get("tags", {})
                    height_str = tags.get("height", tags.get("building:levels", ""))
                    try:
                        height = float(height_str) * 3.0 if "level" in height_str else float(height_str)
                    except ValueError:
                        height = default_height
                        
                    # Create 3D extrusion faces in DXF
                    # Ground Ring
                    for i in range(len(poly_coords) - 1):
                        p1 = poly_coords[i]
                        p2 = poly_coords[i+1]
                        
                        # Ground Vertices
                        g1 = (p1[0], p1[1], 0.0)
                        g2 = (p2[0], p2[1], 0.0)
                        
                        # Roof Vertices
                        r1 = (p1[0], p1[1], height)
                        r2 = (p2[0], p2[1], height)
                        
                        # Wall (3D Face)
                        msp.add_3dface([g1, g2, r2, r1], dxfattribs={"layer": "BUILDING_WALLS"})
                        
                    # Add roof face
                    roof_pts = [(p[0], p[1], height) for p in poly_coords]
                    if len(roof_pts) >= 3 and len(roof_pts) <= 4:
                        msp.add_3dface(roof_pts, dxfattribs={"layer": "BUILDING_ROOFS"})
                    elif len(roof_pts) > 4:
                        # Triangulate or add flat polygon layer
                        msp.add_lwpolyline([(p[0], p[1]) for p in poly_coords], dxfattribs={"layer": "BUILDING_ROOF_OUTLINES", "elevation": height})
                        
                    processed_count += 1
                    
                doc.saveas(out_filename)
                self.log(f"DXF SUCCESS // Exported {processed_count} building meshes to '{out_filename}'.")
                messagebox.showinfo("Export Successful", f"Site model exported successfully to:\n{os.path.abspath(out_filename)}")
                
            except Exception as e:
                self.log(f"DXF ERROR // Failed to build DXF output: {e}")
        else:
            # Simulated process if dependencies are missing
            self.log("SIMULATOR // Simulating 3D extrusion logic...")
            self.log("SIMULATOR // Constructing mock building meshes relative to Lambert 93 center...")
            self.log(f"SIMULATOR // Processed {len(ways)} building shapes.")
            
            # Create a mock DXF text output
            with open(out_filename, "w") as f:
                f.write(f"MOCK DXF FILE // 3D Extrusion Data // Center: {center_x}, {center_y}\n")
                f.write(f"Address: {label}\n")
                f.write(f"Total Buildings Processed: {len(ways)}\n")
            self.log(f"SIMULATOR SUCCESS // Mock site model written to '{out_filename}'.")
            messagebox.showinfo("Simulator Exported", f"Mock model generated successfully (dependencies missing) to:\n{os.path.abspath(out_filename)}")
            
        self.log("SYS:FINISH // Site acquisition pipeline completed successfully.")
        self.acquire_btn.config(state="normal")

if __name__ == "__main__":
    app = AECContextGeneratorApp()
    app.mainloop()