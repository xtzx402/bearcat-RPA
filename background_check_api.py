"""
Bearcat Corporation — Background Check & Risk Policy API v3.0
+ Built-in Email Inbox (replaces Mailtrap for demo purposes)

Endpoints:
    GET  /status
    GET  /background-check?employee_id=EMP001&department=Finance&role=Financial Analyst&api_key=demo-api-key-001
    POST /send-email?api_key=demo-api-key-001   (replaces SMTP)
    GET  /inbox                                  (view all emails - web UI)
    GET  /inbox/api?api_key=demo-api-key-001     (view all emails - JSON)
    DELETE /inbox/clear?api_key=demo-api-key-001 (clear inbox)
    GET  /admin/records?api_key=demo-api-key-001
    PUT  /admin/update?api_key=demo-api-key-001
"""

from flask import Flask, request, jsonify
from datetime import datetime

app = Flask(__name__)

API_KEY = "demo-api-key-001"

# ── In-memory email inbox ─────────────────────────────────────────────────────
EMAIL_INBOX = []

# ── Risk Policy Rules ─────────────────────────────────────────────────────────
RISK_POLICY = {
    "Finance": {
        "risk_level": "HIGH",
        "required_documents": ["Government-Issued ID", "I-9 Form", "Finance/Accounting Transcript", "Signed Employment Agreement"],
        "criminal_record_check_required": True,
        "security_clearance_required": False,
        "equipment": "Laptop + Monitor + Secure Token",
        "risk_policy_notes": "Finance role: clean criminal record required. Any criminal flag must be escalated to HR Manager and Legal per BR-003b."
    },
    "Legal": {
        "risk_level": "HIGH",
        "required_documents": ["Government-Issued ID", "I-9 Form", "Law Degree Transcript", "Signed Employment Agreement", "Security Clearance Form"],
        "criminal_record_check_required": False,
        "security_clearance_required": True,
        "equipment": "Laptop + Monitor + Encrypted USB Drive",
        "risk_policy_notes": "Legal role: security clearance required. IT provisioning on hold until HR Manager confirms clearance per BR-003c."
    },
    "IT": {
        "risk_level": "MEDIUM",
        "required_documents": ["Government-Issued ID", "I-9 Form", "IT/Engineering Transcript", "Signed Employment Agreement"],
        "criminal_record_check_required": False,
        "security_clearance_required": False,
        "equipment": "Laptop + Monitor + Additional Monitor + Docking Station",
        "risk_policy_notes": "IT role: standard checks apply. Academic transcript confirming relevant technical degree required."
    }
}

STANDARD_POLICY = {
    "risk_level": "STANDARD",
    "required_documents": ["Government-Issued ID", "I-9 Form", "Signed Employment Agreement"],
    "criminal_record_check_required": False,
    "security_clearance_required": False,
    "equipment": "Laptop + Monitor",
    "risk_policy_notes": "Standard role: no additional compliance requirements."
}

# ── Background Check Database ─────────────────────────────────────────────────
BACKGROUND_CHECKS = {
    "EMP001": {"employee_id": "EMP001", "full_name": "John Smith", "status": "Pass", "checked_date": "2025-05-01", "days_waiting": 0, "criminal_flag": False, "notes": "All checks passed."},
    "EMP002": {"employee_id": "EMP002", "full_name": "Sarah Johnson", "status": "Fail", "checked_date": "2025-05-05", "days_waiting": 0, "criminal_flag": False, "notes": "Failed due to discrepancy in employment history."},
    "EMP003": {"employee_id": "EMP003", "full_name": "Michael Chen", "status": "Pending", "checked_date": "2025-05-20", "days_waiting": 8, "criminal_flag": False, "notes": "Check in progress."},
    "EMP004": {"employee_id": "EMP004", "full_name": "Emily Davis", "status": "Pending", "checked_date": "2025-05-15", "days_waiting": 3, "criminal_flag": False, "notes": "Check in progress."},
    "EMP005": {"employee_id": "EMP005", "full_name": "James Wilson", "status": "Pending", "checked_date": "2025-04-20", "days_waiting": 25, "criminal_flag": False, "notes": "Extended pending."},
    "EMP006": {"employee_id": "EMP006", "full_name": "Robert Kim", "status": "Pass", "checked_date": "2025-05-10", "days_waiting": 0, "criminal_flag": True, "notes": "Pass — criminal record flag detected. Escalation required per BR-003b."},
}


def verify_api_key():
    key = request.args.get("api_key") or request.headers.get("X-API-Key")
    if key != API_KEY:
        return jsonify({"error": "Unauthorized", "message": "Invalid or missing API key.", "code": 401}), 401
    return None


