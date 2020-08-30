from webcheck.database import conn


def test_connect(mocker):
    m = mocker.patch('psycopg2.connect')

    conn.connect('foobar')

    m.assert_called_once_with('foobar')
