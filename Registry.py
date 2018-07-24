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
        req = urllib2.Request(self.url + '/' + response + '/tags/list', headers=self.headers)
        r = urllib2.urlopen(req)
        tags = json.loads(r.read())
        return tags['tags']

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
            re_tags[i] = self.tags(i)
        return re_tags

    def delete(self, repository, reference):
        req = urllib2.Request(self.url + '/' + repository + '/manifests/' + reference.replace(':', '%3a'),
                              headers=self.headers)
        req.get_method = lambda: 'DELETE'
        try:
            r = urllib2.urlopen(req)
            if r.getCode() == 202:
                return True
            return False
        except Exception as e:
            print("delete image is exception: %s", e)
            return None
