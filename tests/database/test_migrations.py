import pytest

from webcheck.database import migrations


def get_migration_number(conn):
    with conn.cursor() as cur:
        cur.execute('select number from migrations limit 1')
        val = cur.fetchone()
        return int(val[0])


@pytest.fixture
def migrator_default(db_clean_conn):
    yield migrations.Migrator(db_clean_conn)


def test_default_migrations(migrator_default, db_clean_conn):
    assert 0 == migrator_default.current_version()
    assert 0 == get_migration_number(db_clean_conn)
    migrator_default.up()
    assert len(migrations.MIGRATIONS) == migrator_default.current_version()
    assert len(migrations.MIGRATIONS) == get_migration_number(db_clean_conn)
    # once more
    migrator_default.up()
    assert len(migrations.MIGRATIONS) == migrator_default.current_version()
    assert len(migrations.MIGRATIONS) == get_migration_number(db_clean_conn)


def test_migrator__empty(db_clean_conn):
    migrator = migrations.Migrator(db_clean_conn, [])
    assert 0 == migrator.current_version()
    migrator.down()
    assert 0 == migrator.current_version()
    migrator.up()
    assert 0 == migrator.current_version()
    migrator.down(1)
    assert 0 == migrator.current_version()
    migrator.up(1)
    assert 0 == migrator.current_version()


@pytest.fixture
def migrator_custom(db_clean_conn):
    custom = (
        migrations.Migration('select 1', 'select -1'),
        migrations.Migration('select 2', 'select -2'),
        migrations.Migration('select 3', 'select -3'),
    )
    yield migrations.Migrator(db_clean_conn, custom)


def test_migrator(db_clean_conn, migrator_custom):
    m = migrator_custom
    assert 0 == m.current_version()
    m.down()
    assert 0 == m.current_version()
    m.up(1)
    assert 1 == m.current_version()
    m.down(1)
    assert 0 == m.current_version()
    m.up(2)
    assert 2 == m.current_version()
    m.down(1)
    assert 1 == m.current_version()
    m.up()
    assert 3 == m.current_version()
    m.down()
    assert 0 == m.current_version()
