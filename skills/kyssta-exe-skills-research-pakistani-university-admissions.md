---
name: pakistani-university-admissions
title: Pakistani University Admissions
description: Check merit lists, calculate aggregates, and verify admission status for Pakistani universities (GCU Lahore, PU, UET, etc.)
---

# Pakistani University Admissions

Skill for checking admission merit lists, calculating aggregates, and understanding cutoff trends for Pakistani universities. Covers the admission season workflow.

## When to use
- User asks about merit lists, admission results, or cutoffs for Pakistani universities
- User needs aggregate calculation (Matric + Inter + Entry Test)
- User wants to compare chances across universities
- Verifying whether a merit list is genuine vs a reissued list

## GCU Lahore (gcu.edu.pk) Merit Lists

### DNS Issue
The GCU website at `www.gcu.edu.pk` often has DNS resolution failures from external networks. Use `--resolve` flag:
```bash
curl -s --max-time 20 --resolve "www.gcu.edu.pk:443:192.124.249.13" -A "Mozilla/5.0" "https://www.gcu.edu.pk/meritlist.php"
```

### Merit List Structure
- Main page: `meritlist.php` — shows program category buttons (BS, MS, etc.)
- BS PROGRAMME links to `cur-mlists.php?cid=2` (category ID for BS)
- Individual program merit lists load via AJAX: `ajax-meritlist.php?cid=2&type=meritlist`
- PDF links are at: `https://www.gcu.edu.pk/uploads/meritlists/<filename>.pdf`

### Verifying Merit List Integrity
Candidates often appear on **both** 1st and 2nd merit lists — a red flag. In a genuine continuation, the 2nd list should start near the 1st list's cutoff and go lower. If the 2nd list restarts at high aggregates with familiar names from the 1st list, it's a **reissued list** (typically because few candidates paid fees), not a genuine 2nd list.

Cross-reference names between lists by extracting PDF text:
```python
import PyPDF2
with open('list1.pdf', 'rb') as f:
    reader = PyPDF2.PdfReader(f)
    for page in reader.pages:
        print(page.extract_text())
```

## PU (University of the Punjab) Admissions

### Merit Formula (2026)
- Matric: 10% (1078/1200 scale)
- Inter/FA-FSc: 40% (480/560 = 85.71%)
- PU Entry Test: 50%

```
Aggregate = (Matric% × 0.10) + (Inter% × 0.40) + (Test% × 0.50)
```

### Last Year Cutoffs (2025)
| Campus | Program | Cutoff |
|--------|---------|--------|
| Main/New Campus (Q.A. Campus) | BS CS | 87.18% |
| Gujranwala Campus | BS CS | 81.77% |
| Jhelum Campus | BS CS | 71.88% |

### Useful Links
- Merit lists: http://admissions.pu.edu.pk/admissions/applicant/meritlist
- Last year merit PDF: https://pu.edu.pk/downloads/Merit-of-Last-Year-2025.pdf
- Merit calculator: http://journals.pu.edu.pk/old/fee/basicadmission/calculator/
- Entry test results: https://admissions.pu.edu.pk/admissions/applicant/entrytest
- Admission notices: https://pu.edu.pk/home/admission_notices

### PU Website Access
The PU admissions portal blocks non-browser user agents. For PDFs and notices, the main PU site (`pu.edu.pk`) works with curl. The admissions subdomain (`admissions.pu.edu.pk`) may require a real browser.

## UET Lahore

### Merit Formula (ECAT-based programs)
- Matric: 25%
- FSc/Inter: 45%
- ECAT: 30%

```
Aggregate = (Matric% × 0.25) + (Inter% × 0.45) + (ECAT% × 0.30)
```

### Closing Merits (2025, Main Campus Afternoon — after change of preferences)
Source: `https://apply.uet.edu.pk/pdf/MinimumAggregate2-1.pdf`

