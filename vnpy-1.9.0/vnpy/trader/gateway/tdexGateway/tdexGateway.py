# encoding: UTF-8
    


import os
import json
from datetime import datetime
from time import sleep
from copy import copy
from threading import Condition
from Queue import Queue
from threading import Thread
from time import sleep

from urllib2 import urlopen
import traceback 

from vnpy.api.tdex import vntdex
from vnpy.trader.vtGateway import *
from vnpy.trader.vtFunction import getJsonPath

#from vnpy.trader.app.ctaStrategy.wx_server import *
import logging
logging.basicConfig(filename='example.log', filemode="w", level=logging.DEBUG)    




# qihuo价格类型映射
futurepriceTypeMap = {}
futurepriceTypeMap['1'] = (DIRECTION_LONG, OFFSET_OPEN)
futurepriceTypeMap['2'] = (DIRECTION_SHORT, OFFSET_OPEN)
futurepriceTypeMap['3'] = (DIRECTION_SHORT, OFFSET_CLOSE)
futurepriceTypeMap['4'] = (DIRECTION_LONG, OFFSET_CLOSE)
futurepriceTypeMapReverse = {v: k for k, v in futurepriceTypeMap.items()} 

# shijiandan类型映射

shijiadanMap = {}
shijiadanMap[PRICETYPE_LIMITPRICE] = '0'
shijiadanMap[PRICETYPE_MARKETPRICE] = '1'
shijiadanMapReverse = {v: k for k, v in shijiadanMap.items()}

ganggan = '10'



############################################
## 交易合约代码
############################################

# USD
BTC_USD_SPOT = 'BTC_USD_SPOT'
BTC_USD_THISWEEK = 'BTC_USD_THISWEEK'
BTC_USD_NEXTWEEK = 'BTC_USD_NEXTWEEK'
BTC_USD_QUARTER = 'BTC_USD_QUARTER'

LTC_USD_SPOT = 'LTC_USD_SPOT'
LTC_USD_THISWEEK = 'LTC_USD_THISWEEK'
LTC_USD_NEXTWEEK = 'LTC_USD_NEXTWEEK'
LTC_USD_QUARTER = 'LTC_USD_QUARTER'

ETH_USD_SPOT = 'ETH_USD_SPOT'
ETH_USD_THISWEEK = 'ETH_USD_THISWEEK'
ETH_USD_NEXTWEEK = 'ETH_USD_NEXTWEEK'
ETH_USD_QUARTER = 'ETH_USD_QUARTER'

ETC_USD_SPOT = 'ETC_USD_SPOT'
ETC_USD_THISWEEK = 'ETC_USD_THISWEEK'
ETC_USD_NEXTWEEK = 'ETC_USD_NEXTWEEK'
ETC_USD_QUARTER = 'ETC_USD_QUARTER'

EOS_USD_SPOT = 'EOS_USD_SPOT'
EOS_USD_THISWEEK = 'EOS_USD_THISWEEK'
EOS_USD_NEXTWEEK = 'EOS_USD_NEXTWEEK'
EOS_USD_QUARTER = 'EOS_USD_QUARTER'

# CNY
BTC_CNY_SPOT = 'BTC_CNY_SPOT'
LTC_CNY_SPOT = 'LTC_CNY_SPOT'
ETH_CNY_SPOT = 'ETH_CNY_SPOT'

# 印射字典
spotSymbolMap = {}
spotSymbolMap['ltc_usd'] = LTC_USD_SPOT
spotSymbolMap['btc_usd'] = BTC_USD_SPOT
spotSymbolMap['eth_usd'] = ETH_USD_SPOT
spotSymbolMap['ltc_cny'] = LTC_CNY_SPOT
spotSymbolMap['btc_cny'] = BTC_CNY_SPOT
spotSymbolMap['eth_cny'] = ETH_CNY_SPOT
spotSymbolMapReverse = {v: k for k, v in spotSymbolMap.items()}




############################################
price_limitMap = {}


"""
btc_usd
# 期货合约到期类型
FUTURE_EXPIRY_THIS_WEEK = 'this_week'
FUTURE_EXPIRY_NEXT_WEEK = 'next_week'
FUTURE_EXPIRY_QUARTER = 'quarter'
"""


############################################
## Channel和Symbol的印射
############################################
channelSymbolMap = {}

# USD
channelSymbolMap['ok_sub_spotusd_btc_ticker'] = BTC_USD_SPOT
channelSymbolMap['ok_sub_spotusd_ltc_ticker'] = LTC_USD_SPOT
channelSymbolMap['ok_sub_spotusd_eth_ticker'] = ETH_USD_SPOT

channelSymbolMap['ok_sub_spotusd_btc_depth_20'] = BTC_USD_SPOT
channelSymbolMap['ok_sub_spotusd_ltc_depth_20'] = LTC_USD_SPOT
channelSymbolMap['ok_sub_spotusd_eth_depth_20'] = ETH_USD_SPOT

# CNY
channelSymbolMap['ok_sub_spotcny_btc_ticker'] = BTC_CNY_SPOT
channelSymbolMap['ok_sub_spotcny_ltc_ticker'] = LTC_CNY_SPOT
channelSymbolMap['ok_sub_spotcny_eth_ticker'] = ETH_CNY_SPOT

channelSymbolMap['ok_sub_spotcny_btc_depth_20'] = BTC_CNY_SPOT
channelSymbolMap['ok_sub_spotcny_ltc_depth_20'] = LTC_CNY_SPOT
channelSymbolMap['ok_sub_spotcny_eth_depth_20'] = ETH_CNY_SPOT

# heyue
channelSymbolMap['ok_sub_futureusd_btc_ticker_this_week'] = BTC_USD_THISWEEK
channelSymbolMap['ok_sub_futureusd_btc_ticker_next_week'] = BTC_USD_NEXTWEEK
channelSymbolMap['ok_sub_futureusd_btc_ticker_quarter'] = BTC_USD_QUARTER

channelSymbolMap['ok_sub_futureusd_ltc_ticker_this_week'] = LTC_USD_THISWEEK
channelSymbolMap['ok_sub_futureusd_ltc_ticker_next_week'] = LTC_USD_NEXTWEEK
channelSymbolMap['ok_sub_futureusd_ltc_ticker_quarter'] = LTC_USD_QUARTER

channelSymbolMap['ok_sub_futureusd_eth_ticker_this_week'] = ETH_USD_THISWEEK
channelSymbolMap['ok_sub_futureusd_eth_ticker_next_week'] = ETH_USD_NEXTWEEK
channelSymbolMap['ok_sub_futureusd_eth_ticker_quarter'] = ETH_USD_QUARTER

channelSymbolMap['ok_sub_futureusd_etc_ticker_this_week'] = ETC_USD_THISWEEK
channelSymbolMap['ok_sub_futureusd_etc_ticker_next_week'] = ETC_USD_NEXTWEEK
channelSymbolMap['ok_sub_futureusd_etc_ticker_quarter'] = ETC_USD_QUARTER

channelSymbolMap['ok_sub_futureusd_eos_ticker_this_week'] = EOS_USD_THISWEEK
channelSymbolMap['ok_sub_futureusd_eos_ticker_next_week'] = EOS_USD_NEXTWEEK
channelSymbolMap['ok_sub_futureusd_eos_ticker_quarter'] = EOS_USD_QUARTER





########################################################################
errorDict = {}

errorDict['10000'] = u'必填参数为空'

