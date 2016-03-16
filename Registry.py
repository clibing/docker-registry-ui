#!/usr/bin/python
# -*- coding:UTF-8 -*-

import urllib2, json, base64, datetime, time

class V2(object):
    '''
    Connect Private Registry Restful API v2
    '''
    def __init__(self, url, user = None, password = None):
        '''
        url: Registry Service URL
        user: Basic Authorization User,default None
        pasword: Basic Authorization Password,default None
        '''
        self.url = url+'/v2'
        if user and password:
            secret = base64.encodestring("%s:%s" % (user,password))
            secret = secret.replace('\n','')
            self.headers = {
                                'Authorization':'Basic %s' %secret
                            }

    def _ping(self):
        try:
            req = urllib2.Request(self.url,headers = self.headers)
            r = urllib2.urlopen(req)
            return 'OK'
        except:
            return 'Error'

    def catalog(self):
        req = urllib2.Request(self.url+"/_catalog",headers = self.headers)
        r = urllib2.urlopen(req)
        repos = json.loads(r.read())
        return repos['repositories']
        
    def tags(self, response):
        req = urllib2.Request(self.url+'/'+response+'/tags/list',headers=self.headers)
        r = urllib2.urlopen(req)
        tags = json.loads(r.read())
        return tags['tags']
        
    def digest(self, response, tag):
        redata = {}
        req = urllib2.Request(self.url+'/'+response+'/manifests/'+tag,headers=self.headers)
        try:
            r = urllib2.urlopen(req)
            html = json.loads(r.read())
            size = 0 
            for i in html['history']:
                if 'Size' in json.loads(i['v1Compatibility']):
                    size += json.loads(i['v1Compatibility'])['Size']

            redata['tag'] = tag
            redata['id'] = json.loads(html['history'][0]['v1Compatibility'])['id'][:13]
            created_time = json.loads(html['history'][0]['v1Compatibility'])['created']
            created_time = created_time[:-4]
            created_time = datetime.datetime.strptime(created_time, "%Y-%m-%dT%H:%M:%S.%f")
            created_time = created_time - datetime.timedelta(0, time.timezone)
            redata['created'] = created_time.strftime("%Y-%m-%d %H:%M")
            redata['fslayers'] = len(html['fsLayers'])
            redata['size'] = size / 1024 /1024
            redata['digest'] = r.headers['Docker-Content-Digest']
            return redata
        except:
            return None
    
    def retag(self):
        self.retags = {}
        for i in self.catalog():
            self.retags[i] = self.tags(i)
        return self.retags