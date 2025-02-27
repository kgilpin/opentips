import pytest

from opentips.tips.rpc_types import Tip
from opentips.tips.match_tip_in_file import match_tip_in_file


class TestMatchTipInFile:
    @pytest.fixture
    def sample_code(self, tmp_path):
        """Create a sample Python file with some code"""
        code = """def hello_world():
    # This is a comment
    print("Hello, world!")
    
    # Some more code
    x = 42
    if x > 0:
        return True
    return False
"""
        file_path = tmp_path / "sample.py"
        file_path.write_text(code)
        return file_path

    def test_matches_exact_line(self, sample_code):
        tip = Tip(
            id="test1",
            directory=str(sample_code.parent),
            file=str(sample_code),
            line=2,
            context="# This is a comment",
            type="style",
            complexity="low",
            label="Comment",
            description="This is a test comment",
        )
        assert match_tip_in_file(tip) == 2

    def test_matches_within_radius(self, sample_code):
        tip = Tip(
            id="test2",
            directory=str(sample_code.parent),
            file=str(sample_code),
            line=1,  # Original line is actually 6
            context="x = 42",
            type="style",
            complexity="low",
            label="Variable",
            description="This is a test variable",
        )
        assert match_tip_in_file(tip) == 6

    def test_no_match_found(self, sample_code):
        tip = Tip(
            id="test3",
            directory=str(sample_code.parent),
            file=str(sample_code),
            line=1,
            context="this line does not exist",
            type="style",
            complexity="low",
            label="NonExistent",
            description="This should not match",
        )
        assert match_tip_in_file(tip) is None
