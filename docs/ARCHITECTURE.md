# Enterprise AI FinOps Platform Architecture

## 1. High-Level Architecture

```mermaid
flowchart TD
    U[User] --> FE[Streamlit Executive Dashboard / Approval Portal]
    FE --> API[FastAPI Backend]

    API --> RP[Request Parser]
    RP --> PA[Planner Agent]
    PA --> CA[Coordinator Agent]

    CA --> ORG[Organizations Agent]
    CA --> COST[Cost Analysis Agent]
    CA --> CUR[CUR Agent]
    CA --> ANOM[Cost Anomaly Detection Agent]
    CA --> PRICE[Pricing Agent]
    CA --> BUDGET[Budgets Agent]
    CA --> EC2[EC2 Discovery Agent]
    CA --> CW[CloudWatch Agent]
    CA --> CO[Compute Optimizer Agent]

    ORG --> INTEL[Knowledge & Intelligence Layer]
    COST --> INTEL
    CUR --> INTEL
    ANOM --> INTEL
    PRICE --> INTEL
    BUDGET --> INTEL
    EC2 --> INTEL
    CW --> INTEL
    CO --> INTEL

    INTEL --> KG[Knowledge Graph]
    INTEL --> FS[Fact Summarizer]
    INTEL --> SE[Savings Estimation Engine]
    INTEL --> RCA[Root Cause Analysis Engine]

    KG --> OPT[Optimization Planner Agent]
    FS --> OPT
    SE --> OPT
    RCA --> OPT

    OPT --> DE[AI Decision Engine]
    DE --> RE[AI Reasoning Engine]
    RE --> APPROVAL[Approval Workflow Agent]
    APPROVAL --> CM[Enterprise Change Manager]
    CM --> EP[Execution Planner Agent]
    EP --> EXE[Execution Agent]
    EXE --> VERIFY[Verification Agent]
    VERIFY --> RB[Rollback Agent]

    EXE --> SF[AWS Step Functions Foundation]
    SF --> DDB[DynamoDB Workflow Store]
    SF --> CWLOGS[CloudWatch Logs]
    SF --> SNS[SNS Notifications]

    API --> DDB
```

---

## 2. Multi-Agent Workflow Sequence

```mermaid
sequenceDiagram
    actor User
    participant UI as Streamlit UI
    participant API as FastAPI
    participant Parser as Request Parser
    participant Planner as Planner Agent
    participant Coordinator as Coordinator Agent
    participant AWSAgents as AWS FinOps Agents
    participant Optimizer as Optimization Planner
    participant Decision as AI Decision Engine
    participant Reasoning as AI Reasoning Engine
    participant Approval as Approval Workflow
    participant Change as Change Manager
    participant ExecPlanner as Execution Planner
    participant Store as DynamoDB Workflow Store

    User->>UI: Submit FinOps query
    UI->>API: POST /analyze
    API->>Parser: Parse request
    Parser->>Planner: Determine workflow
    Planner->>Coordinator: Optimization workflow
    Coordinator->>AWSAgents: Invoke AWS analysis agents
    AWSAgents-->>Coordinator: Cost, anomaly, pricing, budget, metrics
    Coordinator->>Optimizer: Generate optimization plan
    Optimizer->>Decision: Score ROI, risk, confidence
    Decision->>Reasoning: Generate evidence and hypothesis
    Reasoning->>Approval: Create approval requests
    Approval->>Change: Create enterprise change requests
    Change->>ExecPlanner: Create dry-run execution plans
    ExecPlanner-->>Coordinator: Execution plan result
    Coordinator-->>API: Complete workflow result
    API->>Store: Persist workflow state
    API-->>UI: Return executive response
```

---

## 3. Approval and Execution Flow

