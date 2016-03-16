from flask import Flask, request, g, render_template
from Registry import V2
import os

app = Flask(__name__)

host = os.getenv("HOST")
port = os.getenv("PORT")
user = os.getenv("USER")
passwd = os.getenv('PASSWD')

url = "http://" + host + ":" + port

@app.before_request
def connect():
    g.reg = V2(url, user = user, password = passwd )

@app.route('/')
def index():
    if g.reg._ping() == 'OK':
        return render_template('index.html', data = g.reg.retag())
    else:
        return "Failed to access registry", 502

@app.route('/tags/<repository>')
def tags(repository):
    repository = repository.replace('%','/')
    data = []
    for tag in g.reg.tags(repository):
        data.append(g.reg.digest(repository, tag))
    return render_template('index.html', repository = repository, info = data)

app.debug = True
app.run()