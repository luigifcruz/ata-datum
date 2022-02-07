from bokeh.plotting import figure, output_file, show
from bokeh.tile_providers import ESRI_IMAGERY, get_provider
from pyproj import Transformer
import pandas as pd
import utm
import math
from bokeh.plotting import figure, show, gridplot
from bokeh.models import LinearColorMapper, BasicTicker, ColorBar, ColumnDataSource
from bokeh.transform import transform

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

diff = pd.DataFrame(
    index=["1c", "1g", "1h", "1k", "1e", "2a", "2b", "2c", "2e", "2h", "2j", "2k", "2l", "2m", "3c", "3d", "3l", "4j", "5b", "4g"],
    columns=["1c", "1g", "1h", "1k", "1e", "2a", "2b", "2c", "2e", "2h", "2j", "2k", "2l", "2m", "3c", "3d", "3l", "4j", "5b", "4g"],
)
diff.index.name = 'Antenna_A'
diff.columns.name = 'Antenna_B'

print(data)

for ri, _ in diff.iterrows():
    for ci, _ in diff.iteritems():
        nax = data.loc[data["antenna"] == ri]["e"].values[0]
        nay = data.loc[data["antenna"] == ri]["n"].values[0]
        naz = data.loc[data["antenna"] == ri]["u"].values[0]

        nbx = data.loc[data["antenna"] == ci]["e"].values[0]
        nby = data.loc[data["antenna"] == ci]["n"].values[0]
        nbz = data.loc[data["antenna"] == ci]["u"].values[0]

        ndX = nax - nbx
        ndY = nay - nby
        ndZ = naz - nbz

        lax = data.loc[data["antenna"] == ri]["e_legacy"].values[0]
        lay = data.loc[data["antenna"] == ri]["n_legacy"].values[0]
        laz = data.loc[data["antenna"] == ri]["u_legacy"].values[0]

        lbx = data.loc[data["antenna"] == ci]["e_legacy"].values[0]
        lby = data.loc[data["antenna"] == ci]["n_legacy"].values[0]
        lbz = data.loc[data["antenna"] == ci]["u_legacy"].values[0]

        ldX = lax - lbx
        ldY = lay - lby
        ldZ = laz - lbz

        dX = ldX - ndX
        dY = ldY - ndY
        dZ = ldZ - ndZ

        diff.loc[ri][ci] = math.sqrt(dX**2 + dY**2 + dZ**2)

print(diff)

diff = diff.stack().rename("value").reset_index()

mapper = LinearColorMapper(
    palette="Spectral11", low=diff.value.min(), high=diff.value.max())

d = figure(
    title="ENU Absolute Difference (Original vs New)",
    x_range=list(diff.Antenna_A.drop_duplicates()),
    y_range=list(diff.Antenna_B.drop_duplicates()),
    toolbar_location=None,
    tools="",
    x_axis_location="above")

d.rect(
    x="Antenna_A",
    y="Antenna_B",
    width=1,
    height=1,
    source=ColumnDataSource(diff),
    line_color=None,
    fill_color=transform('value', mapper))

color_bar = ColorBar(color_mapper=mapper, title="Meters")

d.add_layout(color_bar, 'right')

plots = gridplot([
    [p, d],
])
show(plots)
