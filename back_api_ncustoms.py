import sys
from urllib.parse import urlencode, quote_plus,unquote
from urllib import parse
import requests
from bs4 import BeautifulSoup
import get_today
import time
import datetime
import connectDb
import pandas as pd
from xml.etree.ElementTree import parse
import day_calc
import pymssql
import pymssql._mssql
import sendMail

"""
def sendMail():
    conn = connectDb.connect_Db()
    curs = conn.cursor()

    sql1 = "" "select seq,bl,impo_ok_date,bizno,sangho,mrn,jangchijang,singo_end from master2 where impo_singo_date = '' and singo_end = %s" ""
    sql2 = "" "select seq,bl,impo_ok_date,bizno,sangho,mrn,jangchijang,banchul_end from master2 where impo_ok_date != '' and banchul_end = %s" ""


    import get_today
    import day_calc
    dayterms_imp = [20, 10, 5, 1]
    dayterms_banchul = [10, 5, 2, 1]
    today = get_today.get_date()
    ##### 수입신고지연가산세 메일 보내기
    import sendMail
    for i in range(len(dayterms_imp)):  # 20일부터 1일까지 순차적으로 신고건을 검색해서 해당되는 건들의 메일주소를 취합한다.
        day_term = day_calc.get_date(today, dayterms_imp[i])
        day_term = day_term.strftime('%Y%m%d')
        curs.execute(sql1, (day_term))
        res = curs.fetchall()
        print(res)
        if res:
            for ii in range(len(res)):
                chk = check_sendYn(res[ii], dayterms_imp[i], type=1)
                if chk:
                    print("신고지연가산세 안내 메일 발송준비",len(res))
                    seq = res[ii][0]
                    bl = res[ii][1]
                    type = '1'
                    texts = make_text(res[i], type='1')
                    subject = "신고지연 가산세 대상 안내 (수입신고 기한)"
                    bizno = res[ii][3]
                    sql_address = "" "select bizno,damdangja_name, email1 from cust_dtail where bizno = %s" ""
                    curs.execute(sql_address, (bizno))
                    res_address = curs.fetchall()
                    add_list = []
                    for iii in range(len(res_address)):
                        address = res_address[iii][2]
                        add_list.append(address)
                    sendMail.sendMails(add_list, subject, texts)
                    insert_mailsndmng(seq, bl, type, today, dayterms_imp[i])

    for i in range(len(dayterms_banchul)):  # 20일부터 1일까지 순차적으로 신고건을 검색해서 해당되는 건들의 메일주소를 취합한다.
        day_term = day_calc.get_date(today, i)
        day_term = day_term.strftime('%Y%m%d')
        curs.execute(sql2, (day_term))
        res = curs.fetchall()
        if res:
            print(res)
            for ii in range(len(res)):
                chk = check_sendYn(res[ii], dayterms_banchul[i], type=2)
                if chk:
                    print("수리후반출기간안내",len(res))
                    seq = res[ii][0]
                    bl = res[ii][1]
                    type = '2'
                    texts = make_text(res[i], type='2')
                    subject = "신고지연 가산세 대상 안내 (수입신고 기한)"
                    bizno = res[ii][3]
                    sql_address = "select bizno,damdangja_nam, email1 from cust_dtail where bizno = %s"
                    curs.execute(sql_address, (bizno))
                    res_address = curs.fetchall()
                    for iii in range(len(res_address)):
                        address = res_address[iii][2]
                        add_list = add_list.append(address)
                    sendMail.sendMails(address, subject, texts)
                    insert_mailsndmng(seq, bl, type, today, dayterms_banchul[i])
                    """

