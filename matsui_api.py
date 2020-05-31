import json
import requests
import uuid
import hashlib
import time
import urllib.parse
import re

class matsui :
    def __init__(self) :
        self.session = requests.session()
        self.headers = {
            'Accept': '*/*',
            'Accept-Encoding': 'gzip, deflate, br',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36',
        }
        # self.auth_method = self.login_prompt
        self.session_id = ''
        self.ev_sid = ''
        self.attrsrckey = ''

    def login(self, username='', password='') :
        data = {'uid': 'NULLGWDOCOMO'}

        response = requests.get('http://pocket.matsui.co.jp/member/servlet/Login', params=data, headers=self.headers)
        # print(response.text)
        if response.status_code == 200 :
            match = re.search(r'\<INPUT\ type\=\"hidden\"\ value\=\"(.*)\" name\=\"EV\.SID\"\>', response.text, re.MULTILINE)
            self.ev_sid = match.group(1)

            self.headers['Cookie'] = response.headers['Set-Cookie']

        data = {'EV.URL': '/servlet/mobile/login/MbMemberLoginEnter',
                'EV.SID': self.ev_sid,
                'clientCD': username,
                'passwd': password,
                'easyLogin': 'yes',
                'easyTradeFlg': 1}

        response = requests.post('https://pocket.matsui.co.jp/member/servlet/Generic', data=data, headers=self.headers)
        # print(response.text)
        # print(response.headers)
        if 'Set-Cookie' in response.headers :
            self.headers['Cookie'] = response.headers['Set-Cookie']

        if response.status_code == 200 :
            match = re.search(r'\<INPUT\ type\=hidden\ name\=EV\.SID\ value\=(.*)\>', response.text, re.MULTILINE)
            self.ev_sid = match.group(1)
            match = re.search(r'\<INPUT\ type\=hidden\ name\=attrSrcKey\ value\=(.*)\>', response.text, re.MULTILINE)
            self.attrsrckey = match.group(1)

            return True
        else :
            return False

    def token(self, pin='') :
        data = {'EV.URL': urllib.parse.quote('/servlet/mobile/login/MbEasyTradePinNoCheck'),
                'EV.SID': self.ev_sid,
                'attrSrcKey': self.attrsrckey,
                'easyLogin': 'yes',
                'pinNo': pin,
                'CONFIRM': '%91%97%90M'}

        response = requests.get('https://pocket.matsui.co.jp/member/servlet/Generic', params=data, headers=self.headers)
        if 'Set-Cookie' in response.headers :
            self.headers['Cookie'] = response.headers['Set-Cookie']

        if response.status_code == 200 :
            return True
        else :
            return False

    def cash(self) :
        data = {'EV.URL': urllib.parse.quote('/servlet/mobile/asset/MbMoneyToSpare'),
                'EV.SID': self.ev_sid,
                'attrSrcKey': self.attrsrckey}

        response = requests.get('https://pocket.matsui.co.jp/member/servlet/Generic', params=data, headers=self.headers)

        if response.status_code == 200 :
            match = re.search(r'(.*)円<BR>', response.text, re.MULTILINE)

            return match.group(1)
        else :
            return False

    def portfolio(self) :
        data = {'EV.URL': urllib.parse.quote('/servlet/mobile/asset/MbAstDistribution'),
                'EV.SID': self.ev_sid,
                'attrSrcKey': self.attrsrckey}

        response = requests.get('https://pocket.matsui.co.jp/member/servlet/Generic', params=data, headers=self.headers)
        if response.status_code == 200 :
            portfolio = {}
            match = re.search(r'■資産総額<BR>\r\n(.*)円<BR>', response.text, re.MULTILINE)
            portfolio['total'] = match.group(1)
            match = re.search(r'■現金残高<BR>\r\n(.*)円<BR>', response.text, re.MULTILINE)
            portfolio['cash'] = match.group(1)
            match = re.search(r'■株式時価総額<BR>\r\n(.*)円<BR>', response.text, re.MULTILINE)
            portfolio['stock'] = match.group(1)
            match = re.search(r'■投信時価総額<BR>\r\n(.*)円<BR>', response.text, re.MULTILINE)
            portfolio['trust'] = match.group(1)

            return portfolio
        else :
            return False

    def tax(self) :
        data = {'EV.URL': urllib.parse.quote('/servlet/mobile/asset/MbSailPlDetail'),
                'EV.SID': self.ev_sid,
                'attrSrcKey': self.attrsrckey,
                'valueDTFrom': '202001',
                'valueDTTo': '202006',
                'RENEWAL': '%8DX%90V',}

        response = requests.get('https://pocket.matsui.co.jp/member/servlet/Generic', params=data, headers=self.headers)
        print(response.text)
        if response.status_code == 200 :
            tax = {}
            match = re.search(r'■譲渡損益合計<BR>\r\n(.*)円<BR>', response.text, re.MULTILINE)
            tax['taxable'] = match.group(1)
            match = re.search(r'所得税:<BR>\r\n(.*)円<BR>', response.text, re.MULTILINE)
            tax['income'] = match.group(1)
            match = re.search(r'地方税:<BR>\r\n(.*)円<BR>', response.text, re.MULTILINE)
            tax['local'] = match.group(1)

            return tax
        else :
            return False

    def history(self) :
        data = {'EV.URL': '/servlet/mobile/asset/MbDealArchive',
                'EV.SID': self.ev_sid,
                'attrSrcKey': self.attrsrckey}

        response = requests.get('https://pocket.matsui.co.jp/member/servlet/Generic', params=data, headers=self.headers)
        # print(response.text)
        if response.status_code == 200 :
            match = re.search(r'\<INPUT\ type\=hidden\ name\=EV\.SID\ value\=(.*)\>', response.text, re.MULTILINE)
            self.ev_sid = match.group(1)
            match = re.search(r'\<INPUT\ type\=hidden\ name\=attrSrcKey\ value\=(.*)\>', response.text, re.MULTILINE)
            self.attrsrckey = match.group(1)
        else :
            return False

        data = {'EV.URL': urllib.parse.quote('/servlet/mobile/asset/MbDealArchiveDetail'),
                'EV.SID': self.ev_sid,
                'attrSrcKey': self.attrsrckey,
                'CONFIRM': '%8C%9F%8D%F5&',
                'searchFromYear': '1',
                'searchFromMonth': '5',
                'searchFromDay': '30',
                'searchToYear': '0',
                'searchToMonth': '6',
                'searchToDay': '15',
                'searchDscr': '',
                'searchSpAccKbn': '-1',
                'searchSecType': '0',
                'searchTrade': '0',
                'searchSales': '0'}

        response = requests.get('https://pocket.matsui.co.jp/member/servlet/Generic', params=data, headers=self.headers)

        if response.status_code == 200 :
            print(response.text)
            # match = re.search(r'(.*)円<BR>', response.text, re.MULTILINE)

            # return match.group(1)
        else :
            return False

    def stock(self) :
        data = {'EV.URL': urllib.parse.quote('/servlet/mobile/asset/MbBalTransferLst'),
                'EV.SID': self.ev_sid,
                'attrSrcKey': self.attrsrckey,}

        response = requests.get('https://pocket.matsui.co.jp/member/servlet/Generic', params=data, headers=self.headers)
        print(response.text)
        if response.status_code == 200 :
            tax = {}
            match = re.search(r'■譲渡損益合計<BR>\r\n(.*)円<BR>', response.text, re.MULTILINE)
            tax['taxable'] = match.group(1)
            match = re.search(r'所得税:<BR>\r\n(.*)円<BR>', response.text, re.MULTILINE)
            tax['income'] = match.group(1)
            match = re.search(r'地方税:<BR>\r\n(.*)円<BR>', response.text, re.MULTILINE)
            tax['local'] = match.group(1)

            return tax
        else :
            return False

    def sell(self, stock='', count=0, price='') :
        data = {'EV.URL': '/servlet/mobile/stock/MbStkSellOrder',
                'EV.SID': self.ev_sid,
                'attrSrcKey': self.attrsrckey,
                'dscrCD': stock,
                'spAccKbn': 'TOKUTEI',
                'subGuarantyKbnPrm': '1',
                'CONFIRM': '確認'}

        response = requests.get('https://pocket.matsui.co.jp/member/servlet/Generic', params=data, headers=self.headers)
        # print(response.text)
        if response.status_code == 200 :
            match = re.search(r'\<INPUT\ type\=\"hidden\"\ name\=\"EV\.SID\"\ value\=\"(.*)\"\>', response.text, re.MULTILINE)
            self.ev_sid = match.group(1)
            match = re.search(r'\<INPUT\ type\=\"hidden\"\ name\=\"attrSrcKey\"\ value\=\"(.*)\"\>', response.text, re.MULTILINE)
            self.attrsrckey = match.group(1)
        else :
            return False

        data = {'EV.URL': '/servlet/mobile/stock/MbStkSellOrder',
                'EV.SID': self.ev_sid,
                'attrSrcKey': self.attrsrckey,
                'dscrCD': '1306',
                'spAccKbn': 'TOKUTEI',
                'subGuarantyKbnPrm': '1',
                'conditionKbn': '0',
                'commitFlg': 'true',
                'marketCD': 'T',
                'orderNominal': '10',
                'limitPrice': '1750',
                'execCondCD': '0',
                'validDT': 'TODAY',
                'CONFIRM': '発注'}

        response = requests.get('https://pocket.matsui.co.jp/member/servlet/Generic', params=data, headers=self.headers)
        # print(response.text)
        if response.status_code == 200 :
            match = re.search(r'\<INPUT\ type\=\"hidden\"\ name\=\"EV\.SID\"\ value\=\"(.*)\"\>', response.text, re.MULTILINE)
            self.ev_sid = match.group(1)
            match = re.search(r'\<INPUT\ type\=\"hidden\"\ name\=\"attrSrcKey\"\ value\=\"(.*)\"\>', response.text, re.MULTILINE)
            self.attrsrckey = match.group(1)
        else :
            return False

        data = {'EV.URL': urllib.parse.quote('/servlet/mobile/stock/MbStkSellOrderCom'),
                'EV.SID': self.ev_sid,
                'attrSrcKey': self.attrsrckey,
                'dscrCD': stock,
                'marketCD': 'T',
                'orderNominal': count,
                'limitPrice': price,
                'marketPrice': 'N', #N or Y
                'spAccKbn': 'TOKUTEI',
                'subGuarantyKbn': 'null',
                'validDT': '当日',
                'CONFIRM': '発注'
                }

        response = requests.get('https://pocket.matsui.co.jp/member/servlet/Generic', params=data, headers=self.headers)
        print(response.text)
        if response.status_code == 200 :
            return True
        else :
            return False

if __name__ == '__main__' :
    matsui = matsui()
    result = matsui.login()
    matsui.token()
    print(matsui.tax())
