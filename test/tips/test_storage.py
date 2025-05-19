import unittest
import tempfile
from pathlib import Path

from pydantic import BaseModel
from opentips.tips.storage import (
    build_tip_digest,
    parse_tip_external_id,
    build_tip_external_id,
    save_tip_if_new,
    load_tip,
    set_base_storage_dir,
)


class TestStorage(unittest.TestCase):
    def setUp(self):
        # Create a temporary directory for storage
        self.temp_dir = tempfile.TemporaryDirectory()
        self.storage_dir = Path(self.temp_dir.name)
        set_base_storage_dir(self.storage_dir)

    def tearDown(self):
        # Clean up the temporary directory
        self.temp_dir.cleanup()

    def tetxternal_id(self):
        # This is the encoded tip ID
        tip_id = "MS4wCi9Vc2Vycy9rZ2lscGluL3NvdXJjZS9rZ2lscGluL29wZW50aXBzLXZzY29kZQpEakowa3ZkbWNTeUFscmdtc2lhN013OV83SjVwb204NUVpN2M1eEk4ZktJ"

        # Parse the external ID
        version, directory, internal_id = parse_tip_external_id(tip_id)

        self.assertEqual(version, "1.1")
        self.assertEqual(directory, "/Users/kgilpin/source/kgilpin/opentips-vscode")
        self.assertEqual(internal_id, "DjJ0kvdmcSyAlrgmsia7Mw9_7J5pom85Ei7c5xI8fKI")

    def test_build_and_parse_tip_external_id(self):
        # Test round-trip encoding and decoding
        directory = "/test/dir"
        internal_id = "test123"

        # Build external ID
        external_id = build_tip_external_id(internal_id, directory)

        # Parse it back
        version, parsed_directory, parsed_internal_id = parse_tip_external_id(
            external_id
        )

        # Verify round-trip
        self.assertEqual(version, "1.1")
        self.assertEqual(directory, parsed_directory)
        self.assertEqual(internal_id, parsed_internal_id)

    def test_priority_migration(self):
        class TipWithoutPriority(BaseModel):
            id: str
            directory: str
            file: str
            line: int
            type: str
            label: str
            description: str
            complexity: str
            context: str

        """Test that tips without priority are assigned a default 'medium' priority when loaded"""
        # Create a tip without priority field
        tip_without_priority = TipWithoutPriority(
            id="tip1",
            directory="/test/dir",
            file="test.py",
            line=1,
            type="bug",
            label="Test Label",
            description="Test Description",
            complexity="medium",
            context="test context",
        )
        tip_digest = build_tip_digest(tip_without_priority)
        tip_id = build_tip_external_id(
            tip_digest, tip_without_priority.directory, version="1.0"
        )

        # type ignore is needed here because we are deliberately using a different class
        is_saved = save_tip_if_new(tip_without_priority, tip_id)  # type: ignore
        # Verify that the tip is saved
        assert is_saved

        # Load tip using storage functions - should add priority
        loaded_tip = load_tip(tip_without_priority.id)
        self.assertEqual(loaded_tip.priority, "medium")
