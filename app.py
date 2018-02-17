from flask import Flask, request, render_template, redirect, url_for, session, make_response
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


@app.before_request
def make_session_permanent():
    session.permanent = True


@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'GET':
        session['kategoria'] = None
        return render_template('layout.html', html_layout=True)

    elif request.method == 'POST':
        print(request.form)
        list_random_kategorie = ['ranajky_random', 'obed_random', 'vecera_random', 'dezert_random']
        list_kategorie = ['ranajky', 'obed', 'vecera', 'dezert']
        if request.form['btn'] == "DOMOV":
            respond = make_response(redirect(url_for('home')))
            return respond

        elif request.form['btn'] == "ONAS":
            return "nefunguje"

        elif request.form['btn'] == "nahodny_vyber_vsetko":
            session['kategoria'] = 'everything'
            respond = make_response(redirect(url_for('jedlo')))
            return respond

        elif request.form['btn'] == "zoznam":
            respond = make_response(redirect(url_for('zoznam')))
            return respond

        elif request.form['btn'] in list_random_kategorie:
            for a in range(len(list_random_kategorie)):
                print(request.form['btn'], list_random_kategorie[a])
                if request.form['btn'] == list_random_kategorie[a]:
                    session['kategoria'] = list_kategorie[a]
                    break
            respond = make_response(redirect(url_for('jedlo')))
            return respond


@app.route('/jedlo', methods=['GET', 'POST'])
def jedlo():
    if request.method == 'GET':
        kategoria = session['kategoria']
        print('kategoria', kategoria)
        if kategoria == 'everything':
            engine.execute('''SELECT * FROM jedlo ORDER BY RANDOM() LIMIT 1''')
        else:
            hlada = '''SELECT * FROM jedlo WHERE attribute = %s ORDER BY RANDOM() LIMIT 1'''
            engine.execute(hlada, (kategoria,))
        result_set = str(engine.fetchall()).replace("[(", "").replace(")]", "").replace("'", "")
        print(result_set)
        jedlo, attribute, link = result_set.split(",")
        respond = make_response(render_template('jedlo.html', html_jedlo=True, jedlo=jedlo, link=link))
        return respond

    elif request.method == 'POST':
        print(request.form)
        list_random_kategorie = ['ranajky_random', 'obed_random', 'vecera_random', 'dezert_random']
        list_kategorie = ['ranajky', 'obed', 'vecera', 'dezert']
        if request.form['btn'] == "DOMOV":
            respond = make_response(redirect(url_for('home')))
            return respond

        elif request.form['btn'] == "ONAS":
            return "nefunguje"

        elif request.form['btn'] == "nahodny_vyber_vsetko":
            session['kategoria'] = 'everything'
            respond = make_response(redirect(url_for('jedlo')))
            return respond

        elif request.form['btn'] == "zoznam":
            respond = make_response(redirect(url_for('zoznam')))
            return respond

        elif request.form['btn'] in list_random_kategorie:
            for a in range(len(list_random_kategorie)):
                print(request.form['btn'], list_random_kategorie[a])
                if request.form['btn'] == list_random_kategorie[a]:
                    session['kategoria'] = list_kategorie[a]
                    break
            respond = make_response(redirect(url_for('jedlo')))
            return respond


@app.route('/zoznam', methods=['GET', 'POST'])
def zoznam():
    if request.method == 'GET':
        attribute = {'ranajky': [], 'obed': [], 'vecera': [], 'dezert': []}
        list_attributov = ['ranajky', 'obed', 'vecera', 'dezert']
        for a in list_attributov:
            hlada_v_databaze = '''SELECT nazov FROM jedlo WHERE attribute=%s'''
            engine.execute(hlada_v_databaze, (a,))
            result_set = engine.fetchall()
            for b in result_set:
                attribute[a].append(b[0])

        respond = make_response(render_template('zoznam.html',
                                ranajky=attribute['ranajky'],
                                obed=attribute['obed'],
                                vecera=attribute['vecera'],
                                dezert=attribute['dezert']))
        return respond


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        respond = render_template('login.html')
        session['password'] = None
        return respond
    if request.method == 'POST':
        if request.form['btn'] == 'Submit':
            passcode = request.form['passcode']
            mysecretkey = app.secret_key
            if passcode == mysecretkey:
                respond = redirect(url_for('justadminthings'))
                session['password'] = app.secret_key
                return respond
            respond = redirect(url_for('home'))
            return respond


