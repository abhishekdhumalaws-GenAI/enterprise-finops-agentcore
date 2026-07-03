# Enterprise AI FinOps Platform on AWS

![Python](https://img.shields.io/badge/Python-3.11+-blue)
![AWS](https://img.shields.io/badge/AWS-FinOps-orange)
![FastAPI](https://img.shields.io/badge/FastAPI-Backend-green)
![Streamlit](https://img.shields.io/badge/Streamlit-Dashboard-red)
![DynamoDB](https://img.shields.io/badge/DynamoDB-Workflow%20Store-blue)
![Step Functions](https://img.shields.io/badge/Step%20Functions-Orchestration-purple)
![Status](https://img.shields.io/badge/Status-v1.0%20Preview-success)

An enterprise-grade AI FinOps platform that analyzes AWS spend, detects anomalies, estimates savings, generates optimization plans, creates approval workflows, prepares change requests, executes dry-run actions, verifies outcomes, prepares rollback plans, and stores workflow history.

> Built as a production-style portfolio project demonstrating AWS, Agentic AI, FinOps, enterprise governance, workflow orchestration, and dashboard-driven operations.

---

## Product Preview

| Executive Dashboard | Approval Portal |
|---|---|
| Add screenshot: `docs/assets/screenshots/executive-dashboard.png` | Add screenshot: `docs/assets/screenshots/approval-portal.png` |

---

## Why This Project Is Different

Most FinOps demos stop at cost analysis.

This platform goes further:

```text
Cost Analysis
   ↓
Anomaly Detection
   ↓
Optimization Planning
   ↓
ROI / Risk / Confidence Scoring
   ↓
Human Approval Workflow
   ↓
Enterprise Change Management
   ↓
Dry-Run Execution
   ↓
Verification
   ↓
Rollback Preparation
   ↓
Workflow Persistence
   ↓
Executive Dashboard

---

## Business Value

The demo workflow generates:

9 optimization opportunities
5 approval requests
5 enterprise change requests
5 dry-run execution plans
$13,846.89 estimated monthly savings
$166,162.68 estimated annual savings
ROI, risk, confidence, approval, execution, verification, and rollback metadata

---

## Key Capabilities

- Multi-agent FinOps orchestration
- AWS cost analysis
- Cost anomaly detection
- CUR discovery
- EC2 discovery
- CloudWatch metric analysis
- Compute Optimizer integration
- Pricing analysis
- AWS Budgets analysis
- AWS Organizations support
- Optimization planner
- AI decision engine
- AI reasoning engine
- Approval workflow agent
- Enterprise change manager
- Dry-run execution planner
- Verification agent
- Rollback agent
- DynamoDB workflow persistence
- Executive dashboard
- Approval portal
- Demo/mock mode for reliable showcasing

---

## Architecture Overview
For detailed architecture diagrams, see:

[Architecture Documentation](docs/ARCHITECTURE.md)

```text
User
  ↓
Streamlit Executive Dashboard / Approval Portal
  ↓
FastAPI Backend
  ↓
Request Parser
  ↓
Planner Agent
  ↓
Coordinator Agent
  ↓
Specialized AWS Agents
  ├── Organizations Agent
  ├── Cost Analysis Agent
  ├── CUR Agent
  ├── Cost Anomaly Detection Agent
  ├── Pricing Agent
  ├── Budgets Agent
  ├── EC2 Discovery Agent
  ├── CloudWatch Agent
  └── Compute Optimizer Agent
  ↓
Optimization Planner Agent
  ↓
AI Decision Engine
  ↓
AI Reasoning Engine
  ↓
Approval Workflow Agent
  ↓
Enterprise Change Manager
  ↓
Execution Planner Agent
  ↓
Execution Agent
  ↓
Verification Agent
  ↓
Rollback Agent
  ↓
DynamoDB Workflow Store / Step Functions Foundation


---

## Platform Workflow

Analyze
  ↓
Plan
  ↓
Collect AWS facts
  ↓
Detect anomalies
  ↓
Estimate savings
  ↓
Generate optimization plan
  ↓
Score ROI, risk, confidence
  ↓
Generate approval requests
  ↓
Create enterprise change requests
  ↓
Prepare dry-run execution plans
  ↓
Execute after approval
  ↓
Verify
  ↓
Rollback if needed
  ↓
Persist workflow history

---

## Agents

| Agent                        | Responsibility                                    |
| ---------------------------- | ------------------------------------------------- |
| Planner Agent                | Selects workflow based on user intent             |
| Coordinator Agent            | Orchestrates multi-agent execution                |
| Cost Analysis Agent          | Fetches AWS spend data                            |
| Cost Anomaly Detection Agent | Detects unusual spend patterns                    |
| Pricing Agent                | Fetches AWS pricing information                   |
| Budgets Agent                | Reviews AWS Budgets                               |
| EC2 Discovery Agent          | Discovers EC2 resources                           |
| CloudWatch Agent             | Fetches utilization metrics                       |
| Compute Optimization Agent   | Reads Compute Optimizer recommendations           |
| CUR Agent                    | Discovers Cost and Usage Reports                  |
| Organizations Agent          | Handles AWS Organizations context                 |
| Optimization Planner Agent   | Converts findings into optimization opportunities |
| Approval Workflow Agent      | Creates approval-ready requests                   |
| Execution Planner Agent      | Builds dry-run execution plans                    |
| Execution Agent              | Simulates safe execution                          |
| Verification Agent           | Validates execution results                       |
| Rollback Agent               | Prepares rollback plans                           |


---

## Intelligence Engines

| Engine                     | Purpose                                                                |
| -------------------------- | ---------------------------------------------------------------------- |
| Knowledge Graph            | Structures relationships between services, costs, and resources        |
| Fact Summarizer            | Summarizes grounded operational facts                                  |
| Savings Estimation Engine  | Estimates monthly and annual savings                                   |
| Root Cause Analysis Engine | Explains likely cost drivers                                           |
| AI Decision Engine         | Calculates ROI, risk, confidence, and decision type                    |
| AI Reasoning Engine        | Produces hypothesis, evidence, risk, execution, and rollback reasoning |
| Enterprise Change Manager  | Converts approvals into enterprise change records                      |

---

## Demo Mode

Demo mode provides realistic FinOps data without depending on live AWS spend or Bedrock token limits.

Example:

curl -X POST http://localhost:8001/analyze \
-H "Content-Type: application/json" \
-d '{"user_query":"Analyze my AWS bill and recommend optimizations in demo mode."}'

Demo mode generates:

9 optimization opportunities
5 approval requests
5 change requests
5 dry-run execution plans
Estimated monthly savings
Estimated annual savings
Risk and ROI scoring
Workflow persistence

---

## API Endpoints

| Endpoint     | Method | Purpose                       |
| ------------ | ------ | ----------------------------- |
| `/`          | GET    | Health check                  |
| `/analyze`   | POST   | Run FinOps analysis           |
| `/execute`   | POST   | Execute approved dry-run plan |
| `/workflows` | GET    | List persisted workflows      |

---

## Run Locally

1. Create virtual environment
python -m venv venv
source venv/bin/activate

2. Install dependencies
pip install -r requirements.txt

3. Start FastAPI backend
uvicorn backend.api.main:app --host 0.0.0.0 --port 8001 --reload

4. Start Approval Portal
streamlit run frontend/approval_portal.py --server.port 8501 --server.address 0.0.0.0

5. Start Executive Dashboard
streamlit run frontend/executive_dashboard.py --server.port 8502 --server.address 0.0.0.0

---

## Dashboards

#Executive Dashboard

Shows:
Optimization opportunities
Monthly savings
Annual savings
Pending approvals
Change requests
Execution plans
Cost by service
Savings by recommendation
Risk distribution
Approval status
Workflow history
System health

# Approval Portal

Shows:
Pending approvals
Change requests
Dry-run execution plans
Execution results
Raw workflow data

---

## AWS Services Used

Amazon Bedrock
AWS Cost Explorer
AWS Cost Anomaly Detection
AWS Pricing API
AWS Budgets
AWS Organizations
Amazon EC2
Amazon CloudWatch
AWS Compute Optimizer
AWS Cost and Usage Reports
Amazon DynamoDB
AWS Step Functions
AWS CDK

---

## Repository Structure

enterprise-finops-agentcore/
├── backend/
│   ├── agents/
│   ├── api/
│   ├── engines/
│   ├── orchestrators/
│   ├── services/
│   ├── tools/
│   └── utils/
├── frontend/
│   ├── approval_portal.py
│   └── executive_dashboard.py
├── infrastructure/
│   └── cdk/
├── docs/
├── scripts/
└── README.md

---

## Current Safety Model

This platform currently supports dry-run execution only.

It does not directly modify AWS resources during execution.

Live execution should only be enabled after:

IAM least privilege review
Approval workflow hardening
Rollback validation
Step Functions deployment
Audit logging
Production testing

---

## Roadmap
 Multi-agent FinOps orchestration
 Optimization planner
 AI decision engine
 AI reasoning engine
 Approval workflow
 Change manager
 Dry-run execution
 Verification and rollback agents
 Workflow persistence
 Executive dashboard
 Approval portal
 Docker Compose
 GitHub Actions CI/CD
 Cognito authentication
 Step Functions live integration
 AgentCore integration
 Production deployment

---

## Project Status

Version: v1.0-preview

The platform is currently suitable for portfolio demonstration, architecture review, and controlled dry-run demos.
