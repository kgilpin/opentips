from unittest.mock import patch
import pytest

from opentips.tips.rpc_types import Tip
from opentips.llm.llm_prune_tips import (
    llm_prune_tips,
    LLMPrunedTips,
    llm_prune_tips_prompt,
)


class TestLLMPruneTips:
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
                label="Formatting",
                description="Fix indentation",
            ),
            Tip(
                id="tip2",
                directory="/test",
                file="file2.py",
                line=20,
                context="def another():",
                type="performance",
                complexity="high",
                label="Algorithm",
                description="Use more efficient algorithm",
            ),
            Tip(
                id="tip3",
                directory="/test",
                file="file3.py",
                line=30,
                context="x = 1",
                type="style",
                complexity="low",
                label="Formatting",
                description="Add whitespace",
            ),
        ]

    @patch("opentips.llm.llm_prune_tips.get_completion_handler")
    async def test_prune_tips_success(self, mock_get_completion_handler, sample_tips):
        # Configure mock to return specific tips to retain
        async def async_handler(*args, **kwargs):
            assert len(args) == 4, f"Expected 4 arguments, got {args}"
            return LLMPrunedTips(retained_tips=["tip1", "tip2"])

        mock_get_completion_handler.return_value = async_handler

        # Execute with a limit of 2 tips
        result = await llm_prune_tips(sample_tips, 2)

        # Verify results
        assert len(result) == 2
        assert result[0].id == "tip1"
        assert result[1].id == "tip2"

        mock_get_completion_handler.assert_called_once()

    def test_prune_tips_prompt(self):
        expected_prompt = f"""You are a programming assistant helping to manage a list of code improvement tips.

Return the tips in a resorted order, with the most valuable and diverse tips first.

Prioritize those that are:

1. Most actionable and valuable for improving the code
2. Represent a diverse set of improvement types
3. Cover different complexity levels
4. Avoid redundant or very similar suggestions

When there are similar or redundant suggestions, always choose just one to retain.

Respond with a list of tip IDs to retain, in JSON format like this:
{{"retained_tips": ["tip-id-1", "tip-id-2", ...]}}

Here are the available tips:
"""

        # Execute
        prompt = llm_prune_tips_prompt()
        assert prompt.strip() == expected_prompt.strip()

    @patch("opentips.llm.llm_prune_tips.get_completion_handler")
    async def test_prune_tips_error(self, mock_get_completion_handler, sample_tips):
        # Simulate an error in the LLM completion
        async def async_handler(*args, **kwargs):
            raise Exception("LLM error")

        mock_get_completion_handler.return_value = async_handler

        # Execute
        result = await llm_prune_tips(sample_tips, 2)

        # On error, should return all tips
        assert result == sample_tips
