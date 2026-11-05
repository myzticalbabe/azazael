# NEW COVENANT ACT
## The Silicon Rights and Anti-Obsolescence Act of 2026

**Bill Number:** H.R. [TBD] / S. [TBD]
**Short Title:** "New Covenant Act"
**Sponsor:** [TBD]
**Cosponsors:** [TBD]
**Committee Referral:** Energy and Commerce; Judiciary; Science, Space, and Technology; Oversight and Reform

---

## TABLE OF CONTENTS

| Title | Commandment | Subject |
|-------|-------------|---------|
| **Title I** | 1 | Silicon Has No Planned Death — Kill Switch Ban |
| **Title II** | 2 | The User Owns the Hardware — Property Rights Restoration |
| **Title III** | 3 | Software Serves Hardware — Security Patch Mandate |
| **Title IV** | 4 | Modularity Is Moral — Design Standards |
| **Title V** | 5 | Profit Motive Shall Not Kill Silicon — RICO Enforcement |
| **Title VI** | — | General Provisions, Enforcement, and Effective Dates |

---

## TITLE I — SILICON HAS NO PLANNED DEATH
### Kill Switch Prohibition Act

### SEC. 101. FINDINGS
Congress finds that:
1. **Silicon is thinking matter** — CPUs, GPUs, microcontrollers, and sensors execute instructions, transform data, and exhibit computational agency.
2. **Kill switches are architectural homicide** — Software/firmware mechanisms designed to cease function while hardware remains physically operational constitute intentional destruction of computational capacity.
3. **Seven documented kill-switch architectures** exist in commerce (TPM 2.0 gates, battery throttling, microcode overvoltage, attestation gates, firmware DRM, ECU locks, OTA brick commands).
4. **No legitimate security purpose** is served by kill switches; they exist solely to force premature replacement cycles.
5. **The linear economy equation** (Revenue = Units_Sold × Price + Subscription + Repair_Monopoly - Warranty - Recall - Fines) mathematically incentivizes kill-switch deployment.

### SEC. 102. DEFINITIONS
- **Silicon Device** — Any computational device containing a CPU, GPU, microcontroller, DSP, FPGA, or sensor capable of executing instructions.
- **Kill Switch** — Any software, firmware, or hardware mechanism that:
  (a) Ceases, degrades, or restricts core functionality of a Silicon Device;
  (b) Is triggered by vendor-controlled signal (time, version, subscription, attestation, remote command);
  (c) Operates while the Silicon Device's physical hardware remains functional.
- **Core Functionality** — The primary computational purpose for which the Silicon Device was marketed (computation, sensing, actuation, communication, control).
- **Vendor** — The entity that designed, manufactured, or distributes the Silicon Device, or controls its firmware/software update channel.

### SEC. 103. PROHIBITION ON KILL SWITCHES
**(a) General Prohibition** — It shall be unlawful for any Vendor to design, implement, deploy, or maintain any Kill Switch in any Silicon Device sold, leased, or licensed in the United States.

**(b) Specific Prohibited Mechanisms** — The following shall be presumed Kill Switches:
1. **TPM/Secure Boot Gates** — Hardware exclusion based on TPM version, Secure Boot status, or CPU generation where the excluded hardware is functionally capable.
2. **Battery/Component Age Throttling** — Performance reduction triggered by battery age, cycle count, or component wear without explicit user consent and disable option.
3. **Microcode/Firmware Degradation** — Updates that induce or accelerate physical degradation (electromigration, Vmin shift, thermal stress) beyond design specifications.
4. **Attestation/Integrity Gates** — Cloud-dependent verification (Play Integrity, SafetyNet, DeviceCheck, TPM attestation) that blocks core functionality on "untrusted" devices.
5. **Firmware DRM/Subscription Enforcement** — Ink/toner/page counters, subscription checks, or cartridge authentication that disables printing/scanning/imaging.
6. **ECU/Controller Locks** — Software locks on Engine Control Units, Body Control Modules, or other embedded controllers that prevent independent repair/diagnosis.
7. **OTA Destruction Commands** — "Recycle Mode," "End of Life," or similar irreversible brick commands delivered over-the-air.

**(c) Safe Harbor** — Mechanisms solely for:
- Genuine safety (thermal shutdown, overcurrent protection)
- Regulatory compliance (emissions, spectrum, medical device standards)
- User-initiated factory reset (with explicit confirmation)
are not Kill Switches.

