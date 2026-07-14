"""
main.py

AMS Transition Intake & Readiness Assessment - Vibe Coding prototype (Option A + role rule).
Single-file Flask app, SQLite persistence, no external DB required.

Run:
    pip install -r requirements.txt
    python database.py        # creates + seeds app/readiness.db
    python main.py            # starts the app on http://127.0.0.1:5000
"""

from flask import Flask, request, redirect, url_for, render_template_string

import database as db
import readiness_rules as rules
import rfc_rules

app = Flask(__name__)

LAYOUT = """
<!doctype html>
<html>
<head>
  <title>AMS Readiness Intake</title>
  <style>
    body { font-family: sans-serif; max-width: 800px; margin: 40px auto; color: #222; }
    h1 { font-size: 1.4rem; } h2 { font-size: 1.1rem; margin-top: 2rem; }
    table { border-collapse: collapse; width: 100%; margin-top: 0.5rem; }
    th, td { border: 1px solid #ddd; padding: 6px 10px; text-align: left; font-size: 0.9rem; }
    .flag-missing { color: #b00020; font-weight: bold; }
    .flag-stale { color: #b06a00; font-weight: bold; }
    .flag-ready { color: #157a15; font-weight: bold; }
    form { margin-top: 1rem; padding: 1rem; border: 1px solid #ddd; }
    label { display: block; margin-top: 0.5rem; font-size: 0.85rem; }
    input, select { width: 100%; padding: 4px; }
    button { margin-top: 1rem; padding: 6px 14px; }
    .msg { padding: 8px; margin-top: 1rem; }
    .msg.error { background: #fde8e8; }
    .msg.ok { background: #e8fde8; }
  </style>
</head>
<body>{{ body|safe }}</body>
</html>
"""


def render(body):
    return render_template_string(LAYOUT, body=body)


@app.route("/")
def index():
    conn = db.get_connection()
    assessments = db.list_assessments(conn)
    critical = db.get_critical_categories(conn)
    rows = ""
    for a in assessments:
        evidence = db.get_evidence_for_assessment(conn, a["id"])
        readiness = rules.assessment_readiness(evidence, critical)
        status = '<span class="flag-ready">Ready</span>' if readiness["ready"] else '<span class="flag-missing">Missing info</span>'
        rows += f"""<tr>
            <td><a href="/assessment/{a['id']}">{a['name']}</a></td>
            <td>{a['status']}</td>
            <td>{status}</td>
        </tr>"""
    conn.close()
    body = f"""
    <h1>AMS Transition Intake &amp; Readiness Assessment</h1>
    <p>Northwind Retail Services — OrderCare transition</p>
    <table>
      <tr><th>Assessment</th><th>Status</th><th>Readiness</th></tr>
      {rows}
    </table>
    """
    return render(body)


@app.route("/assessment/<int:assessment_id>", methods=["GET"])
def view_assessment(assessment_id):
    conn = db.get_connection()
    assessment = db.get_assessment(conn, assessment_id)
    critical = db.get_critical_categories(conn)
    evidence = db.get_evidence_for_assessment(conn, assessment_id)
    readiness = rules.assessment_readiness(evidence, critical)
    conn.close()

    ev_rows = "".join(
        f"""<tr>
            <td>{e['category']}</td><td>{e['source']}</td><td>{e['owner']}</td>
            <td>{e['freshness_date']}{' <span class="flag-stale">STALE</span>' if rules.is_stale(e['freshness_date']) else ''}</td>
            <td>{e['criticality']}</td>
        </tr>"""
        for e in evidence
    )

    missing_html = (
        f'<p class="flag-missing">Missing critical categories: {", ".join(readiness["missing"])}</p>'
        if readiness["missing"] else '<p class="flag-ready">No critical information missing.</p>'
    )

    options = "".join(f'<option value="{c}">{c}</option>' for c in critical)

    # --- RFC section (Change Request: RFC tool - see docs/09_change_request.md) ---
    conn_rfc = db.get_connection()
    rfcs = db.get_rfcs_for_assessment(conn_rfc, assessment_id)
    conn_rfc.close()
    rfc_rows = ""
    for r in rfcs:
        status_html = (
            f'<span class="flag-ready">answered{" (FAQ candidate)" if r["is_faq_candidate"] else ""}</span>'
            if r["status"] == "answered" else '<span class="flag-missing">open</span>'
        )
        answer_html = f'<br/><i>Answer:</i> {r["answer_text"]} <i>(by {r["answered_by"]})</i>' if r["status"] == "answered" else ""
        rfc_rows += f"""<tr>
            <td>#{r['id']} <b>{r['title']}</b><br/>{r['question']}{answer_html}</td>
            <td>{r['raised_by']} &rarr; {r['assigned_to'] or '(unassigned)'}</td>
            <td>{status_html}</td>
        </tr>"""

    body = f"""
    <p><a href="/">&larr; back</a></p>
    <h1>{assessment['name']}</h1>
    <p>Status: <b>{assessment['status']}</b></p>

    <h2>Readiness view</h2>
    {missing_html}

    <h2>Evidence</h2>
    <table>
      <tr><th>Category</th><th>Source</th><th>Owner</th><th>Freshness date</th><th>Criticality</th></tr>
      {ev_rows}
    </table>

    <h2>Add evidence</h2>
    <form method="post" action="/assessment/{assessment_id}/evidence">
      <label>Category</label>
      <select name="category">{options}</select>
      <label>Source</label>
      <input name="source" required />
      <label>Owner</label>
      <input name="owner" required />
      <label>Freshness date (YYYY-MM-DD)</label>
      <input name="freshness_date" type="date" required />
      <label>Criticality</label>
      <select name="criticality">
        <option>Critical</option><option>Important</option><option>Optional</option>
      </select>
      <button type="submit">Add evidence</button>
    </form>

    <h2>RFCs (Request for Comment)</h2>
    <table>
      <tr><th>RFC</th><th>Raised by &rarr; Assigned to</th><th>Status</th></tr>
      {rfc_rows}
    </table>

    <h3>Raise a new RFC (Transition Lead only)</h3>
    <form method="post" action="/assessment/{assessment_id}/rfc">
      <label>Your username</label>
      <input name="username" required placeholder="e.g. alice.lead" />
      <label>Title</label>
      <input name="title" required />
      <label>Question</label>
      <input name="question" required />
      <label>Category (optional)</label>
      <select name="category"><option value="">-- none --</option>{options}</select>
      <label>Assign to (optional Contributor username)</label>
      <input name="assigned_to" placeholder="e.g. bruno.contrib" />
      <button type="submit">Raise RFC</button>
    </form>

    <h3>Answer an RFC (Contributor or Transition Lead)</h3>
    <form method="post" action="/rfc/answer">
      <input type="hidden" name="next_assessment_id" value="{assessment_id}" />
      <label>RFC id</label>
      <input name="rfc_id" type="number" required />
      <label>Your username</label>
      <input name="username" required placeholder="e.g. bruno.contrib" />
      <label>Answer</label>
      <input name="answer_text" required />
      <button type="submit">Submit answer</button>
    </form>

    <h2>Submit final assessment</h2>
    <form method="post" action="/assessment/{assessment_id}/submit">
      <label>Your username (role lookup)</label>
      <input name="username" required placeholder="e.g. alice.lead" />
      <button type="submit">Submit assessment</button>
    </form>
    """
    return render(body)


