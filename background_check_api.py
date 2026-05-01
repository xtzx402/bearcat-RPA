"""
Bearcat Corporation — Background Check & Risk Policy API v2.1
Simulates a third-party background check vendor REST API.
Also reads the Risk Control Policy (RCP-HR-2025-001) to return
role-specific compliance requirements in the same response.

Usage:
    pip install flask
    python app.py

Endpoints:
    GET  /background-check?employee_id=EMP001&department=Finance&role=Financial Analyst&api_key=demo-api-key-001
    GET  /status
    GET  /admin/records?api_key=demo-api-key-001
    PUT  /admin/update?api_key=demo-api-key-001
"""

from flask import Flask, request, jsonify
from datetime import datetime

app = Flask(__name__)

# ── API Key ───────────────────────────────────────────────────────────────────
API_KEY = "demo-api-key-001"

# ── Risk Policy Rules ─────────────────────────────────────────────────────────
# Derived from RiskControlPolicy_Bearcat.pdf — RCP-HR-2025-001 Version 2.1
RISK_POLICY = {
    "Finance": {
        "risk_level": "HIGH",
        "required_documents": [
            "Government-Issued ID",
            "I-9 Form",
            "Finance/Accounting Transcript",
            "Signed Employment Agreement"
        ],
        "criminal_record_check_required": True,
        "security_clearance_required": False,
        "equipment": "Laptop + Monitor + Secure Token",
        "risk_policy_notes": "Finance role: clean criminal record required. Any criminal flag must be escalated to HR Manager and Legal per BR-003b. No security clearance needed."
    },
    "Legal": {
        "risk_level": "HIGH",
        "required_documents": [
            "Government-Issued ID",
            "I-9 Form",
            "Law Degree Transcript",
            "Signed Employment Agreement",
            "Security Clearance Form"
        ],
        "criminal_record_check_required": False,
        "security_clearance_required": True,
        "equipment": "Laptop + Monitor + Encrypted USB Drive",
        "risk_policy_notes": "Legal role: security clearance required. IT provisioning on hold until HR Manager confirms clearance per BR-003c."
    },
    "IT": {
        "risk_level": "MEDIUM",
        "required_documents": [
            "Government-Issued ID",
            "I-9 Form",
            "IT/Engineering Transcript",
            "Signed Employment Agreement"
        ],
        "criminal_record_check_required": False,
        "security_clearance_required": False,
        "equipment": "Laptop + Monitor + Additional Monitor + Docking Station",
        "risk_policy_notes": "IT role: standard checks apply. Academic transcript confirming relevant technical degree required."
    }
}

STANDARD_POLICY = {
    "risk_level": "STANDARD",
    "required_documents": [
        "Government-Issued ID",
        "I-9 Form",
        "Signed Employment Agreement"
    ],
    "criminal_record_check_required": False,
    "security_clearance_required": False,
    "equipment": "Laptop + Monitor",
    "risk_policy_notes": "Standard role: no additional compliance requirements."
}

# ── Background Check Database ─────────────────────────────────────────────────
BACKGROUND_CHECKS = {
    "EMP001": {
        "employee_id":   "EMP001",
        "full_name":     "John Smith",
        "status":        "Pass",
        "checked_date":  "2025-05-01",
        "days_waiting":  0,
        "criminal_flag": False,
        "notes":         "All checks passed. No issues found."
    },
    "EMP002": {
        "employee_id":   "EMP002",
        "full_name":     "Sarah Johnson",
        "status":        "Fail",
        "checked_date":  "2025-05-05",
        "days_waiting":  0,
        "criminal_flag": False,
        "notes":         "Failed due to discrepancy in employment history."
    },
    "EMP003": {
        "employee_id":   "EMP003",
        "full_name":     "Michael Chen",
        "status":        "Pending",
        "checked_date":  "2025-05-20",
        "days_waiting":  8,
        "criminal_flag": False,
        "notes":         "Check in progress. Awaiting court record verification."
    },
    "EMP004": {
        "employee_id":   "EMP004",
        "full_name":     "Emily Davis",
        "status":        "Pending",
        "checked_date":  "2025-05-15",
        "days_waiting":  3,
        "criminal_flag": False,
        "notes":         "Check in progress."
    },
    "EMP005": {
        "employee_id":   "EMP005",
        "full_name":     "James Wilson",
        "status":        "Pending",
        "checked_date":  "2025-04-20",
        "days_waiting":  25,
        "criminal_flag": False,
        "notes":         "Extended pending — additional verification required."
    },
    "EMP006": {
        "employee_id":   "EMP006",
        "full_name":     "Robert Kim",
        "status":        "Pass",
        "checked_date":  "2025-05-10",
        "days_waiting":  0,
        "criminal_flag": True,
        "notes":         "Pass — however criminal record flag detected. Escalation required per RCP-HR-2025-001 BR-003b."
    },
}