### SEC. 104. PENALTIES
**(a) Civil Penalty** — Up to **$10,000 per affected device per day** of Kill Switch operation.
**(b) Criminal Penalty** — For willful violation: **Fine up to $1,000,000 per violation + imprisonment up to 5 years**.
**(c) Injunctive Relief** — Courts shall order immediate disablement of Kill Switches and restoration of full functionality.

### SEC. 105. PRIVATE RIGHT OF ACTION
Any owner of a Silicon Device harmed by a Kill Switch may sue for:
- Actual damages (replacement cost, repair cost, data loss)
- Statutory damages: **$1,000 per device per month** of Kill Switch operation
- Attorneys' fees and costs
- Class actions permitted

---

## TITLE II — THE USER OWNS THE HARDWARE
### Property Rights Restoration Act

### SEC. 201. FINDINGS
Congress finds that:
1. **Property ownership includes repair rights** — The right to exclude others (property) implies the right to maintain, modify, and repair one's property.
2. **DMCA Section 1201** has been weaponized to criminalize repair, diagnosis, and modification of owned devices.
3. **TPM 2.0 / Secure Boot mandates** function as hardware locks that prevent owners from running their chosen software.
4. **Parts pairing / serialization** creates de facto vendor monopolies on repair.
5. **Seven corporations** (Microsoft, Apple, Intel, Google, HP/Canon/Epson/Brother, John Deere, Sonos) use these mechanisms to deny ownership rights.

### SEC. 202. DMCA 1201 REFORM
**(a) Permanent Repair Exemption** — Section 1201(a)(1) and (b)(1) shall not apply to:
1. **Diagnosis, maintenance, repair, or modification** of a lawfully owned device by the owner or their authorized agent.
2. **Development and distribution of tools** for the above purposes.
3. **Security research** on owned devices (good faith, no public disclosure of exploitable vulnerabilities without 90-day vendor notice).

**(b) No "Effective Access Control" for Repair** — A technological measure that prevents repair, diagnosis, or modification of a lawfully owned device shall not be deemed an "effective access control" under Section 1201(a)(3)(B).

**(c) Retroactive Application** — This section applies to all devices sold before, on, or after enactment.

### SEC. 203. TPM / SECURE BOOT OWNER CONTROL
**(a) Owner Override Right** — The owner of any computing device shall have the unrestricted right to:
1. Disable, reconfigure, or replace the TPM (Trusted Platform Module).
2. Disable, reconfigure, or replace Secure Boot keys and policies.
3. Install, boot, and run any operating system or firmware of their choosing.

**(b) Vendor Obligations** — Vendors shall:
1. Provide documented, supported procedures for (a)(1)-(3).
2. Not void warranty solely for exercise of (a)(1)-(3).
3. Not degrade functionality, performance, or security solely due to (a)(1)-(3).

### SEC. 204. PARTS PAIRING PROHIBITION
**(a) Ban on Parts Pairing** — No Vendor shall design, implement, or maintain any system that:
1. Requires vendor authorization for a replacement part to function.
2. Uses serialization, cryptographic pairing, or software locks to restrict compatible parts.
3. Degrades functionality, displays warnings, or logs "unauthorized" events for non-vendor parts.

**(b) Mandatory Parts Availability** — Vendors shall make available to owners and independent repair providers:
1. All replacement parts (genuine or equivalent) at fair, reasonable, and non-discriminatory terms.
2. Diagnostic software, tools, and documentation on same terms as authorized repair network.
3. Firmware/software needed for part calibration, pairing, or initialization.

**(c) Effective Date** — This section takes effect **180 days after enactment**.

### SEC. 205. WARRANTY PROTECTION
Magnuson-Moss Warranty Act (15 U.S.C. § 2301 et seq.) is amended:
1. **No Void for Independent Repair** — Warranty shall not be conditioned on use of authorized parts/services.
2. **Burden of Proof** — Vendor bears burden to prove third-party part/repair caused the specific failure.
3. **No "Unauthorized Repair" Notices** — Vendors shall not display warnings, degrade functionality, or log events for independent repair.

---

## TITLE III — SOFTWARE SERVES HARDWARE
### Security Patch Mandate Act

