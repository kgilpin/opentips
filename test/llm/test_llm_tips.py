import pytest
from unittest.mock import patch, MagicMock, AsyncMock

from opentips.llm.llm_tips import llm_tips, LLMTipList, FileChunk
from opentips.tips.git import DiffChunk


class TestLLMTipsReview:
    @pytest.fixture
    def sample_diff_chunks(self):
        return [
            DiffChunk(to_file="test1.py", chunk="def test():"),
            DiffChunk(to_file="test2.py", chunk="print('hello')"),
        ]

    @pytest.fixture
    def sample_file_chunk(self):
        return FileChunk(
            file_name="test.py",
            start_line=1,
            end_line=10,
            content="def sample():\n    return 'hello world'\n",
        )

    @pytest.fixture
    def mock_completion_handler(self):
        """Create a mock completion handler that returns a predefined response"""
        mock_handler = AsyncMock()
        mock_handler.return_value = LLMTipList(tips=[])
        return mock_handler

    @patch("opentips.llm.llm_tips.get_completion_handler")
    async def test_llm_tips_with_review_instructions_diff(
        self, mock_get_completion, mock_completion_handler, sample_diff_chunks
    ):
        """Test that review instructions are included in the prompt for diff chunks"""
        mock_get_completion.return_value = mock_completion_handler
        review_instructions = "# Test Review Guidelines\n\nFocus on error handling."

        await llm_tips(sample_diff_chunks, None, review_instructions)

        # Check that the completion handler was called
        mock_completion_handler.assert_called_once()

        # Verify review instructions are included in the prompt
        args = mock_completion_handler.call_args[0]
        prompt = args[0]

        assert (
            "project-specific instructions" in prompt
        ), f"project-specific instructions not found in {prompt}"

    @patch("opentips.llm.llm_tips.get_completion_handler")
    async def test_llm_tips_with_review_instructions_file(
        self, mock_get_completion, mock_completion_handler, sample_file_chunk
    ):
        """Test that review instructions are included in the prompt for file chunks"""
        mock_get_completion.return_value = mock_completion_handler
        review_instructions = "# Test Review Guidelines\n\nFocus on error handling."

        await llm_tips(None, sample_file_chunk, review_instructions)

        # Check that the completion handler was called
        mock_completion_handler.assert_called_once()

        # Verify review instructions are included in the prompt
        args = mock_completion_handler.call_args[0]
        prompt = args[0]

        assert (
            "project-specific instructions" in prompt
        ), f"project-specific instructions not found in {prompt}"

    @patch("opentips.llm.llm_tips.get_completion_handler")
    async def test_llm_tips_without_review_instructions(
        self, mock_get_completion, mock_completion_handler, sample_diff_chunks
    ):
        """Test that no review section is added when no review instructions are provided"""
        mock_get_completion.return_value = mock_completion_handler

        await llm_tips(sample_diff_chunks, None, None)

        # Check that the completion handler was called
        mock_completion_handler.assert_called_once()

        # Verify no review instructions are included in the prompt
        args = mock_completion_handler.call_args[0]
        prompt_parts = args[0]

        # Check that there is no review section in the prompt
        review_section_found = any(
            "project-specific instructions" in part for part in prompt_parts
        )
        assert (
            not review_section_found
        ), "Review section found in prompt when it shouldn't be"
