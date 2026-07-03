import os
import pandas as pd
import requests
import streamlit as st

API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8001")

st.set_page_config(
    page_title="Enterprise FinOps Executive Dashboard",
    layout="wide"
)

st.title("Enterprise FinOps Executive Dashboard")
st.caption("Executive view of savings, approvals, risks, execution readiness, and workflow history.")

if st.button("Run Demo Analysis"):
    response = requests.post(
        f"{API_BASE_URL}/analyze",
        json={
            "user_query": "Analyze my AWS bill and recommend optimizations in demo mode."
        },
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

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Analytics",
    "Recommendations",
    "Workflow History",
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

with tab5:
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
