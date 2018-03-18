from flask import request, render_template, redirect, url_for, session, make_response
import os
import json
import random
from sql_table_maker import db, app, jedlo_sql, docastne_jedlo_sql, insert_one_func
from sqlalchemy import exc


db.create_all()


def whole_db_search():
    
    try:
        pocetjedal = 0
        jat_all_food = []

        all_food = jedlo_sql.query.all()
        for a in all_food:
            jat_all_food.append(a)
            pocetjedal += 1
        return jat_all_food
    
    except exc.SQLAlchemyError:
        return None


def whole_db_temporary_search():
    
    try:
        pocet_temporary_jedal = 0
        jat_all_temporaryfood = []
    
        all_food = docastne_jedlo_sql.query.all()
        for a in all_food:
            jat_all_temporaryfood.append(a)
            pocet_temporary_jedal += 1
        return jat_all_temporaryfood
    except exc.SQLAlchemyError:
        return None


@app.before_request
def make_session_permanent():
    session.permanent = True


@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'GET':
        session['kategoria'] = None
        return render_template('layout.html',
                               html_layout=True)

    elif request.method == 'POST':
        list_random_kategorie = ['ranajky_random',
                                 'obed_random',
                                 'vecera_random',
                                 'dezert_random']

        list_kategorie = ['ranajky',
                          'obed',
                          'vecera',
                          'dezert']

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

        elif request.form['btn'] == "PRIDAVANE":
            respond = make_response(redirect(url_for('pridavanie')))
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

        if kategoria == 'everything':
            aktualne_jedlo_nerandom = jedlo_sql.query.all()
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
        list_random_kategorie = ['ranajky_random',
                                 'obed_random',
                                 'vecera_random',
                                 'dezert_random']
        
        list_kategorie = ['ranajky',
                          'obed',
                          'vecera',
                          'dezert']
        
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
        list_attributov = ['ranajky',
                           'obed',
                           'vecera',
                           'dezert']
        
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
                                                list2=list2,
                                                whats_showing = kategoria.upper()))
        return respond

    elif request.method == 'POST':
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


@app.route('/pridavanie', methods=['GET', 'POST'])
def pridavanie():
    if request.method == 'GET':
        respond = make_response(render_template('pridavanie.html',
                                                 cosadeje="Vase kulinarske zazitky."))
        return respond

    elif request.method == 'POST':
        if request.form['btn'] == 'button_confirm':
            docastne_nazov = request.form['input_name']
            docastne_link = request.form['input_link']
            docastne_kategoria = request.form['select_category']

            len_nazov = len(docastne_nazov)
            len_link = len(docastne_link)
            print(f"{len_nazov} {len_link} {docastne_kategoria}")
            if len_nazov == 0 or len_link == 0 or docastne_kategoria == "None":
                respond = make_response(render_template('pridavanie.html',
                                                         cosadeje="Nezadal si to spravne"))
                return respond

            jedlo_pridavane = docastne_jedlo_sql(nazov=docastne_nazov,
                                                 attribute=docastne_kategoria,
                                                 link=docastne_link)
            db.session.add(jedlo_pridavane)
            db.session.commit()
            respond = make_response(redirect(url_for('home')))
            return respond


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        respond = render_template('login.html')
        session['password'] = None
        return respond

    elif request.method == 'POST':
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
            jat_all_food = whole_db_search()
            jat_all_temporaryfood = whole_db_temporary_search()
            print(jat_all_temporaryfood)
            print(len(jat_all_temporaryfood))

            docastne = ""
            if len(jat_all_temporaryfood) > 0:
                docastne = "DOCASTNE"

            respond = render_template('justadminthings.html',
                                      jat_all_food=jat_all_food,
                                      jat_all_temporaryfood=jat_all_temporaryfood,
                                      DOCASTNE=docastne)
            return respond
        else:
            respond = redirect(url_for('home'))
            return respond

    elif request.method == 'POST':
        if request.form['btn'] == 'Vymazat databazu navrhovanych jedal':
            docastne_jedlo_sql.query.delete()
            db.session.commit()
            jat_all_food = whole_db_search()
            jat_all_temporaryfood = whole_db_temporary_search()

            docastne = ""
            if len(jat_all_temporaryfood) > 0:
                docastne = "DOCASTNE"

            respond = render_template('justadminthings.html',
                                      jat_all_food=jat_all_food,
                                      jat_all_temporaryfood=jat_all_temporaryfood,
                                      DOCASTNE=docastne,
                                      cosatodeje='VSETKO DOCASTNE VYMAZANE')

            return respond

        elif request.form['btn'][:8] == 'all_food':
            jedlo_ktore_chcem_vymazat = jedlo_sql.query.filter_by(nazov=request.form['btn'][8:]).first()
            nazov_jedlo_ktore_chcem_vymazat = jedlo_ktore_chcem_vymazat.nazov
            db.session.delete(jedlo_ktore_chcem_vymazat)
            db.session.commit()
            jat_all_food = whole_db_search()
            jat_all_temporaryfood = whole_db_temporary_search()

            docastne = ""
            if len(jat_all_temporaryfood) > 0:
                docastne = "DOCASTNE"

            respond = render_template('justadminthings.html',
                                      jat_all_food=jat_all_food,
                                      jat_all_temporaryfood=jat_all_temporaryfood,
                                      DOCASTNE=docastne,
                                      cosatodeje=('USPESNE VYMAZANE : ' + nazov_jedlo_ktore_chcem_vymazat))

            return respond

        elif request.form['btn'][:8] == 'temporar':
            print(request.form['btn'][8:12])
            if request.form['btn'][8:12] == '_add':
                jedlo_ktore_chcem_pridat = docastne_jedlo_sql.query.filter_by(nazov=request.form['btn'][12:]).first()
                nazov_jedlo = jedlo_ktore_chcem_pridat.nazov
                attribute_jedlo = jedlo_ktore_chcem_pridat.attribute
                link_jedlo = jedlo_ktore_chcem_pridat.attribute
                insert_one_func(nazov_jedlo, attribute_jedlo, link_jedlo)
                cosatodeje = f"{nazov_jedlo} pridane do databazy"

            elif request.form['btn'][8:12] == '_del':
                jedlo_ktore_chcem_pridat = docastne_jedlo_sql.query.filter_by(nazov=request.form['btn'][12:]).first()
                nazov_jedlo = jedlo_ktore_chcem_pridat.nazov
                cosatodeje = f"{nazov_jedlo} vymazane z docastnej databazy"

            jedlo_ktore_chcem_vymazat = docastne_jedlo_sql.query.filter_by(nazov=request.form['btn'][12:]).first()
            nazov_jedlo_ktore_chcem_vymazat = jedlo_ktore_chcem_vymazat.nazov
            db.session.delete(jedlo_ktore_chcem_vymazat)
            db.session.commit()
            jat_all_food = whole_db_search()
            jat_all_temporaryfood = whole_db_temporary_search()

            docastne = ""
            if len(jat_all_temporaryfood) > 0:
                docastne = "DOCASTNE"

            respond = render_template('justadminthings.html',
                                      jat_all_food=jat_all_food,
                                      jat_all_temporaryfood=jat_all_temporaryfood,
                                      DOCASTNE=docastne,
                                      cosatodeje=cosatodeje)

            return respond


app.secret_key = os.environ["SESSION_KEY"]


if __name__ == '__main__':
    app.run(debug=True, use_reloader=True)
