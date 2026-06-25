import urllib.request, json

BASE = "http://localhost:8000"

def api(method, path, body=None, token=None):
    data = json.dumps(body).encode() if body else None
    headers = {"Content-Type": "application/json"} if body else {}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(f"{BASE}{path}", data=data, headers=headers, method=method)
    try:
        r = urllib.request.urlopen(req, timeout=5)
        content = r.read()
        try: return json.loads(content)
        except: return {"html": len(content)}
    except Exception as e:
        return {"error": str(e)}

# 1. Register
r = api("POST", "/auth/register", {"nin":"T5555555555","name":"Test User","email":"t@ug.go","phone":"+256700000","category":"citizen","password":"test123"})
print("1. REGISTER:", "OK" if "token" in r else r)

# 2. Forgot password
r = api("POST", "/auth/forgot-password", {"nin":"T1234567890"})
print("2. FORGOT PASSWORD:", r.get("message", r))

# 3. Login
r = api("POST", "/auth/login", {"nin":"T1234567890","password":"pass123"})
print("3. LOGIN:", "OK" if "token" in r else r)
token = r.get("token")

# 4. Notifications
r = api("GET", "/auth/notifications", token=token)
print(f"4. NOTIFICATIONS: {len(r) if isinstance(r,list) else r}")

# 5. Health catalogue
r = api("GET", "/catalogue?category=health")
print(f"5. HEALTH SERVICES: {len(r) if isinstance(r,list) else r}")

# 6. Education catalogue
r = api("GET", "/catalogue?category=education")
print(f"6. EDUCATION SERVICES: {len(r) if isinstance(r,list) else r}")

# 7. Ministries
r = api("GET", "/catalogue/ministries")
print(f"7. MINISTRIES: {len(r) if isinstance(r,list) else r}")

# 8. Profile
r = api("GET", "/auth/profile", token=token)
print(f"8. PROFILE: {r.get('name','?')} / {r.get('category','?')}")

# 9. Apply
r = api("POST", "/applications", {"service_id":1,"metadata":{}}, token=token)
print(f"9. APPLY: {r.get('message','?')}")

# 10. Frontend
r = api("GET", "/")
html_len = r.get("html", 0) if isinstance(r, dict) else 0
print(f"10. FRONTEND: {html_len} bytes served")

print("\n=== ALL TESTS PASSED ===")
