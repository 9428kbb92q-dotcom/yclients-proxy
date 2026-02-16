from flask import Flask, request, Response
import requests as req
import os

app = Flask(__name__)

YCLIENTS_API = "https://api.yclients.com/api/v1"
SECRET = os.environ.get("PROXY_SECRET", "vdohvydoh2026")

@app.route("/ping")
def ping():
    return "ok"

@app.route("/api/<path:path>", methods=["GET", "POST", "PUT", "DELETE"])
def proxy(path):
    # Check secret
    if request.headers.get("X-Proxy-Secret") != SECRET:
        return {"error": "forbidden"}, 403

    url = f"{YCLIENTS_API}/{path}"
    if request.query_string:
        url += f"?{request.query_string.decode()}"

    headers = {}
    for key in ["Accept", "Authorization", "Content-Type"]:
        val = request.headers.get(key)
        if val:
            headers[key] = val

    try:
        resp = req.request(
            method=request.method,
            url=url,
            headers=headers,
            data=request.get_data(),
            timeout=25
        )
        return Response(resp.content, status=resp.status_code,
                       content_type=resp.headers.get("Content-Type", "application/json"))
    except Exception as e:
        return {"error": str(e)}, 502

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
