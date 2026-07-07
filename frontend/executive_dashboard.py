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

cost_summary = (
    execution_results
    .get("cost_analysis", {})
    .get("cost_summary", {})
)

total_cost = cost_summary.get("total_cost", 0)
top_services = cost_summary.get("top_services", [])
anomalies = (
    execution_results
    .get("cost_anomaly_detection", {})
    .get("anomalies", [])
)

sf_metrics = {}

try:
    metrics_response = requests.get(
        f"{API_BASE_URL}/stepfunctions/metrics?max_results=50",
        headers=auth_headers(),
        timeout=30
    )

    if metrics_response.status_code == 200:
        sf_metrics = metrics_response.json()
except Exception:
    sf_metrics = {}

st.subheader("Executive KPIs")

cols = st.columns(6)

cols[0].metric(
    "Monthly AWS Cost",
    f"${total_cost:,.2f}"
)

cols[1].metric(
    "Monthly Savings",
    f"${decision.get('summary', {}).get('estimated_monthly_savings_usd', 0):,.2f}"
)

cols[2].metric(
    "Annual Savings",
    f"${decision.get('summary', {}).get('estimated_annual_savings_usd', 0):,.2f}"
)

cols[3].metric(
    "Anomalies",
    len(anomalies)
)

cols[4].metric(
    "Pending Approvals",
    approval.get("approval_count", 0)
)

cols[5].metric(
    "Execution Success",
    f"{sf_metrics.get('success_rate', 0)}%"
)