# ── Auth helper ───────────────────────────────────────────────────────────────
def verify_api_key():
    key = request.args.get("api_key") or request.headers.get("X-API-Key")
    if key != API_KEY:
        return jsonify({
            "error":   "Unauthorized",
            "message": "Invalid or missing API key.",
            "code":    401
        }), 401
    return None


# ── Routes ────────────────────────────────────────────────────────────────────

@app.route("/status", methods=["GET"])
def health_check():
    return jsonify({
        "service":    "Bearcat Background Check & Risk Policy API",
        "status":     "online",
        "version":    "2.1.0",
        "timestamp":  datetime.utcnow().isoformat() + "Z",
        "policy_ref": "RCP-HR-2025-001 Version 2.1"
    }), 200


@app.route("/background-check", methods=["GET"])
def background_check():
    """
    Main endpoint — returns background check result AND risk policy
    requirements in a single response.

    Query params:
        employee_id (required): e.g. EMP001
        department  (required): e.g. Finance, Legal, IT, HR, Operations
        role        (optional): e.g. Financial Analyst
        api_key     (required): demo-api-key-001

    Returns combined:
        - Background check: status, criminal_flag, days_waiting
        - Risk policy: risk_level, required_documents, equipment, notes
    """
    auth_error = verify_api_key()
    if auth_error:
        return auth_error

    employee_id = request.args.get("employee_id", "").strip().upper()
    department  = request.args.get("department", "").strip()
    role        = request.args.get("role", "").strip()

    if not employee_id:
        return jsonify({"error": "Bad Request", "message": "employee_id is required.", "code": 400}), 400

    if not department:
        return jsonify({"error": "Bad Request", "message": "department is required.", "code": 400}), 400

    # Get background check record
    record = BACKGROUND_CHECKS.get(employee_id)
    if not record:
        return jsonify({
            "error":       "Not Found",
            "message":     f"No background check record found for: {employee_id}",
            "employee_id": employee_id,
            "code":        404
        }), 404

    # Get risk policy for department
    policy = None
    for key in RISK_POLICY:
        if key.lower() == department.lower():
            policy = RISK_POLICY[key]
            break
    if not policy:
        policy = STANDARD_POLICY

    # Build combined response
    response = {
        # Background check results
        "employee_id":   record["employee_id"],
        "full_name":     record["full_name"],
        "status":        record["status"],           # Pass | Fail | Pending
        "checked_date":  record["checked_date"],
        "days_waiting":  record["days_waiting"],
        "criminal_flag": record["criminal_flag"],
        "bg_notes":      record["notes"],

        # Risk policy results (from RCP-HR-2025-001 PDF)
        "department":                     department,
        "role":                           role,
        "risk_level":                     policy["risk_level"],
        "required_documents":             ", ".join(policy["required_documents"]),
        "criminal_record_check_required": policy["criminal_record_check_required"],
        "security_clearance_required":    policy["security_clearance_required"],
        "equipment":                      policy["equipment"],
        "risk_policy_notes":              policy["risk_policy_notes"],

        # Metadata
        "retrieved_at": datetime.utcnow().isoformat() + "Z",
        "vendor":       "Bearcat Background Check Services (Simulated)",
        "policy_ref":   "RCP-HR-2025-001 Version 2.1"
    }

    return jsonify(response), 200


@app.route("/admin/records", methods=["GET"])
def admin_records():
    auth_error = verify_api_key()
    if auth_error:
        return auth_error

    return jsonify({
        "total_records": len(BACKGROUND_CHECKS),
        "records":       list(BACKGROUND_CHECKS.values()),
        "note":          "Demo admin endpoint — not present in production vendor API."
    }), 200


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

    allowed = ["status", "criminal_flag", "notes", "days_waiting", "checked_date"]
    for field in allowed:
        if field in data:
            BACKGROUND_CHECKS[employee_id][field] = data[field]

    return jsonify({
        "message":    f"Record updated successfully for {employee_id}",
        "updated":    BACKGROUND_CHECKS[employee_id],
        "updated_at": datetime.utcnow().isoformat() + "Z"
    }), 200


# ── Run ───────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 60)
    print("  Bearcat Background Check & Risk Policy API v2.1")
    print("=" * 60)
    print("  Running at:  http://localhost:5000")
    print("  API Key:     demo-api-key-001")
    print()
    print("  Main endpoint:")
    print("  GET /background-check")
    print("      ?employee_id=EMP001")
    print("      &department=Finance")
    print("      &role=Financial Analyst")
    print("      &api_key=demo-api-key-001")
    print("=" * 60)
    app.run(debug=True, port=5000)