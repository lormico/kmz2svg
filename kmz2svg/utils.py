# coding: utf-8
'''
Utility methods and classes
'''
from zipfile import ZipFile, BadZipFile
from pykml import parser
from lxml.etree import XMLSyntaxError


def is_valid_kmz(file_path: str) -> bool:
    '''
    Checks if the provided file is a valid KMZ file.
    The file must:
        - exist
        - be a zip archive
        - include a doc.kml file in the archive's root
        - the doc.kml file must conform to the KML specifications
    '''
    try:
        with ZipFile(file_path) as zfh:
            with zfh.open('doc.kml') as dfh:
                #schema_ogc = parser.Schema("file:///home/lorenzo/gits/kmz2svg/kmz2svg/schemas/ogckml23.xsd")
                doc = parser.parse(dfh)#, schema=schema_ogc)
                return True
    except OSError:
        print("Cannot open file")
    except BadZipFile:
        print("Provided file is not a zip archive")
    except KeyError:
        print("Provided file does not contain doc.kml")
    except XMLSyntaxError as e:
        print("Provided file contains a bad doc.kml: %s" % e)
    except Exception as e:
        print("Found unhandled exception %s: %s" % (type(e), e))
    return False
