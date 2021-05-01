from flask import Flask, jsonify

app = Flask(__name__)


@app.route('/')
def health_check():
    return jsonify(
        {
            'message': 'I am healthy!'
        }
    )



