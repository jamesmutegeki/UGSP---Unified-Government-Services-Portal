"""
Seed script — populates UGSP with 15 diverse users, sample applications, payments, and notifications.
Run against a running server: python seed.py
"""
import urllib.request, json, sys, time

BASE = "http://localhost:8000"

stats = {"passed": 0, "failed": 0, "warnings": []}


def api(method, path, body=None, token=None, raw=False):
    data = json.dumps(body).encode() if body else None
    headers = {"Content-Type": "application/json"} if body else {}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(f"{BASE}{path}", data=data, headers=headers, method=method)
    try:
        r = urllib.request.urlopen(req, timeout=10)
        content = r.read()
        if raw:
            return content
        return json.loads(content)
    except urllib.error.HTTPError as e:
        detail = e.read().decode()
        try:
            return {"error": True, "status": e.code, "detail": json.loads(detail)}
        except json.JSONDecodeError:
            return {"error": True, "status": e.code, "detail": detail}
    except Exception as e:
        return {"error": True, "detail": str(e)}


def log(step, ok, detail=""):
    status = "PASS" if ok else "FAIL"
    print(f"  [{status}] {step}" + (f" -- {detail}" if detail else ""))
    if ok:
        stats["passed"] += 1
    else:
        stats["failed"] += 1
        stats["warnings"].append(step)


SEED_USERS = [
    {"nin": "T1000000001", "name": "Amos Muwonge", "email": "amos.muwonge@example.ug", "phone": "+256701000001", "category": "citizen", "password": "seed123"},
    {"nin": "T1000000002", "name": "Faith Nakato", "email": "faith.nakato@example.ug", "phone": "+256701000002", "category": "citizen", "password": "seed123"},
    {"nin": "T1000000003", "name": "Peter Kaggwa", "email": "peter.kaggwa@example.ug", "phone": "+256701000003", "category": "business", "password": "seed123"},
    {"nin": "T1000000004", "name": "Sarah Kyomuhangi", "email": "sarah.kyo@example.ug", "phone": "+256701000004", "category": "citizen", "password": "seed123"},
    {"nin": "T1000000005", "name": "David Okwir", "email": "david.okwir@example.ug", "phone": "+256701000005", "category": "citizen", "password": "seed123"},
    {"nin": "T1000000006", "name": "Grace Achieng", "email": "grace.achieng@example.ug", "phone": "+256701000006", "category": "visitor", "password": "seed123"},
    {"nin": "T1000000007", "name": "Joseph Ssewanyana", "email": "joseph.ssewa@example.ug", "phone": "+256701000007", "category": "business", "password": "seed123"},
    {"nin": "T1000000008", "name": "Rebecca Namatovu", "email": "rebecca.nama@example.ug", "phone": "+256701000008", "category": "citizen", "password": "seed123"},
    {"nin": "T1000000009", "name": "Hassan Mbowa", "email": "hassan.mbowa@example.ug", "phone": "+256701000009", "category": "business", "password": "seed123"},
    {"nin": "T1000000010", "name": "Micheal Ochen", "email": "micheal.ochen@example.ug", "phone": "+256701000010", "category": "citizen", "password": "seed123"},
    {"nin": "T1000000011", "name": "Jane Atim", "email": "jane.atim@example.ug", "phone": "+256701000011", "category": "citizen", "password": "seed123"},
    {"nin": "T1000000012", "name": "Robert Mugisha", "email": "robert.mugisha@example.ug", "phone": "+256701000012", "category": "visitor", "password": "seed123"},
    {"nin": "T1000000013", "name": "Doreen Nansubuga", "email": "doreen.nansu@example.ug", "phone": "+256701000013", "category": "citizen", "password": "seed123"},
    {"nin": "T1000000014", "name": "Samuel Ouma", "email": "samuel.ouma@example.ug", "phone": "+256701000014", "category": "business", "password": "seed123"},
    {"nin": "T1000000015", "name": "Esther Nambi", "email": "esther.nambi@example.ug", "phone": "+256701000015", "category": "citizen", "password": "seed123"},
]

SERVICE_CATEGORIES = ["citizen", "business", "visitor", "health", "education", "financial", "environmental"]

# Application templates per category
CATEGORY_SERVICES = {
    "citizen": [1, 2, 5, 8, 10, 12, 13, 14],
    "business": [3, 4, 7, 11],
    "visitor": [6, 9, 17],
    "health": [18, 19, 20],
    "education": [21, 22, 23],
    "financial": [24, 25, 26],
    "environmental": [27, 28, 29],
}