"""
def make_text(values,type):
    if type == '1':
        sangho = values[4]
        bl = values[1]
        mrn = values[5]
        jangchijang = values[6]
        impo_end = values[7]
        hello_text1 = "안녕하세요\n"
        hello_text2 = "관세법인 에스에이엠씨입니다\n"
        content = "\n" + "수신 : " + sangho + "\n" + "B/L NO. : " + bl + "\n" + "화물관리번호 : " + mrn + "\n" + "장치장명 : " + jangchijang + "\n" + "신고기한 : " + impo_end + "\n"
        tailtext = "\n" + "당해건은 신고지연 가산세 적용대상 보세구역에 장치된 물품으로서 2021-10-03 까지 수입신고 하여야 합니다." + "\n" + "확인 후 회신 부탁드립니다."
        print("신고지연간세 안내 메일 발송",bl )
    elif type == '2':
        sangho = values[4]
        bl = values[1]
        mrn = values[5]
        jangchijang = values[6]
        banchul_end = values[7]
        hello_text1 = "안녕하세요\n"
        hello_text2 = "관세법인 에스에이엠씨입니다\n"
        content = "\n" + "수신 : " + sangho + '\n' + "B/L NO. : " + bl + '\n' + "화물관리번호 : " + mrn + '\n' + "장치장명 : " + jangchijang + '\n' + "반출기한 : " + banchul_end + '\n'
        tailtext = "\n" + "당해건은 수입신고 수리물품 반출의무 적용 대상으로서 2021-11-12까지 반출 또는 반출기한 연장신청하여야 합니다." + '\n' + "확인 후 회신 부탁드립니다."

    texts = hello_text1 + hello_text2 + content + tailtext
    return texts


def insert_mailsndmng(seq, bl, type, today, gbn):
    conn = connectDb.connect_Db()
    curs = conn.cursor()
    now = datetime.datetime.now()
    nowstr = datetime.datetime.strftime(now, '%Y%m%d%H%M%S')
    sql = "" "insert into mailsndmng values (%s,%s,%s,%s,%s,%s);" ""
    curs.execute(sql, (seq, bl, "1", type, nowstr, today, gbn))
    conn.commit()


def check_sendYn(lst, i, type):  # seq,bl,imp_ok_date,bizno,sangho,mrn,jangchijang,impo_end
    conn = connectDb.connect_Db()
    curs = conn.cursor()
    seq = lst[0]
    bl = lst[1]
    gbn = i

    sql = "" "select count(*) from mailsndmng where seq = %s and bl = %s and type = %s and daygbn = %s" ""
    curs.execute(sql, (seq, bl, type, gbn))
    res = curs.fetchall()
    rcount = res[0][0]
    print('count',rcount)
    if rcount == 0:
        chk = True
    else:
        chk = False

    return chk
"""
################################################################################

def call_api(): #수입화물진행정보
   # print("sub thread start ", threading.currentThread().getName())
   # time.sleep(3)
   # print("sub thread end ", threading.currentThread().getName())
    today = get_today.get_date()
    yy = today[:4]

    url = "https://unipass.customs.go.kr:38010/ext/rest/cargCsclPrgsInfoQry/retrieveCargCsclPrgsInfo"

    cnt = 0
    condition = 0
    now = time.strftime('%H%M%S')
    conn = connectDb.connect_Db()
    curs = conn.cursor()
    sql = """select bl,seq from master2 where banchul_end is null or banchul_end = '';"""
    curs.execute(sql)
    res_sql = curs.fetchall()
    curs.close()
    now = time.strftime('%H%M%S')
    print("조회대상BL : ", res_sql)
    print("현재시간", now)
    if now > '190000':
        print("See you again, bye~~~~!!!")
        sys.exit()
    for i in range(len(res_sql)):
        bl = res_sql[i][0]
        seq = res_sql[i][1]
        print("bl:",bl)
        if condition == 0:
            print("마스터 BL 조회")
            mbl = bl
            hbl = ''
        elif condition == 1:
            print("하우스 BL 조회")
            mbl = ''
            hbl = bl
        elif condition == 2:
            print("전년도 마스터 BL 조회")
            mbl = bl
            hbl = ''
            yy = int(yy) - 1
        else:
            print("전년도 하우스 BL 조회")
            mbl = ''
            hbl = bl
            yy = int(yy) - 1

        queryString = "?" + urlencode(
           {
               "crkyCn": unquote("p220l271w160d175z040f060i0"),  # 관세법인 에스에이엠씨 인증키
               "cargMtNo": "",
               "mblNo": mbl,
               "hblNo": hbl,
               "blYy": yy

           })

        queryURL = url + queryString
        response = requests.get(queryURL)
        res = response.text
        xmlsoup = BeautifulSoup(res, 'lxml')
        jukhajechl = xmlsoup.find_all('cargtrcnrelabsoptpcd')
        jukhajechl_yn = [x for x in jukhajechl if x.text == "입항적하목록 제출" or x.text == "입항적재화물목록 제출"]
        if len(jukhajechl_yn) == 0: #적하목록이 존재하지 않으면
            condition = condition + 1
            if condition == 4:
                condition = 0
                cnt = cnt + 1
        else:
            print("매칭데이타를 확인")
            save_data(xmlsoup,bl,seq)
            cnt = cnt + 1
            time.sleep(2)
            condition = 0
    print("종료")



