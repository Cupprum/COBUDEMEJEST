from flask import Flask, request, render_template, redirect, url_for
import psycopg2
import os
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
        if request.form['btn'] == 'layout':
            return redirect(url_for('jedlo'))


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
        print('split', nazov)
        return render_template('jedlo.html', nazov=nazov, attribute=attribute, link=link)
    elif request.method == 'POST':
        if request.form['btn'] == 'nove jedlo':
            return redirect(url_for('jedlo'))
        elif request.form['btn'] == 'home':
            return redirect(url_for('home'))


if __name__ == '__main__':
    app.run(debug=True, use_reloader=True)
