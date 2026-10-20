"""Download a bounded public OSM extract and convert the SAME input for both engines.

Requires osmium==4.3.2 in the preprocessing environment. No routing is performed.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import platform
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

QUERY = """[out:xml][timeout:90][maxsize:134217728];
(
  way["highway"](-7.34,112.67,-7.21,112.84);
  node["name"](-7.34,112.67,-7.21,112.84);
  way["name"](-7.34,112.67,-7.21,112.84);
  relation["type"="restriction"](-7.34,112.67,-7.21,112.84);
);
(._;>>;);
out meta;
"""
ENDPOINT = 'https://overpass-api.de/api/interpreter'


def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def main():
    import osmium

    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=False)
    (args.output / 'query.overpass').write_text(QUERY, encoding='utf-8')
    request = urllib.request.Request(
        ENDPOINT, data=urllib.parse.urlencode({'data': QUERY}).encode(),
        headers={'User-Agent': 'NaviPRO-M1-local-research/0.1'}, method='POST')
    xml_path = args.output / 'surabaya.osm'
    with urllib.request.urlopen(request, timeout=120) as response, xml_path.open('wb') as stream:
        total = 0
        for chunk in iter(lambda: response.read(1024 * 1024), b''):
            total += len(chunk)
            if total > 200_000_000:
                raise ValueError('extract exceeds bounded 200 MB budget')
            stream.write(chunk)
    counts = {'node': 0, 'way': 0, 'relation': 0}
    osm_base = None
    for event, element in ET.iterparse(xml_path, events=('end',)):
        if element.tag == 'remark':
            raise ValueError('Overpass returned an incomplete/error extract: ' + (element.text or ''))
        if element.tag == 'meta':
            osm_base = element.attrib.get('osm_base')
        if element.tag in counts:
            counts[element.tag] += 1
            element.clear()
    if not osm_base or counts['node'] == 0 or counts['way'] == 0:
        raise ValueError('OSM timestamp and nonempty road data required')
    pbf_path = args.output / 'surabaya.osm.pbf'
    writer = osmium.SimpleWriter(str(pbf_path))

    class Convert(osmium.SimpleHandler):
        def node(self, node):
            writer.add_node(node)

        def way(self, way):
            writer.add_way(way)

        def relation(self, relation):
            writer.add_relation(relation)

    try:
        Convert().apply_file(str(xml_path))
    finally:
        writer.close()
    receipt = {
        'status': 'SOURCE_EXTRACT_PREPARED_NOT_ROUTED',
        'benchmark_eligible': False,
        'administrative_coverage': 'NOT_VERIFIED',
        'driving_side': 'NOT_VERIFIED',
        'blocked_reason': 'No complete administrative boundaries; use a reviewed regional PBF and admin database before benchmarking',
        'endpoint': ENDPOINT, 'osm_base': osm_base,
        'retrieved_at_utc': datetime.now(timezone.utc).isoformat(),
        'bbox_wsen': [112.67, -7.34, 112.84, -7.21],
        'scope': 'Highways, named nodes/ways, restriction relations and recursively referenced members',
        'coverage_limit': 'Bounded extract; outside-area paths and missing OSM features remain unverified',
        'counts': counts, 'xml_sha256': digest(xml_path),
        'source_pbf_sha256': digest(pbf_path),
        'query_sha256': digest(args.output / 'query.overpass'),
        'python': platform.python_version(), 'converter': 'osmium==4.3.2',
        'attribution': '© OpenStreetMap contributors',
        'license': 'ODbL-1.0', 'license_url': 'https://www.openstreetmap.org/copyright',
    }
    (args.output / 'source-manifest.json').write_text(json.dumps(receipt, indent=2), encoding='utf-8')
    print(json.dumps(receipt, indent=2))


if __name__ == '__main__':
    main()
