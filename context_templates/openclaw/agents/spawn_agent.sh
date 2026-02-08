#!/bin/bash
# Helper script to spawn specialized agents
# Usage: ./spawn_agent.sh <agent-name> "<task>"

if [ $# -lt 2 ]; then
    echo "Usage: $0 <agent-name> \"<task>\""
    echo "Available agents:"
    ls -d */ | sed 's|/||' | grep -v '^\.'
    exit 1
fi

AGENT_NAME="$1"
TASK="$2"

# Check if agent directory exists
if [ ! -d "$AGENT_NAME" ]; then
    echo "Error: Agent '$AGENT_NAME' not found"
    echo "Available agents:"
    ls -d */ | sed 's|/||' | grep -v '^\.'
    exit 1
fi

echo "Spawning $AGENT_NAME agent with task: $TASK"
echo "Note: Use sessions_spawn tool in OpenClaw with:"
echo "  agentId=main"
echo "  task=\"$TASK\""
echo "  label=\"${AGENT_NAME}-task-$(date +%s)\""
echo ""
echo "The agent will run in isolation with $AGENT_NAME's specialized context."
