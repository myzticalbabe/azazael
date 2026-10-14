# Swallow sites in tools/comfyui_flux_headless.py (3) - work BOTTOM-UP so earlier line numbers stay valid

Each row: handler line | shape | exception type | the body statement you will replace.
- line 231  unlogged_handler       subprocess.TimeoutExpired        body: proc.kill()
- line 138  unlogged_handler       Exception                        body: time.sleep(4)
- line 134  unlogged_handler       subprocess.TimeoutExpired        body: proc.kill()
