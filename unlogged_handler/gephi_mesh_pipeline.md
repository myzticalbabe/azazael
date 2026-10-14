# Swallow sites in tools/gephi_mesh_pipeline.py (4) - work BOTTOM-UP so earlier line numbers stay valid

Each row: handler line | shape | exception type | the body statement you will replace.
- line 651  silent_pass            OSError                          body: pass
- line 147  silent_pass            ImportError                      body: pass
- line 135  empty_literal_return   ImportError                      body: return {}
- line 125  empty_literal_return   ImportError                      body: return {}
