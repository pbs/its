from unittest import mock

import pytest


def pytest_collection_finish(session):
    """Handle the pytest collection finish hook: configure pyannotate.
    Explicitly delay importing `collect_types` until all tests have
    been collected.  This gives gevent a chance to monkey patch the
    world before importing pyannotate.
    """
    from pyannotate_runtime import collect_types

    collect_types.init_types_collection()


@pytest.fixture(autouse=True)
def collect_types_fixture():
    from pyannotate_runtime import collect_types

    collect_types.resume()
    yield
    collect_types.pause()


def pytest_sessionfinish(session, exitstatus):
    from pyannotate_runtime import collect_types

    collect_types.dump_stats("type_info.json")


@pytest.fixture(scope='session', autouse=True)
def mock_s3_upload():
    upload_to_s3 = 'its.util.upload_to_s3'
    with mock.patch(upload_to_s3) as s3_upload:
        yield s3_upload
