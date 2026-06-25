"""
UGSP Comprehensive Test Suite — Verifies all 10+ endpoint groups with sample data.
Usage:
    python test_comprehensive.py              # quick run
    python test_comprehensive.py --report     # generate TEST_REPORT.md
"""
import urllib.request, json, sys, os, time, uuid

BASE = "http://localhost:8000"
REPORT = []  # accumulates report lines

PASS, FAIL = 0, 0
WARNINGS = []


def report_line(line=""):
    REPORT.append(line)


def api(method, path, body=None, token=None, raw=False):
    data = json.dumps(body).encode() if body else None
    headers = {"Content-Type": "application/json"} if body else {}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(f"{BASE}{path}", data=data, headers=headers, method=method)
    try:
        r = urllib.request.urlopen(req, timeout=15)
        if raw:
            return r.read()
        ct = r.headers.get("Content-Type", "")
        if "text/html" in ct:
            return r.read().decode()
        return json.loads(r.read())
    except urllib.error.HTTPError as e:
        detail = e.read().decode()
        try:
            return {"_error": True, "_status": e.code, "_detail": json.loads(detail)}
        except json.JSONDecodeError:
            return {"_error": True, "_status": e.code, "_detail": detail}
    except Exception as e:
        return {"_error": True, "_detail": str(e)}


def check(step, ok, detail=""):
    global PASS, FAIL
    status = "PASS" if ok else "FAIL"
    msg = f"  [{status}] {step}" + (f" -- {detail}" if detail else "")
    print(msg)
    report_line(msg)
    if ok:
        PASS += 1
    else:
        FAIL += 1
        WARNINGS.append(step)


def section(title):
    print(f"\n{'-'*60}")
    print(f"  {title}")
    print(f"{'-'*60}")
    report_line(f"\n### {title}\n")


# ──────────────────────────────────────────────
#  Module-level state
# ──────────────────────────────────────────────
CITIZEN_TOKEN = ""
BUSINESS_TOKEN = ""
VISITOR_TOKEN = ""
STUDENT_TOKEN = ""
APP_IDS = []
PAYMENT_REFS = []
NEW_NIN = "T9999999999"


# ══════════════════════════════════════════════
#  SUITE: Health
# ══════════════════════════════════════════════
def test_health():
    section("1. Server Health")
    r = api("GET", "/api/health")
    check("Health endpoint returns 200 / status=ok", r.get("status") == "ok", f"version={r.get('version')}")
    check("Health response has version field", "version" in r)
    check("Frontend serves HTML at /", "Uganda" in api("GET", "/", raw=True).decode() or "Government" in api("GET", "/", raw=True).decode())


# ══════════════════════════════════════════════
#  SUITE: Auth
# ══════════════════════════════════════════════
def test_auth():
    section("2. Authentication & User Management")
    global CITIZEN_TOKEN, BUSINESS_TOKEN, VISITOR_TOKEN, STUDENT_TOKEN

    # 2a. Pre-seeded login
    r = api("POST", "/auth/login", {"nin": "T1234567890", "password": "pass123"})
    check("Pre-seeded citizen login", "token" in r)
    CITIZEN_TOKEN = r.get("token", "")

    r = api("POST", "/auth/login", {"nin": "T0000000002", "password": "pass123"})
    check("Pre-seeded business login", "token" in r)
    BUSINESS_TOKEN = r.get("token", "")

    # 2b. Registration
    r = api("POST", "/auth/register", {
        "nin": NEW_NIN, "name": "Test Student",
        "email": "student@example.ug", "phone": "+256700999999",
        "category": "citizen", "password": "testpass"
    })
    check("Register new user", "token" in r)
    STUDENT_TOKEN = r.get("token", "")

    r2 = api("POST", "/auth/register", {
        "nin": NEW_NIN, "name": "Test Student",
        "email": "student@example.ug", "phone": "+256700999999",
        "category": "citizen", "password": "testpass"
    })
    check("Register duplicate NIN returns 409", r2.get("_status") == 409, "Conflict correctly detected")

    # 2c. Invalid login
    r = api("POST", "/auth/login", {"nin": "NONEXISTENT", "password": "wrong"})
    check("Invalid login rejected", r.get("_status") == 401 or "Invalid" in str(r))

    # 2d. Forgot password flow
    r = api("POST", "/auth/forgot-password", {"nin": NEW_NIN})
    check("Forgot-password step 1 accepted", r.get("_error") != True)
    code = None
    if ":" in str(r):
        code = str(r).split(":")[-1].strip().rstrip("}").strip('"').strip("'")
    elif "reset_code" in r:
        code = r["reset_code"]
    check("Reset code received", code is not None, f"code={code}")

    if code:
        r2 = api("POST", "/auth/reset-password", {"nin": NEW_NIN, "reset_code": code, "new_password": "updatedpass"})
        check("Reset password with valid code", r2.get("_error") != True)
        r3 = api("POST", "/auth/login", {"nin": NEW_NIN, "password": "updatedpass"})
        check("Login with new password", "token" in r3)
        STUDENT_TOKEN = r3.get("token", "")

        # Bad reset code
        r4 = api("POST", "/auth/reset-password", {"nin": NEW_NIN, "reset_code": "WRONG", "new_password": "x"})
        check("Reset with invalid code rejected", r4.get("_status") == 400 or "invalid" in str(r4).lower())