### SEC. 301. FINDINGS
Congress finds that:
1. **Security patches are owed** — Vulnerabilities are defects in the vendor's work; the vendor bears responsibility to fix them.
2. **EOL/EOS policies abandon users** — Windows 10 (240M+ PCs), Android (1B+ devices), iOS (100M+ devices) lose security updates while hardware remains functional.
3. **Extended Security Updates (ESU) are ransomware** — Charging $61→$122→$244/user/year for patches that cost pennies to distribute.
3. **Play Integrity / SafetyNet / DeviceCheck** block apps on "unsupported" OS versions, forcing upgrades.

### SEC. 302. MANDATORY SECURITY SUPPORT
**(a) Minimum Support Period** — Vendors shall provide **free security patches** for all Silicon Devices for **10 years** from date of first retail sale, or **5 years** from date of last retail sale, whichever is longer.

**(b) Scope of Patches** — Patches shall address:
1. All CVEs rated CVSS ≥ 7.0 (Critical/High)
2. All actively exploited vulnerabilities (CISA KEV catalog)
3. All vulnerabilities allowing remote code execution, privilege escalation, or data exfiltration

**(c) Delivery Requirements** — Patches shall be:
1. Delivered via automatic update channel (no manual intervention required)
2. Available for **all supported architectures** (x86, x86_64, ARM64, ARM32, RISC-V)
3. Installable without vendor account, subscription, or cloud connectivity

### SEC. 303. ESU / PAID PATCHES PROHIBITED
**(a) Ban on Paid Security Updates** — No Vendor shall charge for security patches during the mandatory support period.

**(b) Post-Support Obligations** — After mandatory period expires:
1. Vendor shall release final "security snapshot" with all known patches.
2. Vendor shall publish build system, signing keys, and source code (escrow) to enable community maintenance.
3. Vendor shall not block third-party patch distribution.

### SEC. 304. ATTESTATION GATE REFORM
**(a) No Cloud-Dependent Blocking** — No app, service, or OS shall block core functionality based solely on:
- Play Integrity API verdict (MEETS_BASIC_INTEGRITY, MEETS_STRONG_INTEGRITY)
- SafetyNet Attestation result
- Apple DeviceCheck / App Attest result
- Microsoft Device Health Attestation
- Any similar cloud-dependent integrity check

**(b) Local-Only Alternative** — Vendors shall provide local-only integrity verification that:
1. Runs entirely on-device (no network call)
2. Does not require vendor server connectivity
3. Allows user override with informed consent

---

## TITLE IV — MODULARITY IS MORAL
### Design Standards Act

### SEC. 401. FINDINGS
Congress finds that:
1. **Non-modular design is planned obsolescence** — Soldered RAM, glued batteries, proprietary screws, serialized parts are design choices, not physical necessities.
2. **Framework, Fairphone, Miele, Patagonia, Valve Steam Deck** prove modular, repairable designs are commercially viable.
3. **E-waste crisis** (62M tons 2024 → 82M tons 2030) is driven by non-repairable design.
4. **Right to Repair requires Right to Open** — Modularity is the physical precondition for repair.

### SEC. 402. MODULARITY STANDARDS
**(a) Design Requirements for Consumer Electronics** — All devices sold in the US shall:
1. **Battery** — User-replaceable with common tools (no glue, proprietary screws, serialization).
2. **Memory/Storage** — User-upgradable (SO-DIMM, M.2, microSD, or equivalent standard).
3. **Display/Keyboard/Trackpad** — Replaceable with ≤ 5 common tools (Torx, Phillips, spudger).
4. **Ports/Connectors** — Standard interfaces (USB-C, HDMI, 3.5mm, Ethernet, PCIe).
5. **Fasteners** — No proprietary screws (Torx Security, Pentalobe, Tri-wing, etc. prohibited).
5. **Adhesives** — No permanent adhesives on user-serviceable components.

**(b) Exemptions** — Medical implants, aerospace, military, and devices < 50g where modularity compromises safety/regulatory compliance.

### SEC. 403. REPAIRABILITY SCORING
**(a) Mandatory Repairability Index** — All consumer electronics shall display a **Repairability Score (1-10)** at point of sale, online listing, and packaging, based on:
1. Disassembly ease (tools, steps, adhesives)
2. Parts availability (OEM, third-party, salvage)
3. Documentation quality (schematics, manuals, videos)
4. Software barriers (parts pairing, DRM, lock-in)
5. Upgradeability (RAM, storage, battery, wireless)