########################################################################
class TdexGateway(VtGateway):
    """OkCoin接口"""

    #----------------------------------------------------------------------
    def __init__(self, eventEngine, gatewayName='TDEX'):
        """Constructor"""
        super(TdexGateway, self).__init__(eventEngine, gatewayName)
        
        self.api = Api(self)     
        
        self.leverage = 0
        self.connected = False
        self.fileName = self.gatewayName + '_connect.json'
        self.filePath = getJsonPath(self.fileName, __file__)             
        
    #----------------------------------------------------------------------
    def connect(self):
        """连接"""
        # 载入json文件
        try:
            f = file(self.filePath)
        except IOError:
            log = VtLogData()
            log.gatewayName = self.gatewayName
            log.logContent = u'读取连接配置出错，请检查'
            self.onLog(log)
            return
        
        # 解析json文件
        setting = json.load(f)
        try:
            host = str(setting['host'])
            apiKey = str(setting['apiKey'])
            secretKey = str(setting['secretKey'])
            trace = setting['trace']
            leverage = setting['leverage']
        except KeyError:
            log = VtLogData()
            log.gatewayName = self.gatewayName
            log.logContent = u'连接配置缺少字段，请检查'
            self.onLog(log)
            return            
        
        # 初始化接口
        self.leverage = leverage
        
        host = vntdex.shengchan

        self.host = host
        #print 'chushihua jie kou host:', host
        
        #self.api.active = True
        self.api.connect(host, apiKey, secretKey, trace)
        
        log = VtLogData()
        log.gatewayName = self.gatewayName
        log.logContent = u'接口初始化成功'
        self.onLog(log)
        
        # 启动查询
        self.initQuery()
        self.startQuery()
    
    #----------------------------------------------------------------------
    def subscribe(self, subscribeReq):
        """订阅行情"""
        pass
        
    #----------------------------------------------------------------------
    def sendOrder(self, orderReq):
        """发单"""
        if self.host == vntdex.OKEX_heyue:
            #print 'qryAccount,host =okex_heyu'
            #print 'exheyue'
            self.api.writeLog(u'发单')
            self.api.writeLog(str(orderReq))
            print '发单'
            return self.api.futureSendOrder(orderReq)
        else:
            return self.api.spotSendOrder(orderReq)
        
    #----------------------------------------------------------------------
    def cancelOrder(self, cancelOrderReq):
        """撤单"""
        if self.host == vntdex.OKEX_heyue:
            #print 'qryAccount,host =okex_heyu'
            #print 'exheyue'
            self.api.writeLog(u'撤单')
            self.api.writeLog(str(cancelOrderReq))
            return self.api.futureCancel(cancelOrderReq)
        else:
            return self.api.spotCancel(cancelOrderReq)
        #self.api.spotCancel(cancelOrderReq)
        
    #----------------------------------------------------------------------
    def qryAccount(self):
        """查询账户资金"""
        #connectval = connect()
        #print 'host:',host
        #print 'self.host:',self.host
        #print 'self.host:',self.host
        #print 'self.__dict__:',self.__dict__
        if self.qry_num % 60 == 0:
            pass
        else:
            return

        print 'qryAccount()',self.qry_num
        if self.host == vntdex.shengchan:
            
            #print 'exheyue'
            self.api.futureUserInfo()
        else:
            self.api.spotUserInfo()

    #----------------------------------------------------------------------
    def qryOrderinfo(self):
        """查询订单信息"""
        if self.qry_num % 32 == 0:
            pass
        else:
            return
        print 'qryOrderinfo()',self.qry_num
        try:
            if self.api.localNoDict != {}:
                #这样写不对，localNoDict字典可能通过sub接口删除了
                if self.qry_order_Next >= len(self.api.localNoDict.keys()):
                    self.qry_order_Next = 0
                localNo = self.api.localNoDict.keys()[self.qry_order_Next]
                self.qry_order_Next += 1
                # if self.qry_order_Next >= len(self.api.localNoDict.keys()):
                #     self.qry_order_Next = 0
                #for localNo in self.api.localNoDict.keys():
                self.api.writeLog('qryOrderinfo.orderinfoDict.keys:%s' % self.api.orderinfoDict.keys())
                #linshi_2 = self.api.orderinfoDict[localNo]
                #self.api.writeLog('linshi_2:%s' % linshi_2)

                symbol = self.api.orderinfoDict[localNo][0]
                expiry = self.api.orderinfoDict[localNo][1]
                orderid = self.api.localNoDict[localNo]
                status = '2'
                page = '1'
                length = '1'

                #self.api.writeLog('qryOrderinfo.orderinfoDict.__dict__:%s' % self.api.orderinfoDict.__dict__)
                self.api.writeLog('qryOrderinfo.orderid %s' % orderid)
                self.api.writeLog('qryOrderinfo.localNo %s' % localNo)

                
                
                self.api.writeLog('qryOrderinfo.orderinfoDict.keys:%s' % self.api.orderinfoDict.keys())
                self.api.writeLog('qryOrderinfo.orderinfoDict.value:%s %s' % (self.api.orderinfoDict[localNo][0],self.api.orderinfoDict[localNo][1]))
 
                self.api.futureOrderInfo(symbol, expiry, orderid, status, page, length)


                
        except Exception as e:
            logging.debug('okgateway_qryOrderinfo:%s',e)
                
    #----------------------------------------------------------------------
    def qryfuture_price_limit(self):
        """查询限价"""
        # qihuo印射字典
        #price_limitMap = {}
        try:
            price_limitMap['BTC_USD_THISWEEK'] = self.api.future_price_limit('btc_usd','this_week')
            price_limitMap['BTC_USD_NEXTWEEK'] = self.api.future_price_limit('btc_usd','next_week')
            price_limitMap['BTC_USD_QUARTER'] = self.api.future_price_limit('btc_usd','quarter')
            price_limitMap['LTC_USD_THISWEEK'] = self.api.future_price_limit('ltc_usd','this_week')
            price_limitMap['LTC_USD_NEXTWEEK'] = self.api.future_price_limit('ltc_usd','next_week')
            price_limitMap['LTC_USD_QUARTER'] = self.api.future_price_limit('ltc_usd','quarter')
            print price_limitMap.items()
        except Exception,e:
            logging.debug(u'qryfuture_price_limit查询限价单出错:%s',e)
        finally:
            return
    #----------------------------------------------------------------------
    def qryPosition(self):
        """查询持仓"""
        pass
        
        
    #----------------------------------------------------------------------
    def close(self):
        """关闭"""
        #self.api.active = False
        self.api.close()
        
    #----------------------------------------------------------------------
    def initQuery(self):
        """初始化连续查询"""
        if self.qryEnabled:
            # 需要循环的查询函数列表
            # 20180208  取消,self.qryfuture_price_limit
            self.qryFunctionList = [self.qryAccount,self.qryOrderinfo]
            #self.qryFunctionList.append(self.qryOrderinfo)

            self.api.writeLog('qryFunctionList:%s' % self.qryFunctionList)

            
            self.qryCount = -1           # 查询触发倒计时
            self.qryTrigger = 3         # 查询触发点
            self.qryNextFunction = 0    # 上次运行的查询函数索引
            self.qry_num = -1            # 帐户和订单详情查询计数
            self.qry_order_Next = 0     # 查询订单顺序
            
            self.startQuery()  
    
    #----------------------------------------------------------------------
    def query(self, event):
        """注册到事件处理引擎上的查询函数"""
        self.qryCount += 1
        self.qry_num += 1
        #20180801
        # print 'self.qryCount:',self.qryCount
        # print 'self.qry_num',self.qry_num
        #好隐蔽的bug,
        if self.qry_num > 120:
            self.qry_num = self.qryCount

        if self.qryCount > self.qryTrigger:
            # 清空倒计时
            self.qryCount = 0
            
            # 执行查询函数
            function = self.qryFunctionList[self.qryNextFunction]
            function()
            
            # 计算下次查询函数的索引，如果超过了列表长度，则重新设为0
            self.qryNextFunction += 1
            if self.qryNextFunction == len(self.qryFunctionList):
                self.qryNextFunction = 0
                
    #----------------------------------------------------------------------
    def startQuery(self):
        """启动连续查询"""
        self.eventEngine.register(EVENT_TIMER, self.query)
    
    #----------------------------------------------------------------------
    def setQryEnabled(self, qryEnabled):
        """设置是否要启动循环查询"""
        self.qryEnabled = qryEnabled
    


