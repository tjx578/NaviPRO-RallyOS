"""Adapter mode gates and native HTTP contracts, using a local fixture server."""
from contextlib import contextmanager
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from threading import Thread
from urllib.parse import parse_qs, urlsplit

import pytest

from navipro_rallyos.route.osrm_adapter import OSRMAdapter, RouteCandidateError
from navipro_rallyos.route.valhalla_adapter import ValhallaAdapter
from test_osrm_rea import ANCHORS as OSRM_ANCHORS, RESPONSE
from test_valhalla_rea import ANCHORS, PROVENANCE, route_result, matrix_result


def invoke(operation, transport, **mode):
    if operation == 'osrm_route':
        return OSRMAdapter(transport=transport).route(OSRM_ANCHORS, 'graph', 'profile', **mode)
    if operation == 'osrm_table':
        return OSRMAdapter(transport=transport).table(OSRM_ANCHORS, **mode)
    if operation == 'osrm_match':
        return OSRMAdapter(transport=transport).match(OSRM_ANCHORS, [1, 2, 3], [4, 4, 4], **mode)
    return getattr(ValhallaAdapter(transport=transport), operation.removeprefix('valhalla_'))(
        ANCHORS, **PROVENANCE, **mode
    )


OPERATIONS = ['osrm_route', 'osrm_table', 'osrm_match', 'valhalla_route', 'valhalla_matrix']


@pytest.mark.parametrize('operation', OPERATIONS)
@pytest.mark.parametrize('mode', ['LIVE', 'CONFIRMED', '', None, True, 'prep'])
def test_forbidden_mode_never_reaches_transport(operation, mode):
    calls = []
    with pytest.raises(RouteCandidateError, match='PREP or REVIEW'):
        invoke(operation, lambda *args: calls.append(args), mode=mode)
    assert calls == []


@pytest.mark.parametrize('operation', OPERATIONS)
def test_mode_is_mandatory(operation):
    calls = []
    with pytest.raises(TypeError):
        invoke(operation, lambda *args: calls.append(args))
    assert calls == []


@pytest.mark.parametrize('operation', OPERATIONS)
@pytest.mark.parametrize('mode', ['PREP', 'REVIEW'])
def test_allowed_mode_is_preserved(operation, mode):
    response = {
        'osrm_route': RESPONSE,
        'osrm_table': {'code': 'Ok', 'distances': [[0]*3 for _ in range(3)],
                       'durations': [[0]*3 for _ in range(3)]},
        'osrm_match': {'code': 'Ok', 'tracepoints': [{}, {}, {}], 'matchings': []},
        'valhalla_route': route_result(),
        'valhalla_matrix': matrix_result(),
    }[operation]
    result = invoke(operation, lambda *args: response, mode=mode)
    assert result['mode'] == mode
    assert result['route_authority'] is False


@contextmanager
def native_fixture_server():
    receipts = []

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *args):
            pass

        def do_GET(self):
            receipts.append(('GET', self.path, None))
            data = json.dumps(RESPONSE).encode()
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Content-Length', str(len(data)))
            self.end_headers()
            self.wfile.write(data)

        def do_POST(self):
            payload = json.loads(self.rfile.read(int(self.headers['Content-Length'])))
            receipts.append(('POST', self.path, payload))
            response = matrix_result() if self.path == '/sources_to_targets' else route_result()
            data = json.dumps(response).encode()
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Content-Length', str(len(data)))
            self.end_headers()
            self.wfile.write(data)

    server = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield f'http://127.0.0.1:{server.server_port}', receipts
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)


def test_osrm_uses_native_get_coordinates_and_options():
    with native_fixture_server() as (origin, receipts):
        result = OSRMAdapter(origin).route(OSRM_ANCHORS, 'graph', 'profile', mode='REVIEW')
    method, url, body = receipts[0]
    parsed = urlsplit(url)
    assert method == 'GET' and body is None
    assert parsed.path == '/route/v1/driving/' + ';'.join(
        f'{a.lon_e7/1e7:.7f},{a.lat_e7/1e7:.7f}' for a in OSRM_ANCHORS
    )
    query = parse_qs(parsed.query)
    assert query['overview'] == ['full']
    assert query['geometries'] == ['geojson']
    assert query['annotations'] == ['distance,duration,nodes']
    assert query['steps'] == ['true']
    assert 'coordinates' not in query
    assert result['candidates'][0]['graph_distance_mm_candidate'] == 1_234_567


@pytest.mark.parametrize('operation,path', [('route', '/route'), ('matrix', '/sources_to_targets')])
def test_valhalla_still_uses_native_post(operation, path):
    with native_fixture_server() as (origin, receipts):
        result = getattr(ValhallaAdapter(origin), operation)(ANCHORS, mode='PREP', **PROVENANCE)
    method, url, body = receipts[0]
    assert (method, url) == ('POST', path)
    assert body['costing'] == 'auto'
    assert body['units'] == 'kilometers'
    assert result['route_authority'] is False