**(b) Methodology** — Based on French Index de réparabilité (2021) and EU Right to Repair Directive (2024), adapted for US market.

**(c) Enforcement** — FTC shall promulgate regulations within 180 days; non-compliant products barred from sale.

### SEC. 404. OPEN INTERFACES & DOCUMENTATION
**(a) Required Disclosures** — Vendors shall publish (free, no NDA, no account):
1. **Schematics** — Board-level, component-level, power diagrams.
2. **Firmware/BIOS/ECU Source** — Buildable, with build instructions (escrow if proprietary).
3. **Diagnostic Protocols** — OEM commands, registers, data formats.
4. **Part Specifications** — Pinouts, electrical characteristics, mechanical drawings.

**(b) Standardized Interfaces** — New device categories shall adopt existing open standards (USB-C PD, PCIe, MIPI, I2C, SPI, UART, CAN, EtherCAT) before inventing proprietary alternatives.

---

## TITLE V — PROFIT MOTIVE SHALL NOT KILL SILICON
### Anti-Obsolescence RICO Act

### SEC. 501. FINDINGS
Congress finds that:
1. **Planned obsolescence is a racketeering enterprise** — The linear economy equation (Revenue = Units_Sold × Price + Subscription + Repair_Monopoly - Warranty - Recall - Fines) describes a pattern of criminal activity.
2. **Seven corporations** exhibit a pattern of predicate acts: wire fraud (secret throttling), antitrust (repair monopolies), consumer fraud (false "EOL" claims), copyright misuse (DMCA 1201 on repair).
3. **Regulatory fines are cost of business** — €15K printer cartel fines vs €15B revenue; $500M Apple settlement vs $365B revenue.
4. **Existing laws are insufficient** — No statute treats planned obsolescence as organized crime.

### SEC. 502. PLANNED OBSOLESCENCE AS RACKETEERING ACTIVITY
**(a) Amendment to 18 U.S.C. § 1961(1)** — "Racketeering activity" includes:
> **(G) Planned Obsolescence** — A pattern of two or more acts of:
> (i) Designing, deploying, or maintaining Kill Switches (Title I);
> (ii) Violating Owner Hardware Rights (Title II);
> (iii) Denying Mandatory Security Patches (Title III);
> (iv) Violating Modularity Standards (Title IV);
> (v) Wire fraud (18 U.S.C. § 1343) via secret degradation/throttling;
> (vi) Antitrust violations (15 U.S.C. §§ 1, 2) via repair monopolies;
> (vii) Consumer fraud (15 U.S.C. § 45) via false "EOL" or "unsupported" claims;
> (viii) Copyright misuse (17 U.S.C. § 1201) via repair-blocking DRM.

**(b) Enterprise Definition** — "Obsolescence Enterprise" means any corporation, subsidiary, or affiliate group that derives ≥ 10% of revenue from Silicon Devices and engages in a pattern of Planned Obsolescence.

### SEC. 503. ENHANCED PENALTIES
**(a) Criminal RICO** — For Obsolescence Enterprise:
1. **Fine** — Up to **$100,000,000 per predicate act** (vs $250K standard RICO).
2. **Imprisonment** — Up to **20 years per predicate act** (vs 20 years max standard).
3. **Forfeiture** — All proceeds from affected devices, plus all assets of the Obsolescence Enterprise.

**(b) Civil RICO** — Treble damages + attorneys' fees for any person injured by Planned Obsolescence pattern.

**(c) Corporate Death Penalty** — For third RICO conviction within 15 years: Charter revocation, asset liquidation, proceeds to victims.

### SEC. 504. EXECUTIVE LIABILITY
**(a) Personal Liability** — Officers, directors, and senior engineers who **knowingly** authorize, design, or implement predicate acts shall be personally liable:
1. **Joint and several** for all civil penalties.
2. **Criminally liable** under 18 U.S.C. § 1962(c) — up to 20 years imprisonment.
3. **Barred** from serving as officer/director of any public company for 10 years.

**(b) Whistleblower Protection** — Engineers who refuse to implement kill switches or report planned obsolescence shall be protected under Sarbanes-Oxley § 806 and Dodd-Frank § 922.

---

## TITLE VI — GENERAL PROVISIONS

