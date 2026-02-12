import click
import psycopg2
import psycopg2.extras
from flask import current_app, g


def get_db():
    if 'db' not in g:
        g.db = psycopg2.connect(current_app.config['DB_URL'])
        g.db.cursor_factory = psycopg2.extras.DictCursor
    return g.db


def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()


@click.command('init-db')
def init_db_command():
    """Initialisiert die Datenbank."""
    init_db()
    click.echo('Datenbank initialisiert.')


def init_db():
    db = get_db()
    with current_app.open_resource('schema.sql') as f:
        content = f.read().decode('utf-8')
        with db.cursor() as cursor:
            cursor.execute(content)
        db.commit()


def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)