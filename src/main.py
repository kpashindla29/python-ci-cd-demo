
from flask import Flask, jsonify

app = Flask(__name__)


def add(a, b):
    return a+b

def subtract(a, b):
    return a-b



@app.route('/')
def welcome():
    return jsonify({
        "message": "Welcome to my Python Application!",
        "status": "Success",
        "service": "flask-app"
    })

@app.route('/health')
def health_check():
    return jsonify({"status": "healthy"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=False)