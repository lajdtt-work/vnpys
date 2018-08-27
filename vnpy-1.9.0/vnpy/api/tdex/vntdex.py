# encoding: UTF-8
# 


import ssl
import hashlib

import zlib
import json
import time
import traceback
import requests
import hex
import hmac
import queue

from time import sleep
from threading import Thread
from urllib import urlencode
import websocket
from queue import Queue, Empty
from datetime import datetime

#from vnpy.api.tdex.rest import tdexFuture

#http rest
from vnpy.api.tdex.rest.HttpMD5Util import buildMySign,httpGet,httpPost

#from vnpy.trader.gateway.tdexGateway.tdexGateway import tdexGateway
#from vnpy.trader.app.ctaStrategy.wx_server import *
import logging
logging.basicConfig(filename='example.log', filemode="w", level=logging.DEBUG)    


# tdex
REST_HOST = 'https://api.tdex.com/openapi/v1'
WEBSOCKET_HOST = 'wss://tl.tdex.com/realtime'

shengchan = 'wss://tl.tdex.com/realtime'



########################################################################
class tdexApi(object):
    """基于Websocket的API对象"""

    #----------------------------------------------------------------------
    def __init__(self):
        """Constructor"""
        self.apiKey = ''        # 用户名
        self.secretKey = ''     # 密码
        self.host = 'wss://tl.tdex.com/realtime'          # 服务器地址
        
        self.currency = ''      # 货币类型（usd或者cny）
        
        self.ws = None          # websocket应用对象
        #self.thread = None      # 工作线程 旧的


        self.active = False     # 工作状态
        self.wsThread = None    # websocket工作线程
        
        self.heartbeatCount = 0         # 心跳计数
        self.heartbeatThread = None     # 心跳线程
        self.heartbeatReceived = True   # 心跳是否收到
        
        self.reconnecting = False       # 重新连接中

    #++++++++++++++++++++++++++++++++++++++++++++++++++
        self.reqid = 0
        self.sessionDict = {}   # 会话对象字典
        self.queue = Queue()
    #++++++++++++++++++++++++++++++++++++++++++++++++++




    #######################
    ## 通用函数
    #######################
    #----------------------------------------------------------------------
    def heartbeat(self,i):
        """"""
        self.sessionDict[i] = requests.Session()

        while self.active:
            self.heartbeatCount += 1
            
            if self.heartbeatCount < 10:
                sleep(1)
            else:
                self.heartbeatCount = 0

                if not self.heartbeatReceived:
                    print 'heartbeat_reconnect',datetime.now()
                    self.reconnect()

                    self.heartbeatReceived = True
                else:
                    self.heartbeatReceived = False
                    timestamp = int(time.time())
                    print 'timestamp',timestamp
                    d = {'ping': timestamp}
                    j = json.dumps(d)
                    print ('j=',j)
                    try:
                        self.ws.send(j) 
                    except:
                        msg = traceback.format_exc()
                        self.onError(msg)
                        self.reconnect()
                        print 'heartbeat2_reconnect2',datetime.now()
                    print 'ping:',datetime.now()
    #----------------------------------------------------------------------
    def heartbeat_ping(self,data):
        """"""
        if self.active:

            d = {'pong': data}
            j = json.dumps(d)
            print 'j:',j,"******************"
            try:
                self.ws.send(j)
                self.pool = Pool(n)
                self.pool.map_async(self.run, range(n))
            except:
                msg = traceback.format_exc()
                print msg
                self.onError(msg)
                #self.reconnect()
                print 'heartbeat_ping_reconnect2',datetime.now()

            
    #----------------------------------------------------------------------
    def reconnect(self):
        """重新连接"""
        if not self.reconnecting:
            self.reconnecting = True
            print u'重新连接'
            self.closeWebsocket()   # 首先关闭之前的连接
            self.initWebsocket()
        
            self.reconnecting = False
    #----------------------------------------------------------------------
    def connect(self, host, apiKey, secretKey, trace=False):
        """连接"""
        self.host = host
        self.apiKey = apiKey
        self.secretKey = secretKey
        self.currency = 'usd'

        # print host,apiKey,secretKey

        websocket.enableTrace(trace)
        
        self.initWebsocket()
        self.active = True
    #----------------------------------------------------------------------
    #----------------------------------------------------------------------


    def initWebsocket(self):
        """# on_open    可调用的对象，在打开websocket时调用。这个函数有一个参数。这个参数是这个类对象
            on_message  可调用的对象，当接收到的数据时被调用,有2个参数,第一个参数是这个类对象,第二个参数是我们从服务器获取的utf-8字符串
            on_error    当我们出错时，它会被调用,第一个参数是这个类对象,第一个参数是异常对象
            on_close    当关闭连接时调用的可调用对象
        """
        self.ws = websocket.WebSocketApp(self.host,
                                         on_open=self.onOpenCallback,
                                         on_message=self.onMessageCallback,
                                         on_error=self.onErrorCallback,
                                         on_close=self.onCloseCallback
                                         )
        kwargs = {'sslopt': {'cert_reqs': ssl.CERT_NONE}}
        self.wsThread = Thread(target=self.ws.run_forever, kwargs=kwargs)
        # self.wsThread = Thread(target=self.ws.run_forever, args=(None, None, 60, 30))
        self.wsThread.start()
    #----------------------------------------------------------------------
    def closeHeartbeat(self):
        """关闭接口"""
        if self.heartbeatThread and self.heartbeatThread.isAlive():
            self.active = False
            self.heartbeatThread.join()
    #----------------------------------------------------------------------
    def closeWebsocket(self):
        """关闭WS"""
        if self.wsThread and self.wsThread.isAlive():
            self.ws.close()
            self.wsThread.join()
    
    #----------------------------------------------------------------------
    def close(self):
        """"""
        self.closeHeartbeat()
        self.closeWebsocket()
        
    #-
    #----------------------------------------------------------------------
    #原来解码器，暂时先不用
    def readData(self, evt):
        """解压缩推送收到的数据"""
        # 创建解压器
        #print 'read data evt:',evt
        decompress = zlib.decompressobj(-zlib.MAX_WBITS)
        
        # 将原始数据解压成字符串
        inflated = decompress.decompress(evt) + decompress.flush()
        #print 'read data inflated:',inflated
        # 通过json解析字符串
        data = json.loads(inflated)
        print 'readData_qidong'
        
        return data
      #用新的
    def readDatajs(self, evt):
        """解码推送收到的数据"""
        data = json.loads(evt)
        return data
    #----------------------------------------------------------------------
    def generateSign(self, path, expires,  body=None):
        """生成签名"""
        # 对params在HTTP报文路径中，以请求字段方式序列化
        if body is None:
            body = ''
        msg =path + str(expires) + body
        signature = hmac.new(self.secretKey, msg,
                             digestmod=hashlib.sha256).hexdigest()
        return signature


    #----------------------------------------------------------------------
    def onMessage(self, evt):
        """信息推送"""
        print 'onMessage'
        data = self.readData(evt)
        print data
        
    #----------------------------------------------------------------------
    def onError(self, evt):
        """错误推送"""
        print 'onError'
        print evt
        
    #----------------------------------------------------------------------
    def onClose(self):
        """接口断开"""
        print 'onClose'
        
    #----------------------------------------------------------------------
    def onOpen(self):
        """接口打开"""
        print 'onOpen'
        
    #----------------------------------------------------------------------
    def onMessageCallback(self, evt):
        """""" 
        #print 'evt',evt
        if 'ping' in evt or 'pong' in evt or 'ch' in evt:
            print 'b0',evt
            data = self.readDatajs(evt)
        else:
            print 'b1',evt
            data = self.readData(evt)

        if 'ping' in data or 'pong' in data:
            if 'ping' in data:
                print 'ping',data,data,datetime.now()
                data = data['ping']
                #print 'ping_type:',type(data)
                self.heartbeatReceived = True
                self.heartbeat_ping(data)
            elif 'pong' in data:
                print 'pong',data,datetime.now()
                self.heartbeatReceived = True


        else:
            self.onMessage(evt)
        
    #----------------------------------------------------------------------
    def onErrorCallback(self, evt):
        """"""
        self.onError(evt)
        
    #----------------------------------------------------------------------
    def onCloseCallback(self ):
        """"""
        self.onClose()
        
    #----------------------------------------------------------------------
    def onOpenCallback(self ):
        """"""
        if not self.heartbeatThread:
            self.heartbeatThread = Thread(target=self.heartbeat)
            self.heartbeatThread.start()
        
        self.onOpen()
        

    # #----------------------------------------------------------------------
    def sendMarketDataRequest(self, channel):
        """发送行情请求"""
        # 生成请求
        d = {}
        d['id'] = int(time.time())
        d['sub'] = channel

        print d['id']
        print d['sub']

        # 使用json打包并发送
        j = json.dumps(d)
        print ('j=',j)
        # 若触发异常则重连
        try:
            self.ws.send(j)
        except websocket.WebSocketConnectionClosedException:
            self.reconnect()
            pass
        





    #----------------------------------------------------------------------
    def sendTradingRequest(self, path):
        """发送交易请求"""
        # 在参数字典中加上api_key和签名字段
        expires=int(time.time())
        # url = REST_HOST + path
        params['api_key'] = self.apiKey
        params['api-signature'] = self.generateSign(path, expires, params, body=p.body)
        # 生成请求
        d = {}
        d['event'] = 'addChannel'
        # d['channel'] = channel
        d['parameters'] = params
        d['binary'] = '1'
        
        # 使用json打包并发送
        j = json.dumps(d)
        print 'j:',j
        
        # 若触发异常则重连
        try:
            self.ws.send(j)
        except websocket.WebSocketConnectionClosedException:
            pass 





    def addReq(self, method, path, callback, params=None, postdict=None):
        """添加请求"""
        self.reqid += 1
        req = (method, path, callback, params, postdict, self.reqid)
        self.queue.put(req)
        return self.reqid

    #----------------------------------------------------------------------
    def processReq(self, req, i):
        """处理请求"""
        method, path, callback, params, postdict, reqid = req
        url = REST_HOST + path
        expires = int(time() + 5)

        rq = requests.Request(url=url, data=postdict)
        p = rq.prepare()

        header = copy(self.header)
        header['api-expires'] = str(expires)
        header['api-key'] = self.apiKey
        header['api-signature'] = self.generateSign(method, path, expires, params, body=p.body)

        # 使用长连接的session，比短连接的耗时缩短80%
        # session = self.sessionDict[i]
        # resp = session.request(method, url, headers=header, params=params, data=postdict)

        # resp = requests.request(method, url, headers=header, params=params, data=postdict)
        # code = resp.status_code
        # d = resp.json()
        # if code == 200:
        #     callback(d, reqid)
        # else:
        #     self.onError(code, d)

        try:
            response = requests.request(method, url, headers=header, params=params, data=postdict)
            if response.status_code == 200:
                return True, response.json()
            else:
                return False, u'GET请求失败，状态代码：%s' %response.status_code
        except Exception as e:
            return False, u'GET请求触发异常，原因：%s' %e



        '''
        params['api-expires'] = str(expires)
        params['api-key'] = self.apiKey
        params['api-signature'] = self.generateSignature(method, path, expires, params, body=p.body)
    def  hmac_sign(path, expires, data):
        hasher = CryptoApi.getHasher('sha256')
        secret = localStorage.getItem("api-secret")
        hmac = CryptoApi.getHmac(secret, hasher)
        hmac.update(path.toLowerCase() + expires)
        if (data)
            hmac.update(data);
        console.log(path + expires)
        console.log(data)
        return CryptoApi.encoder.toHex(hmac.finalize())
        input = JSON.stringify(param)
        console.log(e.message)

        path = self.url.replace(_apiProject.sampleUrl, "")
        expires = int(new Date().getTime() / 1000)
        sign = hmac_sign(path, expires, input)
        header["api-key"] = localStorage.getItem("api-key")
        header["api-expires"] = expires
        header["api-signature"] = sign

    '''





    #######################
    ## 现货相关
    #######################        
    
    #----------------------------------------------------------------------
    def subscribeSpotTicker(self, symbol):
        """订阅现货普通报价"""
        self.sendMarketDataRequest('ok_sub_spot%s_%s_ticker' %(self.currency, symbol))
    
    #----------------------------------------------------------------------
    def subscribeSpotDepth(self, symbol, depth):
        """订阅现货深度报价"""
        self.sendMarketDataRequest('ok_sub_spot%s_%s_depth_%s' %(self.currency, symbol, depth))   
        
    #----------------------------------------------------------------------
    def subscribeSpotTradeData(self, symbol):
        """订阅现货成交记录"""
        self.sendMarketDataRequest('ok_sub_spot%s_%s_trades' %(self.currency, symbol))
        
    #----------------------------------------------------------------------
    def subscribeSpotKline(self, symbol, interval):
        """订阅现货K线"""
        self.sendMarketDataRequest('ok_sub_spot%s_%s_kline_%s' %(self.currency, symbol, interval))
        
    #----------------------------------------------------------------------
    def spotTrade(self, symbol, type_, price, amount):
        """现货委托"""
        params = {}
        params['symbol'] = str(symbol+self.currency)
        params['type'] = str(type_)
        params['price'] = str(price)
        params['amount'] = str(amount)
        
        channel = 'tdex_spot%s_trade' %(self.currency)
        
        self.sendTradingRequest(channel, params)
        
    #----------------------------------------------------------------------
    def spotCancelOrder(self, symbol, orderid):
        """现货撤单"""
        params = {}
        params['symbol'] = str(symbol+self.currency)
        params['order_id'] = str(orderid)
        
        channel = 'tdex_spot%s_cancel_order' %(self.currency)

        self.sendTradingRequest(channel, params)
        
    #----------------------------------------------------------------------
    def spotUserInfo(self):
        """查询现货账户"""
        channel = 'tdex_spot%s_userinfo' %(self.currency)
        self.sendTradingRequest(channel, {})
        
    #----------------------------------------------------------------------
    def spotOrderInfo(self, symbol, orderid):
        """查询现货委托信息"""
        params = {}
        params['symbol'] = str(symbol+self.currency)
        params['order_id'] = str(orderid)
        
        channel = 'ok_spot%s_orderinfo' %(self.currency)
        
        self.sendTradingRequest(channel, params)
        
    #----------------------------------------------------------------------
    def subscribeSpotTrades(self):
        """订阅现货成交信息"""
        channel = 'ok_sub_spot%s_trades' %(self.currency)
        
        self.sendTradingRequest(channel, {})
        
    #----------------------------------------------------------------------
    def subscribeSpotUserInfo(self):
        """订阅现货账户信息"""
        channel = 'ok_sub_spot%s_userinfo' %(self.currency)
        
        self.sendTradingRequest(channel, {})
    
    #######################
    ## 期货相关
    #######################       
      #----------------------------------------------------------------------
    def subscribeFutureDepthData(self, symbol,type):
        """订阅期货深度数据"""
        # channel='%s_DEPTH_Data5' %(symbol)
        channel='%s_DEPTH_%s' %(symbol,type)
        self.sendMarketDataRequest(channel)


    #----------------------------------------------------------------------
    def subscribeFutureKlineData(self, symbol,time):
        """订阅k线"""
        self.sendMarketDataRequest('%s_KLINE_%s' %(symbol,time))
    #----------------------------------------------------------------------
    def subscribeFuture(self):
        """订阅期货产品"""
        self.sendMarketDataRequest('ALL_FUTURES_DATA')

    #----------------------------------------------------------------------
    def subscribeFutureContract(self,symbol):
        """订阅期货合约"""
        channel='%s_CONTRACT_DATA'%(symbol)
        self.sendMarketDataRequest(channel)

    #----------------------------------------------------------------------
    def subscribeFutureTickerData(self, symbol):
        """订阅行情数据"""
        channel='%s_MARKET_TICKER' %(symbol)
        self.sendMarketDataRequest(channel)


    #----------------------------------------------------------------------
    def subscribeFutureTrade(self, symbol):
        """订阅交易数据"""
        channel='%s_TRADE_DATA' %(symbol)
        self.sendMarketDataRequest(channel)

    def subscribeFutureeInfoData(self,symbol):
        '''订阅用户数据'''
        channel='ACCOUNT_INFO_UPDATE'
        self.sendMarketDataRequest(channel)