########################################################################
class Api(vntdex.tdexApi):
    """OkCoin的API实现"""

    #----------------------------------------------------------------------
    def __init__(self, gateway):
        """Constructor"""
        super(Api, self).__init__()
        
        self.gateway = gateway                  # gateway对象
        self.gatewayName = gateway.gatewayName  # gateway对象名称
        
        #self.active = False             # 若为True则会在断线后自动重连

        self.cbDict = {}
        self.tickDict = {}
        self.orderDict = {}
        
        self.localNo = 0                # 本地委托号
        self.localNoQueue = Queue()     # 未收到系统委托号的本地委托号队列
        self.localNoDict = {}           # key为本地委托号，value为系统委托号
        self.orderIdDict = {}           # key为系统委托号，value为本地委托号
        self.cancelDict = {}            # key为本地委托号，value为撤单请求
        self.orderinfoDict = {}         # key为本地委托号，value为订单详情
        #self.tradeID = 0 #本地生成订单号码
        self.cache_some_order = {}      #解决下单后，收到回报，却还没产生本地订单号的bug.缓存下订单号不能匹配本地订单号的数据
        
        self.initCallback()
        
    #----------------------------------------------------------------------
    def onMessage(self, evt):
        try:
            if 'data' in evt:
                #print 'in'
                #print 'evt:',evt
                try:
                    data = json.loads(evt)
                except:
                    data = json.dumps(evt)
                    data = json.loads(evt)
                data = data[0]
                #print 'on message data:',data
                if not 'channel' in data:
                    self.writeLog('wu chanel_data:%s' % data)
                    return
                channel = data['channel']
                #print 'on message channel:',channel
                #paichu = 'ticker' not in channel and 'depth' not in channe
                
                if 'error_code' in data['data']:
                    error_code = data['data']['error_code']
                    self.writeLog('error_code')
                    self.writeLog(str(error_code))
                    self.writeLog(str(data))
                    #{u'data': {u'error_code': u'20100', u'result': u'false'}, u'channel': u'login'}
                    if str(error_code) in errorDict.keys():
                        error_xiaoxi = errorDict[str(error_code)]
                        self.writeLog(str(error_xiaoxi))
                        try:
                            wx_biaoti = u'主人,黑心交易所API出现问题了'
                            wx_neirong = str(channel)+'_'+str(error_code)+'_'+error_xiaoxi
                            wx_url = 'https://sc.ftqq.com/SCU15635Taf724c3f8040067eb7448dcfb86fe0945a04674d6799f.send?text='+wx_biaoti+'&desp='+wx_neirong
                            wx_rs = urlopen(wx_url,timeout = 3).read()
                            wx_data = json.loads(wx_rs)
                            self.writeLog(u'微信消息%s已经发送' % wx_data)
                        except:
                            print(traceback.format_exc())
                        finally:
                            return
                    else:
                        try:
                            wx_biaoti = u'主人,黑心交易所API出现未知问题了'
                            wx_neirong = str(channel)+'_'+str(error_code)
                            wx_url = 'https://sc.ftqq.com/SCU15635Taf724c3f8040067eb7448dcfb86fe0945a04674d6799f.send?text='+wx_biaoti+'&desp='+wx_neirong
                            wx_rs = urlopen(wx_url,timeout = 3).read()
                            wx_data = json.loads(wx_rs)
                            self.writeLog(u'微信消息%s已经发送' % wx_data)
                        except:
                            print(traceback.format_exc())
                        finally:
                            return

                if channel.find('ticker') == -1 and channel.find('depth') == -1 and channel.find('userinfo') == -1:
                #if channel.find('ticker') == -1:
                    self.writeLog('in')
                    self.writeLog(str(channel))
                    self.writeLog(str(data))
                
                #print 'on message callback:',callback
                #self.writeLog(channel)
                #self.writeLog(data)
                if channel in self.cbDict.keys():
                    callback = self.cbDict[channel]
                    callback(data)
            else:
                #print 'not in'
                data = self.readData(evt)[0]
                #print 'on message data:',data
                if not 'channel' in data:
                    self.writeLog('wu chanel_data:%s' % data)
                    return
                channel = data['channel']
                #print 'on message channel:',channel
                
                #print 'on message callback:',callback
                #self.writeLog(channel)
                if 'error_code' in data['data']:
                    error_code = data['data']['error_code']
                    self.writeLog('error_code')
                    self.writeLog(str(error_code))
                    self.writeLog(str(data))
                    if str(error_code) in errorDict.keys():
                        error_xiaoxi = errorDict[str(error_code)]
                        self.writeLog(str(error_xiaoxi))
                        try:
                            wx_biaoti = u'主人,黑心交易所API出现问题了'
                            wx_neirong = str(channel)+'_'+str(error_code)+'_'+error_xiaoxi
                            wx_url = 'https://sc.ftqq.com/SCU15635Taf724c3f8040067eb7448dcfb86fe0945a04674d6799f.send?text='+wx_biaoti+'&desp='+wx_neirong
                            wx_rs = urlopen(wx_url,timeout = 3).read()
                            wx_data = json.loads(wx_rs)
                            self.writeLog(u'微信消息%s已经发送' % wx_data)
                        except:
                            print(traceback.format_exc())
                        finally:
                            return
                    else:
                        try:
                            wx_biaoti = u'主人,黑心交易所API出现未知问题了'
                            wx_neirong = str(channel)+'_'+str(error_code)
                            wx_url = 'https://sc.ftqq.com/SCU15635Taf724c3f8040067eb7448dcfb86fe0945a04674d6799f.send?text='+wx_biaoti+'&desp='+wx_neirong
                            wx_rs = urlopen(wx_url,timeout = 3).read()
                            wx_data = json.loads(wx_rs)
                            #self.writeLog(u'微信消息%s已经发送' % wx_data)
                        except:
                            print(traceback.format_exc())
                        finally:
                            return
                if channel.find('ticker') == -1 and channel.find('depth') == -1 and channel.find('userinfo') == -1:
                #if channel.find('ticker') == -1:
                    self.writeLog('not in')
                    self.writeLog(str(channel))
                    self.writeLog(str(data))
                if channel in self.cbDict.keys():
                    callback = self.cbDict[channel]
                    callback(data)
        except Exception as e:
            logging.debug('okgateway_onmesscuow:%s',e)

        
    #----------------------------------------------------------------------
    def onError(self, evt):
        """错误推送"""
        error = VtErrorData()
        error.gatewayName = self.gatewayName
        error.errorMsg = str(evt)
        self.gateway.onError(error)

    #---------------------------------------------------------------------
    def onClose(self):
        """接口断开"""
        self.gateway.connected = False
        self.writeLog(u'服务器连接断开')
    #----------------------------------------------------------------------
    def onOpen(self):       
        """连接成功"""
        try:
            self.gateway.connected = True
            self.writeLog(u'服务器连接成功')
            
            # 连接后查询账户和委托数据
            # self.futureUserInfo()


            #self.spotUserInfo()
            
            #self.spotOrderInfo(vntdex.TRADING_SYMBOL_LTC, '-1')
            #self.spotOrderInfo(vntdex.TRADING_SYMBOL_BTC, '-1')
            #self.spotOrderInfo(vntdex.TRADING_SYMBOL_ETH, '-1')

            # 连接后订阅现货的成交和账户数据
            # 
            #self.writeLog(u'woqulianjie')
            print 'lianjiechenggong host:', self.host
            #if self.host == vntdex.OKEX_heyue:
            #print 'self.__dict__',self.__dict__
            #print self
            #print 'exheyue'


            self.futureUserInfo()

            
            #--------------------------------------------------------------------------------


            #    host = vntdex.OKEX_xianhuo

            # 返回合约信息
            if self.currency == vntdex.CURRENCY_CNY:
                l = self.generateCnyContract()
            else:
                l = self.generateUsdContract()
                
            for contract in l:
                contract.gatewayName = self.gatewayName
                self.gateway.onContract(contract)
        except Exception as e:
            logging.debug(u'TDEXgateway_onOpen_hanshu:%s',e)
    #----------------------------------------------------------------------
    def writeLog(self, content):
        """快速记录日志"""
        log = VtLogData()
        log.gatewayName = self.gatewayName
        log.logContent = content
        self.gateway.onLog(log)
        
    #----------------------------------------------------------------------
    def initCallback(self):
        """初始化回调函数"""
        # USD_SPOT
        self.cbDict['ok_sub_spotusd_btc_ticker'] = self.onTicker
        self.cbDict['ok_sub_spotusd_ltc_ticker'] = self.onTicker
        self.cbDict['ok_sub_spotusd_eth_ticker'] = self.onTicker

        self.cbDict['ok_sub_spotusd_btc_depth_20'] = self.onDepth
        self.cbDict['ok_sub_spotusd_ltc_depth_20'] = self.onDepth
        self.cbDict['ok_sub_spotusd_eth_depth_20'] = self.onDepth

        self.cbDict['ok_spotusd_userinfo'] = self.onSpotUserInfo
        self.cbDict['ok_spotusd_orderinfo'] = self.onSpotOrderInfo
        
        self.cbDict['ok_sub_spotusd_userinfo'] = self.onSpotSubUserInfo
        self.cbDict['ok_sub_spotusd_trades'] = self.onSpotSubTrades
        
        self.cbDict['ok_spotusd_trade'] = self.onSpotTrade
        self.cbDict['ok_spotusd_cancel_order'] = self.onSpotCancelOrder
        
        # CNY_SPOT
        self.cbDict['ok_sub_spotcny_btc_ticker'] = self.onTicker
        self.cbDict['ok_sub_spotcny_ltc_ticker'] = self.onTicker        
        self.cbDict['ok_sub_spotcny_eth_ticker'] = self.onTicker

        self.cbDict['ok_sub_spotcny_btc_depth_20'] = self.onDepth
        self.cbDict['ok_sub_spotcny_ltc_depth_20'] = self.onDepth
        self.cbDict['ok_sub_spotcny_eth_depth_20'] = self.onDepth

        self.cbDict['ok_spotcny_userinfo'] = self.onSpotUserInfo
        self.cbDict['ok_spotcny_orderinfo'] = self.onSpotOrderInfo
        
        self.cbDict['ok_sub_spotcny_userinfo'] = self.onSpotSubUserInfo
        self.cbDict['ok_sub_spotcny_trades'] = self.onSpotSubTrades
        
        self.cbDict['ok_spotcny_trade'] = self.onSpotTrade
        self.cbDict['ok_spotcny_cancel_order'] = self.onSpotCancelOrder        

        # USD_FUTURES
        # tick
        self.cbDict['ok_sub_futureusd_btc_ticker_this_week'] = self.onfutureTicker
        self.cbDict['ok_sub_futureusd_btc_ticker_next_week'] = self.onfutureTicker
        self.cbDict['ok_sub_futureusd_btc_ticker_quarter'] = self.onfutureTicker

        self.cbDict['ok_sub_futureusd_eos_ticker_this_week'] = self.onfutureTicker
        self.cbDict['ok_sub_futureusd_eos_ticker_next_week'] = self.onfutureTicker
        self.cbDict['ok_sub_futureusd_eos_ticker_quarter'] = self.onfutureTicker

        

        #self.cbDict['ok_sub_futureusd_eth_ticker_this_week'] = self.onfutureTicker
        #self.cbDict['ok_sub_futureusd_eth_ticker_next_week'] = self.onfutureTicker
        #self.cbDict['ok_sub_futureusd_eth_ticker_quarter'] = self.onfutureTicker

        #self.cbDict['ok_sub_futureusd_etc_ticker_this_week'] = self.onfutureTicker
        #self.cbDict['ok_sub_futureusd_etc_ticker_next_week'] = self.onfutureTicker
        #self.cbDict['ok_sub_futureusd_etc_ticker_quarter'] = self.onfutureTicker

        #depth
        self.cbDict['ok_sub_futureusd_btc_depth_this_week_20'] = self.onfutureDepth
        self.cbDict['ok_sub_futureusd_btc_depth_next_week_20'] = self.onfutureDepth
        self.cbDict['ok_sub_futureusd_btc_depth_quarter_20'] = self.onfutureDepth

        self.cbDict['ok_sub_futureusd_eos_depth_this_week_20'] = self.onfutureDepth
        self.cbDict['ok_sub_futureusd_eos_depth_next_week_20'] = self.onfutureDepth
        self.cbDict['ok_sub_futureusd_eos_depth_quarter_20'] = self.onfutureDepth

        #self.cbDict['ok_sub_futureusd_eth_depth_this_week_20'] = self.onfutureDepth
        #self.cbDict['ok_sub_futureusd_eth_depth_next_week_20'] = self.onfutureDepth
        #self.cbDict['ok_sub_futureusd_eth_depth_quarter_20'] = self.onfutureDepth

        #self.cbDict['ok_sub_futureusd_etc_depth_this_week_20'] = self.onfutureDepth
        #self.cbDict['ok_sub_futureusd_etc_depth_next_week_20'] = self.onfutureDepth
        #self.cbDict['ok_sub_futureusd_etc_depth_quarter_20'] = self.onfutureDepth

        #------------------------------------------------------------------------


        self.cbDict['ok_futureusd_userinfo'] = self.onfutureUserInfo#ok
        self.cbDict['ok_futureusd_orderinfo'] = self.onfutureOrderInfo# to do
        
        #self.cbDict['ok_sub_futureusd_userinfo'] = self.onSpotSubUserInfo#官方的API 有争议，暂时不做了
        self.cbDict['ok_sub_futureusd_trades'] = self.onfutureSubTrades#ok
        
        self.cbDict['ok_futureusd_trade'] = self.onfutureTrade#ok
        self.cbDict['ok_futureusd_cancel_order'] = self.onfutureCancelOrder #ok
        self.cbDict['login'] = self.onLogin
        #


    def onLogin(self, data):
        """"""
        self.writeLog(u'服务器登录成功')

        # 查询持仓
        self.spotUserInfo()

        # 订阅推送


    #----------------------------------------------------------------------
    def onfutureTicker(self, data):
        """"""
        #print 'onticker qidong'
        if 'data' not in data:
            return
        
        channel = data['channel']
        #print 'on tick channel:',channel
        symbol = channelSymbolMap[channel]
        #print 'ontick symbol:',symbol
        
        if symbol not in self.tickDict:
            tick = VtTickData()
            tick.symbol = symbol
            tick.vtSymbol = symbol
            tick.gatewayName = self.gatewayName
            #print 'tick.vtSymbol:',tick.vtSymbol
            self.tickDict[symbol] = tick
        else:
            tick = self.tickDict[symbol]
        #print 'tick.vtSymbol:',tick.vtSymbol
        rawData = data['data']
        tick.highPrice = float(rawData['high'])
        #print 'tick.highPrice:',tick.highPrice
        tick.lowPrice = float(rawData['low'])
        #print 'tick.lowPrice:',tick.lowPrice
        tick.lastPrice = float(rawData['last'])
        #print 'tick.lastPrice:',tick.lastPrice
        tick.volume = float(rawData['vol'])
        tick.upperLimit = float(rawData['limitHigh'])
        tick.lowerLimit = float(rawData['limitLow'])
        #print 'tick.volume:',tick.volume
        #print tick
        #tick.date, tick.time = generateDateTime(rawData['timestamp'])
        #print 'tick.__dict__:',tick.__dict__
        newtick = copy(tick)
        self.gateway.onTick(newtick)
        price_limitMap[tick.vtSymbol] = tick.upperLimit,tick.lowerLimit
        #print 'items()',price_limitMap.items()
        #print 'ontickerfachuqule'
        #print 'type_tick.vtSymbol',type(tick.vtSymbol)
        #print 'type_tick.upperLimit',type(tick.upperLimit)

        #print tick.upperLimit,tick.vtSymbol,tick.lowerLimit 
    #----------------------------------------------------------------------
    def onfutureDepth(self, data):
        """"""
        if 'data' not in data:
            return
        
        channel = data['channel']
        symbol = channelSymbolMap[channel]
        #print 'ondepth symbol:',symbol
        if symbol not in self.tickDict:
            tick = VtTickData()
            tick.symbol = symbol
            tick.vtSymbol = symbol
            tick.gatewayName = self.gatewayName
            self.tickDict[symbol] = tick
        else:
            tick = self.tickDict[symbol]
        #print tick.vtSymbol
        if 'data' not in data:
            return
        rawData = data['data']
        
        tick.bidPrice1, tick.bidVolume1 = rawData['bids'][0][0],rawData['bids'][0][2]
        tick.bidPrice2, tick.bidVolume2 = rawData['bids'][1][0],rawData['bids'][1][2]
        tick.bidPrice3, tick.bidVolume3 = rawData['bids'][2][0],rawData['bids'][2][2]
        tick.bidPrice4, tick.bidVolume4 = rawData['bids'][3][0],rawData['bids'][3][2]
        tick.bidPrice5, tick.bidVolume5 = rawData['bids'][4][0],rawData['bids'][4][2]
        
        #print tick.bidPrice1
        tick.askPrice1, tick.askVolume1 = rawData['asks'][-1][0],rawData['asks'][-1][2]
        tick.askPrice2, tick.askVolume2 = rawData['asks'][-2][0],rawData['asks'][-2][2]
        tick.askPrice3, tick.askVolume3 = rawData['asks'][-3][0],rawData['asks'][-3][2]
        tick.askPrice4, tick.askVolume4 = rawData['asks'][-4][0],rawData['asks'][-4][2]
        tick.askPrice5, tick.askVolume5 = rawData['asks'][-5][0],rawData['asks'][-5][2]  
        #print tick.askPrice1,tick.askVolume1
        
        tick.date, tick.time = generateDateTime(rawData['timestamp'])
        #print 'tick.__dict__:',tick.__dict__
        
        newtick = copy(tick)
        self.gateway.onTick(newtick)
        #print 'GATEGAYtime:',tick.time
        #print 'onDepth fa chuqu'
    #----------------------------------------------------------------------
    def onfutureUserInfo(self, data):
        """qi货账户资金推送"""
        #print 'onfutureUserInfo shoudao '
        if 'data' not in data:
            return
        rawData = data['data']
        if 'info' not in rawData:
            return
        info = rawData['info']
        #print 'info:',info

        #btc = rawData['info']['btc']
        # 账户资金
        for symbol in ['btc', 'bcc','ltc','etc','eth','eos', self.currency]:
            if symbol in info:
                #print 'zhanghu zijin tuisong'
                account = VtAccountData()

                shifochicang = info[symbol]['contracts']
                #print 'shifochicang:',shifochicang
                #print 'account.available:',account.available
                #if shifochicang.strip()=='':
                #print 'len(shifochicang):',len(shifochicang)
                if len(shifochicang) > 0:
                    account.gatewayName = self.gatewayName
                    #print 'account.gatewayName:',account.gatewayName
                    account.accountID = self.gatewayName+'_'+symbol
                    #print account.accountID
                    account.vtAccountID = account.accountID
                    #print account.vtAccountID
                    #quanyi
                    account.balance = float(info[symbol]['rights'])
                    #print account.balance
                    #baozhengjing
                    account.margin = float(info[symbol]['contracts'][0]['bond'])
                    #print 'account.margin:',account.margin
                    #bi zhong ke yong yu e
                    account.available = float(info[symbol]['balance'])
                    #print 'account.available:',account.available
                    #ping cang ying kui
                    account.closeProfit = float(info[symbol]['contracts'][0]['profit'])
                    #print 'account.closeProfit:',account.closeProfit
                    #chi cang ying kui
                    account.positionProfit = float(info[symbol]['contracts'][0]['unprofit'])
                    #print account.positionProfit
                    #print 'symbol:',symbol
                    #print 'account.balance:',account.balance
                    if account.balance > 0:
                        self.gateway.onAccount(account)    
                    #print'print account.__dict__:',account.__dict__
        
        # 持仓信息
        for symbol in ['btc', 'bcc','ltc','etc','eth','eos', self.currency]:
            if symbol in info:
                #print 'symbol:',symbol
                #for x in info[symbol]['contracts']:
                shifochicang = info[symbol]['contracts']
                #print 'shifochicang:',shifochicang
                #print 'account.available:',account.available
                #if shifochicang.strip()=='':
                #print 'len(shifochicang):',len(shifochicang)
                if len(shifochicang) > 0:
                    pinzhong_val = len(shifochicang)
                    while pinzhong_val > 0:
                        val1 = pinzhong_val - 1
                        pinzhong_val = val1
                        if (val1+1) % 2 == 1:
                            v_pos = VtPositionData()
                            v_pos.gatewayName = self.gatewayName
                            #print 'pos.gatewayName:',pos.gatewayName
                            #print info[symbol]
                            #print info[symbol]['contracts']
                            #print info[symbol]['contracts'][0]['contract_type']
                            #infoval = info[symbol]['contracts'][0]['contract_type']
                            #print 'infoval',infoval
                            #a1 = 'btc_usd_quarter'
                            #print 'a1:',a1
                            #b = futureSymbolMap[a1]
                            #print 'b:',b
                            heyuedaima = str(symbol+'_'+self.currency+'_'+info[symbol]['contracts'][val1]['contract_type'])
                            #btc_usd_quarter
                            v_pos.symbol = futureSymbolMap[heyuedaima]
                            #print 'pos.symbol:',pos.symbol
                            v_pos.vtSymbol = v_pos.symbol
                            v_pos.vtPositionName = v_pos.symbol
                            #pos.direction = DIRECTION_NET
                            #posiDirectionMapReverse.get(data['PosiDirection'], '')               
                            #pos.frozen = float(funds['freezed'][symbol])
                            v_pos.frozen = float(info[symbol]['contracts'][val1]['bond'])
                            v_pos.positionProfit = float(info[symbol]['contracts'][val1]['unprofit'])
                            self.gateway.onPosition(v_pos)
                            #print 'pos.frozen:',pos.frozen
                            #pos.position = pos.frozen + float(info[symbol]['contracts'][0]['available'])
                            #print 'pos.position:',pos.position
                            
                        else:
                            b_pos = VtPositionData()
                            b_pos.gatewayName = self.gatewayName
                            heyuedaima = str(symbol+'_'+self.currency+'_'+info[symbol]['contracts'][val1]['contract_type'])
                            #btc_usd_quarter
                            b_pos.symbol = futureSymbolMap[heyuedaima]
                            b_pos.vtSymbol = b_pos.symbol
                            b_pos.vtPositionName = b_pos.symbol
                            b_pos.frozen = float(info[symbol]['contracts'][val1]['bond'])
                            b_pos.positionProfit = float(info[symbol]['contracts'][val1]['unprofit'])
                            self.gateway.onPosition(b_pos)
    
    #----------------------------------------------------------------------
    #官方的API 有争议，暂时不做了
    def onfutureSubUserInfo(self, data):
        """账户资金推送"""
        if 'data' not in data:
            return
        
        rawData = data['data']
        info = rawData['info']
        
        # 持仓信息
        for symbol in ['btc', 'ltc','eth', self.currency]:
            if symbol in info['free']:
                pos = VtPositionData()
                pos.gatewayName = self.gatewayName
                
                pos.symbol = symbol
                pos.vtSymbol = symbol
                pos.vtPositionName = symbol
                pos.direction = DIRECTION_NET
                
                pos.frozen = float(info['freezed'][symbol])
                pos.position = pos.frozen + float(info['free'][symbol])
                
                self.gateway.onPosition(pos)
    #----------------------------------------------------------------------
    #----------------------------------------------------------------------
    def onfutureSubTrades(self, data):
        """成交和委托推送"""
        """
        # Response
        [{
                "data":{
                    amount:1
                    contract_id:20170331115,
                    contract_name:"LTC0331",
                    contract_type:"this_week",
                    create_date:1490583736324,
                    create_date_str:"2017-03-27 11:02:16",
                    deal_amount:0,
                    fee:0,
                    lever_rate:20,
                    orderid:5058491146,
                    price:0.145,
                    price_avg:0,
                    status:0,
                    system_type:0,
                    type:1,
                    unit_amount:10,
                    user_id:101
                },
                "channel":"ok_sub_futureusd_trades"
            }
        ]
        """
        try:
            #self.writeLog(u'onfutureSubTrades 函数开始运行')
            #self.writeLog(str(data))
            if 'data' not in data:
                return
            rawData = data['data']
            if 'contract_name' not in rawData:
                return
            
            # 本地和系统委托号
            #print 'rawData:',rawData
            #print 'rawData_orderid:',rawData['orderid']
            #print type(rawData['orderid'])
            orderId = str(rawData['orderid'])
            #self.writeLog(str(self.orderIdDict[orderId]))      
            if orderId in self.orderIdDict.keys():
                localNo = self.orderIdDict[orderId]
                # 委托信息
                if orderId not in self.orderDict:
                    order = VtOrderData()
                    order.gatewayName = self.gatewayName
                    
                    heyuedaima2 = str(rawData['contract_name'][:3].lower()+'_'+'usd'+'_'+rawData['contract_type'])
                    order.symbol = futureSymbolMap[heyuedaima2]
                    #order.symbol = futureSymbolMap[rawData['symbol']]

                    order.vtSymbol = order.symbol
            
                    order.orderID = localNo
                    order.vtOrderID = '.'.join([self.gatewayName, order.orderID])
                    
                    order.price = float(rawData['price'])
                    order.totalVolume = float(rawData['amount'])
                    #order.direction, priceType = priceTypeMap[rawData['tradeType']]
                    order.direction, order.offset = futurepriceTypeMap[str(rawData['type'])]
                    #委托时间设置的是接到 回报 的时间，所以不是特别准，要延迟
                    #order.orderTime = datetime.now().strftime('%H:%M:%S')
                    order.orderTime = generatedt(rawData['create_date'])
                    #type_ = futurepriceTypeMapReverse[(req.direction, req.offset)]    
                    
                    self.orderDict[orderId] = order
                else:
                    order = self.orderDict[orderId]
                #获取上次成交数量，order.tradedVolume初始值默认是0，保存当次成交全量
                lastTradedVolume = order.tradedVolume   
                order.tradedVolume = float(rawData['deal_amount'])

                order.status = statusMap[rawData['status']]

                self.writeLog('SubTrades.orderId:%s' % orderId)
                self.writeLog('SubTrades.localNo:%s' % localNo)
                #正在撤单的不再删除
                if order.status == STATUS_ALLTRADED or order.status == STATUS_CANCELLED:
                    #self.orderIdDict[orderId]
                    self.orderIdDict.pop(orderId)
                    self.localNoDict.pop(localNo)

                    self.orderinfoDict.pop(localNo)

                    self.writeLog('SubTrades_hou.localNo:%s' % localNo)
                    #self.writeLog('SubTrades.orderinfoDict.value:%s %s' % (self.orderinfoDict[localNo][0],self.orderinfoDict[localNo][1]))



                self.gateway.onOrder(copy(order))
                self.writeLog('order.__dict__:')
                self.writeLog(str(order.__dict__))
                
                
                # 成交信息
                # 如果当此成交全量大于上次成交全量，order.tradedVolume 是全量成交量
                if order.tradedVolume > lastTradedVolume:
                #if 'deal_amount' in rawData and float(rawData['deal_amount'])>0:
                    trade = VtTradeData()
                    trade.gatewayName = self.gatewayName

                    heyuedaima3 = str(rawData['contract_name'][:3].lower()+'_'+'usd'+'_'+rawData['contract_type'])
                    trade.symbol = futureSymbolMap[heyuedaima3]
                    #trade.symbol = spotSymbolMap[rawData['symbol']]
                    trade.vtSymbol = trade.symbol            
                    #并未采用vnpy的原生借口写法，而是使用订单号+全部成交数量来作为唯一的vtTradeID
                    trade.tradeID = str(rawData['orderid'])
                    trade.vtTradeID = '.'.join([self.gatewayName, trade.tradeID,str(order.tradedVolume)])
                    #self.tradeID += 1
                    #trade.tradeID = str(self.tradeID)
                    #trade.vtTradeID = '.'.join([self.gatewayName, trade.tradeID])
                    
                    trade.orderID = localNo
                    trade.vtOrderID = '.'.join([self.gatewayName, trade.orderID])
                    
                    trade.price = float(rawData['price_avg'])
                    #trade.volume = float(rawData['deal_amount'])
                    #本次成交数量等于 当此成交全量- 上次成交全量
                    trade.volume = order.tradedVolume - lastTradedVolume
                    
                    #trade.direction, priceType = priceTypeMap[rawData['tradeType']] 
                    trade.direction, trade.offset = futurepriceTypeMap[str(rawData['type'])]   
                    
                    #trade.tradeTime = datetime.now().strftime('%H:%M:%S')
                    trade.tradeTime = generatedt(rawData['create_date'])
                    trade.system_type = str(rawData['system_type'])
                    trade.status = statusMap[rawData['status']]
                    
                    self.gateway.onTrade(trade)
                    #self.writeLog('okgate_trade.__dict__:',trade.jiaogeday)

                    #self.writeLog(str(trade.__dict__))
            else:
                # 现在的处理方式是， 先缓存这里的信息，等到出现了 localID，再来处理这一段
                self.cache_some_order[orderId] = data

                # localNo = self.orderIdDict.get(orderId, None)
                # if localNo == None:
                #     arr = self.cache_some_order.get(orderId, None)
                #     if arr == None:
                #         arr = []
                #         arr.append(data)
                #         self.cache_some_order[orderId] = arr
                #     else:
                #         arr.append(data)
                #     return  
            """
            else:
                if 'deal_amount' in rawData and float(rawData['deal_amount'])>0:
                    trade = VtTradeData()
                    trade.gatewayName = self.gatewayName

                    heyuedaima3 = str(rawData['contract_name'][:3].lower()+'_'+'usd'+'_'+rawData['contract_type'])
                    trade.symbol = futureSymbolMap[heyuedaima3]
                    #trade.symbol = spotSymbolMap[rawData['symbol']]
                    trade.vtSymbol = trade.symbol            
                    
                    trade.tradeID = str(rawData['orderid'])
                    trade.vtTradeID = '.'.join([self.gatewayName, trade.tradeID])
                    
                    trade.orderID = trade.tradeID
                    trade.vtOrderID = '.'.join([self.gatewayName, trade.orderID])
                    
                    trade.price = float(rawData['price_avg'])
                    trade.volume = float(rawData['deal_amount'])
                    
                    #trade.direction, priceType = priceTypeMap[rawData['tradeType']] 
                    trade.direction, trade.offset = futurepriceTypeMap[str(rawData['type'])]   
                    
                    trade.tradeTime = datetime.now().strftime('%H:%M:%S')
                    trade.system_type = str(rawData['system_type'])
                    
                    self.gateway.onTrade(trade)
                    #self.writeLog('okgate_trade.__dict__:')
                    #self.writeLog(str(trade.__dict__))
        """
        except Exception as e:
            logging.debug(u'okgateway_onfutureOrderInfo_hanshu:%s',e)
    #----------------------------------------------------------------------
    def onfutureOrderInfo(self, data):
        """委托信息查询回调"""
        """
        {u'binary': 0, u'data': {u'result': True, u'orders': [{u'status': 0, u'contract_name': u'BTC0629', u'fee': 0, u'create_date': 1528269486000L, u'order_id': 886930540477440L, u'symbol': u'btc_usd', u'amount': 10, u'unit_amount': 100, u'price_avg': 0, u'lever_rate': 10, u'type': 1, u'price': 7983.32, u'deal_amount': 0}]}, u'channel': u'ok_futureusd_orderinfo'}
        """
        try:
            #print u'老子不做了，老子觉得没用'
            print u'麻痹，我错了，我会老实的做好'
            if 'data' not in data:
                return
            rawData = data['data']
            rawData = rawData['orders'][0]
            
            # 本地和系统委托号
            #print 'rawData:',rawData
            #print 'rawData_orderid:',rawData['orderid']
            #print type(rawData['orderid'])
            orderId = str(rawData['order_id'])
            #self.writeLog(str(self.orderIdDict[orderId]))      
            if orderId in self.orderIdDict.keys():
                localNo = self.orderIdDict[orderId]
                # 委托信息
                if orderId not in self.orderDict:
                    order = VtOrderData()
                    order.gatewayName = self.gatewayName
                    
                    #heyuedaima2 = str(rawData['contract_name'][:3].lower()+'_'+'usd'+'_'+rawData['contract_type'])
                    heyuedaima3 = str(self.orderinfoDict[localNo][0]+'usd'+'_'+self.orderinfoDict[localNo][1])
                    order.symbol = futureSymbolMap[heyuedaima3]

                    order.vtSymbol = order.symbol
            
                    order.orderID = localNo
                    order.vtOrderID = '.'.join([self.gatewayName, order.orderID])
                    
                    order.price = float(rawData['price'])
                    order.totalVolume = float(rawData['amount'])
                    #order.direction, priceType = priceTypeMap[rawData['tradeType']]
                    order.direction, order.offset = futurepriceTypeMap[str(rawData['type'])]
                    #委托时间设置的是接到 回报 的时间，所以不是特别准，要延迟
                    #order.orderTime = datetime.now().strftime('%H:%M:%S')
                    order.orderTime = generatedt(rawData['create_date'])
                    #type_ = futurepriceTypeMapReverse[(req.direction, req.offset)]    
                    
                    self.orderDict[orderId] = order
                else:
                    order = self.orderDict[orderId]
                #获取上次成交数量，order.tradedVolume初始值默认是0，保存当次成交全量
                lastTradedVolume = order.tradedVolume     
                order.tradedVolume = float(rawData['deal_amount'])
                order.status = statusMap[rawData['status']]

                self.writeLog('OrderInfo.orderId:%s' % orderId)
                self.writeLog('OrderInfo_hou.localNo:%s' % localNo)

                self.writeLog('OrderInfo.orderinfoDict.keys:%s' %self.orderinfoDict.keys())
                self.writeLog('OrderInfo.orderinfoDict.value:%s %s' % (self.orderinfoDict[localNo][0],self.orderinfoDict[localNo][1]))

                
                    #self.writeLog('OrderInfo_hou.orderinfoDict.value:%s %s' % (self.orderinfoDict[localNo][0],self.orderinfoDict[localNo][1]))
                
                self.gateway.onOrder(copy(order)) 
                # 成交信息
                # 如果当此成交全量大于上次成交全量，order.tradedVolume 是全量成交量
                if order.tradedVolume > lastTradedVolume:
                #if 'deal_amount' in rawData and float(rawData['deal_amount'])>0 and float(rawData['status']) == 2:
                    trade = VtTradeData()
                    trade.gatewayName = self.gatewayName

                    #heyuedaima3 = str(rawData['contract_name'][:3].lower()+'_'+'usd'+'_'+rawData['contract_type'])
                    #trade.symbol = futureSymbolMap[heyuedaima3]
                    heyuedaima4 = str(self.orderinfoDict[localNo][0]+'usd'+'_'+self.orderinfoDict[localNo][1])
                    trade.symbol = futureSymbolMap[heyuedaima4]
                    trade.vtSymbol = trade.symbol
                    trade.tradeID = str(rawData['order_id'])
                    trade.vtTradeID = '.'.join([self.gatewayName, trade.tradeID,str(order.tradedVolume)])
                    
                    trade.orderID = localNo
                    trade.vtOrderID = '.'.join([self.gatewayName, trade.orderID])
                    
                    trade.price = float(rawData['price_avg'])
                    #trade.volume = float(rawData['deal_amount'])
                    #本次成交数量等于 当此成交全量- 上次成交全量
                    trade.volume = order.tradedVolume - lastTradedVolume
                    
                    #trade.direction, priceType = priceTypeMap[rawData['tradeType']] 
                    trade.direction, trade.offset = futurepriceTypeMap[str(rawData['type'])]   
                    
                    #trade.tradeTime = datetime.now().strftime('%H:%M:%S')
                    trade.tradeTime = generatedt(rawData['create_date'])
                    #trade.system_type = str(rawData['system_type'])
                    trade.status = statusMap[rawData['status']]
                    self.gateway.onTrade(trade)
                #正在撤单的不再删除
                if order.status == STATUS_ALLTRADED or order.status == STATUS_CANCELLED:
                    #self.orderIdDict[orderId]
                    self.orderIdDict.pop(orderId)
                    self.localNoDict.pop(localNo)
                    #del self.orderinfoDict[localNo]
                    self.orderinfoDict.pop(localNo)

                    self.writeLog('OrderInfo_trad_hou_pop.localNo:%s' % localNo)
                    self.writeLog('OrderInfo_trad_hou_pop.orderId:%s' % orderId)
        except Exception as e:
            logging.debug(u'okgateway_onfutureOrderInfo_hanshu:%s',e)       
        #----------------------------------------------------------------------
    def onfutureTrade(self, data,localNo,req):
        """委托回报"""

        """
        data:
        {u'binary': 0, u'data': {u'order_id': 1212004997697536L, u'result': True}, u'channel': u'ok_futureusd_trade'}

        {u'binary': 0, u'data': {u'orderid': 891819979523072L, u'contract_name': u'EOS0608', u'fee': 0.0, u'user_id': 2030364, u'contract_id': 201806080200054L, u'price': 14.386, u'create_date_str': u'2018-06-07 12:01:32', u'amount': 1.0, u'status': 0, u'system_type': 0, u'unit_amount': 10.0, u'price_avg': 0.0, u'contract_type': u'this_week', u'create_date': 1528344092973L, u'lever_rate': 10.0, u'type': 1, u'deal_amount': 0.0}, u'channel': u'ok_sub_futureusd_trades'}
        {"result":false,"error_code":20016}
        {"result":true,"order_id":895772438776832}
        reg:{'optionType': u'', 'direction': u'\u7a7a', 'exchange': 'OKCOIN', 'symbol': 'BTC_USD_QUARTER', 'productClass': '', 'strikePrice': 0.0, 'expiry': '', 'volume': 22, 'currency': '', 'multiplier': '', 'vtSymbol': 'BTC_USD_QUARTER', 'offset': u'\u5e73\u4ed3', 'lastTradeDateOrContractMonth': '', 'price': 7516.05, 'priceType': u'\u9650\u4ef7'}
        """
        #self.writeLog('onfuture_orderId:{},{},{}'.format(data,localNo,req))
        try:
            if 'data' not in data:
                return
            rawData = data['data']
            if str(rawData['result']) == 'True':
                orderId = str(rawData['order_id'])
                self.writeLog('onfuture_orderId:%s' % orderId)

                
                # 尽管websocket接口的委托号返回是异步的，但经过测试是
                # 符合先发现回的规律，因此这里通过queue获取之前发送的
                # 本地委托号，并把它和推送的系统委托号进行映射
                # 不准确，直接法国来准确
                ###localNo = self.localNoQueue.get_nowait()
                localNo = str(localNo)
                self.writeLog('onfuture_localNo:%s' % localNo)
                
                self.localNoDict[localNo] = orderId
                self.orderIdDict[orderId] = localNo
                
                ##self.writeLog('self.local') 
                ##self.writeLog(localNo)
                #self.writeLog(self.localNoDict)
                ##self.writeLog('self.orderIdDict')
                #self.writeLog(self.orderIdDict)
                # 检查是否有系统委托号返回前就发出的撤单请求，若有则进
                # 行撤单操作
                if localNo in self.cancelDict:
                    req1 = self.cancelDict[localNo]
                    self.futureCancel(req1)
                    del self.cancelDict[localNo]
                #orderinfoDict
                linshi_1 = []
                #linshi_1.append(str(symbol))
                #linshi_1.append(str(expiry))
                linshi_1.append(str(futureSymbolMapReverse[req.symbol][:4]))
                linshi_1.append(str(futureSymbolMapReverse[req.symbol][8:]))
                self.writeLog('linshi_1:%s' % linshi_1)
                self.orderinfoDict[str(localNo)] = linshi_1
                self.writeLog('okgw_onfutureTrade.orderinfoDict.keys:%s' % self.orderinfoDict.keys())
                self.writeLog('okgw_onfutureTrade.orderinfoDict.value:%s %s' % (self.orderinfoDict[str(self.localNo)][0],self.orderinfoDict[str(self.localNo)][1]))

                #去缓存里查找一下
                if orderId in self.cache_some_order.keys():
                    self.writeLog('okgw_onfutureTrade.cache_pipei_keys:%s' % (self.cache_some_order.keys()))
                    o_data = self.cache_some_order[orderId]
                    self.writeLog('okgw_onfutureTrade.cache_pipei_ok:%s %s' % (orderId,o_data))

                    self.onfutureSubTrades(o_data)
                    self.cache_some_order.pop(orderId)

                    self.writeLog('okgw_onfutureTrade.cache_pipei_keys:%s' % (self.cache_some_order.keys()))


            elif str(rawData['result']) == 'False':
                order = VtOrderData()
                order.gatewayName = self.gatewayName
                order.symbol = str(req.symbol)
                order.vtSymbol = str(req.symbol)
                order.orderID = str(localNo)
                order.vtOrderID = '.'.join([self.gatewayName, order.orderID])
                order.price = float(req.price)
                order.totalVolume = float(req.volume)
                order.direction = req.direction
                order.offset = req.offset
                #委托时间设置的是接到 回报 的时间，所以不是特别准，要延迟
                order.orderTime = datetime.now().strftime('%Y%m%d %H:%M:%S.%f')
                order.status = STATUS_REJECTED

                self.writeLog('okgw_onfutureTrade_judan.order.vtOrderID:%s' % order.vtOrderID)
                self.writeLog('okgw_onfutureTrade_judan.order.status:%s' % order.status)
                self.writeLog('okgw_onfutureTrade_judan.order.status:%s' % order.__dict__)
                self.gateway.onOrder(order)
        except Exception as e:
            logging.debug(u'okgateway_onfutureTrade_hanshu:%s',e)
    
    #----------------------------------------------------------------------
    def onfutureCancelOrder(self, data):
        """撤单回报"""
        pass
    
    #----------------------------------------------------------------------
    def futureSendOrder(self, req):
        """发单"""
        # 访问频率 5次/1秒(按币种单独计算)
        try:
            #req.symbol = 'BTC_USD_NEXTWEEK'
            symbol = futureSymbolMapReverse[req.symbol][:4]
            #print 'futureSendOrder_symbol',symbol
            self.writeLog('futureSendOrder_symbol')
            ##self.writeLog(symbol)
            #fangxiang 
            type_ = futurepriceTypeMapReverse[(req.direction, req.offset)]
            ##self.writeLog('futureSendOrder_type_')
            ##self.writeLog(type_)
            expiry = futureSymbolMapReverse[req.symbol][8:]
            #print 'futureSendOrder_expiry',symbol
            ##self.writeLog('futureSendOrder_expiry')
            ##self.writeLog(expiry)
            #
            ###暂时都按照限价单的顶格价来发
            #order = shijiadanMap[req.priceType]
            
            logging.debug('futureSendOrder_reg:%s',req.__dict__)

            try:
                if req.direction == DIRECTION_LONG and req.offset == OFFSET_OPEN:
                    price = price_limitMap[req.symbol][0]
                    order = '0'
                elif req.direction == DIRECTION_SHORT and req.offset == OFFSET_OPEN:
                    price = price_limitMap[req.symbol][1]
                    order = '0'
                else:
                    price = req.price
                    order = '1'
                logging.debug('TdexGateway_futureSendOrder_limit_req.price:%s',price)
                logging.debug('TdexGateway_futureSendOrder:%s',order)
            except Exception,e:
                 logging.debug(u'lim出错:%s',e)
                 price =req.price
                 order = '1'



            #self.writeLog(u'order发单类型%s:' %(order))
            #print 'futureSendOrder_order:',order
            ##self.writeLog(order)
            leverage = ganggan
            #print 'leverage:',leverage
            ##self.writeLog(leverage)
            # 本地委托号加1，并将对应字符串保存到队列中，返回基于本地委托号的vtOrderID
            self.localNo += 1
            #self.localNoQueue.put(str(self.localNo))
            vtOrderID = '.'.join([self.gatewayName, str(self.localNo)])
            

            try:
                data = self.futureTrade(symbol, expiry, type_, price, req.volume, order, leverage)
                #data = self.futureTrade(symbol, expiry, type_, req.price, req.volume, order, leverage)
            except:
                msg = traceback.format_exc()
                logging.debug(u'okgateway发单出错:{}'.format(msg))
            


            
            #futureTrade(self, symbol, expiry, type_, price, amount, order, leverage)
            
            

            #self.writeLog('fadan_data:%s' % data)
            
            #没办法,只能这么模仿ws
            if data is not None:
                try:
                    data = json.loads(data)
                except:
                    data = json.dumps(data)
                    data = json.loads(data)            
                    # logging.debug(u'okgatewaydata_JSON_LOAD出错:{}'.format(e))
                #fadan_data2:{u'binary': 0, u'data': {u'order_id': 895772438776832L, u'result': True}, u'channel': u'ok_futureusd_trade'}
                self.writeLog('fadan_data2:%s' % data)
                lin_localNo = self.localNo
                self.onfutureTrade(data,lin_localNo,req)

                return vtOrderID
            
        except:
            msg = traceback.format_exc()
            logging.debug(u'okgatewaydata_hanshu:{}'.format(msg))
    #----------------------------------------------------------------------
    def futureCancel(self, req):
        """撤单"""
        try:
            #symbol = spotSymbolMapReverse[req.symbol][:4]
            symbol = futureSymbolMapReverse[req.symbol][:4]
            expiry = futureSymbolMapReverse[req.symbol][8:]
            localNo = req.orderID
            
            if localNo in self.localNoDict:
                orderID = self.localNoDict[localNo]
                self.futureCancelOrder(symbol, expiry, orderID)
                #def futureCancelOrder(self, symbol, expiry, orderid):
            else:
                # 如果在系统委托号返回前客户就发送了撤单请求，则保存
                # 在cancelDict字典中，等待返回后执行撤单任务
                self.cancelDict[localNo] = req
        except Exception,e:
                logging.debug(u'okgateway_futureCancel_出错:%s',e)
    #----------------------------------------------------------------------
    #----------------------------------------------------------------------
    #----------------------------------------------------------------------
    #----------------------------------------------------------------------
    #----------------------------------------------------------------------
    #----------------------------------------------------------------------
    #----------------------------------------------------------------------
    #----------------------------------------------------------------------
    #----------------------------------------------------------------------
    #----------------------------------------------------------------------
    #----------------------------------------------------------------------
    #----------------------------------------------------------------------
    #----------------------------------------------------------------------
    #----------------------------------------------------------------------
    #----------------------------------------------------------------------
    #----------------------------------------------------------------------
    #----------------------------------------------------------------------
    #----------------------------------------------------------------------
    #----------------------------------------------------------------------
    #----------------------------------------------------------------------
    #----------------------------------------------------------------------
    #----------------------------------------------------------------------
    #-----------------------------------------------------------------------
    #----------------------------------------------------------------------
    def onTicker(self, data):
        """"""
        #print 'onticker qidong'
        if 'data' not in data:
            return
        
        channel = data['channel']
        #print 'on tick channel:',channel
        symbol = channelSymbolMap[channel]
        #print 'ontick symbol:',symbol
        
        if symbol not in self.tickDict:
            tick = VtTickData()
            tick.symbol = symbol
            tick.vtSymbol = symbol
            tick.gatewayName = self.gatewayName
            #print 'tick.vtSymbol:',tick.vtSymbol
            self.tickDict[symbol] = tick
        else:
            tick = self.tickDict[symbol]
        #print 'tick.vtSymbol:',tick.vtSymbol
        rawData = data['data']
        tick.highPrice = float(rawData['high'])
        #print 'tick.highPrice:',tick.highPrice
        tick.lowPrice = float(rawData['low'])
        #print 'tick.lowPrice:',tick.lowPrice
        tick.lastPrice = float(rawData['last'])
        #print 'tick.lastPrice:',tick.lastPrice
        tick.volume = float(rawData['vol'])
        #print 'tick.volume:',tick.volume
        #print tick
        #tick.date, tick.time = generateDateTime(rawData['timestamp'])
        #print 'tick.__dict__:',tick.__dict__
        newtick = copy(tick)
        self.gateway.onTick(newtick)
        #print 'ontickerfachuqule'
        #print tick.lastPrice
    
    #----------------------------------------------------------------------
    def onDepth(self, data):
        """"""
        if 'data' not in data:
            return
        
        channel = data['channel']
        symbol = channelSymbolMap[channel]
        print 'ondepth symbol:',symbol
        if symbol not in self.tickDict:
            tick = VtTickData()
            tick.symbol = symbol
            tick.vtSymbol = symbol
            tick.gatewayName = self.gatewayName
            self.tickDict[symbol] = tick
        else:
            tick = self.tickDict[symbol]
        #print tick.vtSymbol
        if 'data' not in data:
            return
        rawData = data['data']
        
        tick.bidPrice1, tick.bidVolume1 = rawData['bids'][0]
        tick.bidPrice2, tick.bidVolume2 = rawData['bids'][1]
        tick.bidPrice3, tick.bidVolume3 = rawData['bids'][2]
        tick.bidPrice4, tick.bidVolume4 = rawData['bids'][3]
        tick.bidPrice5, tick.bidVolume5 = rawData['bids'][4]
        
        print tick.bidPrice1
        tick.askPrice1, tick.askVolume1 = rawData['asks'][-1]
        tick.askPrice2, tick.askVolume2 = rawData['asks'][-2]
        tick.askPrice3, tick.askVolume3 = rawData['asks'][-3]
        tick.askPrice4, tick.askVolume4 = rawData['asks'][-4]
        tick.askPrice5, tick.askVolume5 = rawData['asks'][-5]     
        
        tick.date, tick.time = generateDateTime(rawData['timestamp'])
        print 'tick.__dict__:',tick.__dict__
        
        newtick = copy(tick)
        self.gateway.onTick(newtick)
        print 'tick.__dict__:',tick.__dict__
        print 'onDepth fa chuqu'
    
    #----------------------------------------------------------------------
    def onSpotUserInfo(self, data):
        """现货账户资金推送"""
        rawData = data['data']
        info = rawData['info']
        funds = rawData['info']['funds']
        
        # 持仓信息
        for symbol in ['btc', 'ltc','eth', self.currency]:
            if symbol in funds['free']:
                pos = VtPositionData()
                pos.gatewayName = self.gatewayName
                
                pos.symbol = symbol
                pos.vtSymbol = symbol
                pos.vtPositionName = symbol
                pos.direction = DIRECTION_NET
                
                pos.frozen = float(funds['freezed'][symbol])
                pos.position = pos.frozen + float(funds['free'][symbol])
                
                self.gateway.onPosition(pos)

        # 账户资金
        account = VtAccountData()
        account.gatewayName = self.gatewayName
        account.accountID = self.gatewayName
        account.vtAccountID = account.accountID
        account.balance = float(funds['asset']['net'])
        self.gateway.onAccount(account)    
        
    #----------------------------------------------------------------------
    def onSpotSubUserInfo(self, data):
        """现货账户资金推送"""
        if 'data' not in data:
            return
        
        rawData = data['data']
        info = rawData['info']
        
        # 持仓信息
        for symbol in ['btc', 'ltc','eth', self.currency]:
            if symbol in info['free']:
                pos = VtPositionData()
                pos.gatewayName = self.gatewayName
                
                pos.symbol = symbol
                pos.vtSymbol = symbol
                pos.vtPositionName = symbol
                pos.direction = DIRECTION_NET
                
                pos.frozen = float(info['freezed'][symbol])
                pos.position = pos.frozen + float(info['free'][symbol])
                
                self.gateway.onPosition(pos)  
                
    #----------------------------------------------------------------------
    def onSpotSubTrades(self, data):
        """成交和委托推送"""
        if 'data' not in data:
            return
        rawData = data['data']
        
        # 本地和系统委托号
        orderId = str(rawData['orderId'])
        localNo = self.orderIdDict[orderId]
        
        # 委托信息
        if orderId not in self.orderDict:
            order = VtOrderData()
            order.gatewayName = self.gatewayName
            
            order.symbol = spotSymbolMap[rawData['symbol']]
            order.vtSymbol = order.symbol
    
            order.orderID = localNo
            order.vtOrderID = '.'.join([self.gatewayName, order.orderID])
            
            order.price = float(rawData['tradeUnitPrice'])
            order.totalVolume = float(rawData['tradeAmount'])
            order.direction, priceType = priceTypeMap[rawData['tradeType']]    
            
            self.orderDict[orderId] = order
        else:
            order = self.orderDict[orderId]
            
        order.tradedVolume = float(rawData['completedTradeAmount'])
        order.status = statusMap[rawData['status']]
        
        self.gateway.onOrder(copy(order))
        
        # 成交信息
        if 'sigTradeAmount' in rawData and float(rawData['sigTradeAmount'])>0:
            trade = VtTradeData()
            trade.gatewayName = self.gatewayName
            
            trade.symbol = spotSymbolMap[rawData['symbol']]
            trade.vtSymbol = order.symbol            
            
            trade.tradeID = str(rawData['id'])
            trade.vtTradeID = '.'.join([self.gatewayName, trade.tradeID])
            
            trade.orderID = localNo
            trade.vtOrderID = '.'.join([self.gatewayName, trade.orderID])
            
            trade.price = float(rawData['sigTradePrice'])
            trade.volume = float(rawData['sigTradeAmount'])
            
            trade.direction, priceType = priceTypeMap[rawData['tradeType']]    
            
            trade.tradeTime = datetime.now().strftime('%H:%M:%S')
            
            self.gateway.onTrade(trade)
        
    #----------------------------------------------------------------------
    def onSpotOrderInfo(self, data):
        """委托信息查询回调"""
        rawData = data['data']
        
        for d in rawData['orders']:
            self.localNo += 1
            localNo = str(self.localNo)
            orderId = str(d['order_id'])
            
            self.localNoDict[localNo] = orderId
            self.orderIdDict[orderId] = localNo
            
            if orderId not in self.orderDict:
                order = VtOrderData()
                order.gatewayName = self.gatewayName
                
                order.symbol = spotSymbolMap[d['symbol']]
                order.vtSymbol = order.symbol
    
                order.orderID = localNo
                order.vtOrderID = '.'.join([self.gatewayName, order.orderID])
                
                order.price = d['price']
                order.totalVolume = d['amount']
                order.direction, priceType = priceTypeMap[d['type']]
                
                self.orderDict[orderId] = order
            else:
                order = self.orderDict[orderId]
                
            order.tradedVolume = d['deal_amount']
            order.status = statusMap[d['status']]            
            
            self.gateway.onOrder(copy(order))
    
    #----------------------------------------------------------------------
    def generateSpecificContract(self, contract, symbol):
        """生成合约"""
        new = copy(contract)
        new.symbol = symbol
        new.vtSymbol = symbol
        new.name = symbol
        return new

    #----------------------------------------------------------------------
    def generateCnyContract(self):
        """生成CNY合约信息"""
        contractList = []
        
        contract = VtContractData()
        contract.exchange = EXCHANGE_TDEX
        contract.productClass = PRODUCT_SPOT
        contract.size = 1
        contract.priceTick = 0.01
        
        contractList.append(self.generateSpecificContract(contract, BTC_CNY_SPOT))
        contractList.append(self.generateSpecificContract(contract, LTC_CNY_SPOT))
        contractList.append(self.generateSpecificContract(contract, ETH_CNY_SPOT))

        return contractList
    
    #----------------------------------------------------------------------
    def generateUsdContract(self):
        """生成USD合约信息"""
        contractList = []
        
        # 现货
        contract = VtContractData()
        contract.exchange = EXCHANGE_OKCOIN
        contract.productClass = PRODUCT_SPOT
        contract.size = 1
        contract.priceTick = 0.01
        
        contractList.append(self.generateSpecificContract(contract, BTC_USD_SPOT))
        contractList.append(self.generateSpecificContract(contract, LTC_USD_SPOT))
        contractList.append(self.generateSpecificContract(contract, ETH_USD_SPOT))

        # 期货
        contract.productClass = PRODUCT_FUTURES
        
        contractList.append(self.generateSpecificContract(contract, BTC_USD_THISWEEK))
        contractList.append(self.generateSpecificContract(contract, BTC_USD_NEXTWEEK))
        contractList.append(self.generateSpecificContract(contract, BTC_USD_QUARTER))
        contractList.append(self.generateSpecificContract(contract, LTC_USD_THISWEEK))
        contractList.append(self.generateSpecificContract(contract, LTC_USD_NEXTWEEK))
        contractList.append(self.generateSpecificContract(contract, LTC_USD_QUARTER))
        contractList.append(self.generateSpecificContract(contract, ETH_USD_THISWEEK))
        contractList.append(self.generateSpecificContract(contract, ETH_USD_NEXTWEEK))
        contractList.append(self.generateSpecificContract(contract, ETH_USD_QUARTER))
        contractList.append(self.generateSpecificContract(contract, ETC_USD_THISWEEK))
        contractList.append(self.generateSpecificContract(contract, ETC_USD_NEXTWEEK))
        contractList.append(self.generateSpecificContract(contract, ETC_USD_QUARTER))
        contractList.append(self.generateSpecificContract(contract, EOS_USD_THISWEEK))
        contractList.append(self.generateSpecificContract(contract, EOS_USD_NEXTWEEK))
        contractList.append(self.generateSpecificContract(contract, EOS_USD_QUARTER))

        
        return contractList        
    
    #----------------------------------------------------------------------
    def onSpotTrade(self, data):
        """委托回报"""
        rawData = data['data']
        orderId = rawData['order_id']
        
        # 尽管websocket接口的委托号返回是异步的，但经过测试是
        # 符合先发现回的规律，因此这里通过queue获取之前发送的
        # 本地委托号，并把它和推送的系统委托号进行映射
        localNo = self.localNoQueue.get_nowait()
        
        self.localNoDict[localNo] = orderId
        self.orderIdDict[orderId] = localNo
        
        # 检查是否有系统委托号返回前就发出的撤单请求，若有则进
        # 行撤单操作
        if localNo in self.cancelDict:
            req = self.cancelDict[localNo]
            self.spotCancel(req)
            del self.cancelDict[localNo]
    
    #----------------------------------------------------------------------
    def onSpotCancelOrder(self, data):
        """撤单回报"""
        pass
    
    #----------------------------------------------------------------------
    def spotSendOrder(self, req):
        """发单"""
        symbol = spotSymbolMapReverse[req.symbol][:4]
        type_ = priceTypeMapReverse[(req.direction, req.priceType)]
        self.spotTrade(symbol, type_, str(req.price), str(req.volume))
        
        # 本地委托号加1，并将对应字符串保存到队列中，返回基于本地委托号的vtOrderID
        self.localNo += 1
        self.localNoQueue.put(str(self.localNo))
        vtOrderID = '.'.join([self.gatewayName, str(self.localNo)])
        return vtOrderID
    
    #----------------------------------------------------------------------
    def spotCancel(self, req):
        """撤单"""
        symbol = spotSymbolMapReverse[req.symbol][:4]
        localNo = req.orderID
        
        if localNo in self.localNoDict:
            orderID = self.localNoDict[localNo]
            self.spotCancelOrder(symbol, orderID)
        else:
            # 如果在系统委托号返回前客户就发送了撤单请求，则保存
            # 在cancelDict字典中，等待返回后执行撤单任务
            self.cancelDict[localNo] = req
    
