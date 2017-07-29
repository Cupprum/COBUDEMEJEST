import psycopg2
import os
from urllib.parse import urlparse

url = urlparse(os.environ["DATABASE_URL"])
db = "dbname=%s user=%s password=%s host=%s " % (url.path[1:], url.username, url.password, url.hostname)
conn = psycopg2.connect(db)
conn.autocommit = True
engine = conn.cursor()
engine.execute("CREATE TABLE IF NOT EXISTS jedlo (nazov text, attribute text, link text);")

print('vloz, vymaz, drop, jedno')
comarobit = input()

if comarobit == 'vloz':
    nazov = input('vloz nazov: ')
    attribute = input('vloz attribute: ')
    link = input('vloz link: ')
    rawformat = '''INSERT INTO jedlo VALUES (%s, %s, %s);'''
    engine.execute(rawformat, (nazov, attribute, link))

elif comarobit == 'vymaz':
    nazov = input('vloz nazov: ')
    rawformat = '''DELETE FROM jedlo WHERE nazov = %s;'''
    engine.execute(rawformat, (nazov,))

elif comarobit == 'drop':
    engine.execute('''DELETE FROM jedlo''')

elif comarobit == 'jedno':
    nazov = input('nazov jedla co chces vypisat: ')
    engine.execute('''SELECT * FROM jedlo WHERE nazov = '%s' ''' % (nazov,))
    result_set = engine.fetchall()
    for r in result_set:
        print(r)
    print(' MEDZERA ')

engine.execute('''SELECT * FROM jedlo''')
result_set = engine.fetchall()
for r in result_set:
    print(r)

print(' RANDOM ')
engine.execute('''SELECT * FROM jedlo ORDER BY RANDOM() LIMIT 1''')
result_set = engine.fetchall()
for r in result_set:
    print(r)