@app.route("/assessment/<int:assessment_id>/rfc", methods=["POST"])
def raise_rfc_route(assessment_id):
    conn = db.get_connection()
    f = request.form
    role = db.get_user_role(conn, f.get("username", ""))
    result = rfc_rules.raise_rfc(role, f.get("title", ""), f.get("question", ""))

    if not result["success"]:
        conn.close()
        reason = "unauthorized role (only TransitionLead can raise an RFC)" if result["reason"] == "unauthorized_role" else "title and question are required"
        return render(f'<p class="msg error">RFC not created: {reason}.</p><p><a href="/assessment/{assessment_id}">back</a></p>')

    db.create_rfc(
        conn, assessment_id, f.get("category") or None, f["title"], f["question"],
        f["username"], f.get("assigned_to") or None,
    )
    conn.close()
    return redirect(url_for("view_assessment", assessment_id=assessment_id))


@app.route("/rfc/answer", methods=["POST"])
def answer_rfc_route():
    conn = db.get_connection()
    f = request.form
    assessment_id = f["next_assessment_id"]
    rfc_id = int(f["rfc_id"])
    role = db.get_user_role(conn, f.get("username", ""))
    rfc = db.get_rfc(conn, rfc_id)

    if not rfc:
        conn.close()
        return render(f'<p class="msg error">RFC #{rfc_id} not found.</p><p><a href="/assessment/{assessment_id}">back</a></p>')

    result = rfc_rules.answer_rfc(role, rfc["status"], f.get("answer_text", ""))

    if not result["success"]:
        conn.close()
        reasons = {
            "unauthorized_role": "unauthorized role (only Contributor or TransitionLead can answer)",
            "already_answered": "this RFC was already answered",
            "empty_answer": "answer text is required",
        }
        return render(f'<p class="msg error">Answer not saved: {reasons.get(result["reason"], result["reason"])}.</p><p><a href="/assessment/{assessment_id}">back</a></p>')

    db.answer_rfc_record(conn, rfc_id, f["answer_text"], f["username"])
    conn.close()
    return redirect(url_for("view_assessment", assessment_id=assessment_id))


@app.route("/assessment/<int:assessment_id>/evidence", methods=["POST"])
def add_evidence(assessment_id):
    conn = db.get_connection()
    f = request.form
    # Validation rule 1: freshness_date is mandatory (enforced by HTML + re-checked server-side)
    if not f.get("freshness_date"):
        conn.close()
        return render('<p class="msg error">freshness_date is required.</p><a href="/">back</a>')
    db.add_evidence(
        conn, assessment_id, f["category"], f["source"], f["owner"],
        f["freshness_date"], f["criticality"],
    )
    conn.close()
    return redirect(url_for("view_assessment", assessment_id=assessment_id))


@app.route("/assessment/<int:assessment_id>/submit", methods=["POST"])
def submit_assessment(assessment_id):
    conn = db.get_connection()
    username = request.form["username"]
    role = db.get_user_role(conn, username)
    critical = db.get_critical_categories(conn)
    evidence = db.get_evidence_for_assessment(conn, assessment_id)

    result = rules.submit_assessment(role, evidence, critical)

    if result["success"]:
        db.mark_submitted(conn, assessment_id, username)
        conn.close()
        return redirect(url_for("view_assessment", assessment_id=assessment_id))

    conn.close()
    if result["reason"] == "unauthorized_role":
        msg = f'Submission denied: role "{role or "unknown user"}" is not authorized to submit (only TransitionLead can submit).'
    else:
        msg = f'Submission blocked: missing critical evidence for {", ".join(result["missing"])}.'
    return render(f'<p class="msg error">{msg}</p><p><a href="/assessment/{assessment_id}">back</a></p>')


if __name__ == "__main__":
    app.run(debug=True)
