import mysql.connector 
from flask import Flask
from flask import jsonify
from flask import request
from flask import Response
import jsonpickle
import requests
import logging


logging.basicConfig(filename='app.log', level=logging.DEBUG)


def get_connection_():
    connection = mysql.connector.connect(
            user = 'root',
            password ='localhost',
            host = '127.0.0.1',
            database = 'swawapi'
)

    return connection

def watering_process(on_off):
    data = {'watering_process': on_off}
    url ="http://(...)/"
    headers = {'Content-Type': 'application/json'}
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        print("Nawadnianie")
    else:
        print("Nie udalo sie")


class SensorData:
    def __init__(self, sensor_id,  humidity, is_sensor_on):
        self.sensor_id = sensor_id
        self.humidity = humidity
        self.is_sensor_on = is_sensor_on

isAutomaticMode = True
manual_threshold = None

app = Flask(__name__)

@app.route('/mainview', methods=['GET'])
def get_sensor_data():
    global isAutomaticMode, manual_threshold
    sensor_data = []
    try:
        connection = get_connection_()
        cursor= connection.cursor(dictionary=True)
        query = """
        (SELECT sensor_id, humidity, is_sensor_on FROM swawapi.sensor_data WHERE sensor_id = 1 ORDER BY created_at DESC LIMIT 1)
        UNION
        (SELECT sensor_id, humidity, is_sensor_on FROM swawapi.sensor_data WHERE sensor_id = 2 ORDER BY created_at DESC LIMIT 1)
                """
        cursor.execute(query)
        rows = cursor.fetchall()
        for row in rows:
            sensor_data.append(SensorData(row['sensor_id'], row['humidity'], row['is_sensor_on']))
        connection.close()

        if isAutomaticMode:
            if sensor_data[0].humidity < 40 and sensor_data[1].humidity < 40:
                watering_process(1)
            elif sensor_data[0].humidity < 30 or sensor_data[1].humidity < 30:
                watering_process(1)
        elif not isAutomaticMode:
            if sensor_data[0].humidity < manual_threshold or sensor_data[1].humidity < manual_threshold:
                watering_process(1)
            elif sensor_data[0].humidity < (manual_threshold-10) or sensor_data[1].humidity < (manual_threshold-10):
                watering_process(1)
    

        resp=Response(jsonpickle.encode(sensor_data, unpicklable=False), mimetype='application/json')
        return resp
     
    except mysql.connector.Error as err:
        logging.error(f'Błąd w połączeniu z bazą danych: {err}')
        return jsonify({'results': 'Nie udało się połączyć z bazą danych.'}), 500


@app.route('/mainview', methods=['POST'])
def add_sensor_data():
    request_data = request.get_json()
    if 'sensor_id' not in request_data or 'humidity' not in request_data or 'is_sensor_on' not in request_data:
        return jsonify(error='Missing parameters'), 400
    
    try:
        connection = get_connection_()
        cursor = connection.cursor()
        query = """INSERT INTO sensor_data (sensor_id, humidity, is_sensor_on) VALUES (%s, %s, %s)"""
        cursor.execute(query, (request_data['sensor_id'], request_data['humidity'], request_data['is_sensor_on']))
        connection.commit()
        sensor_data = SensorData(request_data['sensor_id'], request_data['humidity'], request_data['is_sensor_on'])
        connection.close()

    except mysql.connector.Error as error:
        return jsonify(error=error.msg), 400
    # sensor_data = [SensorData(humidity, is_sensor_on)]

    resp = Response(jsonpickle.encode(sensor_data, unpicklable=False), mimetype='application/json')
    return resp, 201

@app.route('/mode', methods=['POST'])
def set_mode():
    global isAutomaticMode
    request_data = request.get_json()
    isAutomaticMode = request_data['isAutomaticMode']
    return jsonify(results='Mode set to ' + str(isAutomaticMode)), 200

@app.route('/threshold', methods=['POST'])
def set_threshold():
    global manual_threshold
    if 'manual_threshold' not in globals():
        manual_threshold = None
    manual_threshold = request.json['threshold']
    return 'Manual threshold set to {}'.format(manual_threshold)

@app.route('/sprinkler', methods=['POST'])
def sprinkler():
    data = request.get_json()
    if 'sprinkler_on_off' not in data:
        return jsonify(error='Missing parameters'), 400
    
    url = "http://(...)/"
    headers = {'Content-Type': 'application/json'}
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        return jsonify(success=True), 200
    else:
        return jsonify(error='Failed to send sprinkler request'), 500

app.run(debug=True, host='0.0.0.0')
