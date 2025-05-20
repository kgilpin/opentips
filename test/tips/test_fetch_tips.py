import pytest
import tempfile
from pathlib import Path
from unittest.mock import patch

from opentips.tips.fetch_tips import fetch_tips_for_diff, fetch_tips_for_file_range
from opentips.tips.git import DiffChunk
from opentips.llm.llm_tips import LLMTipList, LLMTip, FileChunk
from opentips.tips.rpc_types import TipList


@pytest.fixture
def test_setup():
    # Create a temporary directory for testing
    temp_dir = tempfile.TemporaryDirectory()
    test_dir = Path(temp_dir.name)

    # Sample review instructions
    review_content = "# Test Review Guidelines\n\nFocus on error handling."

    # Create a sample diff
    sample_diff = [
        DiffChunk(to_file="test1.py", chunk="def test():"),
        DiffChunk(to_file="test2.py", chunk="print('hello')"),
    ]

    # Define path for test file
    test_file_path = test_dir / "test_file.py"
    test_file_content = "def sample():\n    print('hello world')\n"
    test_file_path.write_text(test_file_content)

    yield {
        "temp_dir": temp_dir,
        "test_dir": test_dir,
        "review_content": review_content,
        "sample_diff": sample_diff,
        "test_file_path": test_file_path,
        "test_file_content": test_file_content,
    }

    temp_dir.cleanup()


@pytest.mark.asyncio
@patch("opentips.tips.fetch_tips.get_review_instructions")
@patch("opentips.tips.fetch_tips.llm_tips")
async def test_fetch_tips_for_diff_empty_diff(
    mock_llm_tips, mock_get_review, test_setup
):
    """Test fetch_tips_for_diff returns empty list for empty diff"""
    mock_get_review.return_value = None
    mock_llm_tips.return_value = LLMTipList(tips=[])

    result = await fetch_tips_for_diff([])

    assert isinstance(result, TipList)
    assert len(result.tips) == 0
    mock_llm_tips.assert_called_once_with([], None, None)


@pytest.mark.asyncio
@patch("opentips.tips.fetch_tips.get_review_instructions")
@patch("opentips.tips.fetch_tips.llm_tips")
async def test_fetch_tips_for_file_range_invalid_range(
    mock_llm_tips, mock_get_review, test_setup
):
    """Test fetch_tips_for_file_range with invalid line range"""
    mock_get_review.return_value = None
    mock_llm_tips.return_value = LLMTipList(tips=[])

    result = await fetch_tips_for_file_range(str(test_setup["test_file_path"]), 10, 5)

    assert isinstance(result, TipList)
    assert len(result.tips) == 0
    mock_llm_tips.assert_called_once()


