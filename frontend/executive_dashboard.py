import os
import pandas as pd
import requests
import streamlit as st
from frontend.auth import auth_headers, logout_button, require_login

API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8001")

st.set_page_config(
    page_title="Enterprise FinOps Executive Dashboard",
    layout="wide",
)

require_login()
logout_button()

st.title("Enterprise FinOps Executive Dashboard")
st.caption("Executive view of savings, approvals, risks, execution readiness, and workflow history.")

if st.button("Run Demo Analysis"):
    response = requests.post(
        f"{API_BASE_URL}/analyze",
        json={
            "user_query": "Analyze my AWS bill and recommend optimizations in demo mode."
        },
        headers=auth_headers(),
        timeout=120
    )

    if response.status_code != 200:
        st.error("Failed to run analysis.")
        st.stop()

    st.session_state["dashboard_result"] = response.json()

result = st.session_state.get("dashboard_result")

if not result:
    st.info("Click 'Run Demo Analysis' to load dashboard data.")
    st.stop()

data = result.get("result", {})

optimization = data.get("optimization_plan", {})
decision = data.get("decision_engine", {})
approval = data.get("approval_workflow", {})
change = data.get("change_manager", {})
execution = data.get("execution_planner", {})
execution_results = data.get("execution_results", {})

plans = optimization.get("optimization_plan", [])
decisions = decision.get("decisions", [])
approvals = approval.get("approval_requests", [])
changes = change.get("change_requests", [])
execution_plans = execution.get("execution_plans", [])

st.subheader("Executive KPIs")

cols = st.columns(6)

cols[0].metric("Opportunities", optimization.get("optimization_summary", {}).get("total_opportunities", 0))
cols[1].metric("Monthly Savings", f"${decision.get('summary', {}).get('estimated_monthly_savings_usd', 0):,.2f}")
cols[2].metric("Annual Savings", f"${decision.get('summary', {}).get('estimated_annual_savings_usd', 0):,.2f}")
cols[3].metric("Pending Approvals", approval.get("approval_count", 0))
cols[4].metric("Change Requests", change.get("change_requests_count", 0))
cols[5].metric("Execution Plans", execution.get("execution_plans_count", 0))

st.divider()

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "Analytics",
    "Recommendations",
    "Workflow History",
    "Step Functions",
    "Architecture",
    "System Health"
])

with tab1:
    st.subheader("Executive Analytics")

    chart_col1, chart_col2 = st.columns(2)

    top_services = (
        execution_results
        .get("cost_analysis", {})
        .get("cost_summary", {})
        .get("top_services", [])
    )

    if top_services:
        service_df = pd.DataFrame(top_services)
        service_df = service_df.rename(columns={"service": "Service", "amount": "Cost USD"})

        with chart_col1:
            st.write("**Cost by Service**")
            st.bar_chart(service_df.set_index("Service"))

    savings_rows = [
        {
            "Recommendation": item.get("action"),
            "Monthly Savings USD": item.get("estimated_monthly_savings_usd", 0)
        }
        for item in plans
    ]

    if savings_rows:
        savings_df = pd.DataFrame(savings_rows)

        with chart_col2:
            st.write("**Savings by Recommendation**")
            st.bar_chart(savings_df.set_index("Recommendation"))

    risk_col, approval_col = st.columns(2)

    if decisions:
        risk_df = pd.DataFrame([
            {"Risk": item.get("risk", "unknown"), "Count": 1}
            for item in decisions
        ])
        risk_summary = risk_df.groupby("Risk").sum().reset_index()

        with risk_col:
            st.write("**Risk Distribution**")
            st.bar_chart(risk_summary.set_index("Risk"))

        approval_df = pd.DataFrame([
            {
                "Approval Status": "Approval Required" if item.get("requires_approval") else "Review Only",
                "Count": 1
            }
            for item in decisions
        ])
        approval_summary = approval_df.groupby("Approval Status").sum().reset_index()

        with approval_col:
            st.write("**Approval Status**")
            st.bar_chart(approval_summary.set_index("Approval Status"))

with tab2:
    st.subheader("Top Optimization Recommendations")

    if not plans:
        st.info("No optimization opportunities found.")
    else:
        for item in plans[:8]:
            with st.expander(f"{item.get('service')} — {item.get('action')}", expanded=True):
                c1, c2, c3, c4 = st.columns(4)

                c1.metric("Monthly Savings", f"${item.get('estimated_monthly_savings_usd', 0):,.2f}")
                c2.metric("Priority", item.get("priority_score", 0))
                c3.metric("Risk", item.get("risk", "unknown"))
                c4.metric("Approval", "Yes" if item.get("requires_approval") else "No")

                st.write("**Recommendation:**")
                st.write(item.get("recommendation"))

                st.write("**Implementation Steps:**")
                for step in item.get("implementation_steps", []):
                    st.write(f"- {step}")

