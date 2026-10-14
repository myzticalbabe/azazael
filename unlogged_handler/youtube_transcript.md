# Swallow sites in tools/youtube_transcript.py (4) - work BOTTOM-UP so earlier line numbers stay valid

Each row: handler line | shape | exception type | the body statement you will replace.
- line 244  marker_hidden          Exception                        body: pass
- line 161  unlogged_handler       Exception                        body: segs = []
- line 156  unlogged_handler       Exception                        body: text = ''
- line 52   unlogged_handler       subprocess.TimeoutExpired        body: return (124, '', 'timeout')
