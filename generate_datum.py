import utm
import pandas as pd
from pyproj import Transformer

reference_antenna = "2a"
nad_altitude_skew = 23.761
nad_data = pd.read_csv("./ata_coords_nad83.txt")
enu_data = pd.read_csv("./ata_old_enu.txt")

#
# Configure DataFrame.
#

data = pd.DataFrame(columns=[
    "antenna",                              # Antenna Number
    "lat_wgs", "lon_wgs", "alt_wgs",        # WGS84 Coordinates
    "lat_nad", "lon_nad", "alt_nad",        # NAD83 Coordinates
    "x", "y", "z",                          # ECEF Coodinates (WGS84/gecent)
    "e", "n", "u",                          # New ENU Coordinates (2A as ref.)
    "e_legacy", "n_legacy", "u_legacy",     # Legacy ENU Coordinates (2A as ref.)
])

for index, row in nad_data.iterrows():
    df = pd.DataFrame({
        "antenna": row["antenna"],
        "lat_nad": row["latitude"],
        "lon_nad": row["longitude"],
        "alt_nad": row["altitude"],
    }, index=[index])
    data = pd.concat([data, df])

#
# Convert NAD83 coordinates to WGS84.
#

# NAD 1983 to WGS84/ITRF00
# method: position vector
# Source: https://gis.stackexchange.com/questions/112198/proj4-postgis-transformations-between-wgs84-and-nad83-transformations-in-alask/112202#112202
from_nad_to_wgs = Transformer.from_crs(
    {"proj": 'latlong', "ellps": 'GRS80', "datum": 'NAD83',
        'towgs84': '-0.9956,1.9013,0.5215,0.025915,0.009426,0.0011599,-0.00062'},
    {"proj": 'latlong', "ellps": 'WGS84', "datum": 'WGS84'}
)

for index, row in nad_data.iterrows():
    nad_lat = row["latitude"]
    nad_lon = row["longitude"]
    nad_alt = row["altitude"] + nad_altitude_skew

    wgs_lon, wgs_lat, wgs_alt = from_nad_to_wgs.transform(
                                    nad_lon, nad_lat, nad_alt, radians=False)

    data.loc[index]["lon_wgs"] = wgs_lon
    data.loc[index]["lat_wgs"] = wgs_lat
    data.loc[index]["alt_wgs"] = wgs_alt

#
# Convert WGS84 coordinates to ECEF.
#

from_wgs_to_ecef = Transformer.from_crs(
    {"proj": 'latlong', "ellps": 'WGS84', "datum": 'WGS84'},
    {"proj": 'geocent', "ellps": 'WGS84', "datum": 'WGS84'}
)

for index, row in data.iterrows():
    wgs_lat = row["lat_wgs"]
    wgs_lon = row["lon_wgs"]
    wgs_alt = row["alt_wgs"]

    ecef_x, ecef_y, ecef_z = from_wgs_to_ecef.transform(
                                wgs_lon, wgs_lat, wgs_alt, radians=False)

    data.loc[index]["x"] = ecef_x
    data.loc[index]["y"] = ecef_y
    data.loc[index]["z"] = ecef_z

#
# Convert WGS84 coordinates to ENU.
# Here I use UTM to represent actual surface meters.
#

ref_data = data.loc[data['antenna'] == reference_antenna]
ref_lat = float(ref_data["lat_wgs"])
ref_lon = float(ref_data["lon_wgs"])
ref_alt = float(ref_data["alt_wgs"])
ref_x, ref_y, _, _ = utm.from_latlon(ref_lat, ref_lon)

for index, row in data.iterrows():
    wgs_lat = row["lat_wgs"]
    wgs_lon = row["lon_wgs"]
    wgs_alt = row["alt_wgs"]
    ant_x, ant_y, _, _ = utm.from_latlon(wgs_lat, wgs_lon)

    e = ant_x - ref_x
    n = ant_y - ref_y
    u = wgs_alt - ref_alt

    data.loc[index]["e"] = e
    data.loc[index]["n"] = n
    data.loc[index]["u"] = u

#
# Convert WGS84 coordinates to legacy ENU.
# Here the old ENU reference point is being translated to antenna 2A.
#

ref_data = enu_data.loc[enu_data['antenna'] == reference_antenna]
ref_e = float(ref_data["e"])
ref_n = float(ref_data["n"])
ref_u = float(ref_data["u"])

for index, row in enu_data.iterrows():
    ant_e = row["e"]
    ant_n = row["n"]
    ant_u = row["u"]

    e = ant_e - ref_e
    n = ant_n - ref_n
    u = ant_u - ref_u

    data.loc[index]["e_legacy"] = e
    data.loc[index]["n_legacy"] = n
    data.loc[index]["u_legacy"] = u

print(data)

data.to_csv("output_ata_datum.csv", index=False)
