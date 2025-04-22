from urllib import parse
from urllib.parse import urlencode, quote_plus,unquote
import json
import requests
from xml.etree.ElementTree import parse
from bs4 import BeautifulSoup
import pandas as pd
import get_today
import openpyxl
import day_calc
import api_unipass

class getInfo_api_importCargo():
    def tracking_importCargo1(self,bl): #수입화물진행정보
        print("검색",bl)
        self.fails = []
        lst = []
        new_api = api_unipass.unipass_api_Call()
        sub_yn = 'N'
        for x in range(len(bl)):
            try:
                for cnt in range(4): #4번 돈다
                    if cnt == 0:
                        mbl = bl[x][0]
                        hbl = ''
                        key = bl[x][1]
                        yy = bl[x][2]
                        area = bl[x][3]
                        datas = new_api.tracking_importcargo2(mbl,hbl,yy,key,area)
                        if isinstance(datas, tuple):
                            sub_yn = 'N'
                            datas = list(datas)
                            datas.append(sub_yn)
                            lst.append(datas)
                            break
                        elif isinstance(datas, list):  ### BL 하나에 두개 이상의 MRN 이 있는경우 따로 리스트에 저장후에 갯수만큼 mrn을 키로 조회 한번 더한다.
                            sub_yn = 'Y'
                            for dts in datas: #dts == mrn
                                datas = new_api.tracking_importcargo1(dts, yy, key, area)
                                datas = list(datas)
                                datas.append(sub_yn)
                                lst.append(datas)
                            break
                    elif cnt == 1:
                        mbl = ''
                        hbl = bl[x][0]
                        key = bl[x][1]
                        yy = bl[x][2]
                        area = bl[x][3]
                        datas = new_api.tracking_importcargo2(mbl, hbl, yy,key,area)
                        if isinstance(datas, tuple):
                            sub_yn = 'N'
                            datas = list(datas)
                            datas.append(sub_yn)
                            lst.append(datas)
                            break
                        elif isinstance(datas, list):  ### BL 하나에 두개 이상의 MRN 이 있는경우 따로 리스트에 저장후에 갯수만큼 mrn을 키로 조회 한번 더한다.
                            sub_yn = 'Y'
                            for dts in datas:
                                datas = new_api.tracking_importcargo1(dts, yy, key, area)
                                datas = list(datas)
                                datas.append(sub_yn)
                                lst.append(datas)
                            break
                    elif cnt == 2:
                        mbl = bl[x][0]
                        hbl = ''
                        try: # 수기입력건 year 필드에 년도 기재되지 않는 문제 있어, 에러 발생하였음.  수기입력 저장할때 년도 자동입력되도록 변경(2022-08-26)
                            yy = str(int(bl[x][2]) - 1)
                        except:
                            yy = get_today.get_date()[:4]
                            yy = str(int(yy) - 1)
                        key = bl[x][1]
                        area = bl[x][3]
                        datas = new_api.tracking_importcargo2(mbl, hbl, yy,key,area)
                        if isinstance(datas, tuple):
                            sub_yn = 'N'
                            datas = list(datas)
                            datas.append(sub_yn)
                            lst.append(datas)
                            break
                        elif isinstance(datas, list):  ### BL 하나에 두개 이상의 MRN 이 있는경우 따로 리스트에 저장후에 갯수만큼 mrn을 키로 조회 한번 더한다.
                            sub_yn = 'Y'
                            for dts in datas:
                                datas = new_api.tracking_importcargo1(dts, yy, key, area)
                                datas = list(datas)
                                datas.append(sub_yn)
                                lst.append(datas)
                            break
                    else:
                        mbl = ''
                        hbl = bl[x][0]
                        try:
                            yy = str(int(bl[x][2]) - 1)
                        except:
                            yy = get_today.get_date()[:4]
                            yy = str(int(yy) - 1)
                        key = bl[x][1]
                        area = bl[x][3]
                        datas = new_api.tracking_importcargo2(mbl, hbl, yy,key,area)
                        if isinstance(datas, tuple):
                            sub_yn = 'N'
                            datas = list(datas)
                            datas.append(sub_yn)
                            lst.append(datas)
                            break
                        elif isinstance(datas, list):  ### BL 하나에 두개 이상의 MRN 이 있는경우 따로 리스트에 저장후에 갯수만큼 mrn을 키로 조회 한번 더한다.
                            datas = new_api.tracking_importcargo1(datas[0], yy, key,area)
                            sub_yn = 'Y'
                            for dts in datas:
                                datas = new_api.tracking_importcargo1(dts, yy, key, area)
                                datas = list(datas)
                                datas.append(sub_yn)
                                lst.append(datas)
                            break
            except:
                pass
                self.fails.append([mbl,hbl])
        return lst

    def get_text(self,str): #str 은 리스트
        new_list = []
        for i in str:
            new_list.append(i.text)
        return new_list

    def get_bonded_areaCode(self,code):
        url = "https://unipass.customs.go.kr:38010/ext/rest/shedInfoQry/retrieveShedInfo"

        queryString = "?" + urlencode(
            {
                "crkyCn": unquote("c260z211n190e115m000w040f0"),
                "jrsdCstmCd": code[:3],
                "snarSgn": code,

            })
        queryURL = url + queryString
        response = requests.get(queryURL)
        res = response.text
        xmlsoup = BeautifulSoup(res, 'lxml')
        return xmlsoup




