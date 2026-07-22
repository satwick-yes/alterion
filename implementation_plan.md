# Upgrade Jarvis to a Supervisor Multi-Agent System

This plan details the architectural refactor of Jarvis from a single, monolithic tool-handler into a Centralized "Brain" that manages specialized Sub-Agents.

## User Review Required

> [!IMPORTANT]
> This is a major architectural shift. Currently, `main.py` uses the Gemini Live API with all ~30 tools loaded at once. In this new architecture, the Live API will act as the "Brain" and will only be given a few "Delegation Tools" (e.g., `call_system_agent`, `call_research_agent`). When the Live API decides to act, it will pass the goal to the specific agent in the background, which will execute the task. 

## Open Questions

> [!WARNING]
> 1. **Agent Count**: You mentioned 4 agents, but the current `orchestrator.py` defines 5 (System, Research, Developer, Office, Communication). Do you want to consolidate Office and Communication into a single "Creator/Comms" agent to stick exactly to 4, or keep the existing 5?
> 2. **Voice Responsiveness**: Since the Live API (the Brain) will be delegating complex tasks to background agents, the background agents will need to speak their updates back to you (e.g., "Sir, I have finished writing the code."). Is this asynchronous speaking behavior acceptable?

## Proposed Changes

### `main.py` (The Brain)
- **[MODIFY]** Remove the massive monolithic `TOOL_DECLARATIONS` list (30+ tools).
- **[MODIFY]** Create a new slim `TOOL_DECLARATIONS` containing only the Agent Delegation tools:
  - `delegate_to_operator_agent`: "Controls local PC, UI, system settings, desktop."
  - `delegate_to_research_agent`: "Fetches web info, weather, flights, YouTube."
  - `delegate_to_developer_agent`: "Writes code, handles terminal and files."
  - `delegate_to_creator_agent`: "Sends messages, creates presentations and documents."
- **[MODIFY]** Update `_execute_tool` to handle these delegation requests by spawning the `AgentExecutor` for that specific agent.

### `agent/orchestrator.py` (Agent Profiles)
- **[MODIFY]** Update the `SemanticRouter` and `Companion` classes to perfectly align with the 4 finalized Agent roles. 
- **[MODIFY]** Strictly partition the existing `actions/` tools among these 4 agents so no agent has overlapping tool permissions.

### `agent/planner.py` & `agent/executor.py` (Agent Execution)
- **[MODIFY]** Update the `PLANNER_PROMPT` to enforce that when an agent is running a task, it *only* has access to its specific subset of allowed tools. 
- **[MODIFY]** Ensure `_call_tool` securely enforces tool-permissions per agent. (This is partially implemented but needs to be tied directly to the new 4-agent workflow).

## Verification Plan

### Automated Tests
- No formal unit test suite exists, but we will test the routing logic locally using the Python REPL to ensure inputs route to the correct agent.

### Manual Verification
- Start Jarvis via `main.py`.
- Give a complex voice command: *"Jarvis, research the weather in Tokyo and then send a WhatsApp message to John with the details."*
- Verify the Brain parses this and delegates to the Research Agent, which then passes the result to the Creator Agent.
