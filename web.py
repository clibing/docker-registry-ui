# -*- coding: utf-8 -*-

from flask import Flask, request, g, render_template, redirect, url_for
from Registry import V2
import os
import time

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
        return render_template('index.html', data=g.reg.repository_tags())
    else:
        return "Failed to access registry", 502


@app.route('/tags')
def tags():
    repository = request.args.get('repository')
    data = []
    tag_list = g.reg.tags(repository)
    if tag_list:
        for tag in tag_list:
            data.append(g.reg.digest(repository, tag))
        return render_template('index.html', repository=repository, info=data, uri=uri)
    else:
        return render_template('redirect.html', error="the repository %s is deleted, cache hit" % repository,
                               danger=True, url="/", timeout=3)


@app.route('/delete')
def delete():
    repository = request.args.get('repository')
    tag = request.args.get('tag')
    result = g.reg.delete(repository, tag)
    status = result[0]
    message = result[1]
    if status:
        time.sleep(1)
        red_uri = "/tags?repository=%s" % (replace_backslash(repository))
        return render_template('redirect.html', error="delete success, auto jump", url=red_uri, danger=False, timeout=1)
    else:
        return render_template('redirect.html', error=message, url="/", danger=True, timeout=3)


def replace_backslash(value):
    if value:
        return str(value).replace('/', '%2f')
    return value


app.add_template_filter(replace_backslash, 'replace_backslash')
app.logger.debug("app.root_path: %s" % app.root_path)
app.run(host='0.0.0.0', port=8080)
