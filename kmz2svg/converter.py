# coding: utf-8
'''
Module to handle the conversion from a kmz to svg
'''
from dataclasses import dataclass
from typing import IO, List, Tuple
from zipfile import ZipFile

import utm
from lxml import etree
from pykml import parser

from .utils import mymax, mymin

placemark_tag = '{http://www.opengis.net/kml/2.2}Placemark'
line_string_tag = '{http://www.opengis.net/kml/2.2}LineString'


@dataclass
class PathObject:
    name: str
    coordinates: List[Tuple[int, int]]


def convert(kmz: str, svg: str):
    '''
    Handles the conversion process.

    1) The main KML file is extracted from the KMZ archive
    2) Each Placemark in the KML file is converted to a SVG path
    3) Each path is written in the output SVG file
    '''
    doc = load_kmz(kmz)
    placemarks = list(doc.iter(tag=placemark_tag))
    svg_paths, viewbox = convert_placemarks(placemarks)
    write_svg(svg, svg_paths, viewbox)


def get_single_child(element: etree._Element, tag: str) -> etree._Element:
    children = list(element.iter(tag=tag))
    if len(children) > 1:
        raise ValueError(
            "Unexpected multiple children with tag '%s' in single %s" %
            (tag, element.tag))
    elif len(children) == 0:
        raise ValueError("No child with tag '%s' found in %s" %
                         (tag, element.tag))
    return children[0]


def convert_placemarks(placemarks: List[etree._Element]):
    paths: List[etree._Element] = list()

    path_objects: List[PathObject] = list()
    max_north = min_north = max_east = min_east = None
    for placemark in placemarks:
        name = placemark.name.text
        line_string = placemark.LineString
        raw_coordinates: str = line_string.coordinates.text.strip().split()
        latlon_coordinates = [(float(coord.split(',')[0]), float(coord.split(',')[1]))
                              for coord in raw_coordinates]

        utm_coordinates: List[Tuple[int, int]] = list()
        for lon, lat in latlon_coordinates:
            e, n = utm.from_latlon(lat, lon)[:2]
            max_north = mymax(n, max_north)
            max_east = mymax(e, max_east)
            min_north = mymin(n, min_north)
            min_east = mymin(e, max_east)
            utm_coordinates.append((e, n))

        path_objects.append(PathObject(name, utm_coordinates))

    mean_north = (max_north + min_north) / 2
    mean_east = (max_east + min_east) / 2

    for path_object in path_objects:
        data = [("%f,%f" % (e-mean_east, -n+mean_north)) for (e, n) in path_object.coordinates]
        data_string = "M %s L %s" % (data[0], ' '.join(data[1:]))
        path = etree.Element('path',
                             style='fill:none;stroke:#000000;stroke-width:1px',
                             id=path_object.name,
                             d=data_string.encode('utf-8'))
        paths.append(path)

    viewbox = "%.0f %.0f %.0f %.0f" % (min_east, -max_north, max_east, -min_north)
    return paths, viewbox


def load_kmz(kmz: str):
    with ZipFile(kmz, 'r') as kmzfh:
        with kmzfh.open('doc.kml') as docfh:
            return parser.parse(docfh)


def write_svg(svg: str, svg_paths, viewbox: str) -> None:
    with open(svg, 'wb') as svgfh:
        root = etree.Element('svg',
                             xmlns="http://www.w3.org/2000/svg",
                             version="1.1",
                             viewbox=viewbox)
        for path in svg_paths:
            root.append(path)

        svgfh.write(
            etree.tostring(root,
                           xml_declaration=True,
                           encoding='UTF-8',
                           pretty_print=True))
