import day_calc
import requests
from xml.etree.ElementTree import parse
from bs4 import BeautifulSoup
import get_today
from urllib.parse import urlencode, quote_plus,unquote
import datetime
import re

class unipass_api_Call():

    def chk_addTax_bd(self,code):
        print('code', code)
        url = "https://unipass.customs.go.kr:38010/ext/rest/shedInfoQry/retrieveShedInfo"
        queryString = "?" + urlencode(
            {
                "crkyCn": unquote("c260z211n190e115m000w040f0"),
                "snarSgn": code,

            })
        queryURL = url + queryString
        response = requests.get(queryURL)
        res = response.text
        xmlsoup = BeautifulSoup(res, 'lxml')
        jangchi_name = xmlsoup.find('snarnm')
        if jangchi_name:
            jangchi_name = jangchi_name.text
        else:
            jangchi_name = ''
        addtax = xmlsoup.find('adtxcoltpridyn')
        penalty = xmlsoup.find('pnltlvytrgtyn')
        print(addtax, penalty)
        if addtax:
            addtax = addtax.text
        else:
            addtax = 'N'
        if penalty:
            penalty = penalty.text
        else:
            penalty = 'N'
        lst = []
        lst.append(addtax)
        lst.append(penalty)
        lst.append(jangchi_name)

        return lst

    def update_napbu_date(self,okdate, jingsu, napbu_dt):
        print("납부일자 점검")
        import calendar
        gihan_dict = {"28": "14", "29": "15", "30": "16", "31": "17"}
        today = get_today.get_date()
        this_year = today[:4]
        this_month = today[4:6]
        this_month_enddate = str(calendar.monthrange(int(this_year), int(this_month))[1])
        if this_month == "12":
            next_year = int(this_year) + 1
            next_year = str(next_year)
            next_month = "1"
        else:
            next_year = this_year
            next_month = str(int(this_month) + 1)
        this_month = this_month.zfill(2)
        next_month = next_month.zfill(2)
        next_enddate = str(calendar.monthrange(int(next_year), int(next_month))[1])  # 징수형태 43 월말납부 납부일자
        if str(jingsu) == '11' or str(jingsu) == '14':
            napbu_date = napbu_dt
        elif str(jingsu) == '43':
            gihan_t = str(gihan_dict[this_month_enddate])
            gihan_t = gihan_t.zfill(2)
            gihan = this_year + this_month + gihan_t
            print("월/말일", this_month + "/" + this_month_enddate)
            print("납부기준일", gihan)
            print("수리일", okdate)
            if okdate <= gihan:
                napbu_date = this_year + this_month + this_month_enddate
            else:
                print("납부일 익월 이월")
                napbu_date = next_year + next_month + next_enddate
        return napbu_date

    def tracking_importcargo1(self,mrn,yy,key,area): # mrn 으로 조회해야 하는 경우 --> 하나의 bL에 두개이상의 화물관리번호가 존재할때 대비.  tracking_importcargo2 와 거의 중복

        url = "https://unipass.customs.go.kr:38010/ext/rest/cargCsclPrgsInfoQry/retrieveCargCsclPrgsInfo"
        queryString = "?" + urlencode(
            {
                "crkyCn": unquote("q240o252o006o156z060s090m0"),  # 관세법인 에스에이엠씨 인증키
                "cargMtNo": mrn,
                "mblNo": "",
                "hblNo": "",
                "blYy": yy

            })
        queryURL = url + queryString
        response = requests.get(queryURL)
        res = response.text
        xmlsoup = BeautifulSoup(res, 'lxml')
        dict = self.parsing_xml(xmlsoup,key,area)
        return dict

    def tracking_importcargo2(self,mbl,hbl,yy,key,area):

        url = "https://unipass.customs.go.kr:38010/ext/rest/cargCsclPrgsInfoQry/retrieveCargCsclPrgsInfo"
        queryString = "?" + urlencode(
            {
                "crkyCn": unquote("q240o252o006o156z060s090m0"), #관세법인 에스에이엠씨 인증키
                "cargMtNo": "",
                "mblNo": mbl,
                "hblNo": hbl,
                "blYy": yy

            })
        queryURL = url + queryString
        response = requests.get(queryURL)
        res = response.text
        xmlsoup = BeautifulSoup(res, 'lxml')
        dict = self.parsing_xml(xmlsoup,key,area)
        return dict

    def parsing_xml(self,xmlsoup,key,area):
        iphng_banip_storage_cd = ''
        iphng_banip_storage = ''
        iphng_banip_date = ''
        trans_banip_date = ''
        trans_banip_storage = ''
        trans_banip_storage_cd = ''
        impo_ok_date = ''
        impo_end_date = ''
        iphng_jangchi_gihan = ''
        banchul_gihan = ''
        update_complete = 'N'
        impo_singo_date = ''
        delay_add_tax = ''
        spp_stat = ''
        depart_cd = ''
        depart_name = ''

        today = get_today.get_date()

        if xmlsoup.find('ntceinfo').text:
            if "조회 결과가 다건입니다" in xmlsoup.find('ntceinfo').text:
                mrns = xmlsoup.find_all('cargmtno')
                ipdate = xmlsoup.find_all('etprdt')
                #iplst = [x.text for x in ipdate]
                #ms = max(iplst)
                #idx = iplst.index(ms)
                mrn_lst = []
                for mrn in mrns:
                    mrn_lst.append(mrn.text)
                return mrn_lst
        jukhajechl = xmlsoup.find_all('cargtrcnrelabsoptpcd')
        jukhajechl_yn = [x for x in jukhajechl if x.text == "입항적하목록 제출" or x.text == "입항적하목록 심사완료" or x.text == "입항적재화물목록 제출" or x.text == "입항적재화물목록 심사완료"]
        if len(jukhajechl_yn) > 0:
            ata = xmlsoup.find('etprdt').text  # 입항일
            mrn = xmlsoup.find('cargmtno').text  # 화물관리번호
            gweight = xmlsoup.find('ttwg').text
            gw_unit = 'KG'
            ctns = xmlsoup.find('pckgcnt').text
            ctns_unit = xmlsoup.find('pckut').text
            pum_name = xmlsoup.find('prnm').text
            fowarder = xmlsoup.find('frwrentsconm').text
            depart_cd = xmlsoup.find('ldprcd').text # 2022-11-08
            depart_name = xmlsoup.find('ldprnm').text # 2022-11-08
            bulhal_banchul = 'N'
            rmn_ctns = ctns
            rmn_wht = gweight  # 분할반출 대비 잔량 수량 중량 초기화
            tot_ctns = '0'
            tot_wht = '0'
            banchul_delay_gihan = ''
            banchul_date = ''
            nowstat = xmlsoup.find('prgsstts').text
            container = xmlsoup.find('cntrgcnt').text
            notice = xmlsoup.find_all('bfhngdnccn') # 안내사항
            infos = xmlsoup.find_all('cargcsclprgsinfodtlqryvo')
            singos = []
            stemp = []
            temp = []
            for info in reversed(infos):
                cm_code = info.find('shedsgn').text # 장치장 코드
                cm = info.find('shednm').text  # 장치장소
                stat = info.find('rlbrcn').text  # 상태
                stat_dtl = info.find('cargtrcnrelabsoptpcd').text  # 상태(상세)
                prcsdttm = info.find('prcsdttm').text
                dclrno = info.find('dclrno').text
                wght = info.find('wght').text  # 반출되거나 반입, 보세운송 신고등의 개별 이벤트에 대한 중량
                pckgcnt = info.find('pckgcnt').text
                rlbrbssno = info.find('rlbrbssno').text
                rlbrcn = info.find('rlbrcn').text
                if stat == '입항 반입' or stat == '반입신고' or stat == '하선신고수리' or stat_dtl == '하선신고 수리':
                    iphng_banip_storage_cd = cm_code  # 장치장코드
                    iphng_banip_storage = cm  # 장치장소
                    iphng_banip_date = prcsdttm[:8]  # 시간(여기선 장치시간) -- 장치기간 산정해야함
                    iphng_jangchi_gihan = day_calc.get_date(iphng_banip_date, 30)
                    iphng_jangchi_gihan = datetime.datetime.strftime(iphng_jangchi_gihan, '%Y%m%d')
                    vals = self.chk_addTax_bd(iphng_banip_storage_cd)
                    delay_add_tax = vals[0]
                    if delay_add_tax == 'Y':
                        impo_end_date = day_calc.get_date(iphng_banip_date, 30)
                        impo_end_date = datetime.datetime.strftime(impo_end_date, '%Y%m%d')
                    else:
                        impo_end_date = ''
                    banchul_penalty = vals[1]

                elif stat == '보세운송 반입':
                    trans_banip_date = prcsdttm[:8]
                    trans_banip_storage = cm
                    trans_banip_storage_cd = cm_code
                    vals = self.chk_addTax_bd(trans_banip_storage_cd)
                    delay_add_tax = vals[0]
                    if delay_add_tax == 'Y':
                        impo_end_date = day_calc.get_date(trans_banip_date, 30)
                        impo_end_date = datetime.datetime.strftime(impo_end_date, '%Y%m%d')
                    else:
                        impo_end_date = ''
                    banchul_penalty = vals[1]
                elif stat_dtl == '수입신고':
                    impo_singo_date = prcsdttm[:8]
                    if dclrno not in temp:
                        temp.append(dclrno)
                        stemp = [dclrno,impo_singo_date,"","","","",wght,pckgcnt,gweight,ctns,stat_dtl,mrn] ##신고번호,신고일자,수리일자,반출기한,반출연장일자,반출일자,중량,수량,중량(화물관리번호),수량(화물관리번호)
                        singos.append(stemp)
                    if '입항전수입' in cm_code:
                        spp_stat = '입항전수입'
                elif stat_dtl == '수입신고수리':
                    impo_ok_date = prcsdttm[:8]
                    banchul_gihan_notice = "수입신고 수리일로부터 15일이내에 물품을 반출하여야하며"
                    for no in notice:
                        if banchul_gihan_notice in no.text:
                            banchul_gihan = day_calc.get_date(impo_ok_date, 15)
                            banchul_gihan = datetime.datetime.strftime(banchul_gihan, '%Y%m%d')
                            break
                        else:
                            banchul_gihan = ''
                    if dclrno in temp:
                        for x in range(len(singos)):
                            if dclrno == singos[x][0]:
                                singos[x][2] = impo_ok_date
                                singos[x][3] = banchul_gihan
                                singos[x][10] = stat_dtl
                elif stat_dtl == '수입신고수리물품 반출기간연장 승인':
                    gihan = rlbrbssno
                    banchul_delay_gihan = gihan[13:]
                    banchul_delay_gihan = banchul_delay_gihan.replace('-', '')
                    banchul_gihan = banchul_delay_gihan
                    if dclrno in temp:
                        for x in range(len(singos)):
                            if dclrno == singos[x][0]:
                                singos[x][3] = banchul_delay_gihan
                                singos[x][4] = banchul_delay_gihan
                                singos[x][10] = stat_dtl
                elif stat_dtl == '반출신고':
                    banchul_date = prcsdttm[:8]
                    if rlbrcn == '수입신고 수리후 반출':
                        pckgcnt = info.find('pckgcnt').text
                        wght = info.find('wght').text
                        now_banchul_pkg = pckgcnt
                        now_banchul_wght = wght
                        if int(now_banchul_pkg) < int(ctns):  # 반출수량이 포장수량보다 작은 경우
                            bulhal_banchul = 'Y'
                            now_banchul_wght = round(float(now_banchul_wght))
                            tot_ctns = int(tot_ctns) + int(now_banchul_pkg)
                            tot_wht = float(tot_wht) + float(now_banchul_wght)
                            rmn_ctns = int(rmn_ctns) - int(now_banchul_pkg)
                            rmn_wht = float(rmn_wht) - float(now_banchul_wght)
                            tot_wht = round(tot_wht,2)
                            rmn_wht = round(rmn_wht,2)
                            if rmn_ctns == 0:
                                update_complete = 'Y'
                                if nowstat != "반출완료":
                                    nowstat = '반출완료'
                            tot_ctns = str(tot_ctns)
                            tot_wht = str(tot_wht)
                            rmn_ctns = str(rmn_ctns)
                            rmn_wht = str(rmn_wht)
                        else:
                            tot_ctns = str(now_banchul_pkg)
                            tot_wht = str(now_banchul_wght)
                            rmn_ctns = '0'
                            rmn_wht = '0'
                            update_complete = 'Y'
                            if nowstat != "반출완료":
                                nowstat = '반출완료'
                        if rlbrbssno in temp:
                            for x in range(len(singos)):
                                if rlbrbssno == singos[x][0]:
                                    singos[x][5] = banchul_date
                                    singos[x][6] = wght
                                    singos[x][7] = pckgcnt
                                    if singos[x][5] != '':
                                        singos[x][10] = '반출완료'


            reg = r'([0-9])\s개월'
            p = re.compile(reg)
            for ii in range(len(notice)):
                if '장치기간은 최대 ' in notice[ii].text:
                    if iphng_banip_date == '':
                        iphng_banip_date = trans_banip_date
                    m = p.search(notice[ii].text)
                    if m:
                        iphng_jangchi_gihan = m.group(1)
                        if iphng_banip_date != '':
                            iphng_jangchi_gihan = day_calc.get_month(iphng_banip_date, iphng_jangchi_gihan)
                            iphng_jangchi_gihan = datetime.datetime.strftime(iphng_jangchi_gihan, '%Y%m%d')

            dict = (ata,mrn,gweight,gw_unit,ctns,ctns_unit,pum_name,
                   iphng_banip_storage_cd,iphng_banip_storage,
                   iphng_banip_date,trans_banip_storage_cd,
                    trans_banip_storage,trans_banip_date,singos,
                    impo_ok_date,fowarder,impo_end_date,iphng_jangchi_gihan,
                    banchul_gihan,update_complete,impo_singo_date,banchul_delay_gihan,banchul_date,rmn_ctns,rmn_wht,tot_ctns,
                    tot_wht,nowstat,delay_add_tax,spp_stat,depart_cd,depart_name,key,area) # 2022-11-08 depart_cd, depart_name 추가
            return dict
        else:
            return ''


    def api_container_inf(self,mrn):
        url = "https://unipass.customs.go.kr:38010/ext/rest/cntrQryBrkdQry/retrieveCntrQryBrkd"
        queryString = "?" + urlencode(
            {
                "crkyCn": unquote("l250d232q006t207u050x010q0"),  # 관세법인 에스에이엠씨 인증키
                "cargMtNo": mrn,

            })
        queryURL = url + queryString
        response = requests.get(queryURL)
        res = response.text
        xmlsoup = BeautifulSoup(res, 'lxml')
        cntrno = xmlsoup.find_all('cntrno')
        cntrstszcd = xmlsoup.find_all('cntrstszcd')
        cntrselgno1 = xmlsoup.find_all('cntrselgno1')
        cntrselgno2 = xmlsoup.find_all('cntrselgno2')
        cntrselgno3 = xmlsoup.find_all('cntrselgno3')
        cntrs = []
        if len(cntrno) > 0:
            for i in range(len(cntrno)):
                temp = [mrn,cntrno[i].text,cntrstszcd[i].text,cntrselgno1[i].text,cntrselgno2[i].text,cntrselgno3[i].text]
                cntrs.append(temp)
            return cntrs
        else:
            return False