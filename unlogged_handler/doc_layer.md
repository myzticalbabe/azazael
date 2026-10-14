# Swallow sites in tools/graph_semantic/doc_layer.py (3) - work BOTTOM-UP so earlier line numbers stay valid

Each row: handler line | shape | exception type | the body statement you will replace.
- line 205  silent_continue        (ValueError, OSError)            body: continue
- line 194  silent_continue        OSError                          body: continue
- line 103  unlogged_handler       OSError                          body: text = ''
