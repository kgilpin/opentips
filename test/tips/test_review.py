import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from opentips.tips.review import get_review_instructions, REVIEW_FILENAME


class TestReview(unittest.TestCase):
    def setUp(self):
        # Create a temporary directory for testing
        self.temp_dir = tempfile.TemporaryDirectory()
        self.test_dir = Path(self.temp_dir.name)

    def tearDown(self):
        # Clean up the temporary directory
        self.temp_dir.cleanup()

    def test_get_review_instructions_no_file(self):
        """Test when REVIEW.md doesn't exist"""
        # Test with explicit directory
        instructions = get_review_instructions(self.test_dir)
        self.assertIsNone(instructions)

    def test_get_review_instructions_empty_file(self):
        """Test when REVIEW.md exists but is empty"""
        # Create empty REVIEW.md file
        review_path = self.test_dir / REVIEW_FILENAME
        review_path.touch()

        # Test with explicit directory
        instructions = get_review_instructions(self.test_dir)
        self.assertIsNone(instructions)

    def test_get_review_instructions_with_content(self):
        """Test when REVIEW.md exists and has content"""
        # Create REVIEW.md file with content
        review_path = self.test_dir / REVIEW_FILENAME
        test_content = "# Test Review Guidelines\n\nFocus on error handling."
        review_path.write_text(test_content)

        # Test with explicit directory
        instructions = get_review_instructions(self.test_dir)
        self.assertEqual(instructions, test_content)

    @patch("opentips.tips.review.Path.cwd")
    def test_get_review_instructions_default_directory(self, mock_cwd):
        """Test when using the default current working directory"""
        mock_cwd.return_value = self.test_dir

        # Create REVIEW.md file with content
        review_path = self.test_dir / REVIEW_FILENAME
        test_content = "# Test Review Guidelines\n\nFocus on error handling."
        review_path.write_text(test_content)

        # Test without specifying a directory
        instructions = get_review_instructions()
        self.assertEqual(instructions, test_content)

    def test_get_review_instructions_file_error(self):
        """Test when there's an error reading the file"""
        # Create the REVIEW.md file
        review_path = self.test_dir / REVIEW_FILENAME
        test_content = "# Test content"
        review_path.write_text(test_content)

        # Mock open to raise an exception
        with patch("builtins.open", side_effect=IOError("Test error")):
            instructions = get_review_instructions(self.test_dir)
            self.assertIsNone(instructions)


if __name__ == "__main__":
    unittest.main()