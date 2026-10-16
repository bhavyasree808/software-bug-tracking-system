from flask import Flask, request, redirect, url_for, render_template_string, flash
import sqlite3
from pathlib import Path

app = Flask(__name__)
app.secret_key = "change-this-for-local-development"
DB_PATH = Path(__file__).with_name("bugs.db")

SCHEMA = """
CREATE TABLE IF NOT EXISTS bugs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    severity TEXT NOT NULL CHECK(severity IN ('Critical','High','Medium','Low')),
    status TEXT NOT NULL CHECK(status IN ('Open','In Progress','Resolved')),
    assigned_to TEXT NOT NULL DEFAULT '',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""

PAGE = """
<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>BugTrack | Issue Management</title>
<style>
:root{font-family:Inter,Segoe UI,Arial,sans-serif;color:#172033;background:#f3f6fb}
*{box-sizing:border-box}body{margin:0}.top{background:#14233f;color:white;padding:24px max(20px,calc((100% - 1100px)/2))}
.top h1{margin:0 0 5px;font-size:26px}.top p{margin:0;color:#cbd5e1}
main{max-width:1100px;margin:24px auto;padding:0 18px}.stats{display:grid;grid-template-columns:repeat(4,1fr);gap:12px}
.stat,.panel{background:white;border:1px solid #e0e6ef;border-radius:12px;padding:17px;box-shadow:0 3px 12px #15294b08}
.stat span{color:#65738a;font-size:13px}.stat strong{display:block;font-size:28px;margin-top:8px}
.layout{display:grid;grid-template-columns:340px 1fr;gap:16px;margin-top:18px}.panel h2{margin:0 0 14px;font-size:18px}
label{display:block;font-size:13px;font-weight:600;margin:12px 0 5px}
input,textarea,select{width:100%;padding:10px;border:1px solid #ccd5e2;border-radius:7px;font:inherit;background:white}
textarea{min-height:78px;resize:vertical}button,.btn{border:0;background:#2459d3;color:white;padding:10px 13px;border-radius:7px;font-weight:600;cursor:pointer;text-decoration:none;display:inline-block}
button:hover,.btn:hover{background:#1948b8}.secondary{background:#e8eef9;color:#20385f}.secondary:hover{background:#dce6f7}
.filters{display:grid;grid-template-columns:1fr 145px 125px;gap:8px;margin-bottom:12px}
.table-wrap{overflow-x:auto}table{width:100%;border-collapse:collapse;font-size:13px}th,td{text-align:left;padding:11px 8px;border-bottom:1px solid #edf0f5;vertical-align:top}th{color:#65738a;font-weight:600}
.tag{display:inline-block;padding:4px 7px;border-radius:5px;background:#edf2fb;font-size:12px;white-space:nowrap}
.Critical{background:#fee2e2;color:#991b1b}.High{background:#ffedd5;color:#9a3412}.Medium{background:#fef3c7;color:#92400e}.Low{background:#dcfce7;color:#166534}
.notice{padding:10px;border-radius:7px;background:#e8f5e9;color:#1b5e20;margin-bottom:12px}
.actions{display:flex;gap:6px;flex-wrap:wrap}.empty{text-align:center;color:#65738a;padding:30px}
@media(max-width:850px){.layout{grid-template-columns:1fr}.stats{grid-template-columns:repeat(2,1fr)}}
@media(max-width:500px){.filters{grid-template-columns:1fr}.top h1{font-size:22px}}
</style></head><body>
<header class="top"><h1>BugTrack</h1><p>Software Bug Tracking & Issue Management System</p></header>
<main>
{% with messages = get_flashed_messages() %}{% if messages %}{% for message in messages %}<div class="notice">{{message}}</div>{% endfor %}{% endif %}{% endwith %}
<section class="stats">
<div class="stat"><span>Total Issues</span><strong>{{counts.total}}</strong></div>
<div class="stat"><span>Open</span><strong>{{counts.open}}</strong></div>
<div class="stat"><span>In Progress</span><strong>{{counts.progress}}</strong></div>
<div class="stat"><span>Resolved</span><strong>{{counts.resolved}}</strong></div>
</section>
<section class="layout">
<div class="panel"><h2>Report a Bug</h2>
<form method="post" action="{{url_for('create_bug')}}">
<label for="title">Bug title *</label><input id="title" name="title" maxlength="120" required placeholder="e.g. Login button not responding">
<label for="description">Description *</label><textarea id="description" name="description" maxlength="2000" required placeholder="Steps to reproduce and expected result"></textarea>
<label for="severity">Severity</label><select id="severity" name="severity"><option>Medium</option><option>Critical</option><option>High</option><option>Low</option></select>
<label for="assigned_to">Assigned to</label><input id="assigned_to" name="assigned_to" maxlength="80" placeholder="Developer name (optional)">
<button style="margin-top:15px;width:100%" type="submit">Create issue</button></form></div>
<div class="panel"><h2>Issue Tracker</h2>
<form class="filters" method="get" action="{{url_for('index')}}">
<input name="q" value="{{q}}" placeholder="Search title, description, assignee…">
<select name="status"><option value="">All statuses</option>{% for s in statuses %}<option {{'selected' if selected_status==s else ''}}>{{s}}</option>{% endfor %}</select>
<button type="submit">Search</button></form>
<div class="table-wrap"><table><thead><tr><th>ID / Issue</th><th>Severity</th><th>Status</th><th>Assignee</th><th>Update</th></tr></thead><tbody>
{% for bug in bugs %}<tr><td><strong>#{{bug.id}} {{bug.title}}</strong><br><span style="color:#65738a">{{bug.description[:100]}}{{'…' if bug.description|length>100 else ''}}</span><br><span style="color:#8a94a6;font-size:11px">{{bug.created_at}}</span></td>
<td><span class="tag {{bug.severity}}">{{bug.severity}}</span></td><td><span class="tag">{{bug.status}}</span></td><td>{{bug.assigned_to or 'Unassigned'}}</td>
<td><form method="post" action="{{url_for('update_bug', bug_id=bug.id)}}">
<select name="status" aria-label="Status for issue {{bug.id}}">{% for s in statuses %}<option {{'selected' if bug.status==s else ''}}>{{s}}</option>{% endfor %}</select>
<input name="assigned_to" value="{{bug.assigned_to}}" placeholder="Assignee" aria-label="Assignee for issue {{bug.id}}" style="margin:5px 0">
<button type="submit" class="secondary">Save</button>
</form><form method="post" action="{{url_for('delete_bug', bug_id=bug.id)}}" onsubmit="return confirm('Delete issue #{{bug.id}}?')"><button class="secondary" style="margin-top:5px" type="submit">Delete</button></form></td></tr>
{% else %}<tr><td colspan="5" class="empty">No issues found. Create your first bug report.</td></tr>{% endfor %}
</tbody></table></div></div></section>
<p style="color:#7b8798;font-size:12px;margin:18px 2px">Local demo application • Flask + SQLite • Do not use with sensitive production data.</p>
</main></body></html>
"""

from contextlib import contextmanager


@contextmanager
def connect_db():
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row

    try:
        con.execute(SCHEMA)
        yield con
        con.commit()
    except Exception:
        con.rollback()
        raise
    finally:
        con.close()

def valid_text(value, limit):
    value = (value or "").strip()
    return value if value and len(value) <= limit else None

@app.get("/")
def index():
    q = request.args.get("q", "").strip()[:120]
    status = request.args.get("status", "").strip()
    statuses = ["Open", "In Progress", "Resolved"]
    if status not in statuses:
        status = ""
    with connect_db() as con:
        counts_row = con.execute("""SELECT COUNT(*) total,
            SUM(status='Open') open,
            SUM(status='In Progress') progress,
            SUM(status='Resolved') resolved FROM bugs""").fetchone()
        sql = "SELECT * FROM bugs WHERE 1=1"
        params = []
        if q:
            sql += " AND (title LIKE ? OR description LIKE ? OR assigned_to LIKE ?)"
            params.extend([f"%{q}%"] * 3)
        if status:
            sql += " AND status=?"
            params.append(status)
        sql += " ORDER BY id DESC"
        bugs = con.execute(sql, params).fetchall()
    counts = {key: counts_row[key] or 0 for key in ("total", "open", "progress", "resolved")}
    return render_template_string(PAGE, bugs=bugs, counts=counts, q=q, statuses=statuses, selected_status=status)

@app.post("/bugs")
def create_bug():
    title = valid_text(request.form.get("title"), 120)
    description = valid_text(request.form.get("description"), 2000)
    severity = request.form.get("severity", "Medium")
    assigned_to = (request.form.get("assigned_to", "").strip())[:80]
    if not title or not description:
        flash("Enter a title and description (within the allowed length).")
    elif severity not in ("Critical", "High", "Medium", "Low"):
        flash("Invalid severity selected.")
    else:
        with connect_db() as con:
            con.execute("INSERT INTO bugs(title,description,severity,status,assigned_to) VALUES(?,?,?,'Open',?)",
                        (title, description, severity, assigned_to))
        flash("Bug report created successfully.")
    return redirect(url_for("index"))

@app.post("/bugs/<int:bug_id>/update")
def update_bug(bug_id):
    status = request.form.get("status", "")
    assigned_to = request.form.get("assigned_to", "").strip()[:80]
    if status not in ("Open", "In Progress", "Resolved"):
        flash("Invalid status selected.")
    else:
        with connect_db() as con:
            result = con.execute("UPDATE bugs SET status=?, assigned_to=? WHERE id=?",
                                 (status, assigned_to, bug_id))
        flash("Issue updated." if result.rowcount else "Issue not found.")
    return redirect(url_for("index"))

@app.post("/bugs/<int:bug_id>/delete")
def delete_bug(bug_id):
    with connect_db() as con:
        result = con.execute("DELETE FROM bugs WHERE id=?", (bug_id,))
    flash("Issue deleted." if result.rowcount else "Issue not found.")
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True)
