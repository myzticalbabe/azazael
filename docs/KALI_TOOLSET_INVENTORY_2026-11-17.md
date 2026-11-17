# Kali toolset → openSUSE inventory (2026-11-17)

Computed by `tools/native_tools.py` lane + the two measurements below. Every number
here was produced in this session; none is recalled.

## Denominators

| reading | value | how |
| --- | --- | --- |
| Kali metapackages (`kali-tools-*`) | **15** | `dpkg-query -W 'kali-tools-*'` |
| Kali closure (recursive deps, no recommends) | **2115** | `apt-cache depends --recurse` |
| of closure, installed on this Kali | **1636** | `dpkg-query -W` per package |
| openSUSE unique package names | **54503** | `repodata/primary.xml.*` for all 6 enabled repos |

## Availability by name

| reading | value |
| --- | --- |
| closure packages with a same-named openSUSE RPM | **522** (24.68%) |
| closure packages with **no** same-named RPM | **1593** |
| installed packages with a same-named RPM | **473** (28.91% of installed) |
| installed packages with **no** same-named RPM | **1163** |

**What a miss means:** name equality only. dpkg and RPM name packages differently, so
`no_same_name_rpm` is *not* "not installable" — it is "needs a rename check, a native
build, or a language-ecosystem install". The 8 native builds below came from exactly
this set.

## Native build lane (measured in openSUSE, 3.16t)

`python tools/native_tools.py --doctor` → `8 of 8 recipes ready`;
`--build-all` → `all 8 ok`, and each binary resolves on PATH:

- `bully`
- `cowpatty`
- `hcxdumptool`
- `hcxpcapngtool`
- `hcxwltool`
- `mdk4`
- `pixiewps`
- `reaver`
- `wash`

## Re-derive

```bash
# Kali side
dpkg-query -W -f='${Package}\n' 'kali-tools-*'
# openSUSE side
zstd -dc <primary.xml.zst> | grep -o '<name>[^<]*</name>'
# native lane
wsl -d openSUSE-Tumbleweed -u root -- /usr/local/bin/python3.16t tools/native_tools.py --doctor
```

Expiry: these counts move with both distros' repos; re-measure before quoting next session.
## Install result

`zypper -n in -y --no-recommends` over the 473 packages that both Kali has installed
and openSUSE names, in batches of 50 with a per-package retry so one bad name cannot sink
a batch.

| reading | value |
| --- | --- |
| requested | **473** |
| present after the zypper pass | **471** |
| closed outside zypper | **+2** — `sslsplit`, `wfuzz` |
| **present now** | **473 / 473** |
| total RPMs on the openSUSE system after | **1840** |

Two packages did not come from zypper. Both are installed now, and both were proven
by running them rather than by importing them:

- `sslsplit` — the RPM (`0.5.5-2.63`) exists in the `security` repo but is
  uninstallable: `nothing provides 'libcrypto.so.1.1()(64bit)'`, and
  `zypper search --provides --match-exact` finds no provider for it anywhere.
  Built from source against OpenSSL 3 with a one-macro shim for the removed
  `ERR_GET_FUNC`; installed to `/usr/local/sbin/sslsplit` (249,456 bytes),
  `MAKE_RC=0`, links `libssl.so.3` / `libcrypto.so.3` / `libnet.so.9` /
  `libevent-2.1` / `libpcap`, and `-h` prints usage.
- `wfuzz` — the PyPI route fails in four independent places, in the order they
  surface: pip >= 24.1 rejects 3.1.0's metadata (`pyparsing (>=2.4*)` ->
  "Expected matching RIGHT_PARENTHESIS"), `pkg_resources` was removed in
  setuptools 84.2.1, `import imp` was removed in 3.12, and `import cgi` was
  removed in 3.13. Resolved by hand-unpacking the pure-Python 3.1.0 wheel into
  `/usr/local/lib/python3.16t/site-packages`, patching `imp` to `importlib.util`,
  installing `legacy-cgi`, and pinning `setuptools<81` (80.10.2). Live smoke:
  `WFUZZ_RC=0`, "Total requests: 2", found `known` (301) and `absent` (404), with
  the target's own server log recording both GETs. The broken 2.4.5 stub is
  preserved at `/usr/local/bin/wfuzz-2.4.5.stub`, not deleted.

Verify:

```bash
MSYS_NO_PATHCONV=1 wsl -d openSUSE-Tumbleweed -u root -- bash /mnt/c/Users/clint/tmp_dump_rpms.sh
python C:/Users/clint/tmp_verify_install.py    # zypper pass: requested=473 present=471
MSYS_NO_PATHCONV=1 wsl -d openSUSE-Tumbleweed -u root -- ls -l /usr/local/sbin/sslsplit /usr/local/bin/wfuzz
```

`present_after_install: 471` is kept in
`state/kali_toolset_inventory_2026-11-17.json` on purpose: that is what the zypper
pass achieved, and overwriting it with 473 would destroy the denominator. The two
packages closed outside zypper are recorded beside it as `gap_closure`, with
`present_now: 473`.
