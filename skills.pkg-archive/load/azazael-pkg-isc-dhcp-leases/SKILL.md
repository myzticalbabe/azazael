---
name: azazael-pkg-isc-dhcp-leases
description: Callable skill for Python package isc_dhcp_leases 0.10.0 — Small python module for reading /var/lib/dhcp/dhcpd.leases from isc-dhcp-server
metadata:
  category: packages
  project: azazael
  priority: low
---

# isc_dhcp_leases 0.10.0

> Small python module for reading /var/lib/dhcp/dhcpd.leases from isc-dhcp-server

## Identity

| Field | Value |
|-------|-------|
| Distribution | `isc_dhcp_leases` |
| Version | `0.10.0` |
| Interpreter | Python 3.13.12 (`/usr/bin/python3.13`) |

## EXECUTE — Python API

Importable top-level module(s):

- `isc_dhcp_leases`

Invocation pattern:

```python
import isc_dhcp_leases
print("isc_dhcp_leases loaded OK")
```

## Verify

```bash
/usr/bin/python3.13 -c "import isc_dhcp_leases; print('isc_dhcp_leases OK')"
```

## Related

- Environment: Kali Python 3.13.12 system packages (969 total)
- See `azazael-skill-catalog` / SKILLS_CATALOG.md for the full skill inventory