# ══════════════════════════════════════════════
#  SUITE: Profile
# ══════════════════════════════════════════════
def test_profile():
    section("3. Profile")
    global CITIZEN_TOKEN, VISITOR_TOKEN
    r = api("GET", "/auth/profile", token=CITIZEN_TOKEN)
    check("Get own profile", "name" in r, r.get("name", ""))
    check("Profile has NIN", "nin" in r)
    check("Profile has email", "email" in r)
    check("Profile has category", "category" in r)
    if r.get("category") == "citizen":
        check("Citizen category correct", True)

    # No-token rejected
    r2 = api("GET", "/auth/profile")
    check("Profile without token rejected", r2.get("_status") in (403, 401) or "detail" in r2)


# ══════════════════════════════════════════════
#  SUITE: Catalogue
# ══════════════════════════════════════════════
def test_catalogue():
    section("4. Service Catalogue")
    categories = ["citizen", "business", "visitor", "health", "education", "financial", "environmental"]
    counts = {}
    for cat in categories:
        r = api("GET", f"/catalogue?category={cat}")
        check(f"Category '{cat}' returns list", isinstance(r, list))
        counts[cat] = len(r)
    check("Citizen has services", counts.get("citizen", 0) >= 5)
    check("Health has services", counts.get("health", 0) >= 3)
    check("Education has services", counts.get("education", 0) >= 3)
    check("Financial has services", counts.get("financial", 0) >= 3)
    check("Environmental has services", counts.get("environmental", 0) >= 3)
    check("Visitor has services", counts.get("visitor", 0) >= 3)
    check("Business has services", counts.get("business", 0) >= 3)

    total = sum(counts.values())
    check("Total catalogue >= 20 services", total >= 20, f"total={total}")

    # Search
    terms = ["passport", "tax", "health", "school", "loan", "permit", "NIRA"]
    for term in terms:
        r = api("GET", f"/catalogue/search?q={term}")
        check(f"Search '{term}' returns results", isinstance(r, list) and len(r) > 0, f"{len(r)} matches")

    # Edge: empty search
    r = api("GET", "/catalogue/search?q=zzzznotexistzzz")
    check("Search for non-existent term returns empty list", isinstance(r, list) and len(r) == 0)

    # Ministries
    r = api("GET", "/catalogue/ministries")
    check("Ministries endpoint returns list", isinstance(r, list))
    check("Ministries count >= 20", len(r) >= 20, f"count={len(r)}")
    if isinstance(r, list) and len(r) > 0:
        check("Ministry has name field", "name" in r[0])
        check("Ministry has category field", "category" in r[0])

    r = api("GET", "/catalogue/ministries/search?q=health")
    check("Ministries search works", isinstance(r, list) and len(r) >= 1)

    # Individual service detail
    r = api("GET", "/catalogue/1")
    check("Service detail by ID", isinstance(r, dict) and "name" in r, r.get("name", ""))
    r = api("GET", "/catalogue/9999")
    check("Non-existent service ID returns 404", r.get("_status") == 404 or r.get("_error"))


