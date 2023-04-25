from flask import Flask, jsonify
from .request_car import request_car

app = Flask(__name__)

@app.route("/<license_plate>")
def get_license_plate(license_plate):
    try:
        message = request_car([license_plate])
        status = 'success'
    except Exception as exc:
        status = 'fail'
        message = exc
    return jsonify({
        'status:': status,
        'message': message
    })

# if __name__ == '__main__':
#     get_license_plate("yas")