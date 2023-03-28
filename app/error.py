from flask import jsonify
from app import app


@app.errorhandler(400)
def bad_request__error(exception):
    return jsonify(
        {
            "Message": "Sorry you entered wrong values kindly check and resend!"
        },
        {
            "status": 400
        }
    )


@app.errorhandler(401)
def internal_error(error):
    return jsonify(
        {
            "Message": "Access denied ! please register and login to generate API KEY"
        },
        {
            "status": 401
        }
    )


@app.errorhandler(404)
def not_found_error(error):
    return jsonify(
        {
            "Message": "Sorry the page your are looking for is not here kindly go back"
        },
        {
            "status": 404
        }
    )


@app.errorhandler(405)
def method_not_allowed(error):
    return jsonify(
        {
            "Message": "Sorry the requested method is not allowed kindly check and resend !"
        },
        {
            "status": 405
        }
    )


@app.errorhandler(500)
def method_not_allowed(error):
    return jsonify(
        {
            "Message": "Bad request please check your input and resend !"
        },
        {
            "status": 500
        }
    )
