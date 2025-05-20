import pytest
import base64

from opentips.tips.rpc_types import Tip


@pytest.fixture
def sample_tip():
    return Tip(
        id="test_id",
        directory="/test/dir",
        file="test.py",
        line=10,
        type="bug",
        label="Test Label",
        description="Test Description",
        priority="medium",
        complexity="low",
        context="def test_function():\n    pass",
    )


def test_tip_hash():
    """Test that Tip.__hash__() uses only the id field"""
    # Create two tips with the same id but different other fields
    tip1 = Tip(
        id="same_id",
        directory="/test/dir1",
        file="test1.py",
        line=10,
        type="bug",
        label="Label 1",
        description="Description 1",
        priority="medium",
        complexity="low",
        context="def func1():\n    pass",
    )
    
    tip2 = Tip(
        id="same_id",
        directory="/test/dir2",
        file="test2.py",
        line=20,
        type="style",
        label="Label 2",
        description="Description 2",
        priority="high",
        complexity="medium",
        context="def func2():\n    pass",
    )
    
    # The hash should be the same since the id is the same
    assert hash(tip1) == hash(tip2)
    
    # Create a tip with a different id
    tip3 = Tip(
        id="different_id",
        directory="/test/dir1",
        file="test1.py",
        line=10,
        type="bug",
        label="Label 1",
        description="Description 1",
        priority="medium",
        complexity="low",
        context="def func1():\n    pass",
    )
    
    # The hash should be different
    assert hash(tip1) != hash(tip3)


def test_decode_external_id_without_padding():
    """Test that Tip.validate_external_id works without base64 padding"""
    # Create an external ID without padding
    version = "1.1"
    directory = "/test/dir"
    internal_id = "test123"
    
    # Manually create the external ID
    unencoded = f"{version}\n{directory}\n{internal_id}"
    external_id = base64.urlsafe_b64encode(unencoded.encode("utf-8")).decode("utf-8")
    
    # Remove padding if present
    external_id = external_id.rstrip("=")
    
    # Verify the external ID can be validated
    Tip.validate_external_id(external_id, directory)
    

def test_validate_external_id_invalid_version():
    """Test that Tip.validate_external_id raises ValueError for invalid version"""
    # Create an external ID with invalid version
    version = "2.0"  # Invalid version
    directory = "/test/dir"
    internal_id = "test123"
    
    # Manually create the external ID
    unencoded = f"{version}\n{directory}\n{internal_id}"
    external_id = base64.urlsafe_b64encode(unencoded.encode("utf-8")).decode("utf-8")
    
    # Attempt to validate the external ID
    with pytest.raises(ValueError) as excinfo:
        Tip.validate_external_id(external_id, directory)
    
    assert "Invalid tip ID format" in str(excinfo.value)
    

def test_validate_external_id_wrong_format():
    """Test that Tip.validate_external_id raises ValueError for wrong format"""
    # Create an external ID with wrong format (missing internal_id)
    version = "1.1"
    directory = "/test/dir"
    
    # Manually create the external ID with wrong format
    unencoded = f"{version}\n{directory}"  # Missing internal_id
    external_id = base64.urlsafe_b64encode(unencoded.encode("utf-8")).decode("utf-8")
    
    # Attempt to validate the external ID
    with pytest.raises(ValueError) as excinfo:
        Tip.validate_external_id(external_id, directory)
    
    assert "Invalid tip ID" in str(excinfo.value)
    

def test_validate_external_id_directory_mismatch():
    """Test that Tip.validate_external_id raises ValueError for directory mismatch"""
    # Create an external ID with a different directory
    version = "1.1"
    directory_in_id = "/test/dir1"
    directory_to_check = "/test/dir2"  # Different directory
    internal_id = "test123"
    
    # Manually create the external ID
    unencoded = f"{version}\n{directory_in_id}\n{internal_id}"
    external_id = base64.urlsafe_b64encode(unencoded.encode("utf-8")).decode("utf-8")
    
    # Attempt to validate the external ID
    with pytest.raises(ValueError) as excinfo:
        Tip.validate_external_id(external_id, directory_to_check)
    
    assert "Tip directory mismatch" in str(excinfo.value)