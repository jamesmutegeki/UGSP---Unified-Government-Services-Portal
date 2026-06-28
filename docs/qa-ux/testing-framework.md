# Beta & UX Testing Framework — [System/Product Name]

> **System-Neutral Reference Document**  
> Adapt placeholders (`[System/Product Name]`, `[Target Industry]`, etc.) to your project.

---

## 1. Testing Strategy & Objectives

### 1.1 Phase Distinction

| Phase | Primary Goal | Core Question | Typical Duration |
|---|---|---|---|
| **User Testing (Usability)** | Validate that target users can complete core tasks intuitively, without instruction or training. | *"Can a first-time user achieve their goal without error or confusion?"* | 2–4 weeks (iterative) |
| **Beta Testing (Stability & Real-World)** | Expose the system to uncontrolled environments, real data volumes, and unscripted workflows to surface edge cases, performance bottlenecks, and integration failures. | *"Does the system hold up under authentic conditions?"* | 4–8 weeks (phased) |

### 1.2 Exit Criteria (Go / No-Go Gates)

#### User Testing Exit Gate

| Metric | Target | Method |
|---|---|---|
| Task Success Rate (unassisted) | ≥ 85% | Observed sessions |
| Mean Time-on-Task | ≤ [X] seconds per core task | Session recording analytics |
| SUS Score | ≥ 75 / 100 | Post-test survey |
| Critical usability issues | 0 open | Severity matrix (see §5) |
| Major usability issues | ≤ 2 open | Severity matrix |

#### Beta Testing Exit Gate

| Metric | Target | Method |
|---|---|---|
| Crash-free session rate | ≥ 99.5% | Crash reporter / log aggregation |
| Critical / Blocker bugs | 0 open | Bug tracker |
| Major bugs | ≤ 3 open | Bug tracker |
| NPS (Net Promoter Score) | ≥ +30 | End-of-beta survey |
| Performance (P95 response) | ≤ [X] ms | APM / server logs |
| Data-loss / corruption incidents | 0 | Audit trail |

> **Decision Rule:** Both gates must pass. If User Testing fails, iterate design and re-test before opening Beta. If Beta fails, extend the Beta window; do not ship.

---

## 2. Participant Recruitment & Segmentation

### 2.1 Tester Profiles

| Profile | User Testing? | Beta Testing? | Description |
|---|---|---|---|
| **Novice / First-Time User** | Yes | Yes (subset) | No prior experience with `[System/Product Name]` or similar tools. |
| **Power User** | Yes | Yes | Daily-domain user; comfortable with complex workflows. |
| **Technical (IT/Admin)** | No | Yes | Evaluates installation, configuration, upgrades, permissions, scripting. |
| **Edge-Case Persona** | Yes (if available) | Yes | Low-vision, non-native language speaker, low-bandwidth connection, older adult, etc. |
| **Internal Stakeholder** | No | Closed Beta only | Product owner, SME, support lead — observes but does not vote on pass/fail. |

### 2.2 Sourcing Strategy

- **Existing customer / user base:** Email invitation with screener survey.
- **UserTesting / UserZoom / Respondent.io:** Paid panel for unmoderated sessions.
- **Social / community channels:** Discord, Reddit, LinkedIn, industry Slack groups.
- **Closed Beta waitlist:** In-app sign-up during alpha / pre-launch.

### 2.3 Engagement & Retention Tactics

| Tactic | User Testing | Beta Testing |
|---|---|---|
| Incentive (gift card / credit) | $[X] per 60-min session | $[X] per week + bonus for high-quality bug reports |
| Progress emails / check-ins | N/A | Weekly "What We Fixed" digest |
| Private community channel | N/A | `#beta-testers` in Slack / Discord |
| Recognition | Thank-you page + testimonial request | Leaderboard, "Top Bug Hunter" badge, early-access credit |
| 1:1 debrief | Optional | Required for churned testers |

---

## 3. User Testing (Usability) Framework

### 3.1 Session Structure (Moderated, 60 minutes)

| Segment | Duration | Activities |
|---|---|---|
| **Welcome & Consent** | 5 min | Explain purpose, confirm recording consent, reassure "we are testing the system, not you." |
| **Warm-Up / Background** | 5 min | Short interview: role, familiarity with similar tools, what they hope to achieve today. |
| **Core Tasks (3–5)** | 35 min | Participant performs tasks **unassisted**. Moderator does NOT lead; uses "What would you do next?" and "What are you thinking?" (think-aloud protocol). |
| **Post-Task Questions** | 5 min | After each task: "Was that easy or hard?" (Single Ease Question). |
| **Post-Test Interview** | 8 min | Overall impressions,最喜欢 features, biggest frustration, suggestions. Hand them the SUS survey. |
| **Wrap-Up** | 2 min | Thank participant, explain next steps, deliver incentive. |

### 3.2 Writing Unbiased Task Scenarios

