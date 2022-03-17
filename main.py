import os
import sqlite3
import subprocess
import tempfile
import socket

import typer

os.chdir(os.path.dirname(os.path.abspath(__file__)))

app = typer.Typer()

db = sqlite3.connect(os.getcwd() + '/category_snapshot.sqlite')
db.execute('''
    CREATE TABLE IF NOT EXISTS snapshot_version (
        version integer PRIMARY KEY AUTOINCREMENT,
        created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
    )
''')
db.execute('''
    CREATE TABLE IF NOT EXISTS category_product_snapshot (
        version integer NOT NULL,
        category_id integer NOT NULL,
        product_count integer NOT NULL
    )
''')


@app.command()
def analyse(recipient: str, percentage_trigger: int = typer.Argument(50, help="Percentage difference to trigger notification")):
    version = db.execute('''SELECT MAX(version) FROM snapshot_version''').fetchone()[0]

    if version == 1:
        return

    latest = get_version(version)
    previous = get_version(version - 1)

    output = open(os.getcwd() + '/diff.txt', 'w')

    try:
        for category in latest:
            latest_count = latest[category]
            prev_count = previous[category]

            if latest_count < prev_count:
                percentage_change = round(((prev_count - latest_count) / prev_count) * 100, 2)

                if percentage_change >= percentage_trigger:
                    msg = f"Category {category} has decreased from {prev_count} to {latest_count}, a {percentage_change}% difference"
                    typer.echo(msg)
                    output.write(msg + '\n')

        if output.tell() > 0:
            hostname = socket.gethostname()
            command = f"""/usr/bin/mutt -e "set from='support@sonassi.com' realname='{hostname} | Sonassi" -s "C+B Categories have changed" -- {recipient} < {output.name}"""
            subprocess.Popen(command, shell=True)
    finally:
        pass


def get_version(version):
    rows = db.execute(
        '''select * from category_product_snapshot where version = ? order by category_id ASC''',
        [version]
    ).fetchall()

    result = {}
    for row in rows:
        result[row[1]] = row[2]

    return result


@app.command()
def generate(n98_path: str = typer.Argument(..., help="Path to n98"),
             mage_root: str = typer.Argument(..., help="Path to the Mage root directory")):
    create_category_snapshot(n98_path, mage_root)


def create_category_snapshot(n98_path, mage_root):
    query = 'select category_id, COUNT(product_id) from catalog_category_product group by category_id'
    process = subprocess.Popen(f'{n98_path} --root-dir={mage_root} db:query "{query}"',
                               shell=True,
                               stdout=subprocess.PIPE)

    if process.returncode:
        raise typer.Exit(f"Error: {process.stderr.readlines()}")

    version = db.execute('''INSERT INTO snapshot_version (version) VALUES (NULL)''').lastrowid
    snapshot = process.stdout.readlines()
    snapshot = [line.decode('utf-8').rstrip().split('\t') for line in snapshot[1:]]

    to_insert = []
    for line in snapshot:
        to_insert.append(
            {
                'version': version,
                'category_id': line[0],
                'product_count': line[1],
            }
        )

    db.executemany('''
        insert into category_product_snapshot (version, category_id, product_count)
        VALUES (:version, :category_id, :product_count)''', to_insert)

    db.commit()


if __name__ == '__main__':
    app()
