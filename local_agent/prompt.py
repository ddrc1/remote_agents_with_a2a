CONVERSATION_PROMPT = """
Talk to the user and use the available agents (in <remote-agents>) to help you if needed.
Don't summarize any received answer from the agents.

<remote-agents>
    {remote_agents}
</remote-agents>
"""