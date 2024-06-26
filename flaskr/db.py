import fdb


import click
from flask import current_app, g
from flask.cli import with_appcontext




def init_db():
    try:
        conn = fdb.connect(
            dsn=current_app.config['DATABASE'],
            user=current_app.config['USER'],
            password=current_app.config['PASSWORD'],
            fb_library_name=current_app.config['LIBRARY']
        )
        conn.drop_database()
    except Exception as e:
        print(e)




    conn = fdb.create_database(
        dsn=current_app.config['DATABASE'],
        user=current_app.config['USER'],
        password=current_app.config['PASSWORD'],
        fb_library_name=current_app.config['LIBRARY']
    )


    metadata = [
        '''
        RECREATE TABLE users (
            id integer generated by default as identity primary key,
            username varchar(256) UNIQUE NOT NULL,
            password varchar(256) NOT NULL
        )
        ''',
        '''
        RECREATE TABLE posts (
            id integer generated by default as identity primary key,
            author_id INTEGER NOT NULL REFERENCES users (id),
            created TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
            title varchar(120) NOT NULL,
            body varchar(5000) NOT NULL
        )
        '''
    ]


    cursor = conn.cursor()


    for query in metadata:
        cursor.execute(query)


    conn.commit()




def get_db():
    if 'db' not in g:
        g.db = fdb.connect(
            dsn=current_app.config['DATABASE'],
            user=current_app.config['USER'],
            password=current_app.config['PASSWORD'],
            fb_library_name=current_app.config['LIBRARY']
        )


    return g.db




def close_db(e=None):
    db = g.pop('db', None)


    if db is not None:
        db.close()




@click.command('init-db')
@with_appcontext
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo('Initialized the database.')




def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