#######################
#######################
#############_---------------------------------------------------------------------------

    #----------------------------------------------------------------------
    def onDepthData(self, data):
        """行情深度推送 """
        print(data)

    #----------------------------------------------------------------------
    def onTradeDetail(self, data):
        """成交细节推送"""
        print(data)

    #----------------------------------------------------------------------
    def onMarketDetail(self, data):
        """市场细节推送"""
        print(data)
  #----------------------------------------------------------------------
    def futureCancelOrder(self, symbol, expiry, orderid):
        """期货撤单"""
        params = {}
        params['symbol'] = str(symbol+self.currency)
        params['order_id'] = str(orderid)
        params['contract_type'] = str(expiry)

        channel = 'tdex_future%s_cancel_order' %(self.currency)

        self.sendTradingRequest(channel, params)

    #----------------------------------------------------------------------
    def futureUserInfo(self):
        """查询期货账户 访问频率 10次/2秒(不确定，官方文档已经未说明这个接口)"""
        channel = 'tdex_future%s_userinfo' %(self.currency)

        self.sendTradingRequest(channel, {})

    """
    #----------------------------------------------------------------------
    def futureTrade(self, symbol, expiry, type_, price, amount, order, leverage):
        #期货委托
        params = {}
        params['symbol'] = str(symbol+self.currency)
        params['type'] = str(type_)
        params['price'] = str(price)
        params['amount'] = str(amount)
        params['contract_type'] = str(expiry)
        params['match_price'] = str(order)
        params['lever_rate'] = str(leverage)
        
        channel = 'ok_future%s_trade' %(self.currency)

        logging.debug('vntdex_futureTrade:%s',params.items())
        self.sendTradingRequest(channel, params)
    """

        
    #----------------------------------------------------------------------

    #----------------------------------------------------------------------
    def futureOrderInfo(self, symbol, expiry, orderid, status, page, length):
        """查询期货委托信息"""
        params = {}
        params['symbol'] = str(symbol+self.currency)
        params['order_id'] = str(orderid)
        params['contract_type'] = expiry
        params['status'] = status
        params['current_page'] = page
        params['page_length'] = length
        
        channel = 'ok_future%s_orderinfo' %(self.currency)
        
        self.sendTradingRequest(channel, params)


    #rest期货查询限价
    def future_price_limit(self,symbol,expiry):
        self.__url = 'www.tdex.com'
        Tprice_limit_url = "/api/v1/future_price_limit.do"
        """
        params = ''
        if symbol:
            params += '&symbol=' + symbol if params else 'symbol=' +symbol
        if contractType:
            params += '&contract_type=' + contractType if params else 'contract_type=' +symbol
        """
        params = 'symbol='+symbol+'&contract_type='+expiry
        try:
            huibao = httpGet(self.__url,Tprice_limit_url,params)
        except Exception,e:
            logging.debug(u'查询限价单出错:%s',e)
            wx_biaoti = u'主人,rest查询限价单出现问题了'
            wx_neirong = str(e)
            wx_server1(wx_neirong,wx_biaoti)
        finally:
            if huibao is not None:
                #logging.debug('future_price_limit_huibao:%s',huibao)
                if 'high' in huibao:
                    try:
                        huibao = json.dumps(huibao)
                        data = json.loads(huibao)
                    except Exception,e:
                            logging.debug(u'vntdex_JSON_LOAD出错:%s',e)
                            data = json.loads(huibao)
                    return data                   
                else:
                    logging.debug('false huibao:%s',huibao)
                    if 'error_code' in huibao:
                        huibao = json.loads(huibao)
                        #print 
                        error_code = huibao['error_code']
                        wx_biaoti = u'主人,rest查询限价单错误huibao'
                        wx_neirong = str(error_code)
                        wx_server1(wx_neirong,wx_biaoti)
                    return

    #--------------------------------------------------------------------
    #rest期货下单
    #访问频率 5次/1秒(按币种单独计算)
    def futureTrade(self, symbol, expiry, type_, price='', amount='', order='', leverage=''):
        try:
            FUTURE_TRADE = "/api/v1/future_trade.do?"
            self.apikey = self.apiKey
            self.secretkey = self.secretKey
            #self.apiKey = ''        # 用户名
            #self.secretKey = ''     # 密码
            self.__url = 'www.tdex.com'
            params = {
                'api_key':self.apikey,
                'symbol':str(symbol+self.currency),
                'contract_type':expiry,
                'amount':amount,
                'type':type_,
                'match_price':order,
                'lever_rate':leverage
            }
            if price:
                params['price'] = price
            params['api-signature'] = buildMySign(params,self.secretkey)
            #return httpPost(self.__url,FUTURE_TRADE,params)
            try:
                huibao = httpPost(self.__url,FUTURE_TRADE,params)
            except Exception,e:
                logging.debug(u'发单出错:%s',e)
                wx_biaoti = u'主人,rest发单出现问题了'
                wx_neirong = str(e)
                wx_server1(wx_neirong,wx_biaoti)
            finally:
                #{"result":true,"order_id":15419955923}
                if huibao is not None:
                    logging.debug('huibao:%s',huibao)
                    if 'true' in huibao:
                        data = '{"binary":0,"channel":"ok_futureusd_trade","data":'+str(huibao)+'}'
                        logging.debug( 'vntdex_futureTrade_true_huibao_data:%s',data)
                        return data
                        #self.api1 = tdexGateway.api(self) 
                        #tdexGateway.api.onfutureTrade(data)
                        #{"binary":0,"channel":"ok_futureusd_trade","data":{"result":true,"order_id":15421781611}}
                    else:
                        logging.debug(u'发单false huibao:%s',huibao)
                        if 'error_code' in huibao:
                            huibao_2 = json.loads(huibao)
                            #print 
                            error_code = huibao_2['error_code']
                            wx_biaoti = u'主人,rest发单错误huibao'
                            wx_neirong = str(error_code)
                            wx_server1(wx_neirong,wx_biaoti)
                            data3 = '{"binary":0,"channel":"ok_futureusd_trade","data":'+str(huibao)+'}'
                            logging.debug( 'vntdex_futureTrade_true_huibao_data:%s',data3)
                            return data3
                        return
        except Exception as e:
            logging.debug(u'vntdex发单false hanshu_baocuo:%s',e)



    # def sendRequest(self, channel, params):
    #     #"""发送指令请求"""
    #     print u'vntdex.sendRequest:{}'.format(channel)
    #     # 在参数字典中加上api_key和签名字段
    #     params['api_key'] = self.apiKey
    #     params['api-signature'] = self.generateSign(params)
    #
    #     # 生成请求
    #     d = {}
    #     d['event'] = 'addChannel'
    #     d['channel'] = channel
    #     d['parameters'] = params
    #
    #     # 使用json打包并发送
    #     j = json.dumps(d)
    #     print ('j=',j)
    #
    #     # 若触发异常则重连
    #     try:
    #         self.ws.send(j)
    #     except websocket.WebSocketConnectionClosedException as ex:
    #         print(u'vntdex.sendTradingRequest Exception:{}'.format(str(ex)))

    # ----------------------------------------------------------------------
    def subscribeFutureUserInfo(self):
        """订阅期货账户信息"""
        channel = 'ok_sub_futureusd_userinfo'
        self.sendTradingRequest(channel, {})
    
    def getPositionInfo(self):
        url = "https://api.tdex.com/openapi/v1/user/info"
        data = self.http_get_request(url,"")
        print("data=",data)
        # return data

    def http_get_request(self, url, params, add_to_headers=None, TIMEOUT=10):
        headers = {
            "Content-type": "application/x-www-form-urlencoded",
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:53.0) Gecko/20100101 Firefox/53.0'
        }
        if add_to_headers:
            headers.update(add_to_headers)
        #postdata = urllib.urlencode(params)
        try:
            # response = requests.get(url, postdata, headers=headers, timeout=TIMEOUT)
            response = requests.get(url, headers=headers, timeout=TIMEOUT)
            if response.status_code == 200:
                return response.json()
            else:
                return {"status": "fail"}
        except Exception as e:
            print(u'httpGet failed :{}'.format(str(e)))
            return {"status": "fail", "msg": e}


if __name__ == '__main__':
    a = tdexApi()
    host="wss://tl.tdex.com/realtime"
    apiKey= "eAC1Psos5BKRMLeQ6HLwCW5Ffi5H3kr2xrTsuLzjPgx7rEMWG2bmJZ3ToN1K2TAd"
    secretKey= "eAC1PstJSk6kQHZSxYqbbezqbvEWdYCcWoU7q49Dhjac4z6YN3eAmrCgQZX2Cb9y"
    trace= True
    a.connect(host,apiKey,secretKey,trace)
    sleep(1)

    
    #get position
    sleep(1)
    a.getPositionInfo()
    
    #buy spot
    symbol = "BTCUSD"
    type == 'buy'
    price = 6500
    amount = 0.1
    # orderid = a.spotTrade(symbol, type, price, amount)
    #
    #Cancel Order撤单
    # a.spotCancelOrder(symbol, orderid)
    
    #subscribe Spot 订阅现货成交信息
    # a.subscribeSpotTrades()
    
    #spot Order Info 查询现货委托信息
    # a.spotOrderInfo(symbol, orderid)

