import httpx
from dotenv import load_dotenv
import os

from a2a.client import A2ACardResolver, ClientFactory
from a2a.client.client import Client, ClientConfig
from a2a.types import AgentCard

load_dotenv()

A2A_URLS: list[str] = [a2a_url.strip() for a2a_url in set(os.getenv("A2A_URLS", []).split(","))]


class A2AConnection():
    def __init__(self):
        self.loaded_agents = {}
        self.__load_agents()

    async def get_agents(self) -> dict:
        if not self.loaded_agents:
            await self.__load_agents()

        return self.loaded_agents

    async def __load_agents(self):
        httpx_client: httpx.AsyncClient = httpx.AsyncClient(timeout=30)
        for a2a_url in A2A_URLS:
            resolver: A2ACardResolver = A2ACardResolver(httpx_client=httpx_client, base_url=a2a_url)

            public_card: AgentCard | None = None

            try:
                public_card: AgentCard = await resolver.get_agent_card()
            except Exception as e:
                raise RuntimeError("Failed to fetch public agent card", e)
            
            client_config: ClientConfig = ClientConfig(httpx_client=httpx_client, streaming=public_card.capabilities.streaming)
            
            client: Client = await ClientFactory.connect(public_card, client_config=client_config)

            self.loaded_agents[public_card.name] = {
                "card": public_card,
                "client": client
            }
