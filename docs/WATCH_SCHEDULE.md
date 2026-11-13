# Docket Watch Schedule — `eve watch` has no daemon by design

The operator's scheduler is the clock. `eve watch --check` is the
poll: it hits the read endpoints, diffs against snapshots, and
prints only news. Put one of these entries in place and the watch
keeps itself.

## cron (Linux / WSL2 / macOS) — every morning at 06:00

```cron
0 6 * * * C:/Azazael/.venvs/py315t/Scripts/python.exe -m eve_unleashed.cli watch --check >> ~/.azazael/watch/watch.log 2>&1
```

Run from the `azazael/` directory (cron: add `cd C:/Azazael/azazael &&`).
First run seeds snapshots, so it reports everything once; every
run after that reports only new docket ids.

## Windows Task Scheduler — daily 06:00

Action: `C:/Azazael/.venvs/py315t/Scripts/python.exe`
Arguments: `-m eve_unleashed.cli watch --check`
Start in: `C:/Azazael/azazael`
Append stdout to: `%USERPROFILE%\.azazael\watch\watch.log`

## Manage the list

```bash
python -m eve_unleashed.cli watch --add "lead pipes"
python -m eve_unleashed.cli watch --remove "lead pipes"
python -m eve_unleashed.cli watch --check   # the poll itself
```

Snapshots live in `~/.azazael/watch/snap_*.json` (one per term).
Deleting a snapshot re-baselines that term: next poll reports
everything again. That is the documented reset, not a bug.
