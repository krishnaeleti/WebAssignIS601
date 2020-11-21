from typing import List, Dict
import simplejson as json
import mysql.connector
from flask import Flask, request, Response, redirect
from flask import render_template

app = Flask(__name__)
user = {'username': 'Krishna Eleti'}

class MyDb:
    def __init__(self):
        config = {
            'user': 'root',
            'password': 'root',
            'host': 'db',
            'port': '3306',
            'database': 'snakesData'
        }
        self.connection = mysql.connector.connect(**config)

    def closeDb(self):
        self.connection.close()

    def get_alldata(self):
        cursor = self.connection.cursor(dictionary=True)
        cursor.execute('SELECT * FROM snakes')
        return cursor.fetchall()

    def get_rating(self, rating_id):
        cursor = self.connection.cursor(dictionary=True)
        cursor.execute('SELECT * FROM snakes WHERE id=%s', (rating_id,))
        result = cursor.fetchall()
        return result[0]

    def update_rating(self, inputData):
        cursor = self.connection.cursor(dictionary=True)
        sql_update_query = """UPDATE snakes t SET t.Game_Number = %s, t.Game_Length = %s """
        cursor.execute(sql_update_query, inputData)
        self.connection.commit()

    def insert_rating(self, inputData):
        cursor = self.connection.cursor(dictionary=True)
        sql_insert_query = """INSERT INTO snakes (`Game_Number`,Game_Length) VALUES (%s, %s) """
        cursor.execute(sql_insert_query, inputData)
        self.connection.commit()

    def delete_rating(self, snakes_id):
        cursor = self.connection.cursor(dictionary=True)
        sql_delete_query = """DELETE FROM snakes WHERE id = %s """
        cursor.execute(sql_delete_query, (snakes_id,))
        self.connection.commit()


db = MyDb()


@app.route('./app./templates./index.html')
def index():
    snakes = db.get_alldata()
    return render_template("index.html", title='Home', user=user, snakes=snakes)

@app.route('./app./templates./view.html./<int:snakes_id>', methods=['GET'])
def record_view(snakes_id):
    snakes = db.get_rating(snakes_id)
    return render_template('view.html', title='View Form', user=user, snakes=snakes)


@app.route('./edit./<int:snakes_id>', methods=['GET'])
def form_edit_get(snakes_id):
    snakes = db.get_snakes(snakes_id)
    return render_template('edit.html', title='Edit Form', user=user, snakes=snakes)


@app.route('/edit/<int:snakes_id>', methods=['POST'])
def form_update_post(snakes_id):
    inputData = (request.form.get('Game_Number'), request.form.get('Game_Length'), snakes_id)
    db.update_snakes(inputData)
    return redirect("/", code=302)

@app.route('/rating/new', methods=['GET'])
def form_insert_get():
    return render_template('new.html', title='New Rating Form', user=user)


@app.route('/rating/new', methods=['POST'])
def form_insert_post():
    inputData = (request.form.get('Game_Number'), request.form.get('Game_Length'))
    db.insert_snakes(inputData)
    return redirect("/", code=302)

@app.route('/delete/<int:rating_id>', methods=['POST'])
def form_delete_post(snakes_id):
    db.delete_snakes(snakes_id)
    return redirect("/", code=302)


# API v1

@app.route('/api/v1/ratings')
def api_ratings() -> str:
    js = json.dumps(db.get_alldata())
    resp = Response(js, status=200, mimetype='application/json')
    return resp

@app.route('/api/v1/ratings/<int:rating_id>', methods=['GET'])
def api_retrieve(rating_id) -> str:
    result = db.get_rating(rating_id)
    json_result = json.dumps(result)
    resp = Response(json_result, status=200, mimetype='application/json')
    return resp

@app.route('/api/v1/ratings/', methods=['POST'])
def api_add() -> str:
    inputData = (request.form.get('Year'), request.form.get('Score'), request.form.get('Title'))
    db.insert_rating(inputData)
    resp = Response(status=200, mimetype='application/json')
    return resp


@app.route('/api/v1/ratings/<int:rating_id>', methods=['PUT'])
def api_edit(rating_id) -> str:
    inputData = (request.form.get('Year'), request.form.get('Score'), request.form.get('Title'), rating_id)
    db.update_rating(inputData)
    resp = Response(status=201, mimetype='application/json')
    return resp


@app.route('/api/ratings/<int:rating_id>', methods=['DELETE'])
def api_delete(rating_id) -> str:
    db.delete_rating(rating_id)
    resp = Response(status=210, mimetype='application/json')
    return resp




if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True) # set debug=False on deployment
