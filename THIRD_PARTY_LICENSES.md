# Third-Party Licenses & Level 1 SBOM — CleanMarkdown

**Document Version:** 1.0.0  
**Audited:** 2026-10-29  
**Repository:** `doc-bricks/CleanMarkdown`  
**License:** MIT  
**Zero-Copyleft Guarantee:** 100% Permissive (No AGPL, No GPL, PySide6 LGPL-3.0 dynamically linked)  
**Security Execution:** `RunAsInvoker` (Unprivileged User Mode)  
**Network Egress:** 100% Offline / Zero-Egress  

---

## 1. Executive Summary & Level 1 SBOM Compliance

`CleanMarkdown` is designed from the ground up for supply chain transparency, complete offline autonomy, and local-first productivity. It provides a distraction-free Markdown viewer and editor with live reading mode, raw syntax highlighting, image inspection, math preview, and vector PDF export.

- **Zero-Egress Isolation:** All operations execute locally on the host machine. No outbound sockets, telemetry, crash reporting, or remote APIs are invoked.
- **Level 1 SBOM Transparency:** Every direct, build, and development dependency is audited and cataloged with exact license attribution.
- **Non-Elevated Execution:** Operates strictly under standard unprivileged user mode (`RunAsInvoker`) without requiring administrator elevation.
- **Dual-Language & Ecosystem Aligned:** Part of the [`doc-bricks`](https://github.com/doc-bricks) document tooling suite under the [`open-bricks`](https://github.com/open-bricks) umbrella.

---

## 2. Invariant Cross-Reference Matrix (INV-LOCAL-01 to INV-SLA-10)

| Invariant ID | Name | Core Requirement | Verification Method | Status |
|---|---|---|---|---|
| **INV-LOCAL-01** | Zero-Egress Guarantee | No outbound network sockets, telemetry, or remote API calls. | Static inspection & hermetic unit test suite. | **VERIFIED** |
| **INV-LOCAL-02** | Non-Elevation (`RunAsInvoker`) | Strictly runs in unprivileged user mode; no root/admin required. | Security contract tests & execution audit. | **VERIFIED** |
| **INV-LOCAL-03** | Permissive Runtime Isolation | Core runtime uses MIT and BSD-3-Clause; PySide6 linked dynamically. | Static code analysis & package license audit. | **VERIFIED** |
| **INV-LOCAL-04** | Atomic Document Storage | File writes use atomic staging (`QSaveFile`) preventing data corruption. | Automated collision & atomic save tests. | **VERIFIED** |
| **INV-LOCAL-05** | Original Document Protection | PDF export rejects overwriting active Markdown source files. | Automated export protection tests. | **VERIFIED** |
| **INV-LOCAL-06** | CI Workflow Hardening | Timeout limits and concurrency cancellation enforced on all workflows. | Workflow schema checks in CI contract tests. | **VERIFIED** |
| **INV-LOCAL-07** | Multi-Host Sync Protection | `.gitignore` guards against multi-host conflict files and lock leaks. | Repository hygiene tests in `test_metadata.py`. | **VERIFIED** |
| **INV-LOCAL-08** | PEP 621 Standardisation | `pyproject.toml` fully compliant with modern standard metadata. | Metadata verification tests in `test_metadata.py`. | **VERIFIED** |
| **INV-LOCAL-09** | Version Parity & Immutability | Version `1.0.5` immutable and synchronized per T-20260920-167562623. | Cross-manifest parity tests in `test_metadata.py`. | **VERIFIED** |
| **INV-SLA-10** | Security Response SLA | 48h acknowledgment SLA and 5-day initial triage commitment. | Documented in `SECURITY.md` and contract tests. | **VERIFIED** |

---

## 3. Dependency Inventory & License Details

### 3.1 Runtime Dependencies

| Package | Version Range | License | Role / Purpose | Copyleft Compliance |
|---|---|---|---|---|
| `PySide6` | >=6.5.0,!=6.12.0 | LGPL-3.0-only | Official Python Qt bindings for desktop GUI | Dynamic linking (LGPLv3 § 4) |
| `shiboken6` | Companion | LGPL-3.0-only | CPython binding generator runtime | Dynamic linking |
| `Markdown` | >=3.4.0 | BSD-3-Clause | Core Markdown parsing and AST transformation | Permissive (No copyleft) |

### 3.2 Build & Packaging Dependencies

| Package | License | Upstream URL | Role / Purpose |
|---|---|---|---|
| `pyinstaller` | GPL-2.0-or-later WITH exception | https://pypi.org/project/pyinstaller/ | Application binary bundler (Special Exception) |
| `altgraph` | MIT | https://pypi.org/project/altgraph/ | Graph construction for module analysis |
| `pyinstaller-hooks-contrib` | Apache-2.0 | https://pypi.org/project/pyinstaller-hooks-contrib/ | Community hooks for PyInstaller |
| `packaging` | Apache-2.0 OR BSD-2-Clause | https://pypi.org/project/packaging/ | Python package version parsing utilities |

### 3.3 Development, Linting & Test Dependencies

| Package | Version Range | License | Upstream URL | Role / Purpose |
|---|---|---|---|---|
| `pytest` | >=9.1.1 | MIT | https://pypi.org/project/pytest/ | Test framework (CVE-2025-7117 mitigated) |
| `pluggy` | Standard | MIT | https://pypi.org/project/pluggy/ | Plugin management for pytest |
| `iniconfig` | Standard | MIT | https://pypi.org/project/iniconfig/ | Ini file parser for pytest configuration |
| `colorama` | Standard | BSD-3-Clause | https://pypi.org/project/colorama/ | Terminal color output |
| `ruff` | >=0.9.0 | MIT OR Apache-2.0 | https://pypi.org/project/ruff/ | Fast Python linter and formatter |

---

## 4. Statutory Disclaimer & Security SLA

- **Statutory Disclaimer (§ 521 BGB Gefälligkeitsrecht):** CleanMarkdown is provided free of charge as open-source software under the MIT License. In accordance with § 521 BGB, liability is limited to intent and gross negligence.
- **Security Response Target:** Critical vulnerabilities reported to `security@ellmos.ai`, `security@open-bricks.org`, or `support@lukasgeiger.com` are acknowledged within 48 hours, with triage completed within 5 business days.
