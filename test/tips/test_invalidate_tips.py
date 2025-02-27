from typing import List
from unittest.mock import patch
import pytest
import logging

from opentips.tips.rpc_types import Tip
from opentips.tips.git import DiffChunk
from opentips.tips.invalidate_tips import invalidate_tips


class TestInvalidateTips:
    @pytest.fixture
    def sample_tips(self):
        return [
            Tip(
                id="tip1",
                directory="/test",
                file="file1.py",
                line=10,
                context="def example():",
                type="style",
                complexity="low",
                label="Test",
                description="Test description",
            ),
            Tip(
                id="tip2",
                directory="/test",
                file="file2.py",
                line=20,
                context="def another_example():",
                type="style",
                complexity="low",
                label="Test",
                description="Test description",
            ),
        ]

    @pytest.fixture
    def diff_chunks(self):
        return [
            DiffChunk(to_file="file1.py", chunk="@@ -10,5 +10,5 @@\n def example():"),
            DiffChunk(
                to_file="file2.py", chunk="@@ -20,5 +20,5 @@\n def missing_example():"
            ),
        ]

    @patch("opentips.tips.invalidate_tips.match_tip_in_file")
    @patch("opentips.tips.invalidate_tips.update_tip")
    @patch("opentips.tips.invalidate_tips.delete_tip")
    @patch("opentips.tips.invalidate_tips.event_broadcaster")
    def test_invalidate_tips(
        self,
        mock_broadcaster,
        mock_delete_tip,
        mock_update_tip,
        mock_match_tip,
        sample_tips,
        diff_chunks,
    ):
        # First tip found at new line 15, second tip not found
        mock_match_tip.side_effect = [15, None]
        mock_delete_tip.return_value = True

        # Execute
        changed_files = {chunk.to_file for chunk in diff_chunks}
        valid_tips = invalidate_tips(sample_tips, changed_files=changed_files)

        assert valid_tips == [sample_tips[0]]

        # Assert
        assert mock_match_tip.call_count == 2
        mock_match_tip.assert_any_call(sample_tips[0])
        mock_match_tip.assert_any_call(sample_tips[1])

        # First tip should be updated with new line number
        assert sample_tips[0].line == 15
        mock_update_tip.assert_called_once_with(sample_tips[0])

        # Second tip should be deleted
        assert mock_delete_tip.return_value
        mock_delete_tip.assert_called_once_with(sample_tips[1].id)

        mock_broadcaster.enqueue_event.assert_called_once_with(
            "tip_deleted", {"tip_id": sample_tips[1].id, "reason": "invalidated"}
        )

    @patch("opentips.tips.invalidate_tips.match_tip_in_file")
    @patch("opentips.tips.invalidate_tips.update_tip")
    @patch("opentips.tips.invalidate_tips.delete_tip")
    @patch("opentips.tips.invalidate_tips.event_broadcaster")
    def test_invalidate_tips_with_failed_operations(
        self,
        mock_broadcaster,
        mock_delete_tip,
        mock_update_tip,
        mock_match_tip,
        sample_tips,
        diff_chunks,
        caplog,
    ):
        # Setup
        caplog.set_level(logging.WARNING)
        mock_match_tip.side_effect = [15, None]
        # Simulate failures
        mock_update_tip.return_value = False
        mock_delete_tip.side_effect = Exception("Failed to delete")

        # Execute
        changed_files = {chunk.to_file for chunk in diff_chunks}
        valid_tips = invalidate_tips(sample_tips, changed_files=changed_files)

        assert valid_tips == [sample_tips[0]]

        # Verify other behavior
        assert mock_match_tip.call_count == 2
        mock_update_tip.assert_called_once_with(sample_tips[0])
        mock_delete_tip.assert_called_once_with(sample_tips[1].id)
        mock_broadcaster.enqueue_event.assert_not_called()

        # Verify logging of failed operations
        assert (
            "WARNING  opentips.tips.invalidate_tips:log_tip.py:9 Failed to delete tip - tip2 file2.py:20"
            in caplog.text
        )
