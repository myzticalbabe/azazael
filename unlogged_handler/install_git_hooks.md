# Swallow sites in tools/install_git_hooks.py (1) - work BOTTOM-UP so earlier line numbers stay valid

Each row: handler line | shape | exception type | the body statement you will replace.
- line 75   return_default         OSError                          body: return False
