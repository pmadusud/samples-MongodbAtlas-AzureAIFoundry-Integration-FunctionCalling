import asyncio
import logging
import os

from azure.ai.agents.aio import AgentsClient
from azure.ai.agents.models import (
    Agent,
    AgentThread,
    AsyncFunctionTool,
    AsyncToolSet,
)
from azure.identity.aio import DefaultAzureCredential
from dotenv import load_dotenv

from stream_event_handler import StreamEventHandler
from terminal_colors import TerminalColors as tc
from utilities import Utilities
from mongodb_hybridsearch import MongoDBAtlasHybridSearch

logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

load_dotenv()

AGENT_NAME = "Contoso Sales Agent"
TENTS_DATA_SHEET_FILE = "datasheet/contoso-tents-datasheet.pdf"
FONTS_ZIP = "fonts/fonts.zip"
MODEL_DEPLOYMENT_NAME = os.getenv("MODEL_DEPLOYMENT_NAME")
PROJECT_ENDPOINT = os.environ["PROJECT_ENDPOINT"]
#AZURE_BING_CONNECTION_ID = os.environ["AZURE_BING_CONNECTION_ID"]
MAX_COMPLETION_TOKENS = 10240
MAX_PROMPT_TOKENS = 20480
# The LLM is used to generate the SQL queries.
# Set the temperature and top_p low to get more deterministic results.
TEMPERATURE = 0.1
TOP_P = 0.1
INSTRUCTIONS_FILE = None

toolset = AsyncToolSet()
utilities = Utilities()
_mongoDBAtlasHybridSearch = MongoDBAtlasHybridSearch()

agents_client = AgentsClient(
    credential=DefaultAzureCredential(),
    endpoint=PROJECT_ENDPOINT,
)

functions = AsyncFunctionTool(
    {
        _mongoDBAtlasHybridSearch.async_hybrid_search_mongodb_atlas,
    }
)

INSTRUCTIONS_FILE = "instructions/function_calling.txt"

async def add_agent_tools() -> None:
    """Add tools for the agent."""

    # Add the functions tool
    toolset.add(functions)

async def initialize() -> tuple[Agent, AgentThread]:
    """Initialize the agent with the sales data schema and instructions."""

    if not INSTRUCTIONS_FILE:
        return None, None

    font_file_info = await add_agent_tools()

    try:
        instructions = utilities.load_instructions(INSTRUCTIONS_FILE)
        # Replace the placeholder with the database schema string
        #instructions = instructions.replace(
        #    "{database_schema_string}", database_schema_string)

        if font_file_info:
            # Replace the placeholder with the font file ID
            instructions = instructions.replace(
                "{font_file_id}", font_file_info.id)

        print("Creating agent...")
        agent = await agents_client.create_agent(
            model=MODEL_DEPLOYMENT_NAME,
            name=AGENT_NAME,
            instructions=instructions,
            toolset=toolset,
            temperature=TEMPERATURE,
        )

        print(f"Created agent, ID: {agent.id}")

        agents_client.enable_auto_function_calls(tools=toolset)
        print("Enabled auto function calls.")

        print("Creating thread...")
        thread = await agents_client.threads.create()
        print(f"Created thread, ID: {thread.id}")

        return agent, thread

    except Exception as e:
        logger.error("An error occurred initializing the agent: %s", str(e))
        logger.error("Please ensure you've enabled an instructions file.")

async def cleanup(agent: Agent, thread: AgentThread) -> None:
    """Cleanup the resources."""
    await agents_client.threads.delete(thread.id)
    await agents_client.delete_agent(agent.id)
    await _mongoDBAtlasHybridSearch.close()

async def post_message(thread_id: str, content: str, agent: Agent, thread: AgentThread) -> None:
    """Post a message to the Foundry Agent Service."""
    try:
        await agents_client.messages.create(
            thread_id=thread_id,
            role="user",
            content=content,
        )

        async with await agents_client.runs.stream(
            thread_id=thread.id,
            agent_id=agent.id,
            event_handler=StreamEventHandler(
                functions=functions, project_client=agents_client, utilities=utilities),
            max_completion_tokens=MAX_COMPLETION_TOKENS,
            max_prompt_tokens=MAX_PROMPT_TOKENS,
            temperature=TEMPERATURE,
            top_p=TOP_P,
            instructions=agent.instructions,
        ) as stream:
            await stream.until_done()

    except Exception as e:
        utilities.log_msg_purple(
            f"An error occurred posting the message: {e!s}")


async def main() -> None:
    """
    Example questions: Sales by region, top-selling products, total shipping costs by region, show as a pie chart.
    """
    async with agents_client:
        agent, thread = await initialize()
        if not agent or not thread:
            print(f"{tc.BG_BRIGHT_RED}Initialization failed. Ensure you have uncommented the instructions file for the lab.{tc.RESET}")
            print("Exiting...")
            return

        cmd = None

        while True:
            prompt = input(
                f"\n\n{tc.GREEN}Enter your query (type exit or save to finish): {tc.RESET}").strip()
            if not prompt:
                continue

            cmd = prompt.lower()
            if cmd in {"exit", "save"}:
                break

            await post_message(agent=agent, thread_id=thread.id, content=prompt, thread=thread)

        if cmd == "save":
            print("The agent has not been deleted, so you can continue experimenting with it in the Azure AI Foundry.")
            print(
                f"Navigate to https://ai.azure.com, select your project, then playgrounds, agents playgound, then select agent id: {agent.id}"
            )
        else:
            await cleanup(agent, thread)
            print("The agent resources have been cleaned up.")


if __name__ == "__main__":
    print("Starting async program...")
    asyncio.run(main())
    print("Program finished.")