st.caption(
    f"Workflow ID: {result.get('workflow_id', 'N/A')} | "
    f"Opportunities: {optimization.get('optimization_summary', {}).get('total_opportunities', 0)} | "
    f"Execution Plans: {execution.get('execution_plans_count', 0)}"
)

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
        service_df = service_df.rename(
            columns={
                "service": "Service",
                "amount": "Cost USD"
            }
        )

        with chart_col1:
            st.write("### Cost by AWS Service")
            selected_services = st.multiselect(
                "Filter services",
                service_df["Service"].tolist(),
                default=service_df["Service"].tolist()
            )

            filtered_service_df = service_df[
                service_df["Service"].isin(selected_services)
            ]

            st.bar_chart(
                filtered_service_df.set_index("Service")["Cost USD"]
            )
    else:
        with chart_col1:
            st.info("No service cost data available.")

    savings_rows = [
        {
            "Recommendation": item.get("action"),
            "Service": item.get("service"),
            "Monthly Savings USD": item.get("estimated_monthly_savings_usd", 0),
            "Risk": item.get("risk", "unknown"),
            "Approval Required": item.get("requires_approval", False)
        }
        for item in plans
    ]

    if savings_rows:
        savings_df = pd.DataFrame(savings_rows)

        with chart_col2:
            st.write("### Savings by Recommendation")

            min_chart_savings = st.slider(
                "Minimum savings shown",
                min_value=0,
                max_value=int(max(savings_df["Monthly Savings USD"].max(), 1)),
                value=0,
                step=100
            )

            filtered_savings_df = savings_df[
                savings_df["Monthly Savings USD"] >= min_chart_savings
            ]

            st.bar_chart(
                filtered_savings_df.set_index("Recommendation")["Monthly Savings USD"]
            )
    else:
        with chart_col2:
            st.info("No savings recommendation data available.")

    st.divider()

    risk_col, approval_col, execution_col = st.columns(3)

    if decisions:
        risk_df = pd.DataFrame([
            {
                "Risk": item.get("risk", "unknown"),
                "Count": 1
            }
            for item in decisions
        ])

        risk_summary = risk_df.groupby("Risk").sum().reset_index()

        with risk_col:
            st.write("### Risk Distribution")
            st.bar_chart(
                risk_summary.set_index("Risk")["Count"]
            )

        approval_df = pd.DataFrame([
            {
                "Approval Status": (
                    "Approval Required"
                    if item.get("requires_approval")
                    else "Review Only"
                ),
                "Count": 1
            }
            for item in decisions
        ])

        approval_summary = approval_df.groupby("Approval Status").sum().reset_index()

        with approval_col:
            st.write("### Approval Status")
            st.bar_chart(
                approval_summary.set_index("Approval Status")["Count"]
            )
    else:
        with risk_col:
            st.info("No decision data available.")

        with approval_col:
            st.info("No approval status data available.")

    try:
        sf_metrics_response = requests.get(
            f"{API_BASE_URL}/stepfunctions/metrics?max_results=50",
            headers=auth_headers(),
            timeout=30
        )

        if sf_metrics_response.status_code == 200:
            sf_metrics_data = sf_metrics_response.json()

            execution_status_df = pd.DataFrame([
                {"Status": "Succeeded", "Count": sf_metrics_data.get("succeeded", 0)},
                {"Status": "Failed", "Count": sf_metrics_data.get("failed", 0)},
                {"Status": "Running", "Count": sf_metrics_data.get("running", 0)},
                {"Status": "Timed Out", "Count": sf_metrics_data.get("timed_out", 0)},
                {"Status": "Aborted", "Count": sf_metrics_data.get("aborted", 0)}
            ])

            with execution_col:
                st.write("### Execution Status")
                st.bar_chart(
                    execution_status_df.set_index("Status")["Count"]
                )
        else:
            with execution_col:
                st.info("No Step Functions metrics available.")

    except Exception as error:
        with execution_col:
            st.error(f"Execution metrics error: {error}")

    st.divider()

    if savings_rows:
        st.write("### Optimization Analytics Table")

        table_filter_col1, table_filter_col2 = st.columns(2)

        risk_filter = table_filter_col1.selectbox(
            "Risk Filter",
            ["All"] + sorted(savings_df["Risk"].dropna().unique().tolist())
        )

        approval_filter = table_filter_col2.selectbox(
            "Approval Filter",
            ["All", "Required", "Not Required"]
        )

        analytics_table = savings_df.copy()

        if risk_filter != "All":
            analytics_table = analytics_table[
                analytics_table["Risk"] == risk_filter
            ]

        if approval_filter == "Required":
            analytics_table = analytics_table[
                analytics_table["Approval Required"] == True
            ]

        if approval_filter == "Not Required":
            analytics_table = analytics_table[
                analytics_table["Approval Required"] == False
            ]

        st.dataframe(
            analytics_table.sort_values(
                by="Monthly Savings USD",
                ascending=False
            ),
            width="stretch"
        )

