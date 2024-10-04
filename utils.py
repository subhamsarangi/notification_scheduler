import traceback
import logging
from functools import wraps
from flask import jsonify

# Set up logging
logging.basicConfig(level=logging.ERROR)


def handle_exceptions(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception as e:
            logging.error(traceback.format_exc())
            return jsonify({"error": "An unexpected error occurred."}), 500

    return decorated_function
