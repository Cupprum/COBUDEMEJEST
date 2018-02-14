import psycopg2
import os
from urllib.parse import urlparse
import xml.etree.ElementTree as ET

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

elif comarobit == 'vlozvsetko':
    url = urlparse(os.environ["DATABASE_URL"])
    db = "dbname=%s user=%s password=%s host=%s " % (url.path[1:], url.username, url.password, url.hostname)
    conn = psycopg2.connect(db)
    conn.autocommit = True
    engine = conn.cursor()
    engine.execute("CREATE TABLE IF NOT EXISTS jedlo (nazov text, attribute text, link text);")

    tree = ET.parse('jedla.xml')
    root = tree.getroot()

    ypsilon = 1
    for jedlo in root.findall('jedlo'):
        number = jedlo.attrib.get('number')
        if str(ypsilon) == number:
            dlzka = None
            nazov = str(jedlo.find('nazov').text)
            attribute = str(jedlo.find('attribute').text)
            link = str(jedlo.find('link').text)
            nazov = nazov[13:-9]
            attribute = attribute[13:-9]
            link = link[13:-9]
            engine.execute('''SELECT * FROM jedlo WHERE nazov = '%s' ''' % (nazov,))
            result_set = engine.fetchall()
            for r in result_set:
                dlzka = 'something'
            if dlzka is None:
                vklada = '''INSERT INTO jedlo (nazov, attribute, link) VALUES (%s, %s, %s);'''
                engine.execute(vklada, (nazov, attribute, link))
            ypsilon += 1

elif comarobit == 'vymaz':
    nazov = input('vloz nazov: ')
    rawformat = '''DELETE FROM jedlo WHERE nazov = %s;'''
    engine.execute(rawformat, (nazov,))

elif comarobit == 'drop':
    engine.execute('''DROP TABLE jedlo''')

elif comarobit == 'jedno':
    nazov = input('nazov jedla co chces vypisat: ')
    engine.execute('''SELECT * FROM jedlo WHERE nazov = '%s' ''' % (nazov,))
    result_set = engine.fetchall()
    for r in result_set:
        print(r)
    print(' MEDZERA ')

elif comarobit == 'skuska':
    nazov = 'nieco'
    attribute = 'nieco2'
    link = 'nieco3'
    fotka = 'nieco4'
    f = open("nove_jedla", 'a')
    f.write('<nazov>' + nazov + '</nazov>' + '\n')
    f.write('<attribute>' + attribute + '</attribute>' + '\n')
    f.write('<fotka>' + fotka + '</fotka>' + '\n')
    f.close()

engine.execute('''SELECT * FROM jedlo''')
result_set = engine.fetchall()
for r in result_set:
    print(r)

print(' RANDOM ')
engine.execute('''SELECT * FROM jedlo ORDER BY RANDOM() LIMIT 1''')
result_set = engine.fetchall()
for r in result_set:
    print(r)
