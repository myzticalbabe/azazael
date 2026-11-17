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
