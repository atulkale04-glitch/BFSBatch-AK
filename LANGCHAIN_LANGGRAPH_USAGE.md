# LangChain & LangGraph Usage in Loan Approval System

## Overview

This system uses **LangGraph** for orchestration and **Anthropic Claude** for agent reasoning. While not using traditional LangChain abstractions, it implements LangChain-inspired patterns:

- **LangGraph**: Workflow orchestration and state management
- **Claude API**: Multi-turn agentic loops with function calling
- **Tool Use Pattern**: MCP-style tool registration and execution

---

## Architecture

```
┌─────────────────────────────────────────────────────┐
│         FastAPI Application                         │
│         (src/main.py)                               │
└────────────────┬────────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────────┐
│         LangGraph Workflow                          │
│         (src/orchestration/workflow.py)             │
│                                                      │
│    START → Validate → Profile → Risk → Decision    │
│             ↓         ↓        ↓       ↓            │
│         [Nodes with async execution]               │
│                                                      │
│         ↓ State flows through each node             │
│         ↓ Agents invoked at each step              │
│         END                                         │
└────────────────┬────────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────────┐
│         Multi-Agent System                          │
│         (src/agents/)                               │
│                                                      │
│  ┌─────────────────────────────────────────┐      │
│  │  BaseAgent (LangChain-inspired)         │      │
│  │  - Tool registration & management       │      │
│  │  - Agentic loop with Claude             │      │
│  │  - Function calling (tool use)          │      │
│  └─────────────────────────────────────────┘      │
│           ↓          ↓          ↓          ↓       │
│       Applicant  Financial  Decision  Compliance  │
│       Profile    Risk       Agent      Orchestr   │
│       Agent      Agent                           │
└────────────────┬────────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────────┐
│         Tool/MCP Servers                            │
│         (src/mcp_servers/)                          │
│                                                      │
│    ApplicantDB | RiskRulesDB | DecisionSynthesis   │
└────────────────────────────────────────────────────┘
```

---

## 1. LangGraph Usage

### Location: `src/orchestration/workflow.py`

#### StateGraph Definition
```python
from langgraph.graph import END, START, StateGraph

# LangGraph manages the workflow state
# Each node is a step in the workflow
# Edges define the flow between nodes
```

#### Workflow Structure

```
START
  ↓
validate_input_node (synchronous)
  ↓
applicant_profile_node (async - calls Applicant Profile Agent)
  ↓
financial_risk_node (async - calls Financial Risk Agent)
  ↓
loan_decision_node (async - calls Loan Decision Agent)
  ↓
compliance_node (async - calls Compliance Agent)
  ↓
completion_node
  ↓
END
```

#### State Management

```python
from src.orchestration.state import WorkflowState

# TypedDict defining workflow state
class WorkflowState(TypedDict):
    application_id: str
    applicant_id: str
    status: str
    # ... all application data
    applicant_profile_output: dict
    financial_risk_output: dict
    loan_decision_output: dict
    # ... agent outputs accumulate in state
```

**Why LangGraph:**
- Manages complex multi-step workflows
- State is threaded through each node
- Supports conditional edges and parallel execution
- Provides structured execution model

---

## 2. Claude Agent Pattern (LangChain-Inspired)

### Location: `src/agents/base_agent.py`

#### Agentic Loop Implementation

The `BaseAgent` class implements a classic agentic loop:

```
┌─────────────────────────────────────────────────┐
│ 1. SEND: User message + tools to Claude        │
└─────────────────┬───────────────────────────────┘
                  │
┌─────────────────▼───────────────────────────────┐
│ 2. RECEIVE: Claude response with tool calls    │
└─────────────────┬───────────────────────────────┘
                  │
         Is stop_reason "tool_use"?
              ↓         ↓
            NO         YES
            │           │
        Return      Process
        answer      tool calls
            │           │
            │      ┌────▼─────────┐
            │      │ 3. EXECUTE   │
            │      │ Tool handlers│
            │      └────┬─────────┘
            │           │
            │      ┌────▼──────────────┐
            │      │ 4. ADD RESULTS TO │
            │      │ message history   │
            │      └────┬──────────────┘
            │           │
            │      Loop back to step 1
            │           
            └───→ Return final response
```

