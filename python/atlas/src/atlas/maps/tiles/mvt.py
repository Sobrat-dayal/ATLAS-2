"""Mapbox Vector Tile (MVT) Specification 2.1 Binary Encoder.

Encodes spatial features and properties directly into standard Google Protocol Buffer MVT bytes.
Zero external C-library dependency, cross-platform and fully reproducible.
"""

from __future__ import annotations

import struct
from typing import Any, Dict, List, Tuple

from atlas.maps.domain import GeoFeature, GeometryType
from atlas.maps.spatial.projections import epsg4326_to_epsg3857
from atlas.maps.tiles.coordinates import tile_bounds_epsg3857

TILE_EXTENT = 4096


def _encode_varint(value: int) -> bytes:
    """Encodes an integer into standard protobuf varint bytes."""
    bits = value & 0x7FFFFFFFFFFFFFFF
    out = bytearray()
    while True:
        b = bits & 0x7F
        bits >>= 7
        if bits:
            out.append(b | 0x80)
        else:
            out.append(b)
            break
    return bytes(out)


def _encode_zigzag(n: int) -> int:
    """Zigzag encoding for signed integers."""
    return (n << 1) ^ (n >> 31)


def _encode_tag_and_wire(field_number: int, wire_type: int) -> bytes:
    return _encode_varint((field_number << 3) | wire_type)


def _encode_length_delimited(field_number: int, data: bytes) -> bytes:
    return _encode_tag_and_wire(field_number, 2) + _encode_varint(len(data)) + data


def _encode_value(val: Any) -> bytes:
    """Encodes a property Value message."""
    if isinstance(val, str):
        utf8 = val.encode("utf-8")
        return _encode_length_delimited(1, utf8)
    elif isinstance(val, bool):
        return _encode_tag_and_wire(7, 0) + (b"\x01" if val else b"\x00")
    elif isinstance(val, int):
        if val >= 0:
            return _encode_tag_and_wire(5, 0) + _encode_varint(val)
        else:
            return _encode_tag_and_wire(6, 0) + _encode_varint(_encode_zigzag(val))
    elif isinstance(val, float):
        return _encode_tag_and_wire(3, 1) + struct.pack("<d", val)
    else:
        utf8 = str(val).encode("utf-8")
        return _encode_length_delimited(1, utf8)


def _project_point_to_tile(
    lon: float, lat: float, min_x: float, min_y: float, max_x: float, max_y: float
) -> Tuple[int, int]:
    """Projects WGS84 (lon, lat) to tile pixel coordinate [0..4096]."""
    x_m, y_m = epsg4326_to_epsg3857(lon, lat)
    span_x = max_x - min_x
    span_y = max_y - min_y
    if span_x <= 0:
        span_x = 1.0
    if span_y <= 0:
        span_y = 1.0

    px = int(round(((x_m - min_x) / span_x) * TILE_EXTENT))
    # Y is inverted in MVT: 0 at top (max_y), 4096 at bottom (min_y)
    py = int(round(((max_y - y_m) / span_y) * TILE_EXTENT))
    return px, py


def _encode_point_geometry(px: int, py: int) -> bytes:
    """Encodes a single Point geometry."""
    # Command: MoveTo(1), count=1 -> (1 & 0x7) | (1 << 3) = 9
    cmd = 9
    dx = _encode_zigzag(px)
    dy = _encode_zigzag(py)
    geom_bytes = _encode_varint(cmd) + _encode_varint(dx) + _encode_varint(dy)
    return geom_bytes


def _encode_linestring_geometry(points: List[Tuple[int, int]]) -> bytes:
    """Encodes a LineString geometry."""
    if len(points) < 2:
        return b""

    out = bytearray()
    # MoveTo point 0
    out.extend(_encode_varint((1 & 0x7) | (1 << 3)))
    out.extend(_encode_varint(_encode_zigzag(points[0][0])))
    out.extend(_encode_varint(_encode_zigzag(points[0][1])))

    # LineTo remaining points
    curr_x, curr_y = points[0]
    line_count = len(points) - 1
    out.extend(_encode_varint((2 & 0x7) | (line_count << 3)))
    for pt in points[1:]:
        dx = pt[0] - curr_x
        dy = pt[1] - curr_y
        out.extend(_encode_varint(_encode_zigzag(dx)))
        out.extend(_encode_varint(_encode_zigzag(dy)))
        curr_x, curr_y = pt

    return bytes(out)


