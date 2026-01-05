
import pytest
from unittest.mock import MagicMock, patch
from nomad.datamodel import EntryArchive, User
from nomad_training_resources.schema_packages.schema_package import TrainingResource, TrainingResourceRelation

@pytest.fixture
def mock_search():
    with patch('nomad.search.search') as mock:
        yield mock

def test_name_preservation(caplog):
    # Test that name is NOT overwritten if already set
    archive = EntryArchive()
    res = TrainingResource()
    res.identifier = "http://example.com/id"
    res.name = "My Custom Name"
    
    res.normalize(archive, None)
    
    assert res.name == "My Custom Name"

def test_name_fallback(caplog):
    # Test fallback to identifier if name is missing
    archive = EntryArchive()
    res = TrainingResource()
    res.identifier = "http://example.com/id"
    # name is None
    
    res.normalize(archive, None)
    
    assert res.name == "http://example.com/id"

def test_relation_resolution_success(mock_search):
    archive = EntryArchive()
    archive.metadata = MagicMock()
    archive.metadata.main_author.user_id = "user1"

    rel = TrainingResourceRelation()
    rel.target_identifier = "http://target.com"
    
    res = TrainingResource()
    res.relations.append(rel)

    # Mock search result
    mock_result = MagicMock()
    mock_result.pagination.total = 1
    mock_result.data = [{"entry_id": "entry1", "upload_id": "upload1"}]
    mock_search.return_value = mock_result

    res.normalize(archive, None)

    assert rel.target_resource == "../uploads/upload1/archive/entry1#data"
    assert rel.message == "Resolved"
    
    # Check if search was called with correct query
    mock_search.assert_called_with(
        owner="all",
        query={"results.eln.lab_ids": "http://target.com"},
        user_id="user1"
    )

def test_relation_resolution_not_found(mock_search):
    archive = EntryArchive()
    archive.metadata = MagicMock()
    archive = MagicMock() # easier matching
    archive.metadata.main_author.user_id = "user1"

    rel = TrainingResourceRelation()
    rel.target_identifier = "http://target.com"
    
    res = TrainingResource()
    res.relations.append(rel)

    # Mock search result
    mock_result = MagicMock()
    mock_result.pagination.total = 0
    mock_search.return_value = mock_result

    res.normalize(archive, None)

    assert rel.target_resource is None
    assert rel.message == "Not found"

def test_relation_resolution_ambiguous(mock_search):
    archive = EntryArchive()
    archive.metadata = MagicMock()
    archive.metadata.main_author.user_id = "user1"

    rel = TrainingResourceRelation()
    rel.target_identifier = "http://target.com"
    
    res = TrainingResource()
    res.relations.append(rel)

    # Mock search result
    mock_result = MagicMock()
    mock_result.pagination.total = 2
    mock_search.return_value = mock_result

    res.normalize(archive, None)

    assert rel.target_resource is None
    assert rel.message == "Ambiguous: multiple matches"