# ── Routes ────────────────────────────────────────────────────────────────────

@app.route("/status", methods=["GET"])
def health_check():
    return jsonify({
        "service": "Bearcat Background Check & Risk Policy API",
        "status": "online",
        "version": "3.0.0",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "policy_ref": "RCP-HR-2025-001 Version 2.1",
        "inbox_count": len(EMAIL_INBOX)
    }), 200


@app.route("/background-check", methods=["GET"])
def background_check():
    auth_error = verify_api_key()
    if auth_error:
        return auth_error

    employee_id = request.args.get("employee_id", "").strip().upper()
    department = request.args.get("department", "").strip()
    role = request.args.get("role", "").strip()

    if not employee_id:
        return jsonify({"error": "Bad Request", "message": "employee_id is required.", "code": 400}), 400
    if not department:
        return jsonify({"error": "Bad Request", "message": "department is required.", "code": 400}), 400

    record = BACKGROUND_CHECKS.get(employee_id)
    if not record:
        return jsonify({"error": "Not Found", "message": f"No record found for: {employee_id}", "code": 404}), 404

    policy = None
    for key in RISK_POLICY:
        if key.lower() == department.lower():
            policy = RISK_POLICY[key]
            break
    if not policy:
        policy = STANDARD_POLICY

    return jsonify({
        "employee_id": record["employee_id"],
        "full_name": record["full_name"],
        "status": record["status"],
        "checked_date": record["checked_date"],
        "days_waiting": record["days_waiting"],
        "criminal_flag": record["criminal_flag"],
        "bg_notes": record["notes"],
        "department": department,
        "role": role,
        "risk_level": policy["risk_level"],
        "required_documents": ", ".join(policy["required_documents"]),
        "criminal_record_check_required": policy["criminal_record_check_required"],
        "security_clearance_required": policy["security_clearance_required"],
        "equipment": policy["equipment"],
        "risk_policy_notes": policy["risk_policy_notes"],
        "retrieved_at": datetime.utcnow().isoformat() + "Z",
        "vendor": "Bearcat Background Check Services (Simulated)",
        "policy_ref": "RCP-HR-2025-001 Version 2.1"
    }), 200


@app.route("/send-email", methods=["POST"])
def send_email():
    """
    Replaces SMTP — UiPath sends email content here instead.
    Body (JSON):
        {
            "to": "john.smith@bearcat.com",
            "subject": "Welcome to Bearcat",
            "body": "<html>...</html>",
            "type": "welcome" | "rejection" | "hr_notification" | "it_provisioning"
        }
    """
    auth_error = verify_api_key()
    if auth_error:
        return auth_error

    data = request.get_json()
    if not data:
        return jsonify({"error": "Bad Request", "message": "JSON body required.", "code": 400}), 400

    email = {
        "id": len(EMAIL_INBOX) + 1,
        "to": data.get("to", ""),
        "subject": data.get("subject", ""),
        "body": data.get("body", ""),
        "type": data.get("type", "general"),
        "sent_at": datetime.utcnow().isoformat() + "Z"
    }

    EMAIL_INBOX.append(email)

    return jsonify({
        "message": "Email sent successfully",
        "email_id": email["id"],
        "to": email["to"],
        "subject": email["subject"],
        "sent_at": email["sent_at"]
    }), 200


