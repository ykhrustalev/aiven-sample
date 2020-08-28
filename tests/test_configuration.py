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
            host: ""
            name: name
            username: username
            password: password
        """,
        "'host' should be set"
    ),
    (
        """---
        database:
            host: host
            name: ""
            username: username
            password: password
        """,
        "'name' should be set"
    ),
    (
        """---
        database:
            host: host
            name: name
            port: port
            username: username
            password: password
        """,
        "'port' should be int"
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
            host: host
            name: name
            username: username
            password: password
        logging:
            destination: /path/to/file
        """,
        configuration.State(
            database=configuration.Database(
                host='host', port=5432, name='name',
                username='username', password='password'
            ),
            logging=configuration.Logging(
                level='info', destination='/path/to/file'
            ),
        )
    ),
    (
        """---
        database:
            host: host
            port: 1234
            name: name
            username: username
            password: password
        logging:
            level: warning
            destination: /path/to/file
        """,
        configuration.State(
            database=configuration.Database(
                host='host', port=1234, name='name',
                username='username', password='password'
            ),
            logging=configuration.Logging(
                level='warning', destination='/path/to/file'
            ),
        )
    ),
))
def test_load__succeeds(tmp_path, raw, expected):
    path = tmp_path / 'path'
    path.write_text(raw)
    assert expected == configuration.load(str(path))
