from flask import Flask, jsonify
from application.request_car import request_car
from tests.test_response import RES

app = Flask(__name__)

@app.route("/<license_plate>")
def get_license_plate(license_plate):
    """Returns the requested car details

    :param license_plates: Requested license plate
    """
    with app.app_context():
        if license_plate.lower() == "test111":
            # time.sleep(1)
            return jsonify(RES)
        return_data = request_car([license_plate])
        return jsonify(return_data)

if __name__ == '__main__':
    app.run(debug=False, host="127.0.0.1", port=3001)
#     get_license_plate("aAKb294")
#     get_license_plate("gsm140")
#     get_license_plate("HKL138")
# To run it not as an API server, uncomment one of these lines and run it from the IDE
