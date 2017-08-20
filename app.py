from flask import Flask, request, render_template, redirect, url_for, session
import psycopg2
import os
import json
from urllib.parse import urlparse

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
        result_set = result_set.replace("[(", "")
        result_set = result_set.replace(")]", "")
        result_set = result_set.replace("'", "")
        print(result_set)
        x = result_set
        nazov, attribute, link = x.split(",")
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
            print(nazov, attribute, link)
            rawformat = '''INSERT INTO neoverenejedlo VALUES (%s, %s, %s);'''
            engine.execute(rawformat, (nazov, attribute, link))
            engine.execute('''SELECT * FROM neoverenejedlo''')
            result_set = engine.fetchall()
            for r in result_set:
                print(r)
            respond = render_template('pridavanie.html')
            return respond


@app.route('/potvrdzovanie', methods=['GET', 'POST'])
def potvrdzovanie():
    if request.method == 'GET':
        dlzka = engine.execute('''SELECT COUNT(link) FROM neoverenejedlo''')
        print(dlzka)
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
            for r in result_set:
                print(r)

            return respond

        return redirect(url_for('home'))

    elif request.method == 'POST':
        novejedlo = session['novejedlo']
        pole = json.loads(novejedlo)
        nazov = pole['nazov']
        attribute = pole['attribute']
        link = pole['link']

        if request.form['btn'] == 'Potvrdit':
            print(nazov, attribute, link, '||||||||||||||||||||||||')
            rawformat = '''INSERT INTO jedlo VALUES (%s, %s, %s);'''
            engine.execute(rawformat, (nazov, attribute, link))

            return redirect(url_for('potvrdzovanie'))

        elif request.form['btn'] == 'Vymazat':
            rawformat = '''DELETE FROM neoverenejedlo WHERE nazov = %s;'''
            engine.execute(rawformat, (nazov,))

            return redirect(url_for('potvrdzovanie'))


app.secret_key = os.environ["SESSION_KEY"]


if __name__ == '__main__':
    app.run(debug=True, use_reloader=True)