def _encode_polygon_geometry(rings: List[List[Tuple[int, int]]]) -> bytes:
    """Encodes a Polygon geometry."""
    out = bytearray()
    curr_x, curr_y = 0, 0

    for ring in rings:
        if len(ring) < 4:
            continue
        # MoveTo first point
        dx = ring[0][0] - curr_x
        dy = ring[0][1] - curr_y
        out.extend(_encode_varint((1 & 0x7) | (1 << 3)))
        out.extend(_encode_varint(_encode_zigzag(dx)))
        out.extend(_encode_varint(_encode_zigzag(dy)))
        curr_x, curr_y = ring[0]

        # LineTo vertices except closing point
        line_count = len(ring) - 2
        out.extend(_encode_varint((2 & 0x7) | (line_count << 3)))
        for pt in ring[1:-1]:
            dx = pt[0] - curr_x
            dy = pt[1] - curr_y
            out.extend(_encode_varint(_encode_zigzag(dx)))
            out.extend(_encode_varint(_encode_zigzag(dy)))
            curr_x, curr_y = pt

        # ClosePath command: id=7, count=1 -> (7 & 0x7) | (1 << 3) = 15
        out.extend(_encode_varint(15))

    return bytes(out)


def encode_vector_tile_layer(
    layer_name: str,
    features: List[GeoFeature],
    z: int,
    x: int,
    y: int,
) -> bytes:
    """Encodes a single MVT Layer with given features into binary bytes."""
    min_x, min_y, max_x, max_y = tile_bounds_epsg3857(z, x, y)

    keys: List[str] = []
    key_map: Dict[str, int] = {}
    values: List[Any] = []
    val_map: Dict[str, int] = {}

    def get_key_index(k: str) -> int:
        if k not in key_map:
            key_map[k] = len(keys)
            keys.append(k)
        return key_map[k]

    def get_val_index(v: Any) -> int:
        str_repr = f"{type(v).__name__}:{v}"
        if str_repr not in val_map:
            val_map[str_repr] = len(values)
            values.append(v)
        return val_map[str_repr]

    encoded_features: List[bytes] = []

    for idx, feat in enumerate(features, start=1):
        # 1. Properties -> tags
        tags = bytearray()
        props = {
            **feat.properties,
            "feature_id": feat.feature_id,
            "label": feat.label,
            "source_reference": feat.source_reference,
            "data_quality": feat.data_quality.value,
        }
        for pk, pv in props.items():
            if pv is not None:
                ki = get_key_index(str(pk))
                vi = get_val_index(pv)
                tags.extend(_encode_varint(ki))
                tags.extend(_encode_varint(vi))

        # 2. Geometry
        geom_type_code = 0
        geom_bytes = b""

        if feat.geometry_type == GeometryType.POINT:
            geom_type_code = 1
            px, py = _project_point_to_tile(
                feat.coordinates[0], feat.coordinates[1], min_x, min_y, max_x, max_y
            )
            geom_bytes = _encode_point_geometry(px, py)

        elif feat.geometry_type == GeometryType.LINESTRING:
            geom_type_code = 2
            pts = [
                _project_point_to_tile(c[0], c[1], min_x, min_y, max_x, max_y)
                for c in feat.coordinates
            ]
            geom_bytes = _encode_linestring_geometry(pts)

        elif feat.geometry_type == GeometryType.POLYGON:
            geom_type_code = 3
            rings = [
                [_project_point_to_tile(c[0], c[1], min_x, min_y, max_x, max_y) for c in ring]
                for ring in feat.coordinates
            ]
            geom_bytes = _encode_polygon_geometry(rings)

        if not geom_bytes:
            continue

        # Feature message fields:
        # id = 1 (uint64)
        # tags = 2 (packed varints)
        # type = 3 (enum)
        # geometry = 4 (packed varints)
        feat_msg = bytearray()
        feat_msg.extend(_encode_tag_and_wire(1, 0) + _encode_varint(idx))
        if tags:
            feat_msg.extend(_encode_length_delimited(2, bytes(tags)))
        feat_msg.extend(_encode_tag_and_wire(3, 0) + _encode_varint(geom_type_code))
        feat_msg.extend(_encode_length_delimited(4, geom_bytes))

        encoded_features.append(bytes(feat_msg))

    # Layer message fields:
    # 15: version (default 2)
    # 1: name (string)
    # 2: features (repeated Feature)
    # 3: keys (repeated string)
    # 4: values (repeated Value)
    # 5: extent (uint32, default 4096)
    layer_msg = bytearray()
    layer_msg.extend(_encode_tag_and_wire(15, 0) + _encode_varint(2))  # version=2
    layer_msg.extend(_encode_length_delimited(1, layer_name.encode("utf-8")))

    for ef in encoded_features:
        layer_msg.extend(_encode_length_delimited(2, ef))

    for k in keys:
        layer_msg.extend(_encode_length_delimited(3, k.encode("utf-8")))

    for v in values:
        val_bytes = _encode_value(v)
        layer_msg.extend(_encode_length_delimited(4, val_bytes))

    layer_msg.extend(_encode_tag_and_wire(5, 0) + _encode_varint(TILE_EXTENT))

    # Outer Tile message: field 3 = Layer (repeated)
    tile_msg = _encode_length_delimited(3, bytes(layer_msg))
    return bytes(tile_msg)
