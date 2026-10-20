"""Deterministic WGS84 geodetic <-> ECEF conversions for PREP/REVIEW inspection.

Do not use Cartesian (straight-line) distance as an authoritative rally distance.
Height must be explicitly identified as WGS84 ellipsoidal metres; no implicit
geoid/orthometric conversion or 'missing height = 0m' fallback is permitted.
"""
from __future__ import annotations
from dataclasses import dataclass
from math import atan2, cos, degrees, hypot, isfinite, radians, sin, sqrt

WGS84_A_M = 6378137.0
WGS84_F = 1.0 / 298.257223563
WGS84_B_M = WGS84_A_M * (1.0 - WGS84_F)
WGS84_E2 = WGS84_F * (2.0 - WGS84_F)

@dataclass(frozen=True)
class GeodeticWGS84:
    longitude_deg: float
    latitude_deg: float
    height_ellipsoid_m: float
    datum: str = 'WGS84_ELLIPSOID'

    def __post_init__(self):
        if self.datum != 'WGS84_ELLIPSOID':
            raise ValueError('Explicit WGS84 ellipsoidal height required; transform other vertical datums beforehand')
        for x in (self.longitude_deg, self.latitude_deg, self.height_ellipsoid_m):
            if not isinstance(x, (int, float)) or not isfinite(x):
                raise ValueError('All coordinates and ellipsoidal height must be finite numbers')
        if not -180 <= self.longitude_deg <= 180 or not -90 <= self.latitude_deg <= 90:
            raise ValueError('Invalid geographic coordinate range')

@dataclass(frozen=True)
class ECEF:
    x_m: float
    y_m: float
    z_m: float

    def __post_init__(self):
        if not all(isfinite(v) for v in (self.x_m, self.y_m, self.z_m)):
            raise ValueError('ECEF coordinates must be finite numbers')


def wgs84_to_ecef(p: GeodeticWGS84) -> ECEF:
    lon = radians(p.longitude_deg)
    lat = radians(p.latitude_deg)
    sin_lat = sin(lat)
    N = WGS84_A_M / sqrt(1.0 - WGS84_E2 * sin_lat * sin_lat)
    x = (N + p.height_ellipsoid_m) * cos(lat) * cos(lon)
    y = (N + p.height_ellipsoid_m) * cos(lat) * sin(lon)
    z = (N * (1.0 - WGS84_E2) + p.height_ellipsoid_m) * sin_lat
    return ECEF(x, y, z)


def ecef_to_wgs84(p: ECEF) -> GeodeticWGS84:
    r = hypot(p.x_m, p.y_m)
    if r == 0 and p.z_m == 0:
        raise ValueError('Earth center cannot be represented as a unique geodetic point')
    if r < 1e-10:
        return GeodeticWGS84(0.0, 90.0 if p.z_m >= 0 else -90.0, abs(p.z_m) - WGS84_B_M)
    lon = atan2(p.y_m, p.x_m)
    lat = atan2(p.z_m, r * (1 - WGS84_E2))
    # Iterative latitude solution; converges quickly for terrestrial heights.
    for _ in range(20):
        sl = sin(lat)
        N = WGS84_A_M / sqrt(1.0 - WGS84_E2 * sl * sl)
        new_lat = atan2(p.z_m + WGS84_E2 * N * sl, r)
        if abs(new_lat - lat) < 1e-14:
            lat = new_lat
            break
        lat = new_lat
    sl = sin(lat)
    N = WGS84_A_M / sqrt(1.0 - WGS84_E2 * sl * sl)
    cl = cos(lat)
    height = r / cl - N if abs(cl) > 1e-8 else abs(p.z_m) - WGS84_B_M
    return GeodeticWGS84(degrees(lon), degrees(lat), height)


def geopoint_e7_to_wgs84(*, lat_e7: int, lon_e7: int, height_ellipsoid_m: float | None) -> GeodeticWGS84:
    if type(lat_e7) is not int or type(lon_e7) is not int:
        raise TypeError('GeoPointE7 requires integer lat_e7 and lon_e7')
    if not (-900000000 <= lat_e7 <= 900000000) or not (-1800000000 <= lon_e7 <= 1800000000):
        raise ValueError('GeoPointE7 out of WGS84 range')
    if height_ellipsoid_m is None:
        raise ValueError('Unknown altitude cannot silently be interpreted as 0 metres')
    return GeodeticWGS84(lon_e7/1e7, lat_e7/1e7, height_ellipsoid_m)


def validate_height_observation(*, height_m: float | None, vertical_datum: str, provider_id: str, source_sha256: str, resolution_m: float | None) -> dict:
    """Check metadata for an analytic terrain observation; never mark as route authority."""
    import re
    if not provider_id or not re.fullmatch(r'[0-9a-fA-F]{64}', source_sha256):
        raise ValueError('Provider id and source SHA-256 are required')
    if vertical_datum not in {'WGS84_ELLIPSOID','EGM96','EGM2008','OTHER_DECLARED','UNKNOWN'}:
        raise ValueError('Invalid vertical datum')
    if height_m is not None and (not isinstance(height_m,(int,float)) or not isfinite(height_m)):
        raise ValueError('Invalid height sample')
    if resolution_m is not None and (not isinstance(resolution_m,(int,float)) or not isfinite(resolution_m) or resolution_m<=0):
        raise ValueError('Invalid terrain resolution')
    return {'sample_status':'NO_DATA' if height_m is None else 'SAMPLED', 'height_m':height_m,
            'vertical_datum':vertical_datum, 'provider_id':provider_id,
            'source_sha256':source_sha256.lower(), 'resolution_m':resolution_m,
            'route_authority':False, 'eligible_for_authority_promotion':False}