```mermaid
sequenceDiagram
    actor Approver
    participant Portal as Approval Portal
    participant API as FastAPI
    participant Exec as Execution Agent
    participant Verify as Verification Agent
    participant Rollback as Rollback Agent
    participant SF as Step Functions Foundation
    participant Store as DynamoDB

    Approver->>Portal: Approve recommendation
    Portal->>API: POST /execute
    API->>Exec: Execute dry-run plan
    Exec->>Exec: Simulate AWS action
    Exec->>Verify: Verify execution result
    Verify-->>Exec: Verification passed/failed

    alt Verification Passed
        Exec-->>API: Execution successful
        API->>SF: Simulate workflow orchestration
        API->>Store: Persist execution status
        API-->>Portal: Show success
    else Verification Failed
        Verify->>Rollback: Prepare rollback plan
        Rollback-->>Exec: Rollback ready
        Exec-->>API: Execution requires rollback
        API->>Store: Persist rollback status
        API-->>Portal: Show rollback required
    end
```

---

## 4. AWS Deployment Architecture

```mermaid
flowchart TD
    USER[User / FinOps Engineer] --> WEB[Streamlit UI]

    WEB --> API[FastAPI Application]

    API --> BEDROCK[Amazon Bedrock / Nova]
    API --> CE[AWS Cost Explorer]
    API --> CAD[AWS Cost Anomaly Detection]
    API --> PRICING[AWS Pricing API]
    API --> BUDGETS[AWS Budgets]
    API --> ORGS[AWS Organizations]
    API --> EC2[AWS EC2]
    API --> CLOUDWATCH[Amazon CloudWatch]
    API --> CO[AWS Compute Optimizer]
    API --> CUR[AWS Cost and Usage Reports]

    API --> DDB[(Amazon DynamoDB Workflow Store)]
    API --> SF[AWS Step Functions]
    SF --> PRE[PreCheck Lambda]
    SF --> EXEC[Execute Lambda]
    SF --> VER[Verify Lambda]
    SF --> ROLL[Rollback Lambda]

    PRE --> CLOUDWATCH
    EXEC --> EC2
    EXEC --> CLOUDWATCH
    VER --> CLOUDWATCH
    ROLL --> EC2

    SF --> SNS[Amazon SNS Notifications]
    SF --> LOGS[CloudWatch Logs]

    CDK[AWS CDK] --> SF
    CDK --> DDB
    CDK --> SNS
    CDK --> PRE
    CDK --> EXEC
    CDK --> VER
    CDK --> ROLL
```

---

## 5. Runtime Safety Model

```mermaid
flowchart LR
    PLAN[Optimization Plan] --> DECISION[Decision Engine]
    DECISION --> APPROVAL{Approval Required?}

    APPROVAL -- No --> REVIEW[Review Recommended]
    APPROVAL -- Yes --> HUMAN[Human Approval]

    HUMAN --> DRYRUN[Dry-Run Execution]
    DRYRUN --> VERIFY[Verification]

    VERIFY --> PASS{Passed?}
    PASS -- Yes --> COMPLETE[Complete]
    PASS -- No --> ROLLBACK[Prepare Rollback]

    ROLLBACK --> AUDIT[Persist Audit Trail]
    COMPLETE --> AUDIT
```

---

## 6. Current Platform Layers

| Layer | Components |
|---|---|
| User Interface | Streamlit Executive Dashboard, Approval Portal |
| API Layer | FastAPI |
| Planning Layer | Request Parser, Planner Agent, Coordinator Agent |
| AWS Data Layer | Cost Explorer, Anomaly Detection, Pricing, Budgets, EC2, CloudWatch, Compute Optimizer, CUR, Organizations |
| Intelligence Layer | Knowledge Graph, Fact Summarizer, Savings Estimation, Root Cause Analysis |
| Decision Layer | Optimization Planner, AI Decision Engine, AI Reasoning Engine |
| Governance Layer | Approval Workflow Agent, Enterprise Change Manager |
| Execution Layer | Execution Planner, Execution Agent, Verification Agent, Rollback Agent |
| Persistence Layer | DynamoDB Workflow Store |
| Orchestration Layer | Step Functions Foundation, CDK |
