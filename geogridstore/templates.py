"""
multi-dimensional templates for datasets
"""
import numpy as np
import xarray as xr

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

PVGIS_HOURLY_TMY = np.arange(
    np.datetime64('2022-01-01T00:00:00.000000000'),
    np.datetime64('2023-01-01T00:00:00.000000000'),
    np.timedelta64(1, 'h'),
    dtype="datetime64[ns]",
)

PVGIS_TMY_COORDINATES = {
    "time": PVGIS_HOURLY_TMY,
    "gid" : np.array([])
}

_pvgis_weather_data_vars = {
    name : (("gid", "time"), np.empty((0, 8760))) for name in PVGIS_WEATHER_VAR_NAMES
}
_pvgis_meta_data_vars = {
    name: (
            ("gid",), 
            np.empty((0,), dtype="<U5") if name == "Source" else 
            np.empty((0,), dtype="int64") if name == "altitude" else 
            np.empty((0,))
        )
    for name in PVGIS_META_VAR_NAMES
}

PVGIS_TMY_DATAVARS = _pvgis_weather_data_vars | _pvgis_meta_data_vars

PVGIS_TMY_TEMPLATE = xr.Dataset(
    data_vars=PVGIS_TMY_DATAVARS,
    coords=PVGIS_TMY_COORDINATES
)