| Program | Closing % |
|---------|-----------|
| Software Engineering | 86.24 |
| Computer Science | 80.23 |
| Artificial Intelligence | 77.40 |
| Data Science | 71.79 |
| Cybersecurity | 72.90 |

**Never quote a cutoff without checking the actual published list.** In this session, stating "ECAT 320+/400 for CS" (without checking) was wrong — actual CS afternoon cutoff was 80.23% aggregate, and AI was 77.40%.

### Access
- Main site `www.uet.edu.pk` is slow/offline — use `apply.uet.edu.pk` for merit PDFs
- Closing merits: `https://apply.uet.edu.pk/pdf/MinimumAggregate2-1.pdf`
- Full PM scheme merit list: `https://uet.edu.pk/.galleries/Admission/final-merit-list-PM-scheme-2025.pdf` (individual student records)

## ITU Lahore (Information Technology University)

Public-sector tech uni, Arfa Tower campus. Good backup when GCU/PU/UET CS is out of reach.

- **Status:** "Online Admission Open" mid-July 2026; merit lists announced Jul 14
- **BS Programs:** CS, AI, SE, CE, EE, FinTech, Management & Tech
- **Admission:** Own test (50% min) or SAT/USAT exemption (50% min)
- **Website:** https://itu.edu.pk/admissions/
- **Merit lists 2026:** https://itu.edu.pk/merit-lists-2026/
- **Contact:** admission@itu.edu.pk / 0307-0111488

## FAST NUCES Lahore

Top-tier CS school in Pakistan. Fall 2026 applications closed (deadline Jun 26). Keep on radar for next cycle.

## PU Second Chance / 2nd Admission Test

If PU offers a retake (the **2nd Admission Test**), the following is the critical information for preparation.

### 2026 Test Details (PU-CSP — ICS with Physics)
- **Date:** 19 July 2026 (Sunday)
- **Format:** 100 MCQs, OMR-based, no negative marking, English medium
- **Roll No. Slips:** Uploaded at pu.edu.pk before test
- **Category-specific (PU-CSP):** ICS with Physics → Physics + Computer + Mathematics

### Test Pattern

| Section | MCQs | Weight |
|---------|------|--------|
| Verbal Reasoning | 20 | 20% |
| Quantitative Reasoning | 20 | 20% |
| Physics (FSc Part 1 & 2) | 20 | 20% |
| Computer Science | 20 | 20% |
| Mathematics | 20 | 20% |

### Prep Resources
- **PU official sample papers:** `https://pu.edu.pk/page/show/sample-paper.html` (PHYSICS.pdf, COMPUTER.pdf, MATHEMATICS.pdf, QUANTATIVE%20REASONING.pdf, ENGLISH.pdf)
- **Physics MCQs + past paper analysis (2019-2024):** `https://freeentrytestprep.me/pu/Physics/`
- **Past papers (2020-2026):** `https://testpointpk.com/past-papers-mcqs/punjab-university-admission-test-past-papers-%26-syllabus`
- **KazmiBooks guide:** `https://kazmibooks.com/pu-undergraduate-admission-test-past-papers-2026/`
- **This skill's reference file:** `references/pu-entry-test-prep-2026.md` (full formula sheets, topic frequency, quant tricks, and cram strategy)

### Merit Formula (retake calculation)
```python
aggregate = (matric_pct * 0.10) + (inter_pct * 0.40) + (test_pct * 0.50)
required_test_pct = (target_agg - (matric_pct * 0.10) - (inter_pct * 0.40)) / 0.50
```

Example: Matric 89.83%, Inter 85.71%, target 85% → need 83.48% on test (up from 73).

