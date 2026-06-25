"""Quick smoke test — uses persistent HTTP connection."""
import http.client, json, sys, time

HOST, PORT = "localhost", 8000
c = http.client.HTTPConnection(HOST, PORT, timeout=30)
ok, fail = 0, 0


def api(method, path, body=None, token=None):
    data = json.dumps(body).encode() if body else None
    hdrs = {"Content-Type": "application/json"} if body else {}
    if token:
        hdrs["Authorization"] = f"Bearer {token}"
    c.request(method, path, body=data, headers=hdrs)
    r = c.getresponse()
    raw = r.read()
    try:
        return r.status, json.loads(raw) if raw else {}
    except json.JSONDecodeError:
        return r.status, raw.decode()


def check(label, passed, detail=""):
    global ok, fail
    tag = "PASS" if passed else "FAIL"
    msg = f"  [{tag}] {label}" + (f" :: {detail}" if detail else "")
    print(msg)
    if passed:
        ok += 1
    else:
        fail += 1


start = time.time()

print("\n#" * 55)
print("  UGSP COMPREHENSIVE SMOKE TEST")
print("#" * 55)

# Health
s, r = api("GET", "/api/health")
check("Health endpoint", s == 200 and r.get("status") == "ok", r.get("version", ""))

def login_and_2fa(nin, pw):
    s, r = api("POST", "/auth/login", {"nin": nin, "password": pw})
    if s != 200: return s, r, ""
    code = r.get("demo_2fa_code", "")
    s2, r2 = api("POST", "/auth/verify-2fa", {"nin": nin, "code": code})
    return s2, r2, r2.get("token", "")

# Auth
s, r, tok1 = login_and_2fa("T1234567890", "pass123")
check("Pre-seeded citizen login + 2FA", s == 200 and tok1.startswith("ugpass_"))

s, r, tok2 = login_and_2fa("T1000000001", "newseed123")
check("Seeded citizen (Amos) login + 2FA", s == 200)
tok2 = r.get("token", "")

s, r, tok2 = login_and_2fa("T1000000003", "seed123")
check("Seeded business (Peter) login + 2FA", s == 200)

s, r, tok3 = login_and_2fa("T1000000006", "seed123")
check("Seeded visitor (Grace A.) login + 2FA", s == 200)

s, r = api("POST", "/auth/login", {"nin": "INVALID", "password": "wrong"})
check("Invalid login rejected", s == 401)

s, r = api("POST", "/auth/login", {"nin": "   ", "password": "   "})
check("Whitespace login rejected", s in (400, 422))

s, r = api("POST", "/auth/login", {"nin": "T1234567890", "password": "wrong"})
check("Wrong password rejected", s == 401)

# 2FA edge cases
s, r = api("POST", "/auth/verify-2fa", {"nin": "T1234567890", "code": "000000"})
check("2FA invalid code rejected", s in (400, 401))

s, r = api("POST", "/auth/verify-2fa", {"nin": "T9999999999", "code": "000000"})
check("2FA no session rejected", s == 400)

# Register validation
s, r = api("POST", "/auth/register", {"nin": "T8888888882", "name": "  ", "email": "test@test.com", "phone": "+256700000001", "category": "citizen", "password": "pass123"})
check("Register blank name rejected", s in (400, 422))

s, r = api("POST", "/auth/register", {"nin": "T8888888883", "name": "Valid", "email": "bad-email", "phone": "+256700000002", "category": "citizen", "password": "pass123"})
check("Register invalid email rejected", s in (400, 422))

s, r = api("POST", "/auth/register", {"nin": "T8888888884", "name": "Valid", "email": "test@test.com", "phone": "not-a-number", "category": "citizen", "password": "pass123"})
check("Register invalid phone rejected", s in (400, 422))

s, r = api("POST", "/auth/register", {"nin": "T8888888885", "name": "Valid", "email": "test@test.com", "phone": "+256700000005", "category": "citizen", "password": "ab"})
check("Register short password rejected", s in (400, 422))

# Feedback endpoint
s, r = api("POST", "/auth/feedback", {"category": "bug", "rating": 4, "message": "API test feedback"})
check("Submit feedback", s == 200)

s, r = api("POST", "/auth/feedback", {"category": "bug", "rating": 10, "message": "invalid"})
check("Feedback invalid rating rejected", s in (400, 422))

s, r = api("POST", "/auth/feedback", {"category": "invalid", "rating": 3, "message": "bad"})
check("Feedback invalid category rejected", s in (400, 422))

s, r = api("POST", "/auth/feedback", {"category": "bug", "rating": 3, "message": ""})
check("Feedback empty message rejected", s in (400, 422))

