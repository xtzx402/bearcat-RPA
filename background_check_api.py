"""
Bearcat Corporation — Simulated Background Check API
Simulates a third-party background check vendor REST API.
In production, this endpoint would be replaced by the real vendor API
with an identical request/response structure.

Usage:
    pip install flask
    python app.py

Endpoints:
    GET  /background-check?employee_id=EMP001&api_key=demo-api-key-001
    GET  /status          (health check)
    GET  /admin/records   (view all records — demo only)
    PUT  /admin/update    (update a record's status — demo only)
"""

from flask import Flask, request, jsonify
from datetime import datetime

app = Flask(__name__)

# ── API Key (demo) ────────────────────────────────────────────────────────────
API_KEY = "demo-api-key-001"

# ── Simulated background check database ──────────────────────────────────────
# In production this would be the vendor's real database.
# For demo: manually set each employee's status here.
BACKGROUND_CHECKS = {
    "EMP001": {
        "employee_id":    "EMP001",
        "full_name":      "John Smith",
        "status":         "Pass",
        "checked_date":   "2025-05-01",
        "days_waiting":   0,
        "criminal_flag":  False,
        "notes":          "All checks passed. No issues found."
    },
    "EMP002": {
        "employee_id":    "EMP002",
        "full_name":      "Sarah Johnson",
        "status":         "Fail",
        "checked_date":   "2025-05-05",
        "days_waiting":   0,
        "criminal_flag":  False,
        "notes":          "Failed due to discrepancy in employment history."
    },
    "EMP003": {
        "employee_id":    "EMP003",
        "full_name":      "Michael Chen",
        "status":         "Pending",
        "checked_date":   "2025-05-20",
        "days_waiting":   8,
        "criminal_flag":  False,
        "notes":          "Check in progress. Awaiting court record verification."
    },
    "EMP004": {
        "employee_id":    "EMP004",
        "full_name":      "Emily Davis",
        "status":         "Pending",
        "checked_date":   "2025-05-15",
        "days_waiting":   3,
        "criminal_flag":  False,
        "notes":          "Check in progress."
    },
    "EMP005": {
        "employee_id":    "EMP005",
        "full_name":      "James Wilson",
        "status":         "Pending",
        "checked_date":   "2025-04-20",
        "days_waiting":   25,
        "criminal_flag":  False,
        "notes":          "Extended pending — additional verification required."
    },
    "EMP006": {
        "employee_id":    "EMP006",
        "full_name":      "Robert Kim",
        "status":         "Pass",
        "checked_date":   "2025-05-10",
        "days_waiting":   0,
        "criminal_flag":  True,
        "notes":          "Pass — however criminal record flag detected. Escalation required per RCP-HR-2025-001 BR-003b."
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
    """Health check endpoint — no auth required."""
    return jsonify({
        "service":   "Bearcat Background Check API",
        "status":    "online",
        "version":   "1.0.0",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "note":      "Simulated vendor API for demo purposes."
    }), 200


@app.route("/background-check", methods=["GET"])
def background_check():
    """
    Main endpoint — returns background check status for a given employee.

    Query params:
        employee_id (required): e.g. EMP001
        api_key     (required): demo-api-key-001

    Returns:
        200 + JSON result  if found
        404                if employee_id not found
        401                if API key missing or invalid
        400                if employee_id not provided
    """
    # Auth
    auth_error = verify_api_key()
    if auth_error:
        return auth_error

    employee_id = request.args.get("employee_id", "").strip().upper()

    if not employee_id:
        return jsonify({
            "error":   "Bad Request",
            "message": "employee_id query parameter is required.",
            "code":    400
        }), 400

    record = BACKGROUND_CHECKS.get(employee_id)

    if not record:
        return jsonify({
            "error":       "Not Found",
            "message":     f"No background check record found for employee_id: {employee_id}",
            "employee_id": employee_id,
            "code":        404
        }), 404

    # Build response
    response = {
        "employee_id":   record["employee_id"],
        "full_name":     record["full_name"],
        "status":        record["status"],          # Pass | Fail | Pending
        "checked_date":  record["checked_date"],
        "days_waiting":  record["days_waiting"],
        "criminal_flag": record["criminal_flag"],
        "notes":         record["notes"],
        "retrieved_at":  datetime.utcnow().isoformat() + "Z",
        "vendor":        "Bearcat Background Check Services (Simulated)",
        "policy_ref":    "RCP-HR-2025-001"
    }

    return jsonify(response), 200


@app.route("/admin/records", methods=["GET"])
def admin_records():
    """
    Admin endpoint — view all records.
    Demo only: use this to verify data during testing.
    Would NOT exist in a real vendor API.
    """
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
    """
    Admin endpoint — update an employee's status for demo purposes.
    Use this during the live demo to show different workflow branches.

    Body (JSON):
        {
            "employee_id":   "EMP003",
            "status":        "Pass",
            "criminal_flag": false,
            "notes":         "Check completed."
        }
    """
    auth_error = verify_api_key()
    if auth_error:
        return auth_error

    data = request.get_json()
    if not data:
        return jsonify({
            "error":   "Bad Request",
            "message": "JSON body required.",
            "code":    400
        }), 400

    employee_id = data.get("employee_id", "").strip().upper()
    if not employee_id or employee_id not in BACKGROUND_CHECKS:
        return jsonify({
            "error":   "Not Found",
            "message": f"No record found for employee_id: {employee_id}",
            "code":    404
        }), 404

    # Update allowed fields
    allowed = ["status", "criminal_flag", "notes", "days_waiting", "checked_date"]
    for field in allowed:
        if field in data:
            BACKGROUND_CHECKS[employee_id][field] = data[field]

    return jsonify({
        "message":     f"Record updated successfully for {employee_id}",
        "updated":     BACKGROUND_CHECKS[employee_id],
        "updated_at":  datetime.utcnow().isoformat() + "Z"
    }), 200


# ── Run ───────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 55)
    print("  Bearcat Background Check API — Demo Server")
    print("=" * 55)
    print("  Running at:  http://localhost:5000")
    print("  API Key:     demo-api-key-001")
    print()
    print("  Endpoints:")
    print("  GET  /status")
    print("  GET  /background-check?employee_id=EMP001&api_key=demo-api-key-001")
    print("  GET  /admin/records?api_key=demo-api-key-001")
    print("  PUT  /admin/update?api_key=demo-api-key-001")
    print("=" * 55)
    app.run(debug=True, port=5000)