#### Code Implementation

```python
async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
    """Execute agent with agentic loop."""
    
    messages = [{"role": "user", "content": self._format_input_for_claude(input_data)}]
    
    max_iterations = 10
    iteration = 0
    
    while iteration < max_iterations:
        iteration += 1
        
        # STEP 1: Send to Claude with available tools
        response = self.client.messages.create(
            model="claude-opus-4-5-20251101",
            max_tokens=4096,
            system=self.system_prompt,
            tools=self._build_tools_for_claude() if self.tools else None,
            messages=messages,
        )
        
        # STEP 2: Check stop reason
        if response.stop_reason == "end_turn":
            # Agent finished reasoning
            return self._extract_final_response(response, messages, input_data)
        
        if response.stop_reason == "tool_use":
            # STEP 3: Process tool calls
            assistant_message = {"role": "assistant", "content": response.content}
            messages.append(assistant_message)
            
            # Execute each tool call
            tool_results = []
            for block in response.content:
                if block.type == "tool_use":
                    result = self._process_tool_call(block.name, block.input)
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": json.dumps(result),
                    })
            
            # STEP 4: Add results back to messages
            messages.append({"role": "user", "content": tool_results})
```

---

## 3. Tool Registration & Function Calling

### Location: `src/agents/base_agent.py`

#### Tool Definition

```python
class Tool:
    """Tool definition for Claude function calling."""
    
    def __init__(
        self,
        name: str,
        description: str,
        input_schema: Dict[str, Any],  # JSON Schema
        handler: callable,              # Function to execute
    ):
        self.name = name
        self.description = description
        self.input_schema = input_schema
        self.handler = handler
    
    def to_claude_format(self) -> Dict[str, Any]:
        """Convert to Claude API tool format."""
        return {
            "name": self.name,
            "description": self.description,
            "input_schema": {
                "type": "object",
                "properties": self.input_schema.get("properties", {}),
                "required": self.input_schema.get("required", []),
            },
        }
```

#### Example: Loan Decision Agent Tools

```python
# In LoanDecisionAgent.__init__()
tools = [
    Tool(
        name="retrieve_evaluations",
        description="Retrieve all evaluations from other agents",
        input_schema={
            "properties": {"application_id": {"type": "string"}},
            "required": ["application_id"],
        },
        handler=self._handle_retrieve_evaluations,
    ),
    Tool(
        name="calculate_composite_risk",
        description="Calculate composite risk score",
        input_schema={
            "properties": {"application_id": {"type": "string"}},
            "required": ["application_id"],
        },
        handler=self._handle_calculate_composite_risk,
    ),
    # ... more tools
]
```

#### Tool Execution

```python
def _process_tool_call(self, tool_name: str, tool_input: Dict[str, Any]) -> Any:
    """Find and execute tool by name."""
    
    for tool in self.tools:
        if tool.name == tool_name:
            # Tool handler called with arguments
            result = tool.handler(**tool_input)
            return result
    
    return {"error": f"Tool {tool_name} not found"}
```

---

## 4. Agents in the System

### 4.1 Applicant Profile Agent

**Purpose**: Analyze applicant information  
**Location**: `src/agents/applicant_profile_agent.py`

**Tools Available**:
- `get_applicant_profile` - Fetch applicant details
- `get_employment_history` - Get employment records
- `get_credit_history` - Get credit summary
- `calculate_income_stability` - Score income stability
- `get_employment_risk` - Assess employment risk