@app.route("/inbox", methods=["GET"])
def inbox_view():
    """Web UI to view all emails."""
    emails_html = ""
    for email in reversed(EMAIL_INBOX):
        type_colors = {
            "welcome": "#e8f5e9",
            "rejection": "#ffebee",
            "hr_notification": "#fff3e0",
            "it_provisioning": "#e3f2fd",
            "general": "#f5f5f5"
        }
        type_labels = {
            "welcome": "✅ Welcome Email",
            "rejection": "❌ Rejection",
            "hr_notification": "📋 HR Notification",
            "it_provisioning": "🖥️ IT Provisioning",
            "general": "📧 General"
        }
        bg = type_colors.get(email["type"], "#f5f5f5")
        label = type_labels.get(email["type"], "📧 Email")

        emails_html += f"""
        <div style="background:{bg};border-radius:8px;padding:20px;margin-bottom:16px;border:1px solid #ddd;">
            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px;">
                <span style="font-size:14px;font-weight:bold;color:#333;">{label}</span>
                <span style="font-size:12px;color:#888;">{email['sent_at'][:19].replace('T',' ')} UTC</span>
            </div>
            <div style="margin-bottom:8px;"><b>To:</b> {email['to']}</div>
            <div style="margin-bottom:12px;"><b>Subject:</b> {email['subject']}</div>
            <div style="background:white;padding:16px;border-radius:4px;border:1px solid #eee;">
                {email['body']}
            </div>
        </div>
        """

    if not EMAIL_INBOX:
        emails_html = '<div style="text-align:center;color:#888;padding:40px;">No emails yet. Run the UiPath bot to send emails.</div>'

    html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Bearcat Email Inbox</title>
    <meta charset="utf-8">
    <meta http-equiv="refresh" content="10">
    <style>
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{ font-family: Arial, sans-serif; background: #f0f2f5; }}
        .header {{ background: #1F3864; color: white; padding: 20px 40px; }}
        .header h1 {{ font-size: 24px; }}
        .header p {{ font-size: 14px; opacity: 0.8; margin-top: 4px; }}
        .stats {{ background: white; padding: 16px 40px; border-bottom: 1px solid #ddd; display: flex; gap: 24px; }}
        .stat {{ font-size: 14px; color: #555; }}
        .stat b {{ color: #1F3864; font-size: 20px; display: block; }}
        .container {{ max-width: 900px; margin: 24px auto; padding: 0 20px; }}
        .clear-btn {{ background: #dc3545; color: white; border: none; padding: 8px 16px; border-radius: 4px; cursor: pointer; font-size: 14px; float: right; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>📬 Bearcat Corporation — Email Inbox</h1>
        <p>Simulated email inbox for RPA demo · Auto-refreshes every 10 seconds</p>
    </div>
    <div class="stats">
        <div class="stat"><b>{len(EMAIL_INBOX)}</b>Total Emails</div>
        <div class="stat"><b>{sum(1 for e in EMAIL_INBOX if e['type']=='welcome')}</b>Welcome</div>
        <div class="stat"><b>{sum(1 for e in EMAIL_INBOX if e['type']=='rejection')}</b>Rejections</div>
        <div class="stat"><b>{sum(1 for e in EMAIL_INBOX if e['type']=='hr_notification')}</b>HR Notifications</div>
        <div class="stat"><b>{sum(1 for e in EMAIL_INBOX if e['type']=='it_provisioning')}</b>IT Provisioning</div>
    </div>
    <div class="container">
        <a href="/inbox/clear?api_key={API_KEY}" onclick="return confirm('Clear all emails?')" style="text-decoration:none;">
            <button class="clear-btn">🗑️ Clear Inbox</button>
        </a>
        <br><br>
        {emails_html}
    </div>
</body>
</html>"""
    return html


@app.route("/inbox/api", methods=["GET"])
def inbox_api():
    auth_error = verify_api_key()
    if auth_error:
        return auth_error
    return jsonify({"total": len(EMAIL_INBOX), "emails": list(reversed(EMAIL_INBOX))}), 200


@app.route("/inbox/clear", methods=["GET", "DELETE"])
def inbox_clear():
    auth_error = verify_api_key()
    if auth_error:
        return auth_error
    EMAIL_INBOX.clear()
    if request.method == "GET":
        return '<script>window.location="/inbox"</script>'
    return jsonify({"message": "Inbox cleared."}), 200


@app.route("/admin/records", methods=["GET"])
def admin_records():
    auth_error = verify_api_key()
    if auth_error:
        return auth_error
    return jsonify({"total_records": len(BACKGROUND_CHECKS), "records": list(BACKGROUND_CHECKS.values())}), 200


@app.route("/admin/update", methods=["PUT"])
def admin_update():
    auth_error = verify_api_key()
    if auth_error:
        return auth_error

    data = request.get_json()
    if not data:
        return jsonify({"error": "Bad Request", "message": "JSON body required.", "code": 400}), 400

    employee_id = data.get("employee_id", "").strip().upper()
    if not employee_id or employee_id not in BACKGROUND_CHECKS:
        return jsonify({"error": "Not Found", "message": f"No record found for: {employee_id}", "code": 404}), 404

    for field in ["status", "criminal_flag", "notes", "days_waiting", "checked_date"]:
        if field in data:
            BACKGROUND_CHECKS[employee_id][field] = data[field]

    return jsonify({"message": f"Updated {employee_id}", "updated": BACKGROUND_CHECKS[employee_id]}), 200


if __name__ == "__main__":
    print("=" * 60)
    print("  Bearcat API v3.0 — with Built-in Email Inbox")
    print("=" * 60)
    print("  Inbox UI: http://localhost:5000/inbox")
    print("  API Key:  demo-api-key-001")
    print("=" * 60)
    app.run(debug=True, port=5000)