**Bad (leading / biased):**
> "Click the Settings gear icon in the top-right corner, then select 'Export Data' from the dropdown."

**Good (goal-oriented, neutral):**
> "You need to download a copy of all your data from this system. Show me how you would do that."

**Principles:**
1. **Goal, not path** — describe the outcome, never the clicks.
2. **Scenario context** — give a believable real-world reason: *"Imagine you are preparing a quarterly report and need last month's sales figures."*
3. **No UI vocabulary** — avoid "menu," "button," "dropdown," "gear icon."
4. **No task interdependence** — each task must be completable independently of prior tasks.
5. **Pilot first** — run the scenario on a colleague to ensure it is not ambiguous.

### 3.3 What to Observe

| Observation | Record As |
|---|---|
| First click / navigation choice | Pass / Fail (correct first click) |
| Errors (wrong click, wrong input, submission failure) | Count + description |
| Hesitation / confusion | Timestamp + quote ("I'm not sure what to do here") |
| Recovery (did user self-correct?) | Yes / No + method |
| Facial expression / tone | Frustrated / Neutral / Delighted |
| Workaround (did user bypass intended flow?) | Description |

---

## 4. Beta Testing Execution Plan

### 4.1 Phased Rollout

```
Alpha (Internal QA) ──> Closed Beta (Invite-Only) ──> Open Beta (Public) ──> GA
       │                       │                           │
  2-4 wks                  3-4 wks                     2-4 wks
```

| Phase | Audience | Build Cadence | Communication |
|---|---|---|---|
| **Closed Beta** | 50–200 pre-screened users | Weekly (or faster for blockers) | Private channel + weekly digest |
| **Open Beta** | Unlimited (public link) | Bi-weekly | In-app banner + public changelog |

### 4.2 Rollout Checkpoints

Before each phase transition:

- [ ] All critical / blocker bugs from prior phase resolved.
- [ ] Crash-free rate ≥ 99.0%.
- [ ] No PII / security regressions.
- [ ] Monitoring and alerting configured for target scale.
- [ ] Support team briefed on known issues and response scripts.
- [ ] Rollback plan documented and tested.

### 4.3 Feedback Collection Loops

| Channel | What It Captures | Frequency |
|---|---|---|
| **In-app bug reporter** (shake / gesture / button) | Screenshot + logs + user description | Ad-hoc, user-initiated |
| **Feedback form** (qualitative) | Feature requests, general friction, NPS | Always-available link |
| **Weekly survey** (quantitative) | SUS, single-question satisfaction, "what broke this week" | Every Friday (5 min) |
| **Community channel (`#beta`)** | Real-time discussion, peer-supported workarounds | Continuous |
| **Automated telemetry** | Crash, performance (P50/P95/P99), feature usage frequency | Continuous |

### 4.4 Triage SLA

| Severity | Definition | Response Time | Fix Time |
|---|---|---|---|
| **S0 — Blocker** | Data loss, security breach, all users cannot log in. | Immediate (≤1 hour) | ≤ 24 hours |
| **S1 — Critical** | Core workflow (login, checkout, search) broken for subset of users. | ≤ 4 hours | ≤ 48 hours |
| **S2 — Major** | Non-core feature broken; acceptable workaround exists. | ≤ 24 hours | Next release |
| **S3 — Minor** | Cosmetic, typo, missing tooltip, rare edge case. | ≤ 1 week | Backlog |

---

## 5. Data Collection, Metrics & Analysis

### 5.1 Quantitative Metrics Dashboard

| Category | Metric | Collection Method | Target |
|---|---|---|---|
| **Usability** | Task Success Rate (TSR) | Observed / recorded session | ≥ 85% |
| **Usability** | Single Ease Question (SEQ) | Post-task 1–7 scale | ≥ 5.5 |
| **Usability** | System Usability Scale (SUS) | End-of-test 10-item survey | ≥ 75 |
| **Usability** | Time-on-Task (ToT) | Session recording timestamps | ≤ [X] s |
| **Usability** | Error Rate per Task | Observer coding | ≤ 2 / task |
| **Beta** | Crash-free Session Rate | Crash reporter | ≥ 99.5% |
| **Beta** | Daily Active Users (DAU) | Telemetry | ≥ [X] |
| **Beta** | P95 API Response Time | APM | ≤ [X] ms |
| **Beta** | Bug Report Volume | Bug tracker | Track trend |
| **Beta** | NPS | End-of-beta survey | ≥ +30 |

### 5.2 Qualitative Data Management

**Feedback Categorization Taxonomy**

```
┌─ Bug (confirmed defect)
│   ├─ Functional (feature does not work as specified)
│   ├─ Visual (layout, alignment, responsive break)
│   └─ Content (typo, wrong copy, broken link)
├─ Friction (works but felt wrong)
│   ├─ Performance (slow, laggy, janky)
│   ├─ UX (confusing label, hidden action, too many steps)
│   └─ Onboarding (setup difficult, missing guidance)
├─ Feature Request (new capability)
│   ├─ Must-Have (cannot ship without)
│   ├─ Nice-to-Have (improves experience)
│   └─ Future (out of current scope)
└─ Praise (what works well — preserve in next iteration)
```

