To run the example correcly, first you have to create the .env files using the same fields of env.example in the same locations and insert your gemini api key and a gemini model. 
After creating .env files and configuring it, then run both remote agents following the steps below:
1. Open a terminal window
2. Insert this command: `uv run python -m translator_agent.a2a_server` and type enter
3. Open a second terminal window
4. Insert this command: `uv run python -m math_agent.a2a_server` and type enter

With both agents running, execute the local agent with the command on a third terminal window: `uv run main.py`

