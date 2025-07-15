from pathlib import Path

from azure.ai.agents.aio import AgentsClient
from azure.ai.agents.models import ThreadMessage

from terminal_colors import TerminalColors as tc


class Utilities:
    # propert to get the relative path of shared files
    @property
    def shared_files_path(self) -> Path:
        """Get the path to the shared files directory."""
        return Path(__file__).parent.resolve()

    def load_instructions(self, instructions_file: str) -> str:
        """Load instructions from a file."""
        file_path = self.shared_files_path / instructions_file
        with file_path.open("r", encoding="utf-8", errors="ignore") as file:
            return file.read()

    def log_msg_green(self, msg: str) -> None:
        """Print a message in green."""
        print(f"{tc.GREEN}{msg}{tc.RESET}")

    def log_msg_purple(self, msg: str) -> None:
        """Print a message in purple."""
        print(f"{tc.PURPLE}{msg}{tc.RESET}")

    def log_token_blue(self, msg: str) -> None:
        """Print a token in blue."""
        print(f"{tc.BLUE}{msg}{tc.RESET}", end="", flush=True)
    
    async def get_file(self, agents_client: AgentsClient, file_id: str, attachment_name: str) -> None:
        """Retrieve the file and save it to the local disk."""
        self.log_msg_green(f"Getting file with ID: {file_id}")

        attachment_part = attachment_name.split(":")[-1]
        file_name = Path(attachment_part).stem
        file_extension = Path(attachment_part).suffix
        if not file_extension:
            file_extension = ".png"
        file_name = f"{file_name}.{file_id}{file_extension}"

        folder_path = Path(self.shared_files_path) / "files"
        folder_path.mkdir(parents=True, exist_ok=True)
        file_path = folder_path / file_name

        # Save the file using a synchronous context manager
        with file_path.open("wb") as file:
            async for chunk in await agents_client.files.get_content(file_id):
                file.write(chunk)

        self.log_msg_green(f"File saved to {file_path}")

    async def get_files(self, message: ThreadMessage, project_client: AgentsClient) -> None:
        """Get the image files from the message and kickoff download."""
        if message.image_contents:
            for index, image in enumerate(message.image_contents, start=0):
                attachment_name = (
                    "unknown" if not message.file_path_annotations else message.file_path_annotations[index].text + ".png"
                )
                await self.get_file(project_client, image.image_file.file_id, attachment_name)
        elif message.attachments:
            for index, attachment in enumerate(message.attachments, start=0):
                attachment_name = (
                    "unknown" if not message.file_path_annotations else message.file_path_annotations[index].text
                )
                await self.get_file(project_client, attachment.file_id, attachment_name)