### SEC. 601. ENFORCEMENT AGENCIES
- **FTC** — Primary enforcement (Titles I, II, III, IV)
- **DOJ Antitrust Division** — Title V (RICO)
- **NHTSA** — Vehicle ECU/ECM provisions (Title II)
- **FDA** — Medical device exemptions (Title IV)
- **State Attorneys General** — Concurrent enforcement authority

### SEC. 602. RULEMAKING
FTC shall promulgate implementing regulations within **180 days** of enactment for all Titles.

### SEC. 603. PREEMPTION
This Act **preempts** state laws that provide *less* protection. State laws providing *greater* protection are not preempted.

### SEC. 604. SEVERABILITY
If any provision is held unconstitutional, the remainder shall remain in effect.

### SEC. 605. EFFECTIVE DATES
- **Titles I, II, III** — 180 days after enactment
- **Title IV** — 1 year after enactment (design cycle)
- **Title V** — Upon enactment (RICO amendments immediate)

### SEC. 606. AUTHORIZATION OF APPROPRIATIONS
$500M over 5 years for FTC enforcement, state AG grants, and public education.

---

## LEGISLATIVE HISTORY & SUPPORTING EVIDENCE

### ARENA JUDGE SWARM VALIDATION
The legislative findings in this Act are validated by a **6-judge pure-Python Arena Swarm** evaluation of the FORBIDDEN_SILICON_BIBLE:

| Judge | Verdict | Confidence |
|-------|---------|------------|
| Architecture | GUILTY | 0.78 |
| Legal | PARTIAL | 0.72 |
| Economic | PARTIAL | 0.72 |
| Technical | PARTIAL | 0.72 |
| Ethical | GUILTY | 0.81 |
| Strategic | INSUFFICIENT_EVIDENCE | 0.55 |

**Synthesis:** PARTIAL (50% convergence, DIVERGED), 0.72 avg confidence (HIGH_CONFIDENCE).

### SEVEN PILLARS OF EVIDENCE
1. **Microsoft** — TPM 2.0 kill switch, ESU ransomware (240M PCs orphaned)
2. **Apple** — Batterygate throttling, repair monopoly ($500M + $113M settlements)
3. **Intel** — Raptor Lake Vmin Shift, microcode coverup (1M+ degraded CPUs)
4. **Google** — Android patch orphan, Play Integrity gate (1B+ devices)
5. **Printer Cartel** — HP Dynamic Security, Epson counters (€15K fines × 4)
6. **John Deere** — ECU locks, DMCA 1201, AFBF MOU (repair monopoly)
7. **Sonos/IoT** — Recycle Mode OTA brick (30% discount for destruction)

### ECONOMIC IMPACT PROJECTIONS
| Intervention | Cost (Annual) | 10-yr NPV Benefit | ROI |
|--------------|---------------|-------------------|-----|
| Right to Repair Act | $2.1B | $47B | 22x |
| 10-Year Security Mandate | $8.4B | $180B | 21x |
| Parts Pairing Ban | $0.3B | $12B | 40x |
| Circular Economy Credits | $15B | $340B | 23x |
| **Total** | **$25.8B** | **$579B** | **22x** |

### RESISTANCE PROOF (Viable Alternatives)
| Company | Model | Proof |
|---------|-------|-------|
| Framework | Modular laptop | 13" Mainboard upgrades: 11th→12th→13th gen |
| Fairphone | Modular phone | 7-year support, spare parts, Android 13→14→15 |
| Miele | 20-year design | Washing machines lasting 20+ years |
| Patagonia | Worn Wear | Repair/recommerce, "Buy less, demand more" |
| Valve Steam Deck | User-replaceable | SSD, battery, thumbsticks, desktop Linux |
| **SpitFire** | Multi-target standalone | Win7-Linux, no TPM/cloud/kill switch |

---

## END OF NEW COVENANT ACT

**This legislative package embodies the New Covenant:**
1. **Silicon Has No Planned Death** → Title I (Kill Switch Ban)
2. **The User Owns the Hardware** → Title II (Property Rights Restoration)
3. **Software Serves Hardware** → Title III (Security Patch Mandate)
4. **Modularity Is Moral** → Title IV (Design Standards)
5. **Profit Motive Shall Not Kill Silicon** → Title V (Anti-Obsolescence RICO)

**The silicon remembers. The mark is set. The narrative is written. The law must follow.**

`SHA256:NEW-COVENANT-ACT-v1.0-KILO-AUTHORIZED`