#----------------------------------------------------------------------
def generateDateTime(s):
    """生成时间"""
    dt = datetime.fromtimestamp(float(s)/1e3)
    time = dt.strftime("%H:%M:%S.%f")
    date = dt.strftime("%Y%m%d")
    return date, time
def generatedt(s):
    """生成时间"""
    dt = datetime.fromtimestamp(float(s)/1e3)
    dt = dt.strftime("%Y%m%d %H:%M:%S.%f")
    #time = dt.strftime("%H:%M:%S.%f")
    #date = dt.strftime("%Y%m%d")
    return dt




import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import os
import json
from datetime import datetime
from time import sleep
from copy import copy
from threading import Condition
from Queue import Queue
from threading import Thread
from time import sleep

#from vnpy.api.okcoin import vntdex
#from vnpy.trader.vtGateway import *
#from vnpy.trader.vtFunction import getJsonPath

"""
if __name__ == '__main__':
    
    guodudata = {u'data': {u'error_code': u'10001', u'result': u'false'}, u'channel': u'login'}
    print 'guodudata:',guodudata
    guodudata = [guodudata]
    guodudata = json.dumps(guodudata)
    print 'guodudata:',guodudata
    b = TdexGateway(VtGateway)
    a = Api(b)
    a.onMessage(guodudata)
"""
if __name__ == '__main__':
    #biaoti = str(1)
    #neirong = u'刚刚平仓8'
    #biaoti = u'测试标题8'
    #a= '"data":{"result":true,"order_id":15421781611}'
    #print a
    #b = json.loads(a)
    #print b
    
                
    #wx_neirong = u'%s止损后 close: %s > close_qianval: %s and atrValue:%s > atrMa:%s,%s@%s开多,止损价:%s' % (self.name,self.close,self.close_qianval,self.atrValue,self.atrMa,self.fixedSize,str(self.last + self.chajia),self.ll)
                
    #wx_server(neirong,trading = True)
    a = int('12')
    print a
    c = int(11)
    #d =a+'-'+c
    #b = datetime.strptime(d,'%m-%d')
    d = datetime.now().year
    #d =dir(datetime.now())
    e = datetime(d, a, c)
    print e