**Tagging Process:**
1. Ingest all feedback into a single tracker (Notion / Airtable / GitHub Discussions).
2. Tag each item with category, severity, module, and tester cohort.
3. Weekly review: group duplicates, identify top-3 friction themes, escalate S0/S1.

### 5.3 Friction Score (Composite)

A blended metric to surface the most painful flows:

```
Friction Score = (Error Count × 3) + (Hesitation Count × 2) + (Negative Sentiment Count × 4)
```

Gather counts per screen / workflow during User Testing. Flows with Friction Score above `[threshold]` are re-designed before Beta.

---

## 6. Templates & Checklists

### 6.1 User Testing Task Scenario Template

```
─────────────────────────────────────────────
TASK [N] : [SHORT NAME]
─────────────────────────────────────────────

Scenario (read to participant):
  "[Real-world context sentence. State the goal, never the steps.]"

Success Criteria:
  □ Participant reaches [target state] within [X] seconds.
  □ Participant does NOT need moderator assistance.

Post-Task SEQ:
  "Overall, this task was..."  (1 = Very Difficult ... 7 = Very Easy)

Observer Notes:
  - First click / navigation choice: ____________ (correct / incorrect)
  - Errors: ____________
  - Hesitation points: ____________
  - Recovery (Y/N): ____________
  - Sentiment: ____________
  - Quote: "____________"
─────────────────────────────────────────────
```

### 6.2 Beta Bug / Feedback Report Form

```
─────────────────────────────────────────────
BUG / FEEDBACK REPORT
─────────────────────────────────────────────

Reporter Name / ID:  [______________]
Date:   [______________]
Build Version:  [______________]

Type:  □ Bug  □ Friction  □ Feature Request  □ Praise

Severity (Bug only):
  □ S0 – Blocker  □ S1 – Critical  □ S2 – Major  □ S3 – Minor

Title (one-line summary):
  [________________________________________________________]

Environment:
  OS / Browser:  [______________]
  Device:  [______________]
  Network (WiFi / 4G / Offline):  [______________]

Steps to Reproduce (Bug only):
  1. [______________]
  2. [______________]
  3. [______________]

Expected Result:
  [________________________________________________________]

Actual Result:
  [________________________________________________________]

Screenshot / Screen Recording:
  □ Attached  □ N/A

Suggested Fix (optional):
  [________________________________________________________]

─────────────────────────────────────────────
```

### 6.3 Go / No-Go Checklist (Final Deployment)

```
□ 1. ALL S0 (Blocker) bugs are resolved and verified.
□ 2. All S1 (Critical) bugs are resolved and verified.
□ 3. ≤ 3 open S2 (Major) bugs — none in core workflow.
□ 4. Crash-free session rate ≥ 99.5% over last 7 days.
□ 5. P95 response time ≤ [X] ms.
□ 6. No open security or PII findings.
□ 7. SUS ≥ 75 (User Testing) + NPS ≥ +30 (Beta).
□ 8. Rollback procedure documented and tested.
□ 9. Monitoring dashboards configured and alert thresholds set.
□ 10. Support team trained on known issues and escalation path.
□ 11. Changelog / release notes drafted and reviewed.
□ 12. Executive sign-off obtained.

DECISION:  □ GO  □ NO-GO (list blockers below)

Blockers:
  - [______________]
  - [______________]
─────────────────────────────────────────────
```

---

## Appendix A: Severity Matrix

| Severity | User Impact | Business Impact | Frequency |
|---|---|---|---|
| **S0 – Blocker** | Cannot complete core task; data loss | Revenue loss, regulatory non-compliance | Affects all users |
| **S1 – Critical** | Core task severely degraded | High support volume, churn risk | Affects ≥ 10% of users |
| **S2 – Major** | Non-core task broken; workaround exists | Moderate support impact | Affects 1–10% |
| **S3 – Minor** | Cosmetic, rare edge case | Low or no business impact | Affects < 1% |

## Appendix B: Recommended Tool Stack (System-Neutral)

| Function | Tool Options |
|---|---|
| User session recording | Hotjar, FullStory, LogRocket, Smartlook |
| Unmoderated usability testing | UserTesting, Maze, UserZoom, Lookback |
| Bug tracking | GitHub Issues, Jira, Linear, Sentry |
| Beta tester management | TestFlight (iOS), Google Play Console (Android), LaunchDarkly, Firebase |
| Survey (SUS, NPS) | Typeform, SurveyMonkey, Google Forms |
| Community / communication | Discord, Slack, Circle, GitHub Discussions |
| APM / crash reporting | Sentry, Datadog, New Relic, Grafana |
| Prototype testing | Figma (prototype mode), Axure, Balsamiq |
