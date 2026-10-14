# Swallow sites in tools/openvino_worker.py (4) - work BOTTOM-UP so earlier line numbers stay valid

Each row: handler line | shape | exception type | the body statement you will replace.
- line 169  unlogged_handler       Exception                        body: self._send(400, {'error': 'bad request: %s' % e})
- line 130  marker_hidden          Exception                        body: pass
- line 122  marker_hidden          Exception                        body: pass
- line 69   unlogged_handler       Exception                        body: names[d] = None
