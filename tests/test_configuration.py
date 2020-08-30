import pytest

from webcheck import configuration


def test_load__missing_file(tmp_path):
    with pytest.raises(
        configuration.Error,
        match="No such file or director"
    ):
        configuration.load(f'{tmp_path}/path')


def test_load__empty_file(tmp_path):
    path = tmp_path / 'path'
    path.write_text('')

    with pytest.raises(
        configuration.Error,
        match="invalid configuration file"
    ):
        configuration.load(str(tmp_path / 'path'))


@pytest.mark.parametrize('raw, match', (
    (
        "", "invalid configuration file"
    ),
    (
        """---
        database:
            url: ""
        kafka:
            servers:
              - server1
        """,
        "{'url': \\['empty values not allowed'\\]}"
    ),
    (
        """---
        database:
            url: postgres://host
        kafka:
            servers:
              - server1
        logging:
            level: foo
        """,
        "{'level': \\['unallowed value foo'\\]"
    ),
))
def test_load__fails(tmp_path, raw, match):
    path = tmp_path / 'path'
    path.write_text(raw)

    with pytest.raises(
        configuration.Error,
        match=match,
    ):
        configuration.load(str(path))


@pytest.mark.parametrize('raw, expected', (
    (
        """---
        database:
            url: postgres://host
        kafka:
            servers:
              - server1
              - server2
        logging:
            destination: /path/to/file
        """,
        configuration.State(
            database=configuration.Database(url='postgres://host'),
            kafka=configuration.Kafka(servers=['server1', 'server2']),
            http_checker=configuration.HttpChecker(),
            logging=configuration.Logging(
                level='info', destination='/path/to/file'
            ),
        )
    ),
    (
        """---
        database:
            url: postgres://host
        kafka:
            servers:
              - server1
              - server2
            topic_checks: checks
            topic_results: results
        http_checker:
            timeout: 99
            allow_redirects: False
        logging:
            level: warning
            destination: /path/to/file
            format: format
        """,
        configuration.State(
            database=configuration.Database(url='postgres://host'),
            kafka=configuration.Kafka(
                servers=['server1', 'server2'],
                topic_checks="checks",
                topic_results="results",
            ),
            http_checker=configuration.HttpChecker(
                timeout=99,
                allow_redirects=False,
            ),
            logging=configuration.Logging(
                level='warning', destination='/path/to/file',
                format='format',
            ),
        )
    ),
))
def test_load__succeeds(tmp_path, raw, expected):
    path = tmp_path / 'path'
    path.write_text(raw)
    assert expected == configuration.load(str(path))
