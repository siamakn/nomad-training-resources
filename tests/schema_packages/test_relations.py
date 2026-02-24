import sys
from types import ModuleType
from unittest.mock import MagicMock, patch

import pytest
from nomad.datamodel import EntryArchive

from nomad_training_resources.schema_packages.schema_package import (
    TrainingResource,
    TrainingResourceRelation,
)


@pytest.fixture
def mock_search():
    import nomad

    if 'nomad.search' not in sys.modules:
        search_mod = ModuleType('nomad.search')
        sys.modules['nomad.search'] = search_mod
        setattr(nomad, 'search', search_mod)
    else:
        search_mod = sys.modules['nomad.search']

    if not hasattr(search_mod, 'MetadataPagination'):

        class DummyPagination:
            def __init__(self, page_size=None, **kwargs):
                self.page_size = page_size

        setattr(search_mod, 'MetadataPagination', DummyPagination)

    with patch('nomad.search.search', create=True) as mock:
        yield mock


def test_name_preservation(caplog):
    archive = EntryArchive()
    res = TrainingResource()
    res.identifier = 'http://example.com/id'
    res.entry_name = 'My Custom Name'

    res.normalize(archive, None)

    assert res.entry_name == 'My Custom Name'


def test_name_fallback(caplog):
    archive = EntryArchive()
    archive.metadata = MagicMock()
    archive.metadata.entry_name = 'my_custom_name.suffix'

    res = TrainingResource()
    res.identifier = 'http://example.com/id'
    res.entry_name = None
    archive.data = res

    res.normalize(archive, None)

    assert res.entry_name == 'my custom name'


def test_relation_resolution_success(mock_search):
    archive = EntryArchive()
    archive.metadata = MagicMock()
    archive.metadata.main_author.user_id = 'user1'

    rel = TrainingResourceRelation()
    rel.target_identifier = 'http://target.com'

    res = TrainingResource()
    res.relations.append(rel)

    mock_result = MagicMock()
    mock_result.pagination.total = 1
    mock_result.data = [{'entry_id': 'entry1', 'upload_id': 'upload1'}]
    mock_search.return_value = mock_result

    res.normalize(archive, None)

    assert (
        rel.target_resource.m_proxy_value == '../uploads/upload1/archive/entry1#/data'
    )
    assert rel.resolution_status == 'resolved_from_identifier'
    assert 'entry_id=entry1' in rel.resolution_message

    assert mock_search.call_count == 1
    _, kwargs = mock_search.call_args
    assert kwargs.get('owner') == 'visible'
    assert kwargs.get('user_id') == 'user1'
    query = kwargs.get('query') or {}
    assert list(query.values()) == ['http://target.com']


def test_relation_resolution_not_found(mock_search):
    archive = EntryArchive()
    archive.metadata = MagicMock()
    archive.metadata.main_author.user_id = 'user1'

    rel = TrainingResourceRelation()
    rel.target_identifier = 'http://target.com'

    res = TrainingResource()
    res.relations.append(rel)

    mock_result = MagicMock()
    mock_result.pagination.total = 0
    mock_result.data = []
    mock_search.return_value = mock_result

    res.normalize(archive, None)

    assert rel.target_resource is None
    assert rel.resolution_status == 'identifier_not_found'
    assert 'No TrainingResource found' in rel.resolution_message


def test_relation_resolution_ambiguous(mock_search):
    archive = EntryArchive()
    archive.metadata = MagicMock()
    archive.metadata.main_author.user_id = 'user1'

    rel = TrainingResourceRelation()
    rel.target_identifier = 'http://target.com'

    res = TrainingResource()
    res.relations.append(rel)

    mock_result = MagicMock()
    mock_result.pagination.total = 2
    mock_result.data = [
        {'entry_id': 'entry1', 'upload_id': 'upload1', 'entry_name': 'A'},
        {'entry_id': 'entry2', 'upload_id': 'upload2', 'entry_name': 'B'},
    ]
    mock_search.return_value = mock_result

    res.normalize(archive, None)

    assert rel.target_resource is None
    assert rel.resolution_status == 'identifier_ambiguous'
    assert 'Multiple TrainingResources found' in rel.resolution_message