def get_text(str): #str 은 리스트
    new_list = []
    for i in str:
        new_list.append(i.text)
    return new_list

def chk_addTax_bd(code):
    print('code',code)
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
    addtax = xmlsoup.find('adtxcoltpridyn')
    penalty = xmlsoup.find('pnltlvytrgtyn')
    print(addtax,penalty)
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
    return lst

def update_napbu_date(impo_singo_no,okdate):
    print("납부일자 점검")
    import calendar
    conn2 = connectDb.connect_Db2()
    curs2 = conn2.cursor()
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
    next_enddate = str(calendar.monthrange(int(next_year),int(next_month))[1]) #징수형태 43 월말납부 납부일자
    sql = """select impo_singo_no, impo_jingsu_type, impo_napbu_date2 from impo1 where impo_singo_no = %s;"""
    curs2.execute(sql,(impo_singo_no))
    res = curs2.fetchone()
    if str(res[1]) == '11' or str(res[1]) == '14':
        napbu_date = str(res[2])
    elif str(res[1]) == '43':
        gihan_t = str(gihan_dict[this_month_enddate])
        gihan_t = gihan_t.zfill(2)
        gihan = this_year+this_month+gihan_t
        print("월/말일",this_month + "/" + this_month_enddate)
        print("납부기준일",gihan)
        print("수리일",okdate)
        if okdate <= gihan:
            napbu_date = this_year + this_month + this_month_enddate
        else:
            print("납부일 익월 이월")
            napbu_date = next_year + next_month + next_enddate
    curs2.close()
    return napbu_date


