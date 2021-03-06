#!/usr/bin/python
# -*- coding:UTF-8 -*-

import base64
import datetime
import json
import time
import urllib2

BASE_CONTENT_TYPE = 'application/vnd.docker.distribution.manifest'


class V2(object):
    # Connect Private Registry Restful API v2
    def __init__(self, url, user=None, password=None, debug=False):
        # url: Registry Service URL
        # user: Basic Authorization User,default None
        # password: Basic Authorization Password,default None

        self.url = url + '/v2'
        self.__debug = debug
        self.__schema = BASE_CONTENT_TYPE + '.v2+json'
        if user and password:
            secret = base64.encodestring("%s:%s" % (user, password))
            secret = secret.replace('\n', '')
            self.headers = {
                'Authorization': 'Basic %s' % secret
            }

    def _ping(self):
        try:
            req = urllib2.Request(self.url, headers=self.headers)
            urllib2.urlopen(req)
            return 'OK'
        except Exception as e:
            if self.__debug:
                print("exception when ping url: %s, the execption: %s" % (self.url, e))
            return 'Error'

    def catalog(self):
        req = urllib2.Request(self.url + "/_catalog", headers=self.headers)
        r = urllib2.urlopen(req)
        repos = json.loads(r.read())
        return repos['repositories']

    def tags(self, response):
        try:
            req = urllib2.Request(self.url + '/' + response + '/tags/list', headers=self.headers)
            r = urllib2.urlopen(req)
            tags = json.loads(r.read())
            return tags['tags']
        except Exception as e:
            return None

    def add_schema(self):
        self.headers['Accept'] = self.__schema

    def remove_schema(self):
        self.headers.pop('Accept')

    def digest(self, response, tag):
        re_data = {}
        req = urllib2.Request(self.url + '/' + response + '/manifests/' + tag, headers=self.headers)
        try:
            r = urllib2.urlopen(req)
            html = json.loads(r.read())
            size = 0
            for i in html['history']:
                if 'Size' in json.loads(i['v1Compatibility']):
                    size += json.loads(i['v1Compatibility'])['Size']

            re_data['tag'] = tag
            v1_compatibility = json.loads(html['history'][0]['v1Compatibility'])
            re_data['id'] = v1_compatibility['id'][:13]
            created_time = v1_compatibility['created']
            created_time = created_time[:-4]
            created_time = datetime.datetime.strptime(created_time, "%Y-%m-%dT%H:%M:%S.%f")
            created_time = created_time - datetime.timedelta(0, time.timezone)
            re_data['created'] = created_time.strftime("%Y-%m-%d %H:%M:%S")
            re_data['fslayers'] = len(html['fsLayers'])
            if size == 0:
                size = self.layers_size(response, tag)
            re_data['size'] = size / 1024 / 1024
            re_data['digest'] = r.headers['Docker-Content-Digest']
            return re_data
        except Exception as e:
            if self.__debug:
                print("cause exception when digest the response: %s, the tag: %s, detail execption: %s" % (
                    response, tag, e))
            return None

    def repository_tags(self):
        re_tags = {}
        for i in self.catalog():
            re_tag = self.tags(i)
            if re_tag:
                re_tags[i] = re_tag
            else:
                continue

        return re_tags

    def delete(self, repository, tag):
        self.add_schema()
        try:
            req = urllib2.Request(self.url + '/' + repository + '/manifests/' + tag, headers=self.headers)
            r = urllib2.urlopen(req)
            digest = r.headers['docker-content-digest']
        except Exception as e:
            if e.code == 404:
                return False, "the %s:%s not found, may be deleted" % (repository, tag)
            else:
                return False, "get %s:%s digest is error, the code: %s" % (repository, tag, e.code)
        finally:
            self.remove_schema()

        # send DELETE the image
        req = urllib2.Request(self.url + '/' + repository + '/manifests/' + digest, headers=self.headers)
        req.get_method = lambda: 'DELETE'
        try:
            r = urllib2.urlopen(req)
            if r.code == 202:
                return True, "delete will take time"
            return False, "the code：%s" % r.code
        except Exception as e:
            return False, "delete image is exception, the code: %s" % e.code

    def layers_size(self, repository, tag):
        self.add_schema()
        try:
            req = urllib2.Request(self.url + '/' + repository + '/manifests/' + tag, headers=self.headers)
            r = urllib2.urlopen(req)
            layers = json.loads(r.read())
            size = 0
            for layer in layers['layers']:
                size += layer['size']
            size += layers['config']['size']
            return size
        except Exception as e:
            return 0
        finally:
            self.remove_schema()