**Example Agent Call from Workflow**:
```python
async def applicant_profile_node(self, state: WorkflowState) -> WorkflowState:
    input_data = {
        "applicant_id": state["applicant_id"],
        "loan_amount": state["loan_amount"],
        "credit_score": state["credit_score"],
    }
    
    # Agent runs agentic loop internally
    result = await self.applicant_agent.execute(input_data)
    
    # State updated with agent output
    state["applicant_profile_output"] = result["data"]
    merge_evaluation(state, "applicant_profile_agent", result["data"])
    
    return state
```

### 4.2 Financial Risk Agent

**Purpose**: Analyze financial metrics  
**Tools**:
- `calculate_dti_ratio` - DTI calculation
- `analyze_credit_score_risk` - Credit risk level
- `assess_loan_amount_risk` - Loan risk
- `detect_financial_anomalies` - Anomaly detection
- `apply_risk_rules` - Company policies

### 4.3 Loan Decision Agent

**Purpose**: Make final lending decision  
**Tools**:
- `retrieve_evaluations` - Get agent outputs
- `calculate_composite_risk` - Combine scores
- `resolve_conflicting_recommendations` - Resolve conflicts
- `prepare_decision_summary` - Create explanation

### 4.4 Compliance & Action Orchestrator Agent

**Purpose**: Execute decision and log actions  
**Tools**:
- `generate_case_id` - Create unique case ID
- `execute_approval_decision` - Process approval
- `execute_rejection_decision` - Process rejection
- `flag_for_manual_review` - Flag for review
- `send_decision_notification` - Notify applicant
- `log_action` - Audit trail

---

## 5. State Management

### TypedDict Definition

```python
class WorkflowState(TypedDict):
    # Application data
    application_id: str
    applicant_id: str
    age: int
    income: float
    credit_score: int
    # ... more fields
    
    # Workflow status
    status: str  # "processing", "completed", "failed"
    workflow_stage: str  # "validation", "applicant_profile", etc.
    error_message: Optional[str]
    
    # Agent outputs accumulate here
    applicant_profile_output: dict
    financial_risk_output: dict
    loan_decision_output: dict
    compliance_output: dict
    
    # Audit trail
    audit_entries: list
    agent_evaluations: dict
```

### State Helpers

```python
# Update status
update_state_status(state, "processing", "applicant_profile")

# Merge agent evaluation into state
merge_evaluation(state, "applicant_profile_agent", agent_output)

# Add audit entry
add_audit_entry(state, "AGENT_COMPLETED", {"agent": "applicant_profile"})
```

---

## 6. MCP Server Pattern

### Location: `src/mcp_servers/`

MCP (Model Context Protocol) servers provide tools for agents:

```python
class ApplicantDBServer:
    """MCP Server for Applicant Database."""
    
    def get_applicant_profile(self, applicant_id: str):
        """Returns applicant information."""
        # Mock implementation
        return {
            "applicant_id": applicant_id,
            "employment_type": "Full-time",
            "income_stability": 85,
        }
    
    def get_employment_history(self, applicant_id: str):
        """Returns employment history."""
        return [...]
```

**Agents call these servers via tools**:
```
Agent → Tool "get_applicant_profile" → Handler → MCP Server → Response
```

---

## 7. Integration Flow

### Complete Request Journey

