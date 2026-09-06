# KALI OSINT REPORT — BCC Financial Investigation
## Creative Repurposing of Kali Linux Security Tools for Governance Auditing

> **Generated:** Mon Aug  3 01:42:15 PM UTC 2026
> **Environment:** Kali Linux WSL
> **Purpose:** Map every public digital footprint of Berks Counseling Center,
>            its board members, its oversight agencies, and its funders.

---

## Target Domains
```
# BCC Primary
berkscc.org
berkscounselingcenter.org

# Oversight Agencies
readingpa.gov
countyofberks.com
berkspa.gov
samhsa.gov
hud.gov
pa.gov
attorneygeneral.gov

# Funders
uwberks.org
bccf.org
pennstatehealth.org

# Board Member Affiliations
edwardjones.com
councilonchemicalabuse.com
```

## DNS Enumeration — Governance Transparency Audit

| Domain | MX | SPF | DMARC | Governance Grade |
|--------|-----|-----|-------|------------------|
| berkscc.org | 5 d109566a.ess.barracudanetworks.com. | FOUND | FOUND | A |
| readingpa.gov | 20 gw16014.fortimail.com. | FOUND | NONE | D |
| countyofberks.com | 10 countyofberks-com.mail.protection.outlook.com. | FOUND | FOUND | A |
| samhsa.gov | 10 primary.us.etp.fireeyegov.com. | FOUND | FOUND | A |
| uwberks.org | 10 d148834a.ess.barracudanetworks.com. | FOUND | FOUND | A |

## WHOIS Domain Ownership

### berkscc.org
- **Registrar:** GoDaddy.com, LLC
- **Created:** 2004-06-10T22:20:39Z
- **Registrant:** PRIVACY-PROTECTED

### berkscounselingcenter.org
- **Registrar:** GoDaddy.com, LLC
- **Created:** 2011-03-04T16:50:07Z
- **Registrant:** PRIVACY-PROTECTED

### readingpa.gov
- **Registrar:** get.gov
- **Created:** 2006-03-24T11:47:05Z
- **Registrant:** REDACTED FOR PRIVACY

### countyofberks.com
- **Registrar:** Network Solutions, LLC
- **Created:** 1998-11-19T05:00:00Z
- **Registrant:** 


## SSL/TLS Certificate Audit — IT Governance Quality

| Domain | HTTPS | Cert Valid | TLS Version | IT Gov Grade |
|--------|-------|------------|-------------|--------------|
| berkscc.org | PARTIAL (405) | CHECK | CHECK | C |
| berkscounselingcenter.org | YES (HTTP 301) | CHECK | CHECK | A |
| readingpa.gov | YES (HTTP 301) | CHECK | CHECK | A |
| countyofberks.com | YES (HTTP 302) | CHECK | CHECK | A |
| samhsa.gov | YES (HTTP 301) | CHECK | CHECK | A |

## SMTP Verification BYPASS (swaks)

**Tool availability:** swaks INSTALLED

**Null sender strategy:** Using "<>" (bounce address) to avoid SPF rejection.

| Email | MX Server | RCPT TO Response | Status |
|-------|-----------|-----------------|--------|
| jplageman@berkscc.org | d109566a.ess.barracudanetworks.com. | Unknown | [?] UNKNOWN |
| cseitz@berkscc.org | d109566a.ess.barracudanetworks.com. | Unknown | [?] UNKNOWN |
