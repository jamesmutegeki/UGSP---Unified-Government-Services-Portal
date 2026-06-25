"""
Fast seed script — uses HTTP connection reuse, smaller batch per user.
Usage: python seed_fast.py
"""
import http.client, json, sys, time

HOST = "localhost"
PORT = 8000
conn = http.client.HTTPConnection(HOST, PORT, timeout=30)
stats = {"ok": 0, "fail": 0}


def api(method, path, body=None, token=None):
    data = json.dumps(body).encode() if body else None
    headers = {"Content-Type": "application/json"} if body else {}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    conn.request(method, path, body=data, headers=headers)
    r = conn.getresponse()
    raw = r.read()
    try:
        return r.status, json.loads(raw)
    except json.JSONDecodeError:
        return r.status, raw.decode()


def log(step, ok, detail=""):
    tag = "PASS" if ok else "FAIL"
    print(f"  [{tag}] {step}" + (f" -- {detail}" if detail else ""))
    if ok:
        stats["ok"] += 1
    else:
        stats["fail"] += 1


SEED_USERS = [
    {"nin":"T1000000001","name":"Amos Muwonge","email":"amos.muwonge@example.ug","phone":"+256701000001","category":"citizen","password":"seed123"},
    {"nin":"T1000000002","name":"Faith Nakato","email":"faith.nakato@example.ug","phone":"+256701000002","category":"citizen","password":"seed123"},
    {"nin":"T1000000003","name":"Peter Kaggwa","email":"peter.kaggwa@example.ug","phone":"+256701000003","category":"business","password":"seed123"},
    {"nin":"T1000000004","name":"Sarah Kyomuhangi","email":"sarah.kyo@example.ug","phone":"+256701000004","category":"citizen","password":"seed123"},
    {"nin":"T1000000005","name":"David Okwir","email":"david.okwir@example.ug","phone":"+256701000005","category":"citizen","password":"seed123"},
    {"nin":"T1000000006","name":"Grace Achieng","email":"grace.achieng@example.ug","phone":"+256701000006","category":"visitor","password":"seed123"},
    {"nin":"T1000000007","name":"Joseph Ssewanyana","email":"joseph.ssewa@example.ug","phone":"+256701000007","category":"business","password":"seed123"},
    {"nin":"T1000000008","name":"Rebecca Namatovu","email":"rebecca.nama@example.ug","phone":"+256701000008","category":"citizen","password":"seed123"},
    {"nin":"T1000000009","name":"Hassan Mbowa","email":"hassan.mbowa@example.ug","phone":"+256701000009","category":"business","password":"seed123"},
    {"nin":"T1000000010","name":"Micheal Ochen","email":"micheal.ochen@example.ug","phone":"+256701000010","category":"citizen","password":"seed123"},
    {"nin":"T1000000011","name":"Jane Atim","email":"jane.atim@example.ug","phone":"+256701000011","category":"citizen","password":"seed123"},
    {"nin":"T1000000012","name":"Robert Mugisha","email":"robert.mugisha@example.ug","phone":"+256701000012","category":"visitor","password":"seed123"},
    {"nin":"T1000000013","name":"Doreen Nansubuga","email":"doreen.nansu@example.ug","phone":"+256701000013","category":"citizen","password":"seed123"},
    {"nin":"T1000000014","name":"Samuel Ouma","email":"samuel.ouma@example.ug","phone":"+256701000014","category":"business","password":"seed123"},
    {"nin":"T1000000015","name":"Esther Nambi","email":"esther.nambi@example.ug","phone":"+256701000015","category":"citizen","password":"seed123"},
]