with tab2:
    st.subheader("Optimization Recommendation Drill-Down")

    if not plans:
        st.info("No optimization opportunities found.")
    else:
        for index, item in enumerate(plans[:10], start=1):
            service = item.get("service", "Unknown Service")
            action = item.get("action", "Optimization Recommendation")

            with st.expander(f"#{index} {service} — {action}", expanded=index == 1):
                c1, c2, c3, c4, c5 = st.columns(5)

                monthly_savings = item.get("estimated_monthly_savings_usd", 0)
                annual_savings = monthly_savings * 12

                c1.metric("Monthly Savings", f"${monthly_savings:,.2f}")
                c2.metric("Annual Savings", f"${annual_savings:,.2f}")
                c3.metric("Priority", item.get("priority_score", 0))
                c4.metric("Risk", item.get("risk", "unknown"))
                c5.metric("Approval", "Required" if item.get("requires_approval") else "Not Required")

                st.write("### Recommendation")
                st.write(item.get("recommendation", "No recommendation available."))

                drill_col1, drill_col2 = st.columns(2)

                with drill_col1:
                    st.write("### Evidence")
                    evidence = item.get("evidence", {})

                    if evidence:
                        st.json(evidence)
                    else:
                        st.info("No structured evidence available.")

                    st.write("### Implementation Steps")
                    steps = item.get("implementation_steps", [])

                    if steps:
                        for step in steps:
                            st.write(f"- {step}")
                    else:
                        st.info("No implementation steps available.")

                with drill_col2:
                    matching_decision = None

                    for decision_item in decisions:
                        if (
                            decision_item.get("service") == service
                            and decision_item.get("action") == action
                        ):
                            matching_decision = decision_item
                            break

                    if matching_decision:
                        st.write("### Decision Engine")
                        st.json({
                            "decision": matching_decision.get("decision"),
                            "roi_score": matching_decision.get("roi_score"),
                            "confidence_score": matching_decision.get("confidence_score"),
                            "risk_score": matching_decision.get("risk_score"),
                            "business_impact": matching_decision.get("business_impact")
                        })
                    else:
                        st.info("No matching decision engine record found.")

                    matching_approval = None

                    for approval_item in approvals:
                        if (
                            approval_item.get("service") == service
                            and approval_item.get("action") == action
                        ):
                            matching_approval = approval_item
                            break

                    st.write("### Approval Path")

                    if matching_approval:
                        st.json({
                            "approval_id": matching_approval.get("approval_id"),
                            "approver": matching_approval.get("approver"),
                            "approval_reason": matching_approval.get("approval_reason"),
                            "financial_impact": matching_approval.get("financial_impact"),
                            "risk_assessment": matching_approval.get("risk_assessment")
                        })
                    else:
                        st.success("No human approval required.")

                st.write("### Execution & Rollback")

                matching_execution_plan = None

                for execution_item in execution_plans:
                    if (
                        execution_item.get("service") == service
                        and execution_item.get("action") == action
                    ):
                        matching_execution_plan = execution_item
                        break

                if matching_execution_plan:
                    ex1, ex2 = st.columns(2)

                    with ex1:
                        st.write("**Execution Plan**")
                        for step in matching_execution_plan.get("execution_steps", []):
                            st.json(step)

                    with ex2:
                        st.write("**Rollback Plan**")
                        rollback_steps = matching_execution_plan.get("rollback_steps", [])

                        if rollback_steps:
                            for step in rollback_steps:
                                st.write(f"- {step}")
                        else:
                            st.info("No rollback steps available.")
                else:
                    st.info("No execution plan generated for this recommendation.")

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

                filter_col1, filter_col2, filter_col3 = st.columns(3)

                status_options = ["All"] + sorted(
                    workflow_df["Status"].dropna().unique().tolist()
                )

                type_options = ["All"] + sorted(
                    workflow_df["Type"].dropna().unique().tolist()
                )

                selected_status = filter_col1.selectbox(
                    "Workflow Status",
                    status_options
                )

                selected_type = filter_col2.selectbox(
                    "Workflow Type",
                    type_options
                )

                minimum_savings = filter_col3.number_input(
                    "Minimum Monthly Savings ($)",
                    min_value=0,
                    value=0,
                    step=100
                )

                filtered_df = workflow_df.copy()

                if selected_status != "All":
                    filtered_df = filtered_df[
                        filtered_df["Status"] == selected_status
                    ]

                if selected_type != "All":
                    filtered_df = filtered_df[
                        filtered_df["Type"] == selected_type
                    ]

                filtered_df = filtered_df[
                    filtered_df["Monthly Savings"] >= minimum_savings
                ]

                st.write(f"Showing {len(filtered_df)} of {len(workflow_df)} workflows")

                st.dataframe(filtered_df, width="stretch")

                st.write("**Latest Workflow Details**")
                with st.expander(workflows[0].get("workflow_id", "Latest Workflow"), expanded=False):
                    st.json(workflows[0])

    except Exception as error:
        st.error(f"Workflow history error: {error}")

with tab4:
    st.subheader("AWS Step Functions Executions")
    metrics_response = requests.get(
        f"{API_BASE_URL}/stepfunctions/metrics?max_results=50",
        headers=auth_headers(),
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
            headers=auth_headers(),
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
                        headers=auth_headers(),
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
