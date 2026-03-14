import os
import uvicorn
from dotenv import load_dotenv

from a2a.server.apps import A2AFastAPIApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from a2a.types import AgentCapabilities, AgentCard, AgentSkill

from .agent_executor import TranslatorAgentExecutor

load_dotenv(dotenv_path="translator_agent/.env")


def main():
    host = "localhost"
    port = 5002

    try:
        if not os.getenv("GOOGLE_API_KEY"):
            raise Exception("GOOGLE_API_KEY environment variable not set.")

        capabilities = AgentCapabilities(streaming=True)
        skill = AgentSkill(
            id="language_translator",
            name="Translation Tool",
            description="Helps the user with translations",
            tags=["translation"],
            examples=["How to translate hello to portuguese"],
        )
        agent_card = AgentCard(
            name="Translator Agent",
            description="Do some translations",
            url=f"http://{host}:{port}/",
            version="1.0.0",
            defaultInputModes=["text", "text/plain"],
            defaultOutputModes=["text", "text/plain"],
            capabilities=capabilities,
            skills=[skill],
        )

        request_handler = DefaultRequestHandler(
            agent_executor=TranslatorAgentExecutor(),
            task_store=InMemoryTaskStore()
        )

        server = A2AFastAPIApplication(
            agent_card=agent_card, 
            http_handler=request_handler)

        uvicorn.run(server.build(), host=host, port=port)

    except Exception as e:
        print(f"An error occurred during server startup: {e}")


if __name__ == "__main__":
    main()