# Garden Irrigation System API

RESTful API for controlling and monitoring a garden irrigation system.

## Requirements

- Python 3.9/10.x
- Flask
- MySQL Connector/Python
- jsonpickle
- flask-cors
- Configured MySQL database

## Usage

1. Send POST requests to `/mainview` to add sensor data.
2. Send GET requests to `/mainview` to retrieve sensor data.
3. Send POST requests to `/mode` to set the operating mode.
4. Send GET requests to `/mode` to retrieve the current operating mode.
5. Send POST requests to `/threshold` to set the manual threshold.
6. Send GET requests to `/threshold` to retrieve the current manual threshold.
7. Send POST requests to `/sprinkler` to toggle the sprinkler state.

## API Endpoints

- `POST /mainview`: Add sensor data.
- `GET /mainview`: Retrieve sensor data.
- `POST /mode`: Set the operating mode.
- `GET /mode`: Retrieve the current operating mode.
- `POST /threshold`: Set the manual threshold.
- `GET /threshold`: Retrieve the current manual threshold.
- `POST /sprinkler`: Toggle the sprinkler state.

## Author

- Agata Krześniak


## Additional Information

- This project was created for the subject 'Sensors in Embedded Applications'.
