from flask import Flask, render_template_string
import psycopg2
import os

DB_URL = os.getenv("DATABASE_URL")

app = Flask(__name__)

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
tr:hover {
    background: #1e293b;
}
.footer {
    text-align: center;
    padding: 15px;
    font-size: 12px;
    color: #94a3b8;
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
<h3>Delhi SLDC Schedule Change Monitor</h3>
<div class="clock" id="clock"></div>
</header>

<table>
<tr>
<th>Time</th>
<th>Revision</th>
<th>Plant</th>
<th>Block</th>
<th>Old MW</th>
<th>New MW</th>
<th>Δ MW</th>
</tr>

{% for r in rows %}
<tr>
<td>{{ r[0] }}</td>
<td>{{ r[1] }}</td>
<td>{{ r[2] }}</td>
<td>{{ r[3] }}</td>
<td>{{ r[4] }}</td>
<td>{{ r[5] }}</td>
<td>{{ r[6] }}</td>
</tr>
{% endfor %}

</table>

<div class="footer">
Auto-refresh every 30 seconds • Powered by Supabase + Render
</div>
</body>
</html>
"""

@app.route("/")
def index():
    conn = psycopg2.connect(DB_URL)
    cur = conn.cursor()
    cur.execute("""
        SELECT time_detected, revision, plant, block, old_mw, new_mw, delta_mw
        FROM schedule_changes
        ORDER BY time_detected DESC
        LIMIT 200
    """)
    rows = cur.fetchall()
    conn.close()
    return render_template_string(HTML, rows=rows)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