@pytest.mark.asyncio
@patch("opentips.tips.fetch_tips.get_review_instructions")
@patch("opentips.tips.fetch_tips.llm_tips")
async def test_fetch_tips_for_nonexistent_file(
    mock_llm_tips, mock_get_review, test_setup
):
    """Test fetch_tips_for_file_range with nonexistent file"""
    mock_get_review.return_value = None

    result = await fetch_tips_for_file_range("nonexistent.py", 1, 2)

    assert isinstance(result, TipList)
    assert len(result.tips) == 0
    assert "File not found" in (result.error or "")
    mock_llm_tips.assert_not_called()

    @patch("opentips.tips.fetch_tips.get_review_instructions")
    @patch("opentips.tips.fetch_tips.llm_tips")
    async def test_fetch_tips_for_diff_with_review(
        self, mock_llm_tips, mock_get_review
    ):
        """Test fetch_tips_for_diff uses review instructions when available"""
        # Setup mocks
        mock_get_review.return_value = self.review_content
        mock_tip = LLMTip(
            file="test1.py",
            line=1,
            type="style",
            context="def test():",
            complexity="low",
            label="Test Tip",
            description="This is a test tip",
            priority="medium",
        )
        mock_llm_tips.return_value = LLMTipList(tips=[mock_tip])

        # Execute
        result = await fetch_tips_for_diff(self.sample_diff)

        # Verify
        mock_get_review.assert_called_once()
        mock_llm_tips.assert_called_once_with(
            self.sample_diff, None, self.review_content
        )
        self.assertEqual(len(result.tips), 1)
        self.assertEqual(result.tips[0].file, "test1.py")

    @patch("opentips.tips.fetch_tips.get_review_instructions")
    @patch("opentips.tips.fetch_tips.llm_tips")
    async def test_fetch_tips_for_diff_without_review(
        self, mock_llm_tips, mock_get_review
    ):
        """Test fetch_tips_for_diff works correctly when no review instructions available"""
        # Setup mocks
        mock_get_review.return_value = None
        mock_tip = LLMTip(
            file="test1.py",
            line=1,
            type="style",
            context="def test():",
            complexity="low",
            label="Test Tip",
            description="This is a test tip",
            priority="medium",
        )
        mock_llm_tips.return_value = LLMTipList(tips=[mock_tip])

        # Execute
        result = await fetch_tips_for_diff(self.sample_diff)

        # Verify
        mock_get_review.assert_called_once()
        mock_llm_tips.assert_called_once_with(self.sample_diff, None, None)
        self.assertEqual(len(result.tips), 1)
        self.assertEqual(result.tips[0].file, "test1.py")

    @patch("opentips.tips.fetch_tips.get_review_instructions")
    @patch("opentips.tips.fetch_tips.llm_tips")
    async def test_fetch_tips_for_file_range_with_review(
        self, mock_llm_tips, mock_get_review
    ):
        """Test fetch_tips_for_file_range uses review instructions when available"""
        # Setup mocks
        mock_get_review.return_value = self.review_content
        mock_tip = LLMTip(
            file=str(self.test_file_path),
            line=1,
            type="style",
            context="def sample():",
            complexity="low",
            label="Test Tip",
            description="This is a test tip",
            priority="medium",
        )
        mock_llm_tips.return_value = LLMTipList(tips=[mock_tip])

        # Execute
        result = await fetch_tips_for_file_range(str(self.test_file_path), 1, 2)

        # Verify
        mock_get_review.assert_called_once()
        # Check that llm_tips was called with a FileChunk and review instructions
        mock_llm_tips.assert_called_once()
        args = mock_llm_tips.call_args[0]
        self.assertIsNone(args[0])  # diff_chunks should be None
        self.assertIsInstance(args[1], FileChunk)  # file_chunk should be a FileChunk
        self.assertEqual(
            args[2], self.review_content
        )  # review_instructions should match

        self.assertEqual(len(result.tips), 1)
        self.assertEqual(result.tips[0].file, str(self.test_file_path))

    @patch("opentips.tips.fetch_tips.get_review_instructions")
    @patch("opentips.tips.fetch_tips.llm_tips")
    async def test_fetch_tips_for_file_range_without_review(
        self, mock_llm_tips, mock_get_review
    ):
        """Test fetch_tips_for_file_range works correctly when no review instructions available"""
        # Setup mocks
        mock_get_review.return_value = None
        mock_tip = LLMTip(
            file=str(self.test_file_path),
            line=1,
            type="style",
            context="def sample():",
            complexity="low",
            label="Test Tip",
            description="This is a test tip",
            priority="medium",
        )
        mock_llm_tips.return_value = LLMTipList(tips=[mock_tip])

        # Execute
        result = await fetch_tips_for_file_range(str(self.test_file_path), 1, 2)

        # Verify
        mock_get_review.assert_called_once()
        # Check that llm_tips was called with a FileChunk but no review instructions
        mock_llm_tips.assert_called_once()
        args = mock_llm_tips.call_args[0]
        self.assertIsNone(args[0])  # diff_chunks should be None
        self.assertIsInstance(args[1], FileChunk)  # file_chunk should be a FileChunk
        self.assertIsNone(args[2])  # review_instructions should be None

        self.assertEqual(len(result.tips), 1)
        self.assertEqual(result.tips[0].file, str(self.test_file_path))