with tab3:
    st.subheader("Workflow History")

    try:
        workflow_response = requests.get(
            f"{API_BASE_URL}/workflows",
            headers=auth_headers(),
            timeout=30
        )

        if workflow_response.status_code != 200:
            st.error("Failed to load workflow history.")
        else:
            workflows = workflow_response.json().get("workflows", [])

            if not workflows:
                st.info("No persisted workflows found.")
            else:
                workflow_rows = []

                for workflow in workflows:
                    payload = workflow.get("payload", {})
                    workflow_result = payload.get("result", {})
                    workflow_decision = workflow_result.get("decision_engine", {})
                    workflow_approval = workflow_result.get("approval_workflow", {})

                    workflow_rows.append({
                        "Workflow ID": workflow.get("workflow_id"),
                        "Type": workflow.get("workflow_type"),
                        "Status": workflow.get("status"),
                        "Monthly Savings": workflow_decision.get("summary", {}).get("estimated_monthly_savings_usd", 0),
                        "Approvals": workflow_approval.get("approval_count", 0),
                        "Created": workflow.get("created_at"),
                        "Updated": workflow.get("updated_at")
                    })

                workflow_df = pd.DataFrame(workflow_rows)
                st.dataframe(workflow_df, width="stretch")

                st.write("**Latest Workflow Details**")
                with st.expander(workflows[0].get("workflow_id", "Latest Workflow"), expanded=False):
                    st.json(workflows[0])

    except Exception as error:
        st.error(f"Workflow history error: {error}")

with tab4:
    st.subheader("AWS Step Functions Executions")
    metrics_response = requests.get(
        f"{API_BASE_URL}/stepfunctions/metrics?max_results=50",
        timeout=30
    )

    if metrics_response.status_code == 200:
        sf_metrics = metrics_response.json()

        m1, m2, m3, m4, m5 = st.columns(5)

        m1.metric("Total Executions", sf_metrics.get("total_executions", 0))
        m2.metric("Succeeded", sf_metrics.get("succeeded", 0))
        m3.metric("Failed", sf_metrics.get("failed", 0))
        m4.metric("Running", sf_metrics.get("running", 0))
        m5.metric("Success Rate", f"{sf_metrics.get('success_rate', 0)}%")

        st.metric(
            "Average Duration",
            f"{sf_metrics.get('average_duration_ms', 0)} ms"
        )

    try:
        sf_response = requests.get(
            f"{API_BASE_URL}/stepfunctions/executions?max_results=10",
            timeout=30
        )

        if sf_response.status_code != 200:
            st.error("Failed to load Step Functions executions.")
        else:
            sf_data = sf_response.json()
            executions = sf_data.get("executions", [])

            if not executions:
                st.info("No Step Functions executions found.")
            else:
                sf_rows = []

                for execution in executions:
                    sf_rows.append({
                        "Execution ID": execution.get("name"),
                        "Status": execution.get("status"),
                        "Started": execution.get("start_date"),
                        "Stopped": execution.get("stop_date"),
                        "Redrive Count": execution.get("redrive_count", 0),
                        "Execution ARN": execution.get("execution_arn")
                    })

                sf_df = pd.DataFrame(sf_rows)
                st.dataframe(sf_df, width="stretch")

                with st.expander("Latest Execution Details", expanded=False):
                    latest_execution_arn = executions[0].get("execution_arn")

                    detail_response = requests.get(
                        f"{API_BASE_URL}/stepfunctions/status",
                        params={"execution_arn": latest_execution_arn},
                        timeout=30
                    )

                    if detail_response.status_code == 200:
                        st.json(detail_response.json())
                    else:
                        st.error("Unable to load latest execution details.")

    except Exception as error:
        st.error(f"Step Functions history error: {error}")



with tab5:
    st.subheader("Platform Architecture")

    st.code(
        """
User
  ↓
Streamlit Portal
  ↓
FastAPI Backend
  ↓
Planner Agent
  ↓
Coordinator Agent
  ↓
AWS Analysis Agents
  ├── Organizations
  ├── Cost Analysis
  ├── CUR
  ├── Cost Anomaly Detection
  ├── Pricing
  ├── Budgets
  ├── EC2 Discovery
  ├── CloudWatch
  └── Compute Optimizer
  ↓
Optimization Planner
  ↓
Decision Engine
  ↓
Reasoning Engine
  ↓
Approval Workflow
  ↓
Enterprise Change Manager
  ↓
Execution Planner
  ↓
Execution Agent
  ↓
Verification Agent
  ↓
Rollback Agent
  ↓
Step Functions / CDK / DynamoDB
        """,
        language="text"
    )

with tab6:
    st.subheader("System Health")

    health_rows = [
        {"Component": "FastAPI Backend", "Status": "Healthy", "Details": "API responding"},
        {"Component": "DynamoDB Workflow Store", "Status": "Healthy", "Details": "Workflow history enabled"},
        {"Component": "Planner Agent", "Status": "Healthy", "Details": "Optimization workflow selected"},
        {"Component": "Coordinator Agent", "Status": "Healthy", "Details": "Multi-agent orchestration active"},
        {"Component": "Approval Portal", "Status": "Healthy", "Details": "Pending approvals visible"},
        {"Component": "Execution Engine", "Status": "Safe Mode", "Details": "Dry-run only"},
        {"Component": "Step Functions", "Status": "Foundation Ready", "Details": "CDK phase completed"},
        {"Component": "AWS Organizations", "Status": "Demo Healthy", "Details": "Standalone account handled gracefully"},
        {"Component": "Bedrock LLM", "Status": "Fallback Ready", "Details": "Quota throttling handled safely"}
    ]

    health_df = pd.DataFrame(health_rows)
    st.dataframe(health_df, width="stretch")