```
1. HTTP POST /api/v1/applications
   ├─ FastAPI receives loan application
   ├─ Creates LoanApplication database record
   └─ Calls ApplicationOrchestrator.process_application()

2. Orchestrator invokes LangGraph workflow
   ├─ Graph.compile() creates executable workflow
   └─ Workflow.invoke(state) executes

3. LangGraph executes workflow nodes
   ├─ validate_input_node
   │   └─ Checks required fields
   │
   ├─ applicant_profile_node (async)
   │   └─ Invokes ApplicantProfileAgent.execute()
   │       ├─ Sends prompt + tools to Claude
   │       ├─ Claude runs agentic loop
   │       ├─ Claude calls tools (MCP servers)
   │       └─ Returns evaluation
   │
   ├─ financial_risk_node (async)
   │   └─ Similar to applicant_profile_node
   │
   ├─ loan_decision_node (async)
   │   └─ Synthesizes all evaluations
   │       └─ Makes final decision
   │
   ├─ compliance_node (async)
   │   └─ Executes decision actions
   │
   └─ completion_node
       └─ Finalizes state

4. State flows back to orchestrator
   └─ Results returned to API

5. FastAPI returns decision to client
   ├─ Decision: APPROVED/REJECTED/MANUAL_REVIEW
   ├─ Risk score, confidence, reasoning
   └─ Case ID for tracking
```

---

## 8. Key LangChain-Style Patterns

### Pattern 1: Agent + Tools
```
User Input → Agent → Claude with Tools → Tool Calls → Execution → Results → Response
```

### Pattern 2: Orchestration
```
Workflow State → Node 1 → State Update → Node 2 → State Update → Node N → Final State
```

### Pattern 3: State Threading
```
Input State → Process → Output State (includes all previous + new data)
```

### Pattern 4: Tool Use Loop
```
While Claude.stop_reason == "tool_use":
    Execute tools
    Add results to message history
    Call Claude again
```

---

## 9. Why This Architecture?

| Aspect | Benefit |
|--------|---------|
| **LangGraph** | Manages multi-step workflow without complexity |
| **Claude API** | Direct tool calling enables agentic loops |
| **TypedDict State** | Type-safe state management |
| **Tool Pattern** | Agents can "call" MCP servers without tight coupling |
| **Async Execution** | Agents run concurrently for speed |
| **Separation** | Each agent focuses on one responsibility |

---

## 10. Comparison with Traditional LangChain

### Traditional LangChain Approach
```python
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(model="gpt-4")
tools = [get_profile_tool, analyze_risk_tool]
agent_executor = AgentExecutor.from_agent_and_tools(agent, tools)
result = agent_executor.invoke({"input": "evaluate applicant"})
```

### This System's Approach
```python
# More control over agentic loop
class LoanDecisionAgent(BaseAgent):
    def __init__(self):
        self.client = Anthropic()
        self.tools = [tool1, tool2]
    
    async def execute(self, input_data):
        # Manual agentic loop implementation
        while iteration < max_iterations:
            response = self.client.messages.create(
                model="claude-opus",
                tools=self._build_tools_for_claude(),
                messages=messages,
            )
            # Process tool calls manually
            # Thread state through workflow
```

**Advantages:**
- Direct control over agent behavior
- Tighter integration with workflow
- Clearer debugging
- Custom state management
- Better for specialized domains

---

## 11. Current Implementation Note

### Important: Decision Engine Bypass

⚠️ **Current Runtime**: The system uses a rule-based `decision_engine.py` instead of invoking the full LangGraph workflow.

**Declared Flow**:
```
LangGraph Workflow → All 4 Agents → Decisions
```

**Actual Flow**:
```
FastAPI → Decision Engine (rule-based) → Response
```

**Why**: Faster decisions (< 1s vs. 1-3 min), lower API costs

**To Enable Full LangGraph**: Update orchestrator.py to call:
```python
workflow = create_workflow_graph().compile()
result = await workflow.ainvoke(initial_state)
```

---

## Summary

This system implements **LangChain-inspired patterns** using:

1. **LangGraph** for workflow orchestration
2. **Claude API** with tool calling for agentic loops
3. **Custom BaseAgent** class managing agent execution
4. **Tool registration** pattern for function calling
5. **State threading** through workflow nodes
6. **MCP-style servers** for tool implementations

The architecture is **production-ready** but currently uses a **rule-based decision engine** instead of full multi-agent execution for performance reasons.

---

*For more details, see workflow.py, base_agent.py, and orchestrator.py*
