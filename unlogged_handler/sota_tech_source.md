# Swallow sites in tools/sota_tech_source.py (2) - work BOTTOM-UP so earlier line numbers stay valid

Each row: handler line | shape | exception type | the body statement you will replace.
- line 34   unlogged_handler       (urllib.error.URLError, ssl.SSLE body: return ('ABSTRACT_FETCH_FAILED', 'arxiv fetch failed (' + type(exc).__name__ + '); see video description')
- line 23   unlogged_handler       ImportError                      body: ctx = None
