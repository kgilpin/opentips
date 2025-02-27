from abc import abstractmethod
import base64
from typing import Any, Dict, Optional, List, Protocol
from pydantic import BaseModel


class Tip(BaseModel):
    id: str
    directory: str
    file: str
    line: int
    context: str
    type: str
    complexity: str
    label: str
    description: str
    deleted: Optional[bool] = False

    # TODO: Add created_at so that we can consider the age of the tip.

    def __str__(self):
        return self.format_as_line()

    def __hash__(self):
        # Create hash based on immutable identifying fields
        return hash((self.id))

    def __eq__(self, other):
        if not isinstance(other, Tip):
            return False
        return self.id == other.id

    @staticmethod
    def parse_from_line(directory: str, line: str) -> "Tip":
        parts = line.split(" - ")
        try:
            id, file_info, tip_type, complexity, label, description, *context = parts
        except ValueError:
            raise ValueError(f"Invalid Tip line format: {line}")

        return Tip(
            id=id,
            directory=directory,
            file=file_info.split(":")[0],
            line=int(file_info.split(":")[1]),
            type=tip_type,
            complexity=complexity,
            label=label,
            description=description,
            context=" - ".join(context),
        )

    @staticmethod
    def validate_external_id(external_id: str, directory: str) -> None:
        """
        Parse an external ID into its constituent parts and validate it.

        Args:
            external_id: The external ID to parse
            directory: The directory to validate against (optional)

        Raises:
            ValueError: If the tip ID is invalid
            ValueError: If the tip directory does not match the provided directory

        Returns:
            The decoded tip ID
        """
        decoded_id = base64.urlsafe_b64decode(external_id + "===").decode("utf-8")
        tokens = decoded_id.split("\n")
        version = tokens[0]
        if version != "1.0":
            raise ValueError(f"Invalid tip ID format: {tokens[0]}")

        if len(tokens) != 3:
            raise ValueError(f"Invalid tip ID: {external_id}")

        _, directory_from_id, _ = tokens
        if directory is not None and directory != directory_from_id:
            raise ValueError(
                f"Tip directory mismatch: {directory} != {directory_from_id}"
            )

    def format_as_line(self) -> str:
        context_line = self.context.split("\n")[0]
        return f"{self.id} {self.file}:{self.line} - {self.type} - {self.complexity} - {self.label} - {self.description} - {context_line}"


class TipList(BaseModel):
    """Collection of tips"""

    tips: List[Tip]
    error: Optional[str] = None
    """
    Optional error message.
    If set, it indicates that an error occurred during tip collection.
    The 'tips' list may be empty or partially populated in this case.
    """


class ExplanationResponse(BaseModel):
    """Response containing a tip explanation"""

    explanation: Optional[str]


class ChangedResponse(BaseModel):
    """Response containing changed files"""

    file_names: List[str]


class Patch(BaseModel):
    file_name: str
    search: str
    replace: str


class PatchResponse(BaseModel):
    """Response containing a patch"""

    success: bool
    patches: list[Patch]


class OpenTipsRPC(Protocol):
    @abstractmethod
    def echo(self, message: str) -> str:
        """Echo a message"""
        pass

    @abstractmethod
    def changed(
        self, file_names: list[str], immediate: Optional[bool]
    ) -> ChangedResponse:
        """Handle notification of changed files"""
        pass

    @abstractmethod
    async def suggest(self, new_only: Optional[bool]) -> TipList:
        """Get suggestions for changed files"""
        pass

    @abstractmethod
    async def suggest_file_range(
        self, file_name: str, start_line: int, end_line: int
    ) -> TipList:
        """Get suggestions for a specific file range"""
        pass

    @abstractmethod
    async def list_tips(self, limit: Optional[int] = None) -> List[Tip]:
        """List all tips in a directory"""
        pass

    @abstractmethod
    async def fetch_tip(self, tip_id: str) -> Tip:
        """Fetch a specific tip"""
        pass

    @abstractmethod
    async def explain_tip(self, tip_id: str) -> ExplanationResponse:
        """Get explanation for a tip"""
        pass

    @abstractmethod
    async def apply_tip(self, tip_id: str, delete_after_apply: bool) -> PatchResponse:
        """Apply a tip"""
        pass

    @abstractmethod
    async def delete_tip(self, tip_id: str) -> bool:
        """Logically delete a tip"""
        pass

    @abstractmethod
    def poll_events(self) -> List[Dict[str, Any]]:
        """Get pending events"""
        pass