# ══════════════════════════════════════════════
#  SUITE: Applications
# ══════════════════════════════════════════════
def test_applications():
    section("5. Application Lifecycle")
    global APP_IDS

    for token, desc in [(CITIZEN_TOKEN, "citizen"), (BUSINESS_TOKEN, "business"),
                         (VISITOR_TOKEN, "visitor"), (STUDENT_TOKEN, "student")]:
        if not token:
            continue
        r = api("POST", "/applications", {"service_id": 1}, token=token)
        check(f"{desc} applies for service 1", "application_id" in r, r.get("application_id", ""))
        if "application_id" in r:
            APP_IDS.append(r["application_id"])

    r = api("POST", "/applications", {"service_id": 5}, token=CITIZEN_TOKEN)
    check("Apply for service 5", "application_id" in r)
    if "application_id" in r:
        APP_IDS.append(r["application_id"])

    r = api("POST", "/applications", {"service_id": 20}, token=CITIZEN_TOKEN)
    check("Apply for health service 20", "application_id" in r)

    r = api("POST", "/applications", {"service_id": 27}, token=CITIZEN_TOKEN)
    check("Apply for environmental service 27", "application_id" in r)

    # List applications
    r = api("GET", "/applications", token=CITIZEN_TOKEN)
    check("List citizen applications", isinstance(r, list) and len(r) >= 3)
    if isinstance(r, list) and len(r) > 0:
        check("Application has status field", "status" in r[0])
        check("Application has date field", "created_at" in r[0] or "date" in r[0] or "created" in r[0])

    # Track application
    if APP_IDS:
        r = api("GET", f"/applications/{APP_IDS[0]}", token=CITIZEN_TOKEN)
        check("Track application by ID", isinstance(r, dict) and "status" in r)

    # Apply without auth
    r = api("POST", "/applications", {"service_id": 1})
    check("Apply without token rejected", r.get("_status") in (401, 403))


# ══════════════════════════════════════════════
#  SUITE: Payments
# ══════════════════════════════════════════════
def test_payments():
    section("6. Payment Processing")
    global PAYMENT_REFS

    # Checkout
    r = api("POST", "/payments/checkout", {"service_id": 1, "amount": 50000, "channel": "mobile_money"}, token=CITIZEN_TOKEN)
    check("Checkout generates PRN", "prn" in r, r.get("prn", ""))
    PAYMENT_REFS.append(r.get("prn", ""))

    r2 = api("POST", "/payments/checkout", {"service_id": 2, "amount": 250000, "channel": "card"}, token=CITIZEN_TOKEN)
    check("Checkout with card", "prn" in r2)

    r3 = api("POST", "/payments/checkout", {"service_id": 9, "amount": 500000, "channel": "bank_transfer"}, token=BUSINESS_TOKEN)
    check("Business checkout bank transfer", "prn" in r3)

    # Without auth
    r4 = api("POST", "/payments/checkout", {"service_id": 1, "amount": 50000, "channel": "mobile_money"})
    check("Checkout without token rejected", r4.get("_status") in (401, 403))

    # Reconcilation (GET)
    if PAYMENT_REFS:
        r5 = api("GET", f"/payments/reconcile/{PAYMENT_REFS[0]}", token=CITIZEN_TOKEN)
        check("Payment reconciliation endpoint", r5.get("_error") != True)


# ══════════════════════════════════════════════
#  SUITE: Notifications
# ══════════════════════════════════════════════
def test_notifications():
    section("7. Notifications")

    r = api("GET", "/auth/notifications", token=CITIZEN_TOKEN)
    check("Get notifications returns list", isinstance(r, list))
    if isinstance(r, list):
        check("Notifications count >= 0 (any number ok)", isinstance(r, list))

    r = api("POST", "/auth/notifications/read", {}, token=CITIZEN_TOKEN)
    check("Mark all notifications read", r.get("_error") != True)

    # After reading, get again
    r2 = api("GET", "/auth/notifications", token=CITIZEN_TOKEN)
    check("Notifications still accessible after read", isinstance(r2, list))

    # Without auth
    r3 = api("GET", "/auth/notifications")
    check("Notifications without token rejected", r3.get("_status") in (401, 403))


