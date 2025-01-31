"""
multi-dimensional templates for datasets
"""
import numpy as np
import xarray as xr

# constants
##########################################
PVGIS_WEATHER_VAR_NAMES = [
    'temp_air',
    'relative_humidity',
    'ghi',
    'dni',
    'dhi',
    'IR(h)',
    'wind_speed',
    'wind_direction',
    'pressure'
]

PVGIS_META_VAR_NAMES = [
    'latitude',
    'longitude',
    'irradiance_time_offset',
    'altitude',
    'wind_height',
    'Source'
]

COMB_WEATHER_VAR_NAMES = [
    'temp_air',
    'relative_humidity',
    'ghi',
    'dni',
    'dhi',
    'IR(h)',
    'wind_speed',
    'wind_direction',
    'pressure'
]

COMB_META_VAR_NAMES = [
    'latitude',
    'longitude',
    'altitude',
    'wind_height',
    'Source'
]


# coordinates
##########################################
HOURLY_TMY = np.arange(
    np.datetime64('2022-01-01T00:00:00.000000000'),
    np.datetime64('2023-01-01T00:00:00.000000000'),
    np.timedelta64(1, 'h'),
    dtype="datetime64[ns]",
)

TMY_COORDINATES = {
    "time": HOURLY_TMY,
    "gid" : np.array([], dtype=int)
}

# helper functions
##########################################
def create_weather_data_vars(var_names):
    """
    Creates weather data variables template.
    """
    return {
        name: (("gid", "time"), np.empty((0, 8760)))
        for name in var_names
    }

def create_meta_data_vars(var_names):
    """
    Creates metadata variables template.
    """
    return {
        name: (
            ("gid",),
            np.empty((0,), dtype="<U5") if name == "Source" else
            np.empty((0,), dtype="int64") if name == "wind_height" else
            np.empty((0,), dtype="float64")
        )
        for name in var_names
    }

# 4. Dataset Templates
# ---------------------------------------------------------------------
# PVGIS Template
_pvgis_weather_data_vars = create_weather_data_vars(PVGIS_WEATHER_VAR_NAMES)
_pvgis_meta_data_vars = create_meta_data_vars(PVGIS_META_VAR_NAMES)

PVGIS_TMY_DATAVARS = {**_pvgis_weather_data_vars, **_pvgis_meta_data_vars}

PVGIS_TMY_TEMPLATE = xr.Dataset(
    data_vars=PVGIS_TMY_DATAVARS,
    coords=TMY_COORDINATES,
)

# COMB Template
_comb_weather_data_vars = create_weather_data_vars(COMB_WEATHER_VAR_NAMES)
_comb_meta_data_vars = create_meta_data_vars(COMB_META_VAR_NAMES)

COMB_TMY_DATAVARS = {**_comb_weather_data_vars, **_comb_meta_data_vars}

COMB_TMY_TEMPLATE = xr.Dataset(
    data_vars=COMB_TMY_DATAVARS,
    coords=TMY_COORDINATES,
)


# _pvgis_weather_data_vars = {
#     name : (("gid", "time"), np.empty((0, 8760))) for name in PVGIS_WEATHER_VAR_NAMES
# }
# _pvgis_meta_data_vars = {
#     name: (
#             ("gid",), 
#             np.empty((0,), dtype="<U5") if name == "Source" else 
#             np.empty((0,), dtype="int64") if name == "altitude" else 
#             np.empty((0,))
#         )
#     for name in PVGIS_META_VAR_NAMES
# }

# PVGIS_TMY_DATAVARS = _pvgis_weather_data_vars | _pvgis_meta_data_vars

# PVGIS_TMY_TEMPLATE = xr.Dataset(
#     data_vars=PVGIS_TMY_DATAVARS,
#     coords=TMY_COORDINATES
# )



# _comb_weather_data_vars = {
#     name : (("gid", "time"), np.empty((0, 8760))) for name in COMB_WEATHER_VAR_NAMES
# }
# _comb_meta_data_vars = {
#     name: (
#             ("gid",), 
#             np.empty((0,), dtype="<U5") if name == "Source" else 
#             np.empty((0,), dtype="int64") if name == "altitude" else 
#             np.empty((0,))
#         )
#     for name in COMB_META_VAR_NAMES
# }

# COMB_TMY_DATAVARS = _comb_weather_data_vars | _comb_meta_data_vars

# COMB_TMY_TEMPLATE = xr.Dataset(
#     data_vars=COMB_TMY_DATAVARS,
#     coords=TMY_COORDINATES
# )