# KALI OSINT REPORT — BCC Financial Investigation
## Creative Repurposing of Kali Linux Security Tools for Governance Auditing

> **Generated:** Fri Jul 31 10:12:19 PM UTC 2026
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
| samhsa.gov | 30 alt2.us.etp.fireeyegov.com. | FOUND | FOUND | A |
| uwberks.org | 20 d148834b.ess.barracudanetworks.com. | FOUND | FOUND | A |

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
| countyofberks.com | PARTIAL (000000) | CHECK | CHECK | C |
| samhsa.gov | YES (HTTP 301) | CHECK | CHECK | A |

## SMTP Verification BYPASS (swaks)

**Tool availability:** swaks NOT INSTALLED — run: apt install swaks

**Null sender strategy:** Using "<>" (bounce address) to avoid SPF rejection.

| Email | MX Server | RCPT TO Response | Status |
|-------|-----------|-----------------|--------|
| * | * | * | swaks NOT AVAILABLE |

## OSINT Email Discovery (theHarvester)

**Tool availability:** theHarvester NOT INSTALLED — run: apt install theharvester

theHarvester not available.

## PDF Forensic Analysis — IRS 990 Redaction Audit

**No PDFs found.** Download IRS 990 PDFs from:
- [ProPublica Nonprofit Explorer](https://projects.propublica.org/nonprofits/organizations/232043478)
- [IRS Tax Exempt Organization Search](https://apps.irs.gov/app/eos/)


## Alternative UA Web Scraping

| URL | HTTP Code | Content-Type | Size | Notes |
|-----|-----------|-------------|------|-------|
| https://www.berkspa.gov/departments/commissioners | 200 | text/html; charset=utf-8 | 117503B | |
| https://www.readingpa.gov/government/city-council | 403 | text/html; charset=UTF-8 | 72448B | |
| https://www.countyofberks.com/departments/human-services | 302 | text/html; charset=UTF-8 | 173B | |
| https://www.berkscc.org/about/board-of-directors | 405 | text/plain; charset=utf-8 | 10B | |
| https://www.attorneygeneral.gov/charities | 404 | text/html; charset=UTF-8 | 81704B | |
| https://www.samhsa.gov/grants/grants-dashboard | 200 | text/html | 118B | |

## Network Footprint — Service Enumeration

| Domain | Port 80 | Port 443 | Port 25 | Other | Assessment |
|--------|---------|----------|---------|-------|------------|
| berkscc.org | OPEN | OPEN | CLOSED | — | HTTP exposed |
| berkscounselingcenter.org | OPEN | OPEN | CLOSED | — | HTTP exposed |

## Public Document Metadata (metagoofil)

**Tool availability:** metagoofil NOT INSTALLED

metagoofil not available.


---

## Summary: Kali Creative Repurposing for BCC Financial Investigation

| Tool | Original Purpose | BCC Financial Repurpose | Value |
|------|-----------------|------------------------|-------|
| **swaks** | SMTP pentesting | Bypass Spamhaus PBL for email verification | HIGH |
| **theHarvester** | Attack surface recon | Discover undisclosed BCC/agency emails | HIGH |
| **dnsrecon** | DNS attack surface | SPF/DMARC governance audit | MEDIUM |
| **whois** | Domain ownership recon | Registration transparency audit | MEDIUM |
| **sslscan** | SSL vulnerability scan | IT governance quality indicator | LOW |
| **pdf-parser** | Malicious PDF analysis | Schedule B redaction forensic audit | **CRITICAL** |
| **exiftool** | Metadata extraction | 990 preparation tracing (who filed it?) | MEDIUM |
| **metagoofil** | Public doc harvesting | Find hidden public documents | MEDIUM |
| **curl (Linux)** | HTTP client | Bypass Windows UA blocking | LOW |
| **nmap** | Network scanning | Digital service maturity assessment | LOW |

### Key Finding
Kali's most valuable contribution is **pdf-parser for Schedule B redaction analysis**. 
IRS 990 Schedule B (major donors) is redacted in public filings with black rectangles.
pdf-parser can detect whether this redaction used overlay (text still present underneath) 
vs true deletion. If overlay was used, the donor names can be recovered.

### Next Steps
1. Download IRS 990 PDFs from ProPublica: https://projects.propublica.org/nonprofits/organizations/232043478
2. Run pdf-parser on Schedule B pages specifically
3. Run theHarvester with full API keys (Hunter.io, SecurityTrails) for deeper email discovery
4. Attempt swaks SMTP verification with a VPN/proxy for the 10 blocked emails

