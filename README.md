# Bearcat RPA – Employee Onboarding Automation System

## Overview

Bearcat RPA is an end-to-end employee onboarding automation system built using UiPath Studio Web, a Flask-based REST API, and Google Sheets integration. The system automates onboarding decision-making, policy compliance evaluation, background check routing, and IT provisioning notifications through a unified workflow.

The solution simulates an enterprise onboarding pipeline by combining rule-based policy processing (derived from a structured HR policy document), external API orchestration, and automated communication workflows.

---

## Key Features

- End-to-end onboarding process automation using UiPath Studio Web
- Policy-driven decision engine based on structured HR compliance rules (RCP-HR-2025-001)
- REST API-based background check and risk classification service
- Automated routing logic for onboarding decisions (Pass, Fail, Pending, Escalation)
- Automated email notification system for IT provisioning, HR escalation, and candidate communication
- Google Sheets integration for real-time data ingestion and result write-back
- Structured audit logging for all onboarding decisions
- Robust exception handling using Try-Catch-Finally workflow design

---

## System Architecture

The system is orchestrated by UiPath Studio Web and integrates multiple services into a modular workflow architecture:

- UiPath Studio Web: Primary orchestration layer for workflow execution
- Google Sheets: Source system for new hire records and destination for processed results
- Flask REST API: Central service for policy evaluation, background check simulation, and email handling
- Policy Document (RCP-HR-2025-001): Encoded compliance rules used for risk classification logic

---

## Data Flow

1. UiPath retrieves new hire records from Google Sheets
2. Employee data is sent to the Flask API for evaluation
3. Flask API processes:
   - Risk classification based on policy rules
   - Background check status simulation
   - Required document validation
4. UiPath applies routing logic based on API response
5. System triggers automated actions:
   - IT provisioning notifications
   - Candidate onboarding or rejection emails
   - HR escalation workflows
6. All results are written back to Google Sheets for audit and tracking purposes

---

## Business Logic

The onboarding workflow follows a rule-based decision model:

- Pass: Initiates IT provisioning workflow and sends onboarding communications
- Fail: Sends rejection notification and terminates onboarding process
- Pending (< 15 days): Workflow is paused and retried in the next scheduled execution cycle
- Pending (≥ 15 days): HR escalation notification is triggered
- Missing Documents: HR notification is sent and onboarding is halted

---

## Technology Stack

- RPA Platform: UiPath Studio Web
- Backend: Flask (Python)
- Data Layer: Google Sheets API
- Policy Engine: PDF-based rule extraction and structured logic mapping
- Deployment: Render cloud hosting
- Integration Protocols: REST APIs, OAuth-based Google Workspace integration

---

## Design Highlights

- Modular workflow architecture separating orchestration, decision logic, and integration layers
- Stateless API design for scalability and maintainability
- Structured exception handling to ensure row-level fault isolation
- Real-time data synchronization between UiPath and Google Sheets
- Policy-driven automation logic enabling configurable onboarding rules without code changes

---

## Constraints

- Flask service hosted on free-tier infrastructure may experience cold start delays
- Email system implemented as internal Flask inbox for demonstration purposes
- UiPath Studio Web operates under low-code constraints without direct scripting capabilities
- Google Sheets API rate limits may introduce controlled processing delays in large datasets

---

## Project Objective

The objective of this system is to demonstrate an enterprise-grade implementation of intelligent RPA combined with lightweight AI-driven decision support. The system enables automated onboarding workflows with minimal manual intervention while maintaining auditability and compliance traceability.
