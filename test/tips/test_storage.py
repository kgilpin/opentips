import unittest
import base64
from opentips.tips.storage import parse_tip_external_id, build_tip_external_id


class TestStorage(unittest.TestCase):
    def test_parse_tip_external_id(self):
        # This is the encoded tip ID
        tip_id = "MS4wCi9Vc2Vycy9rZ2lscGluL3NvdXJjZS9rZ2lscGluL29wZW50aXBzLXZzY29kZQpEakowa3ZkbWNTeUFscmdtc2lhN013OV83SjVwb204NUVpN2M1eEk4ZktJ"

        # Parse the external ID
        directory, internal_id = parse_tip_external_id(tip_id)

        # Verify the decoded directory
        self.assertEqual(directory, "/Users/kgilpin/source/kgilpin/opentips-vscode")

        # Verify the internal ID
        self.assertEqual(internal_id, "DjJ0kvdmcSyAlrgmsia7Mw9_7J5pom85Ei7c5xI8fKI")

    def test_build_and_parse_tip_external_id(self):
        # Test round-trip encoding and decoding
        directory = "/test/dir"
        internal_id = "test123"

        # Build external ID
        external_id = build_tip_external_id(internal_id, directory)

        # Parse it back
        parsed_directory, parsed_internal_id = parse_tip_external_id(external_id)

        # Verify round-trip
        self.assertEqual(directory, parsed_directory)
        self.assertEqual(internal_id, parsed_internal_id)
