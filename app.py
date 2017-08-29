from flask import Flask, request, render_template, redirect, url_for, session
import psycopg2
import os
import json
from urllib.parse import urlparse
import xml.etree.ElementTree as ET
import random


app = Flask(__name__)
url = urlparse(os.environ["DATABASE_URL"])
db = "dbname=%s user=%s password=%s host=%s " % (url.path[1:], url.username, url.password, url.hostname)
conn = psycopg2.connect(db)
conn.autocommit = True
engine = conn.cursor()


@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'GET':
        return render_template('layout.html')
    elif request.method == 'POST':
        if request.form['btn'] == 'Čo si dneska navaríme?':
            return redirect(url_for('jedlo'))
        elif request.form['btn'] == 'Pridať jedlo':
            return redirect(url_for('pridavanie'))


@app.route('/jedlo', methods=['GET', 'POST'])
def jedlo():
    if request.method == 'GET':
        engine.execute('''SELECT * FROM jedlo ORDER BY RANDOM() LIMIT 1''')
        result_set = engine.fetchall()
        result_set = str(result_set)
        result_set = result_set.replace("[(", "").replace(")]", "").replace("'", "")
        x = result_set
        nazov, attribute, link = x.split(",")
        print(nazov, attribute, link)
        return render_template('jedlo.html', nazov=nazov, attribute=attribute, link=link)
    elif request.method == 'POST':
        if request.form['btn'] == 'Iné jedlo.':
            respond = redirect(url_for('jedlo'))
            return respond
        elif request.form['btn'] == 'Domov':
            respond = redirect(url_for('home'))
            return respond


@app.route('/pridavanie', methods=['GET', 'POST'])
def pridavanie():
    if request.method == 'GET':
        engine.execute("CREATE TABLE IF NOT EXISTS neoverenejedlo (nazov text, attribute text, link text);")
        respond = render_template('pridavanie.html')
        return respond
    elif request.method == 'POST':
        if request.form['btn'] == 'Pridat':
            nazov = request.form['vloztemeno']
            attribute = request.form['vlozteattribute']
            link = request.form['vloztelink']
            rawformat = '''INSERT INTO neoverenejedlo VALUES (%s, %s, %s);'''
            engine.execute(rawformat, (nazov, attribute, link))
            engine.execute('''SELECT * FROM neoverenejedlo''')
            respond = render_template('pridavanie.html')
            return respond


@app.route('/justadminthings', methods=['GET', 'POST'])
def justadminthings():
    if request.method == 'GET':
        global engine
        pocetjedal = 0
        loopdata = []
        try:
	        engine.execute('''SELECT nazov FROM jedlo''')
	        result_set = engine.fetchall()
	        for r in result_set:
	            print(r)
	            r = random.choice(r[0:1])
	            pocetjedal += 1
	            loopdata.append(r)
        except psycopg2.ProgrammingError:
        	pass
        respond = render_template('justadminthings.html', loopdata=loopdata)
        return respond

    elif request.method == 'POST':
        if request.form['btn'] == 'Potvrdit nove jedla':
            respond = redirect(url_for('potvrdzovanie'))
            return respond

        elif request.form['btn'] == 'Pridat vsetko z xml':
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
                    print('nazov', nazov)
                    print('attribute', attribute)
                    print('link', link)
                    engine.execute('''SELECT * FROM jedlo WHERE nazov = '%s' ''' % (nazov,))
                    result_set = engine.fetchall()
                    for r in result_set:
                        print('RRRRRRRRRR', r)
                        dlzka = 'something'
                    if dlzka is None:
                        vklada = """INSERT INTO jedlo (nazov, attribute, link) VALUES (%s, %s, %s);"""
                        engine.execute(vklada, (nazov, attribute, link))
                    ypsilon += 1
            return 'prepisane do databazy'

        elif request.form['btn'] == 'Vymazat vsetko z databazy':
            engine.execute('''DELETE FROM jedlo''')
            return 'v databaze sa nic nenachadza'

        elif request.form['btn'] == 'Vymaz jedno':
            dlzka = None
            nazov = str(request.form['txt'])
            print(nazov, '|||||||||||||||||||')
            engine.execute('''SELECT * FROM jedlo WHERE nazov = '%s' ''' % (nazov,))
            result_set = engine.fetchall()
            for r in result_set:
                print(r)
                dlzka = 'something'
            if dlzka is None:
                return 'nenachadza sa v databaze'

            rawformat = '''DELETE FROM jedlo WHERE nazov = %s;'''
            engine.execute(rawformat, (nazov,))
            return 'uspesne vymazane'


@app.route('/potvrdzovanie', methods=['GET', 'POST'])
def potvrdzovanie():
    if request.method == 'GET':
        dlzka = None
        engine.execute('''SELECT * FROM neoverenejedlo''')
        result_set = engine.fetchall()
        for r in result_set:
            dlzka = 'Something'
        if dlzka is not None:
            engine.execute('''SELECT * FROM neoverenejedlo ORDER BY RANDOM() LIMIT 1''')
            result_set = engine.fetchall()
            result_set = str(result_set)
            result_set = result_set.replace("[(", "")
            result_set = result_set.replace(")]", "")
            result_set = result_set.replace("'", "")
            x = result_set
            nazov, attribute, link = x.split(",")
            pole = {'nazov': nazov, 'attribute': attribute, 'link': link}
            respond = render_template('potvrdzovanie.html', nazov=nazov, attribute=attribute, link=link)
            session['novejedlo'] = json.dumps(pole)

            engine.execute('''SELECT * FROM neoverenejedlo''')
            result_set = engine.fetchall()
            return respond

        return redirect(url_for('home'))

    elif request.method == 'POST':
        novejedlo = session['novejedlo']
        pole = json.loads(novejedlo)
        nazov = pole['nazov']
        attribute = pole['attribute']
        link = pole['link']

        if request.form['btn'] == 'Potvrdit':
            rawformat = '''INSERT INTO jedlo VALUES (%s, %s, %s);'''
            engine.execute(rawformat, (nazov, attribute, link))

        rawformat = '''DELETE FROM neoverenejedlo WHERE nazov = %s;'''
        engine.execute(rawformat, (nazov,))

        return redirect(url_for('potvrdzovanie'))


app.secret_key = os.environ["SESSION_KEY"]


if __name__ == '__main__':
    app.run(debug=True, use_reloader=True)