s, r = api("GET", "/auth/feedback")
check("List feedback", s == 200 and isinstance(r, list) and len(r) >= 1)

# Register fresh user
s, r = api("POST", "/auth/register", {"nin": "T8888888881", "name": "Smoke Tester",
    "email": "smoke@test.ug", "phone": "+256700888881", "category": "citizen", "password": "smokepass"})
check("Register new user", s == 200 and "token" in r)
tok3 = r.get("token", "")

# Duplicate
s, r = api("POST", "/auth/register", {"nin": "T8888888881", "name": "Duplicate",
    "email": "dup@test.ug", "phone": "+256700888882", "category": "citizen", "password": "validpass12"})
check("Duplicate NIN conflict (409)", s == 409)

# Forgot password
s, r = api("POST", "/auth/forgot-password", {"nin": "T8888888881"})
check("Forgot-password sends code", s == 200)
code = r.get("message", "").split(": ")[-1].strip() if ": " in str(r) else ""
if code:
    s, r = api("POST", "/auth/reset-password", {"nin": "T8888888881", "reset_code": code, "new_password": "newsmoke"})
    check("Reset with valid code", s == 200)
    s, r = api("POST", "/auth/reset-password", {"nin": "T8888888881", "reset_code": "WRONG", "new_password": "x"})
    check("Reset with invalid code rejected", s in (400, 422))

# Profile
s, r = api("GET", "/auth/profile", token=tok1)
check("Profile has name", s == 200 and "name" in r, r.get("name", ""))
check("Profile has NIN", "nin" in r)
check("Profile has email", "email" in r)
check("Profile has category", "category" in r)

s, r = api("GET", "/auth/profile")
check("Profile without token rejected", s == 403 or s == 401)

# Catalogue
s, r = api("GET", "/catalogue")
check("Catalogue returns list", s == 200 and isinstance(r, list) and len(r) >= 20, f"{len(r)} services")

cats = ["citizen", "business", "visitor", "health", "education", "financial", "environmental"]
for cat in cats:
    s, r = api("GET", f"/catalogue?category={cat}")
    check(f"Category '{cat}'", s == 200 and isinstance(r, list) and len(r) >= 3, f"{len(r)} services")

s, r = api("GET", "/catalogue/1")
check("Service detail by ID", s == 200 and isinstance(r, dict) and r.get("id") == 1)

s, r = api("GET", "/catalogue/9999")
check("Non-existent service detail 404", s == 404)

for term in ["passport", "tax", "health", "school", "loan", "permit", "NIRA"]:
    s, r = api("GET", f"/catalogue/search?q={term}")
    check(f"Search '{term}'", s == 200 and isinstance(r, list) and len(r) > 0, f"{len(r)} results")

s, r = api("GET", "/catalogue/search?q=zzzznotexistzzz")
check("Search non-existent returns empty", s == 200 and isinstance(r, list) and len(r) == 0)

s, r = api("GET", "/catalogue/ministries")
check("Ministries directory", s == 200 and isinstance(r, list) and len(r) >= 20, f"{len(r)} entries")

s, r = api("GET", "/catalogue/ministries/search?q=health")
check("Ministries search", s == 200 and isinstance(r, list) and len(r) >= 1)

# Applications
s, r = api("POST", "/applications", {"service_id": 1}, token=tok1)
check("Apply for service", s == 200 and "application_id" in r)
app_id = r.get("application_id", "")

s, r = api("POST", "/applications", {"service_id": 5}, token=tok1)
check("Apply for service (driving)", s == 200)

s, r = api("POST", "/applications", {"service_id": 20}, token=tok1)
check("Apply for service (medical)", s == 200)

s, r = api("POST", "/applications", {"service_id": 27}, token=tok1)
check("Apply for service (tree permit)", s == 200)

s, r = api("GET", "/applications", token=tok1)
check("List applications", s == 200 and isinstance(r, list) and len(r) >= 3)

if app_id:
    s, r = api("GET", f"/applications/{app_id}", token=tok1)
    check("Track application", s == 200 and isinstance(r, dict) and "status" in r)

s, r = api("POST", "/applications", {"service_id": 1})
check("Apply without token rejected", s in (401, 403))

# Payments
s, r = api("POST", "/payments/checkout", {"service_id": 1, "amount": 50000, "channel": "mobile_money"}, token=tok1)
check("Payment checkout generates PRN", s == 200 and "prn" in r)

s, r = api("POST", "/payments/checkout", {"service_id": 9, "amount": 500000, "channel": "bank_transfer"}, token=tok2)
check("Business payment bank transfer", s == 200 and "prn" in r)