def save_data(xmlsoup,bl,seq):
    print("데이타 업데이트중")
    ata = xmlsoup.find('etprdt').text  # 입항일
    mrn = xmlsoup.find('cargmtno').text
    master_field = ['reqno', 'stat', 'stat_dtl', 'cm', 'cm_code', 'dttm', 'notice', 'ata', 'mrn']
    dttm = xmlsoup.find_all('rlbrdttm')  # 처리일시
    prcsdttm = xmlsoup.find_all('prcsdttm')  # 처리일시(모든항목)
    reqno = xmlsoup.find_all('dclrno')  # 신청번호
    stat = xmlsoup.find_all('rlbrcn')  # 상태
    stat_dtl = xmlsoup.find_all('cargtrcnrelabsoptpcd')  # 상태(상세)
    notice = xmlsoup.find_all('bfhngdnccn')  # 안내사항
    cm_code = xmlsoup.find_all('shedsgn')  # 장치장 코드
    cm = xmlsoup.find_all('shednm')  # 장치장소

    dttm = get_text(dttm)
    prcsdttm = get_text(prcsdttm)
    reqno = get_text(reqno)
    stat = get_text(stat)
    stat_dtl = get_text(stat_dtl)
    notice = get_text(notice)
    cm_code = get_text(cm_code)
    cm = get_text(cm)
    df = pd.DataFrame(columns=master_field)
    del prcsdttm[-1]  # 헤드부분에도 이 항목이 있어 다른 항목보다 갯수가 하나더 많음(마지막 항목 삭제)
    df["reqno"] = reqno
    df['stat'] = stat
    df['stat_dtl'] = stat_dtl
    df['notice'] = notice
    df['cm_code'] = cm_code
    df['cm'] = cm
    df['dttm'] = dttm
    df['ata'] = ata  # 입항시간
    df['mrn'] = mrn
    df['prcsdttm'] = prcsdttm
    print(df)
    sers = df.loc[0]
    ata = sers.ata
    mrn = sers.mrn
    jangchi_code = sers.cm_code
    jangchijang = sers.cm

    # 로직 생각해서 가져와야 하는값들 예) 반입일, 신고기한,수입면허일등
    df_temp = df[df["stat_dtl"] == '반입신고']
    if df_temp.empty:
        banip_date_replaced = ''
        cm = ''
        cm_code = ''
        jangchijang = ''
    else:
        banip_date = df_temp['dttm'].values[0]
        cm = df_temp['cm'].values[0]
        cm_code = df_temp['cm_code'].values[0]
        addtax_yn = chk_addTax_bd(cm_code)
        jangchi_code = cm_code
        jangchijang = cm
        banip_date = banip_date[:10]
        banip_date_replaced = banip_date.replace('-', '')
        """if addtax_yn[0] == 'Y': #신고지연가산세 확인
            singo_end = day_calc.get_date(banip_date, days=30)  # banip_date 부터 30일 이내 (익일기준)
            singo_end = singo_end.strftime('%Y%m%d')
        else:
            singo_end = '해당사항없음'"""  #신고지연가산세는 의미 현재(20211207)없음
    df_temp = df[df['stat_dtl'] == '수입신고']
    if df_temp.empty:
        impo_singo_date = ''
        impo_singo_no = ''
    else:
        impo_singo_date = df_temp['prcsdttm'].values[0]
        impo_singo_date = impo_singo_date[:8]
        impo_singo_no = df_temp['reqno'].values[0]
    df_temp = df[df["stat_dtl"] == '수입신고수리']
    if df_temp.empty:
        impo_ok_date = ''
        banchul_date_replaced = ''
        banchul_end = ''
        napbu_date = ''
    else:
        impo_ok_date = df_temp['prcsdttm'].values[0]
        impo_ok_date = impo_ok_date[:8]
        if addtax_yn[1] == 'Y': #과태료 대상
            banchul_end = day_calc.get_date(impo_ok_date,days=15)
            banchul_end = banchul_end.strftime('%Y%m%d')
        else:
            banchul_end = '해당사항없음'
        napbu_date = update_napbu_date(impo_singo_no,impo_ok_date)
        print("납부",napbu_date)
    df_temp = df[df['stat_dtl'] == '반출신고']
    if df_temp.empty:
        banchul_date_replaced = ''
    else:
        banchul_date = df_temp['dttm'].values[0]
        banchul_date = banchul_date[:10]
        banchul_date_replaced = banchul_date.replace('-','')

    reflash_itmsList = ['ata', 'mrn', 'jangchi_code','jangchijang', 'banip_date', 'impo_singo_date', 'impo_singo_no',
                        'impo_ok_date','banchul_date','banchul_end','napbu_date']


    conn = connectDb.connect_Db()
    curs = conn.cursor()
    tstr = " = %s,".join(reflash_itmsList) + "= %s"
    sql = """update master2 set %s where seq = '%s'""" % (tstr,seq)
    cols = tuple(reflash_itmsList)
    print(sql)
    curs.execute(sql,(ata,mrn,jangchi_code,jangchijang,banip_date_replaced,impo_singo_date,impo_singo_no,impo_ok_date,banchul_date_replaced,banchul_end,napbu_date))
    conn.commit()
    conn.close()
    print("update complete")


#sendMail()
import getNcustoms
getNcustoms.getNcustoms.getNcustoms_data()
call_api()
sys.exit()




