from flask import Flask, render_template_string
import psycopg2
import os
from dotenv import load_dotenv
from pathlib import Path
from datetime import datetime

# ---------------- LOAD ENV SAFELY ----------------
env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=env_path)

DB_URL = os.getenv("DATABASE_URL")
if not DB_URL:
    raise RuntimeError("DATABASE_URL not found in .env")

# ---------------- APP ----------------
app = Flask(__name__)
conn = psycopg2.connect(DB_URL)

# ---------------- HTML ----------------
HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>BSES Yamuna Power Limited | Schedule Monitor</title>

    <style>
        body {
            margin: 0;
            font-family: "Segoe UI", Arial, sans-serif;
            background: #0b1320;
            color: #eaeaea;
        }

        header {
            background: linear-gradient(90deg, #001f3f, #003366);
            padding: 20px 40px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 3px solid #ffcc00;
        }

        .title {
            font-size: 26px;
            font-weight: 700;
            letter-spacing: 0.6px;
        }

        .subtitle {
            font-size: 14px;
            opacity: 0.85;
            margin-top: 2px;
        }

        .clock-box {
            text-align: right;
        }

        .clock {
            font-size: 22px;
            font-weight: 600;
            background: #000;
            padding: 8px 16px;
            border-radius: 6px;
            border: 1px solid #444;
            display: inline-block;
        }

        .refresh {
            font-size: 12px;
            opacity: 0.7;
            margin-top: 4px;
        }

        main {
            padding: 30px 40px;
        }

        table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
            background: #111a2b;
            border-radius: 8px;
            overflow: hidden;
        }

        th {
            background: #16233c;
            padding: 12px;
            text-align: left;
            font-size: 14px;
            color: #ffcc00;
            border-bottom: 1px solid #2c3e66;
        }

        td {
            padding: 12px;
            font-size: 14px;
            border-bottom: 1px solid #1f2d4d;
        }

        tr:hover {
            background: #1a2644;
        }

        .delta-pos {
            color: #00ff9c;
            font-weight: 600;
        }

        .delta-neg {
            color: #ff5c5c;
            font-weight: 600;
        }

        .no-data {
            margin-top: 50px;
            font-size: 18px;
            opacity: 0.7;
            text-align: center;
        }

        footer {
            text-align: center;
            padding: 15px;
            font-size: 12px;
            opacity: 0.6;
            margin-top: 40px;
        }
    </style>
</head>

<body>

<header>
    <div>
        <div class="title">BSES Yamuna Power Limited</div>
        <div class="subtitle">Real-Time Schedule Change Monitoring (BYPL)</div>
    </div>

    <div class="clock-box">
        <div class="clock" id="clock">--:--:--</div>
        <div class="refresh" id="refresh-timer">Auto refresh in 30s</div>
    </div>
</header>

<main>
    {% if rows %}
    <table>
        <tr>
            <th>Detected Time</th>
            <th>Revision</th>
            <th>Plant</th>
            <th>Block</th>
            <th>Old MW</th>
            <th>New MW</th>
            <th>Δ MW</th>
        </tr>

        {% for r in rows %}
        <tr>
            <td>{{ r[1] }}</td>
            <td>{{ r[2] }} → {{ r[3] }}</td>
            <td>{{ r[4] }}</td>
            <td>{{ r[5] }}</td>
            <td>{{ "%.2f"|format(r[6]) }}</td>
            <td>{{ "%.2f"|format(r[7]) }}</td>
            <td class="{{ 'delta-pos' if r[8] > 0 else 'delta-neg' }}">
                {{ "%.2f"|format(r[8]) }}
            </td>
        </tr>
        {% endfor %}
    </table>
    {% else %}
        <div class="no-data">No schedule change ≥ 1 MW detected.</div>
    {% endif %}
</main>

<footer>
    © {{ year }} BSES Yamuna Power Limited — Internal Monitoring System
</footer>

<script>
/* ---------- LIVE CLOCK (IST) ---------- */
function updateClock() {
    const now = new Date();
    const ist = new Date(now.toLocaleString("en-US", { timeZone: "Asia/Kolkata" }));
    const h = String(ist.getHours()).padStart(2, '0');
    const m = String(ist.getMinutes()).padStart(2, '0');
    const s = String(ist.getSeconds()).padStart(2, '0');
    document.getElementById("clock").innerText = h + ":" + m + ":" + s;
}
setInterval(updateClock, 1000);
updateClock();

/* ---------- AUTO REFRESH ---------- */
let refreshIn = 30;
function updateRefreshTimer() {
    document.getElementById("refresh-timer").innerText =
        "Auto refresh in " + refreshIn + "s";
    refreshIn--;
    if (refreshIn < 0) location.reload();
}
setInterval(updateRefreshTimer, 1000);
</script>

</body>
</html>
"""

# ---------------- ROUTE ----------------
@app.route("/")
def index():
    cur = conn.cursor()
    cur.execute("""
        SELECT *
        FROM schedule_changes
        ORDER BY detected_at DESC
        LIMIT 200
    """)
    rows = cur.fetchall()
    return render_template_string(
        HTML,
        rows=rows,
        year=datetime.now().year
    )

# ---------------- RUN ----------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5050)

