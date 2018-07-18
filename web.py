from flask import Flask, request, g, render_template
from Registry import V2
import os

app = Flask(__name__)

host = os.getenv("HOST")
port = os.getenv("PORT")
user = os.getenv("USER")
passwd = os.getenv('PASSWD')

if __name__ == '__main__':
    host = '172.16.0.36'
    port = '5000'
    user = 'admin'
    passwd = 'admin'

url = "http://" + host + ":" + port


@app.before_request
def connect():
    g.reg = V2(url, user=user, password=passwd)


@app.route('/')
def index():
    if g.reg._ping() == 'OK':
        return render_template('index.html', data=g.reg.retag())
    else:
        return "Failed to access registry", 502


@app.route('/tags/<repository>')
def tags(repository):
    new_repository = repository.replace('%', '/')
    data = []
    for tag in g.reg.tags(new_repository):
        data.append(g.reg.digest(new_repository, tag))
    return render_template('index.html', repository=repository, info=data)


@app.route('/tags/<repository>/<reference>')
def delete(repository, reference):
    if g.reg.delete(repository, reference):
        return tags(repository)
    else:
        return render_template('error.html', repository=repository, error='error or not exist')


app.debug = False
app.run(host='0.0.0.0', port=8080)
