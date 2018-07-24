from flask import Flask, request, g, render_template
from Registry import V2
import os

app = Flask(__name__)

host = os.getenv("HOST")
port = os.getenv("PORT", "5000")
user = os.getenv("USER")
passwd = os.getenv('PASSWD')
debug = os.getenv('DEBUG', False)
uri = "%s:%s" % (host, port)
app.debug = debug


@app.before_request
def connect():
    url = "http://" + host + ":" + port
    g.reg = V2(url, user=user, password=passwd, debug=app.debug)


@app.route('/')
def index():
    if g.reg._ping() == 'OK':
        return render_template('index.html', data=g.reg.retag())
    else:
        return "Failed to access registry", 502


@app.route('/tags')
def tags():
    repository = request.args.get('repository')
    data = []
    for tag in g.reg.tags(repository):
        data.append(g.reg.digest(repository, tag))
    return render_template('index.html', repository=repository, info=data, uri=uri)


@app.route('/delete')
def delete():
    repository = request.args.get('repository')
    reference = request.args.get('reference') 
    if g.reg.delete(repository, reference):
        return tags(repository)
    else:
        return render_template('error.html', repository=repository, error='error or not exist')


def replace_backslash(value):
    if value:
        return str(value).replace('/', '%2f')
    return value


app.add_template_filter(replace_backslash, 'replace_backslash')
app.logger.debug("app.root_path: %s" % app.root_path)
app.run(host='0.0.0.0', port=8080)
