import json
import requests
import streamlit as st

ANALYZE_API_URL = "http://localhost:8001/analyze"
EXECUTE_API_URL = "http://localhost:8001/execute"

st.set_page_config(
    page_title="Enterprise FinOps Approval Portal",
    layout="wide"
)

st.title("Enterprise FinOps Approval Portal")
st.caption("Review optimization decisions, approvals, change requests, and dry-run execution plans.")

query = st.text_area(
    "FinOps Request",
    value="Analyze my AWS bill and recommend optimizations in demo mode.",
    height=80
)


def find_execution_plan_for_approval(approval_item, execution_plans):
    approval_service = approval_item.get("service")
    approval_category = approval_item.get("category")
    approval_action = approval_item.get("action")

    for plan in execution_plans:
        same_service = plan.get("service") == approval_service
        same_category = plan.get("category") == approval_category

        if same_service and same_category:
            return plan

    for plan in execution_plans:
        if approval_action and approval_action.lower() in str(plan.get("title", "")).lower():
            return plan

    return None


if st.button("Run FinOps Analysis"):
    with st.spinner("Running multi-agent FinOps workflow..."):
        response = requests.post(
            ANALYZE_API_URL,
            headers={"Content-Type": "application/json"},
            data=json.dumps({"user_query": query}),
            timeout=120
        )

    if response.status_code != 200:
        st.error(f"API error: {response.status_code}")
        st.stop()

    st.session_state["finops_result"] = response.json()
    st.session_state["execution_results"] = {}

result = st.session_state.get("finops_result")

if not result:
    st.info("Click 'Run FinOps Analysis' to load approval workflow.")
    st.stop()

data = result.get("result", {})

st.subheader("Executive Summary")
st.markdown(result.get("final_answer", "No summary available."))

optimization = data.get("optimization_plan", {})
decision = data.get("decision_engine", {})
approval = data.get("approval_workflow", {})
change = data.get("change_manager", {})
execution = data.get("execution_planner", {})

execution_plans = execution.get("execution_plans", [])

summary_cols = st.columns(5)

summary_cols[0].metric(
    "Optimization Opportunities",
    optimization.get("optimization_summary", {}).get("total_opportunities", 0)
)

summary_cols[1].metric(
    "Monthly Savings",
    f"${decision.get('summary', {}).get('estimated_monthly_savings_usd', 0):,.2f}"
)

summary_cols[2].metric(
    "Annual Savings",
    f"${decision.get('summary', {}).get('estimated_annual_savings_usd', 0):,.2f}"
)

summary_cols[3].metric(
    "Pending Approvals",
    approval.get("approval_count", 0)
)

summary_cols[4].metric(
    "Change Requests",
    change.get("change_requests_count", 0)
)

st.divider()

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Approval Queue",
    "Change Requests",
    "Execution Plans",
    "Execution Results",
    "Raw JSON"
])

with tab1:
    st.subheader("Pending Approval Requests")

    approvals = approval.get("approval_requests", [])

    if not approvals:
        st.success("No approvals required.")
    else:
        for item in approvals:
            approval_id = item.get("approval_id")
            matching_execution_plan = find_execution_plan_for_approval(
                item,
                execution_plans
            )

            with st.expander(
                f"{item.get('service')} — {item.get('action')}",
                expanded=True
            ):
                col1, col2, col3 = st.columns(3)

                col1.metric(
                    "Monthly Savings",
                    f"${item.get('financial_impact', {}).get('monthly_savings_usd', 0):,.2f}"
                )
                col2.metric(
                    "Annual Savings",
                    f"${item.get('financial_impact', {}).get('annual_savings_usd', 0):,.2f}"
                )
                col3.metric(
                    "Confidence",
                    item.get("confidence", {}).get("score", 0)
                )

                st.write("**Approver:**", item.get("approver"))
                st.write("**Reason:**", item.get("approval_reason"))
                st.write("**Hypothesis:**", item.get("hypothesis"))

                st.write("**Risk Assessment**")
                st.json(item.get("risk_assessment", {}))

                st.write("**Rollback Plan**")
                for step in item.get("rollback_plan", []):
                    st.write(f"- {step}")

                if matching_execution_plan:
                    st.write("**Linked Execution Plan:**")
                    st.code(matching_execution_plan.get("execution_id"))
                else:
                    st.warning("No matching execution plan found for this approval.")

                approve_col, reject_col, schedule_col = st.columns(3)

                if approve_col.button(
                    "Approve & Dry Run Execute",
                    key=f"approve-{approval_id}"
                ):
                    if not matching_execution_plan:
                        st.error("Cannot execute because no matching execution plan was found.")
                    else:
                        execute_response = requests.post(
                            EXECUTE_API_URL,
                            json={
                                "approved": True,
                                "execution_plan": matching_execution_plan
                            },
                            timeout=120
                        )

                        if execute_response.status_code == 200:
                            execution_result = execute_response.json()

                            st.session_state["execution_results"][approval_id] = execution_result

                            st.success("Dry-run execution completed.")
                            st.json(execution_result)
                        else:
                            st.error(f"Execution failed: {execute_response.status_code}")

                if reject_col.button(
                    "Reject",
                    key=f"reject-{approval_id}"
                ):
                    st.error(f"Rejected: {approval_id}")

                if schedule_col.button(
                    "Schedule",
                    key=f"schedule-{approval_id}"
                ):
                    st.info(f"Scheduled for maintenance window: {approval_id}")

with tab2:
    st.subheader("Enterprise Change Requests")

    changes = change.get("change_requests", [])

    if not changes:
        st.success("No change requests generated.")
    else:
        for item in changes:
            with st.expander(f"{item.get('change_id')} — {item.get('title')}"):
                st.write("**Status:**", item.get("status"))
                st.write("**Business Justification:**", item.get("business_justification"))
                st.write("**Approver:**", item.get("approver"))
                st.write("**Risk Level:**", item.get("risk_level"))
                st.write("**Maintenance Window:**")
                st.json(item.get("maintenance_window", {}))

                st.write("**Validation Plan**")
                for step in item.get("validation_plan", []):
                    st.write(f"- {step}")

                st.write("**Rollback Plan**")
                for step in item.get("rollback_plan", []):
                    st.write(f"- {step}")

with tab3:
    st.subheader("Dry-Run Execution Plans")

    if not execution_plans:
        st.success("No execution plans generated.")
    else:
        for item in execution_plans:
            with st.expander(f"{item.get('execution_id')} — {item.get('title')}"):
                st.write("**Mode:**", item.get("execution_mode"))
                st.write("**Status:**", item.get("status"))
                st.write("**Service:**", item.get("service"))
                st.write("**Approver:**", item.get("approver"))

                st.write("**Safety Controls**")
                for control in item.get("safety_controls", []):
                    st.write(f"- {control}")

                st.write("**Execution Steps**")
                for step in item.get("execution_steps", []):
                    st.json(step)

with tab4:
    st.subheader("Execution Results")

    stored_execution_results = st.session_state.get("execution_results", {})

    if not stored_execution_results:
        st.info("No executions triggered yet. Approve an item from the Approval Queue.")
    else:
        for approval_id, execution_result in stored_execution_results.items():
            with st.expander(f"Execution Result for {approval_id}", expanded=True):
                st.json(execution_result)

with tab5:
    st.subheader("Raw Response")
    st.json(result)