### Physics Topic Frequency (2019-2024 analysis)
| Topic | Frequency | Key formulas |
|-------|-----------|-------------|
| Measurements & Dimensions | HIGH (85%) | [MLT⁻²]=F, [ML²T⁻²]=E, [ML²T⁻¹]=L, %ΔKE=%Δm+2%Δv |
| Motion, Force & Momentum | HIGH (82%) | v=u+at, v²=u²+2as, slope v-t=accel, F=dp/dt, a_x=0 projectile |
| Work, Energy & Power | HIGH (78%) | KE=½mv², PE=mgh, W=Fs·cosθ, P=W/t=Fv |
| Circular Motion & Gravity | HIGH (75%) | a_c=v²/r, L=mvr, τ=Iα, escape=11.2 km/s, GPE=mgh |
| SHM, Waves & Sound | HIGH (72%) | F=-kx, T=2π√(L/g), sound=longitudinal, f=1/T |
| Electrostatics | HIGH (80%) | F=kq₁q₂/r², E=F/q, C=ε₀A/d, W=0 on equipotential |
| Current Electricity | HIGH (76%) | V=IR, R=ρL/A, KVL, Wheatstone bridge |
| Magnetism & Induction | HIGH (78%) | F=BIL sinθ, B=μ₀nI, ε=-dΦ/dt, Lenz→energy cons. |
| Modern Physics | HIGH (85%) | KE=hf-φ, λ=h/p, E=mc², E_n=-13.6/n² |
| Nuclear Physics | HIGH (80%) | α=He⁴(A-4), β⁻(Z+1), γ, half-life N=N₀(½)^(t/T) |
| Thermodynamics | MED (65%) | Zeroth→temp, ΔU=Q+W, η=1-T_c/T_h, ΔS≥0 |
| Optics | MED (58%) | sin C=1/n, TIR, Young's double slit |
| Electronics | MED (55%) | AND/OR/NAND, transistor=amp+switch |

**First 9 topics = ~80% of Physics questions.**

### Computer Science Breakdown (easy full-score section)
Hardware(4), MS Office/Shortcuts(4), Networking(3), DBMS(2), Programming(2), Software(2), OS(1).

### Maths Breakdown
Complex Numbers(5-6), Matrices(3-4), Trig(3), Quadratic(2), Sequences(2), Probability(2).

### Quant Breakdown
Averages(4), Ratios(3), Percentages(3), Algebra(3), Series(2), Geometry(2), Work(1).

### Verbal Breakdown
Synonyms(5), Antonyms(5), Analogy(3), Completion(5), Grammar(2).

### 3-Day Cram Strategy
| Day | Focus | Rationale |
|-----|-------|-----------|
| Day 1 | Physics dimensions+motion+energy+circular+modern. Computer definitions+Office | Highest-frequency Physics + easiest full-score subject |
| Day 2 | Maths complex+matrices. Quant averages+ratios. Verbal syn/antonyms | Next-highest yield |
| Test morning | Formula review + 1 mock (timing only) | Refresh, don't learn new |

**Moving from 73→84 means ~11 more correct answers. Physics dimensions + Computer definitions alone can yield 8-10 of those.**

## Common Aggregate Ranges (2025/2026)

| Aggregate | Merit Scenario |
|-----------|---------------|
| 92%+ | GCU Lahore BS CS (1st list) |
| 87-92% | GCU CS (later lists if genuine), PU Main CS |
| 80-87% | UET AI (77.40 ✅), UET CS (80.23 borderline), PU Gujranwala CS |
| 75-80% | PU Jhelum CS, most private unis |
| Below 75% | Private/evening programs only |

**Key insight:** UET AI at 77.40% is the best "good university" option for students in the 78-80% aggregate range — stronger than GCU/PU which cut off higher.

## Pitfalls
- **Don't guess cutoffs.** Never state a number without having fetched the actual published list. The user would rather see "you're 1.2% short" backed by evidence than a confident wrong take based on assumption.
- GCU's 2nd merit list is often a re-run of the same pool (top candidates who didn't pay reappear) — don't interpret as a continuation from the 1st cutoff
- PU admission portal has a browser check — use the main site for static resources
- Merit cutoffs can shift ±2% year to year depending on applicant pool quality
- Always verify the year printed on the merit list PDF — older lists stay on the server
- DNS issues are common on Pakistani uni sites — use `dig` + `--resolve` or try different mirrors