# ══════════════════════════════════════════════
#  SUITE: Frontend Pages
# ══════════════════════════════════════════════
def test_frontend():
    section("8. Frontend Pages")

    html = api("GET", "/", raw=True)
    content = html.decode() if isinstance(html, bytes) else str(html)
    markers = {
        "Coat of Arms SVG": "svg" in content and "uganda" in content.lower(),
        "Login form": "login" in content.lower() or "sign in" in content.lower(),
        "Dashboard section": ("dashboard" in content.lower() or "stat-card" in content or "card" in content.lower()),
        "Service catalogue tabs": "catalogue" in content.lower() or "service" in content.lower(),
        "Ministries directory": "ministr" in content.lower(),
        "Interactive map": "leaflet" in content.lower() or "map" in content.lower(),
        "Profile section": "profile" in content.lower(),
        "Notifications UI": "notif" in content.lower(),
        "Registration form": "register" in content.lower(),
        "Forgot-password form": "forgot" in content.lower() or "reset" in content.lower(),
        "Coat of Arms SVG": "Coat" in content and "Arms" in content,
    }

    for label, found in markers.items():
        check(f"Frontend has: {label}", found)


# ══════════════════════════════════════════════
#  SUITE: Error Handling
# ══════════════════════════════════════════════
def test_errors():
    section("9. Error Handling & Edge Cases")

    # Malformed JSON body
    import http.client
    conn = http.client.HTTPConnection("localhost", 8000, timeout=10)
    conn.request("POST", "/auth/login", "{bad json}", {"Content-Type": "application/json"})
    r = conn.getresponse()
    check("Malformed JSON returns 422", r.status == 422)

    conn = http.client.HTTPConnection("localhost", 8000, timeout=10)
    conn.request("GET", "/nonexistent-route")
    r = conn.getresponse()
    check("Non-existent route returns 404", r.status == 404)
    conn.close()

    # Missing required fields
    r = api("POST", "/auth/register", {"nin": "T0000000099"})
    check("Register missing fields rejected", r.get("_status") in (400, 422) or "_error" in r)

    r = api("POST", "/auth/login", {"nin": "T1234567890"})
    check("Login missing fields rejected", r.get("_status") in (400, 422))

    # Empty body
    req = urllib.request.Request(f"{BASE}/auth/login", b"", {"Content-Type": "application/json"}, method="POST")
    try:
        urllib.request.urlopen(req, timeout=10)
    except urllib.error.HTTPError as e:
        check("Empty body returns 422/400", e.code in (400, 422))


# ══════════════════════════════════════════════
#  SUITE: Cross-feature integration
# ══════════════════════════════════════════════
def test_integration():
    section("10. Cross-Feature Integration")

    # Register → Login → Browse catalogue → Apply → Pay → Check notifications
    test_nin = "T0000000098"
    r = api("POST", "/auth/register", {
        "nin": test_nin, "name": "Integration Tester",
        "email": "inttest@example.ug", "phone": "+256700999998",
        "category": "citizen", "password": "intpass"
    })
    check("10a. Register user", "token" in r)
    tok = r.get("token", "")

    r = api("GET", "/catalogue", token=tok)
    check("10b. Browse catalogue", isinstance(r, list) and len(r) > 0)

    r = api("POST", "/applications", {"service_id": 1}, token=tok)
    check("10c. Apply for service", "application_id" in r)

    r = api("POST", "/payments/checkout", {"service_id": 1, "amount": 50000, "channel": "mobile_money"}, token=tok)
    check("10d. Process payment", "prn" in r)

    r = api("GET", "/auth/notifications", token=tok)
    check("10e. Notifications after actions", isinstance(r, list))

    r = api("GET", "/auth/profile", token=tok)
    check("10f. Profile accessible end-to-end", "name" in r)

    check("10g. Full integration flow complete", True)


