from flask import Flask, render_template_string
import json
import os

app = Flask(__name__)

DATA_FILE = "Schedule_New/Delhi_SLDC_DC.json"

HTML = """
<!DOCTYPE html>
<html>
<head>
<title>BSES Yamuna Power Limited | SLDC Monitor</title>
<meta http-equiv="refresh" content="30">
<style>
body {
    font-family: Arial, sans-serif;
    background: #0f172a;
    color: white;
    margin: 0;
}
header {
    background: linear-gradient(90deg, #2563eb, #1e40af);
    padding: 20px;
    text-align: center;
}
.clock {
    font-size: 32px;
    margin-top: 10px;
}
table {
    width: 95%;
    margin: 30px auto;
    border-collapse: collapse;
}
th, td {
    padding: 10px;
    border-bottom: 1px solid #334155;
    text-align: center;
}
th {
    background: #1e293b;
}
</style>
<script>
function updateClock(){
    const now = new Date();
    document.getElementById("clock").innerText =
        now.toLocaleTimeString();
}
setInterval(updateClock,1000);
</script>
</head>

<body onload="updateClock()">
<header>
<h1>BSES Yamuna Power Limited</h1>
<h3>Delhi SLDC Schedule Monitor</h3>
<div class="clock" id="clock"></div>
</header>

<table>
<tr>
<th>Revision</th>
<th>Plant</th>
<th>Block</th>
<th>MW</th>
</tr>

{% for r in rows %}
<tr>
<td>{{ r.get("revision","-") }}</td>
<td>{{ r.get("plant","-") }}</td>
<td>{{ r.get("block","-") }}</td>
<td>{{ r.get("mw","-") }}</td>
</tr>
{% endfor %}
</table>
</body>
</html>
"""

@app.route("/")
def index():
    rows = []
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE) as f:
                rows = json.load(f)
        except Exception:
            rows = []
    return render_template_string(HTML, rows=rows)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

