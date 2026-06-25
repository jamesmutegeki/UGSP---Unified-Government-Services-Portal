"""Verify front-end changes are applied correctly."""
import http.client
c = http.client.HTTPConnection("localhost", 8000, timeout=10)
c.request("GET", "/")
r = c.getresponse()
html = r.read().decode()

checks = [
    ("Title: Unified Government Service Portal", "Unified Government Service Portal" in html),
    ("Login password toggle wrapper", "pw-wrap" in html and "togglePw" in html),
    ("Login password eye icon", "visibility_off" in html),
    ("Register password toggle", "regPass" in html and "pw-wrap" in html),
    ("Forgot password toggle", "forgotNewPass" in html and "pw-wrap" in html),
    ("Toggle CSS class", ".pw-toggle" in html),
    ("Sidebar avatar JS function", "updateSidebarAvatar" in html),
    ("Upload updates sidebar avatar", "STATE.user.photo_url = d.photo_url" in html),
    ("Profile load updates sidebar", "updateSidebarAvatar(STATE.user)" in html),
    ("Register page has Ken Burns bg", html.count("ken-burns-bg") >= 2),
    ("Register page has gradient overlay", html.count("login-overlay") >= 2),
    ("Old title NOT present", "Unified Government Portal" not in html.replace("Unified Government Service Portal", "")),
]

for label, cond in checks:
    tag = "PASS" if cond else "FAIL"
    print(f"  [{tag}] {label}")

p = sum(1 for _, c in checks if c)
print(f"\n{p}/{len(checks)} verified")
c.close()