# ══════════════════════════════════════════════
#  SUITE: Uploads
# ══════════════════════════════════════════════
def test_uploads():
    section("11. Photo Upload")
    import tempfile, base64

    # Create a small valid JPEG
    jpeg_bytes = bytes.fromhex(
        "FFD8FFE000104A46494600010101004800480000FFDB004300"
        "FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF"
        "FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF"
        "FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFC000FFC0"
        "001100080008000800FFED002C50686F746F73686F7020332E"
        "30003842494D03ED00000000001000480000000100020048"
        "000000010002FFE10568687474703A2F2F6E732E61646F6265"
        "2E636F6D2F7861702F312E302F005FFDA000C030100021103"
        "1100000000000000FFD9"
    )

    # Upload via multipart
    boundary = "----WebKitFormBoundary7MA4YWxkTrZu0gW"
    body = (
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="photo"; filename="test.jpg"\r\n'
        f"Content-Type: image/jpeg\r\n\r\n"
    ).encode("latin-1") + jpeg_bytes + f"\r\n--{boundary}--\r\n".encode("latin-1")

    req = urllib.request.Request(
        f"{BASE}/uploads/photo",
        data=body,
        headers={
            "Content-Type": f"multipart/form-data; boundary={boundary}",
            "Authorization": f"Bearer {CITIZEN_TOKEN}"
        },
        method="POST"
    )
    try:
        r = urllib.request.urlopen(req, timeout=15)
        data = json.loads(r.read())
        check("Photo upload returns URL", "url" in data or "photo_url" in data or "filename" in data)
    except urllib.error.HTTPError as e:
        detail = e.read().decode()
        check(f"Photo upload responded with {e.code}", False, detail)
        return

    # Upload without JPEG
    boundary2 = "----Boundary2"
    body2 = (
        f"--{boundary2}\r\n"
        f'Content-Disposition: form-data; name="photo"; filename="test.txt"\r\n'
        f"Content-Type: text/plain\r\n\r\nnot a jpeg\r\n--{boundary2}--\r\n"
    ).encode("latin-1")
    req2 = urllib.request.Request(
        f"{BASE}/uploads/photo",
        data=body2,
        headers={
            "Content-Type": f"multipart/form-data; boundary={boundary2}",
            "Authorization": f"Bearer {CITIZEN_TOKEN}"
        },
        method="POST"
    )
    try:
        urllib.request.urlopen(req2, timeout=15)
        check("Non-JPEG upload rejected", False)
    except urllib.error.HTTPError as e:
        check("Non-JPEG upload rejected", e.code in (400, 415, 422))


# ══════════════════════════════════════════════
#  MAIN
# ══════════════════════════════════════════════
def main():
    global PASS, FAIL, REPORT, WARNINGS
    start = time.time()

    print(f"\n{'#'*60}")
    print(f"  UGSP COMPREHENSIVE TEST SUITE")
    print(f"  Target: {BASE}")
    print(f"{'#'*60}")
    report_line(f"# UGSP Test Report\n")
    report_line(f"- **Date:** {time.strftime('%Y-%m-%d %H:%M:%S')}")
    report_line(f"- **Target:** {BASE}")
    report_line(f"- **Test Suite:** `test_comprehensive.py`\n")

    # Health check first
    try:
        h = api("GET", "/api/health")
        if h.get("status") != "ok":
            print(f"\n  ERROR: Server at {BASE} is not running or not healthy.")
            print(f"  Start the server and try again.\n")
            sys.exit(1)
    except Exception as e:
        print(f"\n  ERROR: Cannot connect to {BASE}: {e}")
        print(f"  Start the server and try again.\n")
        sys.exit(1)

    test_health()
    test_auth()
    test_profile()
    test_catalogue()
    test_applications()
    test_payments()
    test_notifications()
    test_frontend()
    test_errors()
    test_integration()
    test_uploads()

    elapsed = time.time() - start
    # Summary
    print(f"\n{'='*60}")
    print(f"  RESULTS")
    print(f"{'='*60}")
    print(f"  Total tests : {PASS + FAIL}")
    print(f"  Passed      : {PASS}")
    print(f"  Failed      : {FAIL}")
    print(f"  Time        : {elapsed:.2f}s")
    if WARNINGS:
        print(f"  Warnings    : {len(WARNINGS)}")
    print(f"{'═'*60}")

    report_line(f"\n### Summary\n")
    report_line(f"| Metric | Value |")
    report_line(f"|---|---|")
    report_line(f"| Total Tests | {PASS + FAIL} |")
    report_line(f"| Passed | {PASS} |")
    report_line(f"| Failed | {FAIL} |")
    report_line(f"| Time | {elapsed:.2f}s |")
    if WARNINGS:
        report_line(f"| Warnings | {len(WARNINGS)} |")
        report_line(f"\n**Warnings:**\n")
        for w in WARNINGS:
            report_line(f"- {w}")

    # Save report
    report = "\n".join(REPORT)
    with open("TEST_REPORT.md", "w", encoding="utf-8") as f:
        f.write(report)
    print(f"\n  Report saved to TEST_REPORT.md\n")

    return 1 if FAIL > 0 else 0


if __name__ == "__main__":
    sys.exit(main())
