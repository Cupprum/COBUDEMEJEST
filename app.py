from flask import request, render_template, redirect, url_for, session, make_response
import os
import json
import random
from sql_table_maker import db, app, jedlo_sql, create_func, drop_func, insert_one_func, insert_all_func


db.create_all()


@app.before_request
def make_session_permanent():
    session.permanent = True


@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'GET':
        session['kategoria'] = None
        return render_template('layout.html',
                               html_layout=True
                               )

    elif request.method == 'POST':
        list_random_kategorie = ['ranajky_random', 'obed_random', 'vecera_random', 'dezert_random']
        list_kategorie = ['ranajky', 'obed', 'vecera', 'dezert']
        list_set_category = ['set_category_all',
                             'set_category_ranajky',
                             'set_category_obed',
                             'set_category_vecera',
                             'set_category_dezert']
        list_attributov = ['vsetko',
                           'ranajky',
                           'obed',
                           'vecera',
                           'dezert']

        if request.form['btn'] == "DOMOV":
            respond = make_response(redirect(url_for('home')))
            return respond

        elif request.form['btn'] == "ONAS":
            return "nefunguje"

        elif request.form['btn'] in list_set_category:
            for a in range(0, len(list_attributov)):
                if request.form['btn'] == list_set_category[a]:
                    session['zoznam_kategoria'] = list_attributov[a]
            respond = make_response(redirect(url_for('zoznam')))
            return respond

        elif request.form['btn'] == "nahodny_vyber_vsetko":
            session['kategoria'] = 'everything'
            respond = make_response(redirect(url_for('jedlo')))
            return respond

        elif request.form['btn'] in list_random_kategorie:
            for a in range(len(list_random_kategorie)):
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
            aktualne_jedlo_nerandom = jedlo_sql.query.all()
            print(len(aktualne_jedlo_nerandom))
            random_number = random.randint(0, len(aktualne_jedlo_nerandom))
            aktualne_jedlo = aktualne_jedlo_nerandom[random_number]
        else:
            aktualne_jedlo_nerandom = jedlo_sql.query.filter_by(attribute=kategoria).all()
            print(len(aktualne_jedlo_nerandom))
            if len(aktualne_jedlo_nerandom) == 1:
                aktualne_jedlo = aktualne_jedlo_nerandom[0]
            else:
                random_number = random.randint(0, len(aktualne_jedlo_nerandom) + 1)
                aktualne_jedlo = aktualne_jedlo_nerandom[random_number]
        respond = make_response(render_template('layout.html',
                                                html_jedlo=True,
                                                jedlo=aktualne_jedlo.nazov,
                                                link=aktualne_jedlo.link
                                                ))
        return respond

    elif request.method == 'POST':
        list_random_kategorie = ['ranajky_random', 'obed_random', 'vecera_random', 'dezert_random']
        list_kategorie = ['ranajky', 'obed', 'vecera', 'dezert']
        list_set_category = ['set_category_all',
                             'set_category_ranajky',
                             'set_category_obed',
                             'set_category_vecera',
                             'set_category_dezert']
        list_attributov = ['vsetko',
                           'ranajky',
                           'obed',
                           'vecera',
                           'dezert']

        if request.form['btn'] == "DOMOV":
            respond = make_response(redirect(url_for('home')))
            return respond

        elif request.form['btn'] == "ONAS":
            return "nefunguje"

        elif request.form['btn'] in list_set_category:
            for a in range(0, len(list_attributov)):
                if request.form['btn'] == list_set_category[a]:
                    session['zoznam_kategoria'] = list_attributov[a]
            respond = make_response(redirect(url_for('zoznam')))
            return respond

        elif request.form['btn'] == "nahodny_vyber_vsetko":
            session['kategoria'] = 'everything'
            respond = make_response(redirect(url_for('jedlo')))
            return respond

        elif request.form['btn'] in list_random_kategorie:
            for a in range(len(list_random_kategorie)):
                if request.form['btn'] == list_random_kategorie[a]:
                    session['kategoria'] = list_kategorie[a]
                    break
            respond = make_response(redirect(url_for('jedlo')))
            return respond


@app.route('/zoznam', methods=['GET', 'POST'])
def zoznam():
    if request.method == 'GET':
        list_attributov = ['ranajky', 'obed', 'vecera', 'dezert']
        kategoria = session.get('zoznam_kategoria')

        if kategoria not in list_attributov:
            searching_for_food = jedlo_sql.query.all()

        else:
            for a in list_attributov:
                if a == kategoria:
                    searching_for_food = jedlo_sql.query.filter_by(attribute=a).all()

        list1 = []
        list2 = []
        y = 0
        for x in searching_for_food:
            if y % 2 == 0:
                list1.append(x)
            elif y % 2 == 1:
                list2.append(x)
            y += 1

        respond = make_response(render_template('zoznam.html',
                                list1=list1,
                                list2=list2))
        return respond

    elif request.method == 'POST':
        print(request.form['btn'])
        list_set_category = ['set_category_all',
                             'set_category_ranajky',
                             'set_category_obed',
                             'set_category_vecera',
                             'set_category_dezert']
        list_attributov = ['vsetko',
                           'ranajky',
                           'obed',
                           'vecera',
                           'dezert']

        if request.form['btn'] == "DOMOV":
            respond = make_response(redirect(url_for('home')))
            return respond

        elif request.form['btn'] == "ONAS":
            return "nefunguje"

        elif request.form['btn'] in list_set_category:
            for a in range(0, len(list_attributov)):
                if request.form['btn'] == list_set_category[a]:
                    session['zoznam_kategoria'] = list_attributov[a]
            respond = make_response(redirect(url_for('zoznam')))
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
            all_food = jedlo_sql.query.all()
            for a in all_food:
                loopdata.append(a.nazov)
                pocetjedal += 1
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
            insert_all_func()
            respond = render_template('justadminthings.html', cosatodeje='PREPISANE DO DATABAZY')
            return respond

        elif request.form['btn'] == 'Vymazat vsetko z databazy':
            drop_func()
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