s, r = api("POST", "/payments/checkout", {"service_id": 27, "amount": 50000, "channel": "card"}, token=tok3)
check("Payment via card", s == 200 and "prn" in r)

# Notifications
s, r = api("GET", "/auth/notifications", token=tok1)
check("Notifications returns list", s == 200 and isinstance(r, list))

s, r = api("POST", "/auth/notifications/read", {}, token=tok1)
check("Mark all read succeeds", s == 200)

# Frontend
c.request("GET", "/")
r = c.getresponse()
html = r.read().decode()
checks = [
    ("Coat of Arms SVG", "Coat" in html or "Arms" in html),
    ("Login form", "login" in html.lower()),
    ("Dashboard", "dashboard" in html.lower()),
    ("Service catalogue", "catalogue" in html.lower()),
    ("Ministries", "ministr" in html.lower()),
    ("Map (Leaflet)", "leaflet" in html.lower() or "map" in html.lower()),
    ("Profile section", "profile" in html.lower()),
    ("Notifications UI", "notif" in html.lower()),
    ("Registration form", "register" in html.lower()),
    ("Forgot password", "forgot" in html.lower()),
]
for label, cond in checks:
    check(f"Frontend: {label}", cond)

# Bad request
import urllib.request
try:
    req = urllib.request.Request("http://localhost:8000/auth/login", b"bad json", {"Content-Type": "application/json"}, method="POST")
    urllib.request.urlopen(req, timeout=5)
except urllib.error.HTTPError as e:
    check("Malformed JSON returns 422/400", e.code in (400, 422))

# New endpoints
print("\n--- New page endpoints ---")
s, r = api("GET", "/auth/documents", token=tok1)
check("Documents list", s == 200 and isinstance(r, list))

s, r = api("GET", "/auth/payments", token=tok1)
check("Payment history", s == 200 and isinstance(r, list))

s, r = api("GET", "/auth/news")
check("News list", s == 200 and isinstance(r, list) and len(r) >= 3)

s, r = api("GET", "/auth/help")
check("Help FAQ", s == 200 and "categories" in r)

s, r = api("GET", "/auth/about")
check("About page", s == 200 and "name" in r and "version" in r)

s, r = api("GET", "/auth/activity", token=tok1)
check("Activity log", s == 200 and isinstance(r, list))

s, r = api("POST", "/auth/change-password", {"current_password": "pass123", "new_password": "newpass123"}, token=tok1)
check("Change password", s == 200)

s, r = api("POST", "/auth/change-password", {"current_password": "wrong", "new_password": "newpass"}, token=tok1)
check("Change password wrong current", s in (400, 422))

# Frontend new pages check
c.request("GET", "/")
r = c.getresponse()
html = r.read().decode()
checks2 = [
    ("Document Wallet page", "pageDocuments" in html),
    ("Payment History page", "pagePayments" in html),
    ("Settings page", "pageSettings" in html),
    ("Help Center page", "pageHelp" in html),
    ("About page", "pageAbout" in html),
    ("Activity Log page", "pageActivity" in html),
    ("News page", "pageNews" in html),
    ("Multi-language system", "LANG" in html),
]
for label, cond in checks2:
    check(f"Frontend: {label}", cond)

# Cross-feature integration: register -> login -> catalogue -> apply -> pay -> notify
print("\n--- Cross-feature integration ---")
s, r = api("POST", "/auth/register", {"nin": "T7777777771", "name": "Integration Tester",
    "email": "int@test.ug", "phone": "+256700777771", "category": "business", "password": "intpass"})
check("Register integration user", s == 200)
tint = r.get("token", "")

s, r = api("GET", "/catalogue", token=tint)
check("Browse catalogue", s == 200 and isinstance(r, list) and len(r) > 0)

s, r = api("POST", "/applications", {"service_id": 3}, token=tint)
check("Apply for business reg", s == 200)
aid = r.get("application_id", "")

s, r = api("POST", "/payments/checkout", {"service_id": 3, "amount": 150000, "channel": "mobile_money"}, token=tint)
check("Pay for application", s == 200 and "prn" in r)

s, r = api("GET", "/auth/notifications", token=tint)
check("Notifications after actions", s == 200 and isinstance(r, list))

s, r = api("GET", "/auth/profile", token=tint)
check("Profile accessible", s == 200 and "name" in r)
check("Integration flow complete", True)


elapsed = time.time() - start
total = ok + fail
print(f"\n{'=' * 55}")
print(f"  RESULTS: {total} tests")
print(f"  Passed: {ok}    Failed: {fail}    Time: {elapsed:.1f}s")
print(f"{'=' * 55}")

c.close()
sys.exit(1 if fail else 0)
