#!/usr/bin/python
# -*- coding: utf-8 -*-
#用于进行http请求，以及MD5加密，生成签名的工具类

#import http.client
import httplib
#import urllib
import urllib
import json
import hashlib
import time

def buildMySign(params,secretKey):
    sign = ''
    for key in sorted(params.keys()):
        sign += key + '=' + str(params[key]) +'&'
    data = sign+'secret_key='+secretKey
    return  hashlib.md5(data.encode("utf8")).hexdigest().upper()

def httpGet(url,resource,params=''):
    #conn = http.client.HTTPSConnection(url, timeout=10)
    conn = httplib.HTTPSConnection(url, timeout=10)
    conn.request("GET",resource + '?' + params)
    response = conn.getresponse()
    data = response.read().decode('utf-8')
    return json.loads(data)

def httpPost(url,resource,params):
    """
    headers = {
            "Content-type" : "application/x-www-form-urlencoded",
    }
    """
    headers = {"Content-type": "application/x-www-form-urlencoded",
            'Accept-Language':'zh-CN,zh;q=0.8',
            'User-Agent': "Mozilla/5.0 (Windows NT 6.1; rv:32.0) Gecko/20100101 Firefox/32.0",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Connection": "close",
            "Cache-Control": "no-cache"}
    #conn = http.client.HTTPSConnection(url, timeout=10)
    conn = httplib.HTTPSConnection(url, timeout=10)
    temp_params = urllib.urlencode(params)
    conn.request("POST", resource, temp_params, headers)
    response = conn.getresponse()
    data = response.read().decode('utf-8')
    params.clear()
    conn.close()
    return data


        
     
