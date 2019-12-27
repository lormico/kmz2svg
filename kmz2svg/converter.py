# coding: utf-8
'''
Module to handle the conversion from a kmz to svg
'''
from lxml import etree
from typing import IO, List
from zipfile import ZipFile

from pykml import parser

placemark_tag = '{http://www.opengis.net/kml/2.2}Placemark'
line_string_tag = '{http://www.opengis.net/kml/2.2}LineString'


def convert(kmz: str, svg: str):
    '''
    Handles the conversion process.

    1) The main KML file is extracted from the KMZ archive
    2) Each Placemark in the KML file is converted to a SVG path
    3) Each path is written in the output SVG file
    '''
    doc = load_kmz(kmz)
    placemarks = list(doc.iter(tag=placemark_tag))
    svg_paths = [convert_placemark(placemark) for placemark in placemarks]
    write_svg(svg, svg_paths)


def get_single_child(element: etree._Element, tag: str) -> etree._Element:
    children = list(element.iter(tag=tag))
    if len(children) > 1:
        raise ValueError("Unexpected multiple children with tag '%s' in single %s" % (tag, element.tag))
    elif len(children) == 0:
        raise ValueError("No child with tag '%s' found in %s" % (tag, element.tag))
    return children[0]

def convert_placemark(placemark: etree._Element) -> etree._Element:
    line_string = get_single_child(placemark, line_string_tag)
    name = get_single_child(placemark, 'name')
    print("anvedi, dice che so %s" % name.text)

    path = etree.Element('path', style='fill:none;stroke:#000000;stroke-width:1px')
    print("anvedi, %s" % line_string.getchildren())


def load_kmz(kmz: str):
    with ZipFile(kmz, 'r') as kmzfh:
        with kmzfh.open('doc.kml') as docfh:
            return parser.parse(docfh)


def write_svg(svg: str, svg_paths) -> None:
    with open(svg, 'wb') as svgfh:
        root = etree.Element('svg',
                             xmlns="http://www.w3.org/2000/svg",
                             version="1.1")
        for path in svg_paths:
            root.append(path)

        svgfh.write(
            etree.tostring(root, xml_declaration=True, encoding='UTF-8'))
