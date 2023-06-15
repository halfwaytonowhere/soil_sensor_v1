import mysql.connector
from flask import Flask
from flask import jsonify
from flask import request
from flask import Response
import jsonpickle
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

class SensorData:
    def __init__(self, sensor_id, humidity, is_sensor_on, sprinkler_state=None):
        self.sensor_id = sensor_id
        self.humidity = humidity
        self.is_sensor_on = is_sensor_on
        self.sprinkler_state = sprinkler_state

    def to_dict(self):
        return {"sensor_id": self.sensor_id, "humidity": self.humidity, "is_sensor_on": self.is_sensor_on, "sprinkler_state": self.sprinkler_state}
    
isAutomaticMode = True
manual_threshold = None

app = Flask(__name__)

@app.route('/mainview', methods=['GET'])
def get_sensor_data():
    global isAutomaticMode, manual_threshold
    try:
        connection = get_connection_()
        cursor = connection.cursor(dictionary=True)
        query = """
        (SELECT sensor_id, humidity, is_sensor_on, sprinkler_state FROM swawapi.sensor_data WHERE sensor_id = 1 ORDER BY created_at DESC LIMIT 1)
        UNION
        (SELECT sensor_id, humidity, is_sensor_on, sprinkler_state FROM swawapi.sensor_data WHERE sensor_id = 2 ORDER BY created_at DESC LIMIT 1)
        """
        cursor.execute(query)
        rows = cursor.fetchall()
        sensor_data = []
        for row in rows:
            sensor_data.append(SensorData(row['sensor_id'], row['humidity'], row['is_sensor_on'], row['sprinkler_state']))
#        sprinkler_value = rows[-1]['sprinkler']
        connection.close()

        watering_process_value = 0
        error_msg = None

        if sensor_data[0].is_sensor_on == 1 and sensor_data[1].is_sensor_on == 1:
            if sensor_data[0].humidity is not None and sensor_data[1].humidity is not None:
                if isAutomaticMode:
                    if sensor_data[0].humidity < 40 and sensor_data[1].humidity < 40:
                        watering_process_value = 1
                    elif sensor_data[0].humidity < 30 or sensor_data[1].humidity < 30:
                        watering_process_value = 1
                else:
                    if manual_threshold is None:
                        return jsonify(error='Wprowadz prog nawadniania'), 400
                    if sensor_data[0].humidity < manual_threshold and sensor_data[1].humidity < manual_threshold:
                        watering_process_value = 1
                    elif sensor_data[0].humidity < (manual_threshold - 10) or sensor_data[1].humidity < (manual_threshold - 10):
                        watering_process_value = 1

        elif sensor_data[0].is_sensor_on == 1:
            if sensor_data[0].humidity is not None:
                if isAutomaticMode:
                    if sensor_data[0].humidity < 40:
                        watering_process_value = 1
                else:
                    if manual_threshold is None:
                        return jsonify(error='Wprwoadz prog nawadniania'), 400
                    elif sensor_data[0].humidity < manual_threshold:
                        watering_process_value = 1

        elif sensor_data[1].is_sensor_on == 1:
            if sensor_data[1].humidity is not None:
                if isAutomaticMode:
                    if sensor_data[1].humidity < 40:
                        watering_process_value = 1
                else:
                    if manual_threshold is None:
                        return jsonify(error='Wprowadz prog nawadniania'), 400
                    elif sensor_data[1].humidity < manual_threshold:
                        watering_process_value = 1


        if sensor_data[0].humidity is None and sensor_data[1].humidity is None:
            error_msg = "Humidity values for both sensors are missing"
        elif sensor_data[0].humidity is None:
            error_msg = f"Humidity value for sensor {sensor_data[0].sensor_id} is missing"
        elif sensor_data[1].humidity is None:
            error_msg = f"Humidity value for sensor {sensor_data[1].sensor_id} is missing"
        elif sensor_data[0].humidity < 10:
            error_msg = f"Humidity value for sensor {sensor_data[0].sensor_id} is below 10"
        elif sensor_data[1].humidity < 10:
            error_msg = f"Humidity value for sensor {sensor_data[1].sensor_id} is below 10"


        sensor_data_dicts = [data.to_dict() for data in sensor_data]
        response_data = {"sensor_data": sensor_data_dicts, "watering_process": watering_process_value, "sprinkler_state": sensor_data[-1].sprinkler_state, "error_message": error_msg}
        return jsonify(response_data)

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

    resp = Response(jsonpickle.encode(sensor_data, unpicklable=False), mimetype='application/json')
    return resp, 201

@app.route('/mode', methods=['POST'])
def set_mode():
    global isAutomaticMode
    request_data = request.get_json()
    isAutomaticMode = request_data['isAutomaticMode']
    return_data = { "AutomaticMode" : isAutomaticMode}
    return jsonify(return_data), 200

######################################################################################
# --------------------------------------------------------------------------------------------------
#    Sprawdzenie za pomocą GET czy AutomaticMode ustawił sie według żądania POST
# --------------------------------------------------------------------------------------------------
@app.route('/mode', methods=['GET'])
def get_mode():
    global isAutomaticMode
    return_data = { "AutomaticMode" : isAutomaticMode}
    return jsonify(return_data)
######################################################################################

@app.route('/threshold', methods=['POST'])
def set_threshold():
    global manual_threshold
    if 'manual_threshold' not in globals():
        manual_threshold = None
    manual_threshold = request.json['threshold']
    return 'Manual threshold : {}'.format(manual_threshold)

######################################################################################
# --------------------------------------------------------------------------------------------------
#    Sprawdzenie za pomocą GET czy threshold ustawił według żądania POST
# --------------------------------------------------------------------------------------------------
@app.route('/threshold', methods=['GET'])
def get_threshold():
    global manual_threshold
    return 'Manual threshold : {}'.format(manual_threshold)
######################################################################################

@app.route('/sprinkler', methods=['POST'])
def sprinkler_toggle():
    data = request.get_json()
    if 'sprinkler_on' not in data:
        return jsonify(error='Missing parameters'), 400

    connection = get_connection_()
    cursor = connection.cursor()
    query = """
        UPDATE sensor_data SET sprinkler_state=%s
        WHERE sensor_id IN (1, 2)
    """
    cursor.execute(query, [int(data['sprinkler_on'])])
    connection.commit()
    connection.close()

    return jsonify(success=True), 200

app.run(debug=True, host='0.0.0.0')
