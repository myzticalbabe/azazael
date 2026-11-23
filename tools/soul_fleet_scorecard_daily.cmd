@echo off
REM SoulFleetScorecard daily wrapper -- token from gh auth (never on disk), binary explicit.
for /f "delims=" %%t in ('gh auth token') do set GITHUB_AUTH_TOKEN=%%t
C:\Azazael\.venvs\py316t\Scripts\python.exe "C:\Azazael\azazael\tools\soul_fleet_scorecard.py" --root "C:\Azazael" --binary "C:\Users\clint\go\bin\scorecard.exe" --json "C:\Azazael\logs\soul_fleet_scorecard.json"
