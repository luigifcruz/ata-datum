# ata-datum

This repository contains the scripts to derivate the [ENU](https://en.wikipedia.org/wiki/Local_tangent_plane_coordinates) and [ECEF](https://en.wikipedia.org/wiki/Earth-centered,_Earth-fixed_coordinate_system) coordinates from the longitude, latitude, and altitude values encoded in the NAD83 coordinates. These coordinates can be verified with the ESRI satellite imagery in this [website](https://luigifcruz.github.io/ata-datum/). The pre-computed coordinates are provided by the [CSV file](https://github.com/luigifcruz/ata-datum/blob/main/output_ata_datum.csv) containing the ENU, ECEF, WGS84, and NAD83 values derived from the original [NAD83 file](https://github.com/luigifcruz/ata-datum/blob/main/ata_coords_nad83.txt) coordinates. The previously used, and slightly wrong, legacy ENU coordinates are also present in the CSV file for completeness. Both ENU coordinates have antenna 2A as the reference point. Keep in mind that these values might change in the future. Therefore, it's a good practice not to hard-code the pre-computed coordinates values in your software.

The process starts with the latitude, longitude, and altitude in NAD83 (ellipsoid GRS80) coordinates of each antenna. These values are [converted to the WGS84](https://github.com/luigifcruz/ata-datum/blob/ed8ccdbd7df7ba728d9aafcae32edfa254e42afe/generate_datum.py#L32-L55) coordinate system using the position vector approximation [described here](https://gis.stackexchange.com/questions/112198/proj4-postgis-transformations-between-wgs84-and-nad83-transformations-in-alask/112202#112202). This method visually appears to perform better than the coordinate frame approximation. The obtained WGS84 coordinates are then [transformed into ECEF](https://github.com/luigifcruz/ata-datum/blob/ed8ccdbd7df7ba728d9aafcae32edfa254e42afe/generate_datum.py#L57-L76) using PyProj. Finally, the ENU position of each antenna relative to the position of antenna 2A is [obtained](https://github.com/luigifcruz/ata-datum/blob/ed8ccdbd7df7ba728d9aafcae32edfa254e42afe/generate_datum.py#L78-L101) by converting the WGS84 values into meters using the optimal [Universal Transverse Mercator](http://wiki.gis.com/wiki/index.php/Universal_Transverse_Mercator) grid for the area. The UTM value of the reference point (antenna 2A) is then subtracted from the UTM value of each antenna.

The columns present in the [pre-computed CSV-file](https://github.com/luigifcruz/ata-datum/blob/main/output_ata_datum.csv) are the following:
- `antenna`: Antenna designation. It starts with a number and ends with a letter. The map below illustrates the positions.
- `lat_wgs`: Point latitude in WGS84.
- `lon_wgs`: Point longitude in WGS84.
- `alt_wgs`: Point altitude in WGS84.
- `lat_nad`: Point latitude in NAD83 (ellipsoid GRS80).
- `lon_nad`: Point longitude in NAD83 (ellipsoid GRS80).
- `alt_nad`: Point altitude in NAD83 (ellipsoid GRS80).
- `x`: The X-axis of the point in ECEF.
- `y`: The Y-axis of the point in ECEF.
- `z`: The Z-axis of the point in ECEF.
- `e`: Point east coordinate in ENU in reference to antenna 2A.
- `n`: Point north coordinate in ENU in reference to antenna 2A.
- `u`: Point up coordinate in ENU in reference to antenna 2A.
- `e_legacy`: Legacy point east coordinate in ENU in reference to antenna 2A (inaccurate).
- `n_legacy`: Legacy point north coordinate in ENU in reference to antenna 2A (inaccurate).
- `u_legacy`: Legacy points up coordinate in ENU in reference to antenna 2A (inaccurate).

![](https://github.com/luigifcruz/ata-datum/raw/main/site_map_feeds.jpg)

## Dependencies

- Python 3.6+
- [Pandas](https://pandas.pydata.org/)
- [PyProj](https://pyproj4.github.io/pyproj/stable/)
- [utm](https://github.com/Turbo87/utm)