def main():
    print(f"\n{'='*60}")
    print("  UGSP -- Fast Seeder")
    print(f"{'='*60}")

    s, r = api("GET", "/api/health")
    log("Server health check", s == 200, r.get("version", "?"))

    print("\n[1] Registering 15 users...")
    tokens = {}
    for u in SEED_USERS:
        s, r = api("POST", "/auth/register", u)
        if s == 200 and "token" in r:
            tokens[u["nin"]] = r["token"]
            log(f"Registered {u['name']}", True)
        elif s == 409:
            s2, r2 = api("POST", "/auth/login", {"nin": u["nin"], "password": u["password"]})
            if "demo_2fa_code" in r2:
                s3, r3 = api("POST", "/auth/verify-2fa", {"nin": u["nin"], "code": r2["demo_2fa_code"]})
                if "token" in r3:
                    tokens[u["nin"]] = r3["token"]
                    log(f"Login {u['name']}", True)
                else:
                    log(f"Login {u['name']}", False, str(r3))
            else:
                log(f"Login {u['name']}", False, str(r2))
        else:
            log(f"Register {u['name']}", False, str(r))

    print("\n[2] Catalogue check...")
    cats = ["citizen","business","visitor","health","education","financial","environmental"]
    for cat in cats:
        s, r = api("GET", f"/catalogue?category={cat}")
        ok = s == 200 and isinstance(r, list)
        log(f"Category '{cat}': {len(r) if isinstance(r, list) else 0} services", ok, f"status={s}")

    print("\n[3] Creating applications (1-3 per user)...")
    app_count = 0
    cat_svc = {"citizen":[1,2,5],"business":[3,4,7],"visitor":[6,9,17],"health":[20],"education":[21],"financial":[25],"environmental":[27]}
    for nin, tok in tokens.items():
        u = next((x for x in SEED_USERS if x["nin"] == nin), None)
        if not u:
            continue
        for sid in cat_svc.get(u["category"], [1])[:3]:
            s, r = api("POST", "/applications", {"service_id": sid}, token=tok)
            if s == 200:
                app_count += 1
    log(f"Applications created: {app_count}", True)

    print("\n[4] Sample payments (first app per user)...")
    pay_count = 0
    fee_map = {1:50000,2:250000,3:150000,5:180000,7:20000,9:500000,17:200000,20:15000,21:100000,25:25000,27:50000}
    for nin, tok in tokens.items():
        s, r = api("GET", "/applications", token=tok)
        if s == 200 and isinstance(r, list) and r:
            app = r[0]
            sid = app.get("service_id", 1)
            fee = fee_map.get(sid, 10000)
            s2, r2 = api("POST", "/payments/checkout", {"service_id": sid, "amount": fee, "channel": "mobile_money"}, token=tok)
            if s2 == 200 and "prn" in r2:
                pay_count += 1
    log(f"Payments processed: {pay_count}", pay_count > 0)

    print("\n[5] Notifications check...")
    for nin in list(tokens.keys())[:3]:
        s, r = api("GET", "/auth/notifications", token=tokens[nin])
        log(f"Notifications for {nin[:12]}...: {len(r) if isinstance(r, list) else 'N/A'}", s == 200)

    print("\n[6] Forgot-password flow...")
    s, r = api("POST", "/auth/forgot-password", {"nin": "T1000000001"})
    if s == 200:
        log("Forgot-password step 1", True)
        code = r.get("message", "").split(": ")[-1].strip() if ": " in str(r) else "RESET7890"
        s2, r2 = api("POST", "/auth/reset-password", {"nin":"T1000000001","reset_code":code,"new_password":"newseed123"})
        log("Reset password step 2", s2 == 200)
    else:
        log("Forgot-password", False, str(r))

    print("\n[7] Ministries + search...")
    s, r = api("GET", "/catalogue/ministries")
    log(f"Ministries: {len(r) if isinstance(r, list) else 0}", s == 200 and isinstance(r, list))
    s, r = api("GET", "/catalogue/ministries/search?q=health")
    log("Ministries search", s == 200 and isinstance(r, list) and len(r) >= 1)

    print("\n[8] Cross-category search...")
    for t in ["passport","tax","health","school","loan","permit"]:
        s, r = api("GET", f"/catalogue/search?q={t}")
        log(f"Search '{t}': {len(r) if isinstance(r,list) else 0} results", s == 200)

    print(f"\n{'='*60}")
    print(f"  SEEDING COMPLETE")
    print(f"  Passed: {stats['ok']}   Failed: {stats['fail']}")
    print(f"{'='*60}")
    print("\nDemo logins:")
    print("  T1234567890 / pass123  (Grace Akello, pre-seeded)")
    print("  T1000000001 / newseed123 (Amos Muwonge)")
    print("  T1000000003 / seed123 (Peter Kaggwa, business)")
    print("  T1000000006 / seed123 (Grace Achieng, visitor)")

    conn.close()


if __name__ == "__main__":
    main()
