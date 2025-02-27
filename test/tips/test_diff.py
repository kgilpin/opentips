import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from opentips.tips.diff import diff, DiffChunk
from opentips.tips.storage import BASE_STORAGE_DIR, set_base_storage_dir


class TestDiff(unittest.TestCase):
    def setUp(self):
        self.sample_diff_chunks = [
            DiffChunk(to_file="test1.py", chunk="def test():"),
            DiffChunk(to_file="test2.py", chunk="print('hello')"),
        ]
        # Create a working directory for the test and set base_storage_dir
        self.tempdir = tempfile.TemporaryDirectory()
        self.base_storage_dir = BASE_STORAGE_DIR
        set_base_storage_dir(Path(self.tempdir.name))

    def tearDown(self):
        """Cleanup the temporary directory after each test."""
        self.tempdir.cleanup()
        set_base_storage_dir(self.base_storage_dir)

    @patch("opentips.tips.diff.git_detect_branch_in_history")
    @patch("opentips.tips.diff.git_diff")
    def test_diff_no_base_branch(self, mock_git_diff, mock_detect_branch):
        # Setup
        mock_detect_branch.return_value = None

        # Execute
        result = diff()

        # Assert
        self.assertIsNone(result)
        mock_git_diff.assert_not_called()

    @patch("opentips.tips.diff.git_detect_branch_in_history")
    @patch("opentips.tips.diff.git_diff")
    def test_diff_empty_chunks(self, mock_git_diff, mock_detect_branch):
        # Setup
        mock_detect_branch.return_value = "main"
        mock_git_diff.return_value = []

        # Execute
        result = diff()

        # Assert
        self.assertEqual(result, [])
        mock_detect_branch.assert_called_once()
        mock_git_diff.assert_called_once()

    @patch("opentips.tips.diff.git_detect_branch_in_history")
    @patch("opentips.tips.diff.git_diff")
    def test_diff_new_only(self, mock_git_diff, mock_detect_branch):
        # Setup
        mock_detect_branch.return_value = "main"
        mock_git_diff.return_value = self.sample_diff_chunks

        result = diff(new_only=True)

        self.assertEqual(result, self.sample_diff_chunks)
        mock_detect_branch.assert_called_once()
        mock_git_diff.assert_called_once()

        # Repeat the diff() to see that the sample diff chunks are filtered out
        result = diff(new_only=True)
        self.assertEqual(result, [])


if __name__ == "__main__":
    unittest.main()
