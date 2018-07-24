FROM clibing/armhf-python-flask:2.7

MAINTAINER clibing <wmsjhappy@gmail.com>

ADD . /webapp/

WORKDIR /webapp

EXPOSE 8080/tcp

CMD ["/usr/bin/python","web.py"]
