# Swallow sites in tools/install_dual_abi.py (3) - work BOTTOM-UP so earlier line numbers stay valid

Each row: handler line | shape | exception type | the body statement you will replace.
- line 277  return_default         subprocess.TimeoutExpired        body: return 'TIMEOUT'
- line 226  silent_pass            OSError                          body: pass
- line 87   return_default         Exception                        body: return False
