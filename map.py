from bokeh.plotting import figure, output_file, show
from bokeh.tile_providers import ESRI_IMAGERY, get_provider
from pyproj import Transformer
import pandas as pd
import utm

reference_antenna = "2a"
data = pd.read_csv("./output_ata_datum.csv")


output_file("docs/index.html")

tile_provider = get_provider(ESRI_IMAGERY)

p = figure(x_axis_type="mercator", y_axis_type="mercator")

p.add_tile(tile_provider)

TRAN_4326_TO_3857 = Transformer.from_crs("EPSG:4326", "EPSG:3857")

ref_data = data.loc[data['antenna'] == reference_antenna]
ref_lat = float(ref_data["lat_wgs"])
ref_lon = float(ref_data["lon_wgs"])
ref_alt = float(ref_data["alt_wgs"])
ref_x, ref_y, a, b = utm.from_latlon(ref_lat, ref_lon)

for index, row in data.iterrows():
    x = row["e"] + ref_x
    y = row["n"] + ref_y
    z = row["u"] + ref_alt

    lat, lon = utm.to_latlon(x, y, a, b)

    map_x, map_y = TRAN_4326_TO_3857.transform(lat, lon)
    ll_x, ll_y = TRAN_4326_TO_3857.transform(row["lat_wgs"], row["lon_wgs"])

    p.circle(ll_x, ll_y, color="red")
    p.circle(map_x, map_y, color="yellow", size=2.0)

for index, row in data.iterrows():
    x = row["e_legacy"] + ref_x
    y = row["n_legacy"] + ref_y
    z = row["u_legacy"] + ref_alt
    lat, lon = utm.to_latlon(x, y, a, b)
    map_x, map_y = TRAN_4326_TO_3857.transform(lat, lon)
    p.circle(map_x, map_y, color="blue", size=2.0)

show(p)