def main():
    print(f"\n{'='*60}")
    print("  UGSP — Sample Data Seeder")
    print(f"{'='*60}\n")

    # 0. Health check
    print("[0] Checking server health...")
    r = api("GET", "/api/health")
    if r.get("status") == "ok":
        log("Server is running", True, f"v{r.get('version','?')}")
    else:
        log("Server unreachable", False, str(r))
        sys.exit(1)

    # 1. Register 15 users
    print("\n[1] Registering 15 sample users...")
    tokens = {}
    for u in SEED_USERS:
        r = api("POST", "/auth/register", u)
        if "token" in r:
            tokens[u["nin"]] = r["token"]
            log(f"Registered {u['name']} ({u['nin']}, {u['category']})", True)
        elif r.get("status") == 409:
            # Already exists — log in
            r2 = api("POST", "/auth/login", {"nin": u["nin"], "password": u["password"]})
            if "token" in r2:
                tokens[u["nin"]] = r2["token"]
                log(f"Login {u['name']} (already registered)", True)
            else:
                log(f"Login {u['name']} failed", False, str(r2))
        else:
            log(f"Register {u['name']} failed", False, str(r))

    # 2. Verify notifications work
    print("\n[2] Verifying notifications...")
    for nin, tok in list(tokens.items())[:3]:
        r = api("GET", "/auth/notifications", token=tok)
        if isinstance(r, list):
            log(f"Notifications for {nin}: {len(r)} items", True)
        else:
            log(f"Notifications for {nin}", False, str(r))

    # 3. Verify service catalogue
    print("\n[3] Verifying service catalogue...")
    for cat in SERVICE_CATEGORIES:
        r = api("GET", f"/catalogue?category={cat}")
        if isinstance(r, list):
            log(f"Category '{cat}': {len(r)} services", True)
        else:
            log(f"Category '{cat}'", False, str(r))

    # 4. Create applications for each user
    print("\n[4] Creating sample applications...")
    apps_created = 0
    for nin, tok in tokens.items():
        user = next(u for u in SEED_USERS if u["nin"] == nin)
        cat = user["category"]
        service_ids = CATEGORY_SERVICES.get(cat, [1])
        # Apply for 2-3 services per user
        for sid in service_ids[:3]:
            r = api("POST", "/applications", {"service_id": sid, "metadata": {"source": "seed"}}, token=tok)
            if "application_id" in r:
                apps_created += 1
    log(f"Applications created: {apps_created}", True)

    # 5. Process payments for fee-based services
    print("\n[5] Processing sample payments...")
    for nin, tok in tokens.items():
        apps = api("GET", "/applications", token=tok)
        if not isinstance(apps, list):
            continue
        for app in apps[:1]:
            sid = app.get("service_id", 1)
            fee_map = {1: 50000, 2: 250000, 3: 150000, 5: 180000, 7: 20000, 8: 75000,
                       9: 500000, 10: 30000, 11: 120000, 12: 55000, 15: 50000, 16: 300000,
                       17: 200000, 20: 15000, 23: 100000, 25: 25000, 27: 50000, 28: 75000, 29: 150000}
            fee = fee_map.get(sid, 0)
            if fee > 0:
                r = api("POST", "/payments/checkout", {"service_id": sid, "amount": fee, "channel": "mobile_money"}, token=tok)
                if "prn" in r:
                    log(f"Payment PRN for {nin}: {r['prn']}", True)
    log("Payment processing complete", True)

    # 6. Verify forgot password flow
    print("\n[6] Testing forgot password flow...")
    r = api("POST", "/auth/forgot-password", {"nin": "T1000000001"})
    if "reset code" in str(r).lower() or "RESET" in str(r):
        log("Forgot password step 1 (send code)", True)
        code = r.get("message", "").split(": ")[-1].strip()
        # Step 2: reset
        r2 = api("POST", "/auth/reset-password", {"nin": "T1000000001", "reset_code": code, "new_password": "newseed123"})
        if "Password reset" in str(r2):
            log("Forgot password step 2 (reset with code)", True)
        else:
            log("Forgot password step 2", False, str(r2))
    else:
        log("Forgot password step 1", False, str(r))

    # 7. Verify search works across categories
    print("\n[7] Testing cross-category search...")
    terms = ["passport", "tax", "health", "school", "loan", "permit", "NIRA", "NSSF"]
    for term in terms:
        r = api("GET", f"/catalogue/search?q={term}")
        if isinstance(r, list):
            log(f"Search '{term}': {len(r)} results", True)
        else:
            log(f"Search '{term}'", False, str(r))

    # 8. Verify ministries
    print("\n[8] Testing ministries endpoint...")
    r = api("GET", "/catalogue/ministries")
    if isinstance(r, list):
        log(f"Ministries directory: {len(r)} entries", True)
    else:
        log("Ministries directory", False, str(r))

    # 9. Profile check for each category type
    print("\n[9] Verifying profile for each user category...")
    cat_checked = set()
    for nin, tok in tokens.items():
        user = next(u for u in SEED_USERS if u["nin"] == nin)
        if user["category"] not in cat_checked:
            r = api("GET", "/auth/profile", token=tok)
            if "name" in r:
                log(f"Profile for {user['category']} user: {r['name']}", True)
                cat_checked.add(user["category"])
            else:
                log(f"Profile for {user['category']}", False, str(r))

    print(f"\n{'='*60}")
    print(f"  SEEDING COMPLETE")
    print(f"  Passed: {stats['passed']}  Failed: {stats['failed']}")
    if stats["warnings"]:
        print(f"  Warnings: {len(stats['warnings'])}")
    print(f"{'='*60}\n")
    print("Demo credentials:")
    print("  NIN: T1234567890  /  pass123  (Grace Akello, pre-seeded)")
    print("  NIN: T1000000001  /  newseed123  (Amos Muwonge, seeded)")
    print("  NIN: T1000000003  /  seed123  (Peter Kaggwa, business)")
    print("  NIN: T1000000006  /  seed123  (Grace Achieng, visitor)")


if __name__ == "__main__":
    main()
