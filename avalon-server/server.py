from flask import Flask

app = Flask(__name__)

@app.route('/avalon')
def avalon():
    return {'merciful': 'merceval'}