@app.route('/justadminthings', methods=['GET', 'POST'])
def justadminthings():
    if request.method == 'GET':
        kookie = session.get('password')
        if kookie == app.secret_key:
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
        else:
            respond = redirect(url_for('home'))
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

            tree = ET.parse('jedlo.xml')
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
            respond = render_template('justadminthings.html', cosatodeje='PREPISANE DO DATABAZY')
            return respond

        elif request.form['btn'] == 'Vymazat vsetko z databazy':
            engine.execute('''DROP TABLE jedlo''')
            respond = render_template('justadminthings.html', cosatodeje='V DATABAZE SA NIC NENACHADZA')
            return respond

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
                respond = render_template('justadminthings.html', cosatodeje='NENACHADZA SA V DATABAZE')
                return respond

            rawformat = '''DELETE FROM jedlo WHERE nazov = %s;'''
            engine.execute(rawformat, (nazov,))
            respond = render_template('justadminthings.html', cosatodeje='USPESNE VYMAZANE')
            return respond

        elif request.form['btn'] == 'Vymazat vsetko z databazy pridanych jedal':
            engine.execute('''DROP TABLE neoverenejedlo''')
            respond = render_template('justadminthings.html', cosatodeje='V DATABAZE S NAVRHOVANYMI JEDLAMI SA NIC NENACHADZA')
            return respond


"""
@app.route('/vsetkojedlo', methods=['GET', 'POST'])
def vsetkojedlo():
    if request.method == 'GET':
        moznosti1 = ['RANAJKY', 'HLAVNE JEDLA', 'POLIEVKY', 'VECERE', 'KOLACE A DEZERTY']
        kategoria = moznosti1[session['kategoria_vsetky']]
        session['kategoria_vsetky'] = None
        hladavdatabaze = '''SELECT nazov FROM jedlo WHERE attribute=%s'''
        engine.execute(hladavdatabaze, (kategoria,))
        list_jedal = []
        for row in engine:
            list_jedal.append(row[0])
        list_jedal.sort()
        respond = render_template('vsetky.html', loopdata=list_jedal)
        return respond
    if request.method == 'POST':
        hladavdatabaze = '''SELECT * FROM jedlo WHERE nazov=%s'''
        engine.execute(hladavdatabaze, (request.form['btn'],))
        result_set = engine.fetchall()
        result_set = str(result_set)
        result_set = result_set.replace("[(", "").replace(")]", "").replace("'", "")
        x = result_set
        nazov, attribute, link, fotka = x.split(",")
        return render_template('jedlo.html', nazov=nazov, attribute=attribute, link=link, fotka=fotka[1:])


@app.route('/pridavanie', methods=['GET', 'POST'])
def pridavanie():
    if request.method == 'GET':
        engine.execute("CREATE TABLE IF NOT EXISTS neoverenejedlo (nazov text, attribute text, link text, fotka text);")
        respond = render_template('pridavanie.html')
        return respond
    elif request.method == 'POST':
        if request.form['btn'] == 'Pridat':
            try:
                nazov = request.form['vloztemeno']
                attribute = request.form['vlozteattribute']
                link = request.form['vloztelink']
                fotka = request.form['vloztefotku']
                rawformat = '''INSERT INTO neoverenejedlo VALUES (%s, %s, %s, %s);'''
                engine.execute(rawformat, (nazov, attribute, link, fotka))
                engine.execute('''SELECT * FROM neoverenejedlo''')
                respond = render_template('pridavanie.html', vysledok='Podarilo sa')
            except:
                respond = render_template('pridavanie.html', vysledok='Nevyslo :( zrejme tam mas chybu :(')
            return respond



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
            nazov, attribute, link, fotka = x.split(",")
            pole = {'nazov': nazov, 'attribute': attribute, 'link': link, 'fotka': fotka}
            respond = render_template('potvrdzovanie.html', nazov=nazov, attribute=attribute, link=link, fotka=fotka)
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
        fotka = pole['fotka']

        if request.form['btn'] == 'Potvrdit':
            rawformat = '''INSERT INTO jedlo VALUES (%s, %s, %s, %s);'''
            engine.execute(rawformat, (nazov, attribute, link, fotka))
            f = open("nove_jedla", 'a')
            f.write('<nazov>' + nazov + '</nazov>' + '\n')
            f.write('<attribute>' + attribute + '</attribute>' + '\n')
            f.write('<link>' + link + '</link>' + '\n')
            f.write('<fotka>' + fotka + '</fotka>' + '\n')
            f.close()
            
        rawformat = '''DELETE FROM neoverenejedlo WHERE nazov = %s;'''
        engine.execute(rawformat, (nazov,))

        return redirect(url_for('potvrdzovanie'))
"""

app.secret_key = os.environ["SESSION_KEY"]


if __name__ == '__main__':
    app.run(debug=True, use_reloader=True)
