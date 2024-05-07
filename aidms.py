import datetime
from winreg import *
import winreg
import api_unipass
import connectDb
import day_calc
import get_today
import import_bl
import api_call
import json
import requests
import winreg
import pymssql
import pandas as pd
from datetime import datetime,timedelta
from dateutil.relativedelta import relativedelta
import re



class api_For_Worksmobile():
    def __init__(self):
        self.client_id = 'NZEIZ_Jx9ie_XLxQ4kE2'
        self.client_secret = 'iM9isoQXQx'

    def get_tokens(self): #reflash token 이 갱신되면 akys 의 토큰을 서버실의 PC에도 입력해야 함
        """key = winreg.HKEY_CURRENT_USER
        key_value = r"SOFTWARE\Tks\Ssks\Keys"
        reg = winreg.OpenKey(key, key_value, 0, winreg.KEY_ALL_ACCESS)
        token, type = winreg.QueryValueEx(reg, "akys")
        return token"""
        conn = connectDb.connect_Db_ttks()
        curs = conn.cursor()
        sql = """SELECT AES_DECRYPT(UNHEX(ttks),'tTH!ksdid89!@') FROM ttks where ktype = 'access' and appname = 'aidms' """
        curs.execute(sql)
        res = curs.fetchall()
        if res[0][0] is not None:
            token = res[0][0]
            conn.close()
            return token.decode()
        else:
            with open('c:/samc/log.log','w') as f:
                f.write("aidms access token 갱신 실패 " + datetime.now().strftime('%Y%m%d %H%M%S'))

    def send_mail(self,mails):
        errcnt = 0
        while True:
            url = 'https://www.worksapis.com/v1.0/users/njw@clsam.com/mail'
            tokens = self.get_tokens()
            headers = {"authorization":"Bearer "+ tokens,
                        "Content-Type":"application/json"}
            data = mails
            response = requests.post(url, data=json.dumps(data), headers=headers)
            if response.status_code != 202:
                """reg = winreg.OpenKey(key, key_value, 0, winreg.KEY_ALL_ACCESS)
                ref_token, type = winreg.QueryValueEx(reg, "rkys")
                reg = winreg.OpenKey(key, key_value2, 0, winreg.KEY_ALL_ACCESS)
                client_id, type =  winreg.QueryValueEx(reg, "ids")
                client_secret, type = winreg.QueryValueEx(reg, "sds")
                reg = winreg.OpenKey(key, key_value, 0, winreg.KEY_ALL_ACCESS)
                reflash_token_expire, type = winreg.QueryValueEx(reg, "refresh_updated")
                self.update_accesstokens(ref_token,client_id,client_secret,reflash_token_expire)"""
                errcnt = errcnt + 1
                if errcnt > 5:
                    break
                self.request_acc_token()

            elif response.status_code == 202:
                return  response.status_code



    def request_acc_token(self):
        client_id = self.client_id
        client_secret = self.client_secret
        conn = connectDb.connect_Db_ttks()
        curs = conn.cursor()
        sql = """SELECT AES_DECRYPT(UNHEX(ttks),'adD!!UYIKdd90=!'),rmndt FROM ttks where ktype = 'reflash' and appname = 'aidms'"""
        curs.execute(sql)
        res = curs.fetchall()
        conn.close()
        ref_token = res[0][0].decode()
        reflash_token_expire = res[0][1]
        self.update_accesstokens(ref_token, client_id, client_secret, reflash_token_expire)


    def update_accesstokens(self,ref_token,client_id,client_secret,reflash_token_expire): #Access token 갱신
        url = 'https://auth.worksmobile.com/oauth2/v2.0/token'
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        refresh_token = ref_token
        grant_type = "refresh_token"
        data = {"refresh_token": refresh_token,
                "grant_type": grant_type,
                "client_id": client_id,
                "client_secret": client_secret}

        resp = requests.post(url, data=data, headers=headers)
        ttoken = resp.json()
        token = ttoken['access_token']
        rkey = 'access' # access_token 저장
        reflash_token_expire = str(int(reflash_token_expire) - 1)
        self.regist_token(token,reflash_token_expire)
        if int(reflash_token_expire) < 15: #리프레시 토큰 잔여일이 15일 아래면 나한테
            self.send_mail_tokens_expire_alert(reflash_token_expire)


    def regist_token(self,token, reflash_token_expire): # 갱신된 Access Token 레지스트리 저장 (24시간 유효)
        """key = winreg.HKEY_CURRENT_USER
        key_value = r"SOFTWARE\Tks\Ssks\Keys"
        key_value2 = r"SOFTWARE\GNU\XviD\Clis"
        try:
            reg = winreg.OpenKey(key, key_value, 0, winreg.KEY_ALL_ACCESS)
            winreg.SetValueEx(reg, kys, 0, REG_SZ, token)
        except FileNotFoundError:
            reg = winreg.CreateKey(key, key_value)
            winreg.SetValueEx(reg, kys, 0, REG_SZ, token)
        try:
            reg = winreg.OpenKey(key, key_value2, 0, winreg.KEY_ALL_ACCESS)
            winreg.SetValueEx(reg, 'ids', 0, REG_SZ, client_id)
            winreg.SetValueEx(reg, 'sds', 0, REG_SZ, client_secret)
        except FileNotFoundError:
            reg = winreg.CreateKey(key, key_value2)
            winreg.SetValueEx(reg, 'ids', 0, REG_SZ, client_id)
            winreg.SetValueEx(reg, 'sds', 0, REG_SZ, client_secret)
        try:
            reg = winreg.OpenKey(key, key_value, 0, winreg.KEY_ALL_ACCESS)
            winreg.SetValueEx(reg, 'refresh_updated', 0, REG_SZ, reflash_token_expire)
        except FileNotFoundError:
            reg = winreg.CreateKey(key, key_value)
            winreg.SetValueEx(reg, 'refresh_updated', 0, REG_SZ, reflash_token_expire)

        winreg.CloseKey(reg)"""

        today = get_today.get_date()
        sql_del = """delete from ttks where ktype = 'access' and appname = 'aidms'"""
        sql = """insert into ttks (ttks,upddt,rmndt,ktype,appname) values (HEX(AES_ENCRYPT('{}','tTH!ksdid89!@')),'{}','{}','access','aidms')""".format(
            token, today, '')
        sql_update = """update ttks set rmndt = '{}' where ktype = 'reflash' and appname = 'aidms'""".format(reflash_token_expire)
        conn = connectDb.connect_Db_ttks()
        curs = conn.cursor()
        curs.execute(sql_del)
        curs.execute(sql)
        curs.execute(sql_update)
        conn.commit()
        conn.close()

    def send_mail_tokens_expire_alert(self,reflash_token_expire):
        mails = {'to': 'jnoo74@gmail.com', 'cc': '', 'bcc': '', 'userName': '',
                 'subject': '관세법인 에스에이엠씨 메일 리프레시 토큰 갱신 알림',
                 'body': "관세법인 에스에이엠씨 메일 네이버웍스 모바일을 통한 메일 API 리프레시 토큰 갱신 만료일이 " + reflash_token_expire + "일 남았습니다.", 'contentType': 'text'}
        self.send_mail(mails)


###희래(주) 수입신고 후 25일이상 수리되지 않을때 리마인드 메일 발송
import connectDb
from datetime import datetime, timedelta


class HEE_LAE_remind_mails():
    def begin(self):
        chk = self.get_sendyn_info() #레지스트리에 오늘날짜를 넣고 다음번 실행될때 오늘날짜가 들어가있는게 확인되면 이단계 건너뛴다.  아마 두번이상 메일 보내지 않도록 하기위한 듯...
        if chk:
            for i in range(2):
                if i == 0:
                    conn = connectDb.connect_Db()
                    db_name = """ ncustoms.kcba.impo1"""
                elif i == 1:
                    conn = connectDb.connect_Db2()
                    db_name = """ ncustoms.dbo.impo1"""
                sql = """select impo_singo_no,impo_singo_date,impo_bl_no from {} where impo_napse_sangho = '희래(주)' and impo_ok_date = ''""".format(db_name)
                curs = conn.cursor()
                curs.execute(sql)
                res = curs.fetchall()
                conn.close()
                if res:
                    datas = self.process(res)
                    if datas:
                        self.send_mail(datas)

    def process(self,res): # 신고일로 부터 25일 경과건 집계 --> 테스트 3일이상 경과건 집계
        datas = []
        for i in range(len(res)):
            singono = res[i][0]
            singo_date = res[i][1]
            bl = res[i][2]
            today = datetime.today()
            remind_napbu_date = datetime.strptime(singo_date,'%Y%m%d') + timedelta(days=23)
            napbu_date = datetime.strptime(singo_date,'%Y%m%d') + timedelta(days=25)
            if today >= remind_napbu_date:
                napbu_date = napbu_date.strftime('%Y-%m-%d')
                temp = [singono, singo_date, bl, napbu_date]
                datas.append(temp)
        return datas


    def send_mail(self,datas):
        mailto = 'ischo@clsam.com'
        ccto = 'njw@clsam.com'
        subject = "희래(주) 수입신고 미면허건 안내"
        for i in range(len(datas)):
            bodys = """안녕하세요, 관세법인 에스에이엠씨입니다. \n
\n
당해 수입 신고 건은 *확정일자*까지 관세 납부를 완료하여야 합니다.\n 
*확정일자*까지 미납부시 가산금이 발생되오니, 확인 후 회신 부탁드립니다.\n
(최초 납부기한 경과 시 3% , 매 1개월 경과 시 1.2% 추가가산)\n
\n
BL NO : {} \n
수입신고번호 : {} \n
납부일자 : {}\n
근거 : 관세법 제 41조(가산금)\n
\n
※주의사항 : 반드시 납부기일 은행영업시간(오후 4시)까지 납부하셔야 합니다.\n
은행 영업시간을 넘겨서 입금할 경우에는 반드시 저희에게 연락 바랍니다.\n
\n
\n
관련하여 문의사항 있으시면 연락 바랍니다.\n
감사합니다.\n
\n
\n
\n
S.A.M.C. customs Co., Ltd.\n
Office : 82-31-462-0303\n
Fax : 82-31-462-0308\n
Email : sam01@clsam.com\n
                    """.format(datas[i][2],datas[i][0],datas[i][3])


            mails = {'to': mailto, 'cc': ccto, 'bcc': '', 'userName': "관세법인 에스에이엠씨", 'subject': subject,
                     'body': bodys, 'contentType': 'text'}
            senders = api_For_Worksmobile()
            status = senders.send_mail(mails)

            if status == 202:
                now = datetime.now()
                now = datetime.strftime(now, '%Y%m%d%H%M%S')
                sql = """insert into dsnsmsg.dbo.mailmng (ref_no,mail_to,cc,usernm,subject,body,content_type,send_yn,snd_time1, snd_time2) 
                            values {}""".format(tuple([datas[i][0],mailto,ccto,'관세법인 에스에이엠씨',subject,bodys,'text','Y',now,now]))
                conn2 = connectDb.connect_Db2()
                curs2 = conn2.cursor()
                curs2.execute(sql)
                conn2.commit()
                conn2.close()


    def get_sendyn_info(self):
        from datetime import datetime
        today = datetime.now().strftime('%Y%m%d')
        key = winreg.HKEY_CURRENT_USER
        key_value = r"SOFTWARE\SAMC\local_inf\info"
        reg = winreg.OpenKey(key, key_value, 0, winreg.KEY_ALL_ACCESS)
        value = winreg.QueryValueEx(reg,"heelae_send")[0]
        if today == value:
            return False
        else:
            winreg.SetValueEx(reg,"heelae_send",0, REG_SZ,today)
            return True





def get_cust(idx):
    ####거래처 정보에서 import_yn 이 y 인 화주만 검색 -- 현재는 납세의무자만 쿼리.. 수입자와 납세의무자 다른경우 대한 쿼리 만들 필요 있음
    #### idx 인자 추가 : 각 지사별 데이타 가져오기 위함
    if idx == 0:
        area = '01'
    elif idx == 1:
        area = '02'
    elif idx == 2:
        area = '03'
    conn = connectDb.connect_Db2()
    curs = conn.cursor()
    sql_cust = """select cust_code from samc_cts.dbo.tnm_cust1 where import_yn = 'Y' and area = '{}'""".format(area)
    curs.execute(sql_cust)
    res = curs.fetchall()
    cust_cd = tuple([x[0] for x in res])
    return cust_cd

def apiinfo_update_tnm(updaters):
    ###### 리스트의 신고번호중 한건만 남기고, 나머진 외 몇건 이런식으로 처리###########
    cols = ['ata','mrn','gweight','gw_unit','ctns','ctns_unit','pum_name','iphng_banip_storage_cd',
            'iphng_banip_storage','iphng_banip_date','trans_banip_storage_cd','trans_banip_storage',
            'trans_banip_date','impo_singo_no','impo_ok_date','vo_company','import_declaration_gihan',
            'iphng_jangchi_gihan','banchul_gihan','update_cargo_complete','impo_singo_date','banchul_delay_gihan',
            'last_banchul_date','rmn_qty','rmn_weight','tot_banchul_qty','tot_banchul_weight','stat','import_delay_gasan','spp_stat','depart_cd','depart_name','tnm_key','area'] # 2022-11-08 depart_cd, depart_name 추가
    tstr = ','.join(cols)
    conn = connectDb.connect_Db2()
    curs = conn.cursor()
    for x in range(len(updaters)):
        xlst = list(updaters[x])
        if len(xlst) == 1:
            continue
        tnm_key = xlst[-3]
        if len(xlst[13]) > 1:
            addtext = "외" + str(len(xlst[13]) - 1)
            update_singos(xlst[13], tnm_key)
            xlst[13] = xlst[13][0][0]
        elif len(xlst[13]) ==  1:
            addtext = ''
            update_singos(xlst[13], tnm_key)
            xlst[13] = xlst[13][0][0]
        else:
            addtext = ''
            xlst[13] = ''
        del xlst[-1]

        ########통관시스템에 없는 건은 업데이트 진행하지 않음

        mrn = xlst[1]
        area = xlst[-1]
        dbs = ['ncustoms.kcba.impo1','ncustoms.dbo.impo1']
        if area == '01':
            con = connectDb.connect_Db()
            i = 0
        else:
            con = connectDb.connect_Db2()
            i = 1
        curs2 = con.cursor()
        sql_check = """select impo_mrn_no from {} where impo_mrn_no = '{}'""".format(dbs[i],mrn)
        curs2.execute(sql_check)
        res = curs2.fetchall()
        con.close()
       # if not res:
       #     continue

        try:
            sql = """update samc_cts.dbo.tnm_master set ata = %s, mrn = %s, gweight = %s,gw_unit = %s, ctns = %s, ctns_unit = %s, pum_name = %s, iphng_banip_storage_cd = %s,
             iphng_banip_storage = %s, iphng_banip_date = %s, trans_banip_storage_cd = %s, trans_banip_storage = %s, trans_banip_date = %s,
             impo_singo_no = %s, impo_ok_date = %s,vo_company = %s, import_declaration_gihan = %s,iphng_jangchi_gihan = %s, 
             banchul_gihan = %s, update_cargo_complete = %s, impo_singo_date = %s,banchul_delay_gihan = %s, last_banchul_date = %s, rmn_qty = %s, rmn_weight = %s,
              tot_banchul_qty = %s, tot_banchul_weight = %s,stat = %s,import_delay_gasan = %s,spp_stat = %s,depart_cd = %s, depart_name = %s, 
              singono_addtext = '{}' where tnm_key = %s and area = %s""".format(
                addtext) # # 2022-11-08 depart_cd, depart_name 추가
            curs.execute(sql, tuple(xlst))
            conn.commit()
        except:
            print(x)
            print(sql)
            print(updaters[x])

        tnm_key = xlst[32]
        sql = """delete from samc_cts.dbo.tnm_submst where tnm_key = '{}' and mrn = '{}'""".format(tnm_key,mrn)
        curs.execute(sql)
        try:
            sql = """insert into samc_cts.dbo.tnm_submst ({}) values {}""".format(tstr,tuple(xlst))
            curs.execute(sql)
            sql_update_freetime = """update samc_cts.dbo.tnm_submst 
                                set dem_ft = a.dem_ft, det_ft = a.det_ft, sto_ft = a.sto_ft 
                                from samc_cts.dbo.tnm_master a 
                                where samc_cts.dbo.tnm_submst.tnm_key = a.tnm_key and a.tnm_key = '{}'""".format(tnm_key)
            curs.execute(sql_update_freetime)
            conn.commit()
        except:
            txts = xlst[6][:15]
            xlst[6] = txts.replace("'","")
            sql = """insert into samc_cts.dbo.tnm_submst ({}) values {}""".format(tstr, tuple(xlst))
            curs.execute(sql)
            sql_update_freetime = """update samc_cts.dbo.tnm_submst 
                                            set dem_ft = a.dem_ft, det_ft = a.det_ft, sto_ft = a.sto_ft 
                                            from samc_cts.dbo.tnm_master a 
                                            where samc_cts.dbo.tnm_submst.tnm_key = a.tnm_key and a.tnm_key = '{}'""".format(tnm_key)
            curs.execute(sql_update_freetime)
            conn.commit()

        sql = """update samc_cts.dbo.tnm_master set sub_yn = 'Y' where tnm_key = '{}'""".format(tnm_key)
        curs.execute(sql)

        if xlst[14] != '' and xlst[27] == '반출완료':
            sql = """update samc_cts.dbo.tnm_submst set update_cargo_complete = 'Y' where tnm_key = '{}'""".format(tnm_key) # api 에서 반출완료된 경우 update_cargo_complete (tnm_submst)완료처리 함.(화물관리번호  두개 이상일때 문제 있음)
        else:
            sql = """update samc_cts.dbo.tnm_submst set update_cargo_complete = 'N' where tnm_key = '{}'""".format(tnm_key)
        curs.execute(sql)
        conn.commit()
        sql = """select tnm_key from samc_cts.dbo.tnm_submst where tnm_key = '{}' and update_cargo_complete != 'Y'""".format(tnm_key) #
        curs.execute(sql)
        res = curs.fetchall()
        if len(res) == 0: #submst 에 있는 MRN 에 최종 반출완료되지 않은 화물이 하나라도 있는경우 해당 bL역시 최종반출처리 되지 아니한다.--2023-05-09
            sql = """update samc_cts.dbo.tnm_master set update_cargo_complete = 'Y' where tnm_key = '{}'""".format(tnm_key)
            curs.execute(sql)
            conn.commit()
    conn.close()

def update_singos(singos,tnm_key):
    conn = connectDb.connect_Db2()
    for i in range(len(singos)):
        curs = conn.cursor()
        singono = singos[i][0]
        last_banchul_date = singos[i][5]
        banchul_gihan = singos[i][3]
        weight = singos[i][6]
        qty = singos[i][7]
        stat = singos[i][10]
        mrn = singos[i][11]
        #########################해외거래처 정보 업데이트
        sql_exporter = """select Impo_gonggub_sangho from ncustoms.dbo.impo1 where impo_singo_no = '{}'""".format(
            singono)
        curs.execute(sql_exporter)
        exporter = curs.fetchone()
        if exporter:
            exporter = exporter[0]
        else:
            exporter = ''
        sql1 = """delete from samc_cts.dbo.tnm_singos where impo_singo_no = '{}'""".format(singono)
        curs.execute(sql1)
        sql2 = """insert into samc_cts.dbo.tnm_singos (tnm_key,mrn,impo_singo_no,last_banchul_date,banchul_gihan,weight,qty,stat,exporter) 
        values {}""".format((tnm_key,mrn,singono,last_banchul_date,banchul_gihan,weight,qty,stat,exporter))
        try:
            curs.execute(sql2)
        except:
            print(sql2)
        conn.commit()




def napbu_gihan_update(idx):
    if idx == 0:
        area = '01'
        conn2 = connectDb.connect_Db()
        db_owner = 'ncustoms.kcba.'
    elif idx == 1:
        area = '02'
        conn2 = connectDb.connect_Db2()
        db_owner = 'ncustoms.dbo.'
    elif idx == 2:
        area = '03'
        conn2 = connectDb.connect_Db3()
        db_owner = ''
    print("납부일자 업데이트")
    conn = connectDb.connect_Db2()
    curs = conn.cursor()
    sql1 = """select tnm_key from samc_cts.dbo.tnm_master where update_cargo_complete != 'Y' and area = '{}'""".format(area)
    curs.execute(sql1)
    res = curs.fetchall()
    api_napbu = api_unipass.unipass_api_Call()
    lst1 = []
    tnm_keys = tuple([res[x][0] for x in range(len(res))])
    curs2 = conn2.cursor()
    if len(tnm_keys) > 0:
        if len(tnm_keys) == 1:
            sql2 = """select impo_singo_date, impo_jingsu_type, impo_napbu_date2,impo_ok_date,impo_key from {}impo1 a 
                where a.impo_send_result != '' and impo_key = '{}'""".format(db_owner,tnm_keys[0])
        else:
            sql2 = """select impo_singo_date, impo_jingsu_type, impo_napbu_date2,impo_ok_date,impo_key from {}impo1 a 
                where a.impo_send_result != '' and impo_key in {}""".format(db_owner,tnm_keys)
        curs2.execute(sql2)
        res = curs2.fetchall()
        updatersnot43 = [res[x] for x in range(len(res)) if res[x][1] != '43']
        updatersis43 = [res[x] for x in range(len(res)) if res[x][1] == '43']
        sql3 = """update samc_cts.dbo.tnm_master set impo_singo_date = %s,jingsu_code = %s,napbu_date = %s,impo_ok_date = %s where tnm_key = %s """
        curs.executemany(sql3,tuple(updatersnot43))

        for i in updatersis43:
            lst2 = []
            key = i[-1]
            ok_date = i[3]
            jingsu_code = i[1]
            napbu_dt = i[2]
            napbu_date = api_napbu.update_napbu_date(ok_date,jingsu_code,napbu_dt)
            lst2 = [napbu_date,key]
            lst1.append(tuple(lst2))
        lst1 = tuple(lst1)
        sql2 = """update samc_cts.dbo.tnm_master set napbu_date = %s where tnm_key = %s"""
        print(sql2)
        curs.executemany(sql2,lst1)
        conn.commit()
        conn.close()
    conn.close()

def chk_cntr_inf():
    conn = connectDb.connect_Db2()
    curs = conn.cursor()
    cols = ['mrn','cntr_no','cntr_stszcd','seal_no1','seal_no2','seal_no3','tnm_key','area']
    cols = ','.join(cols)
    sql = """select mrn,area,tnm_key from samc_cts.dbo.tnm_master where update_cargo_complete != 'Y' and cntr_chk_yn != 'Y'"""
    curs.execute(sql)
    res = curs.fetchall()
    keys = []
    new_cntrs = []
    for i in range(len(res)):
        temp = []
        mrn = res[i][0]
        key = res[i][-1]
        area = res[i][1]
        apis = api_unipass.unipass_api_Call()
        cntrs = apis.api_container_inf(mrn)
        if cntrs: # 하나의 MRN 에 컨테이너가 복수 이상 들어올 수 있음
            for ii in range(len(cntrs)):
                cntrs[ii].append(key)
                cntrs[ii].append(area)# 결과 리스트에 tnm_key 를 더해주고
                new_cntrs.append(tuple(cntrs[ii]))
            temp.append(key)
            keys.append(tuple(temp))
            sql_delete = """delete from samc_cts.dbo.tnm_cntr where tnm_key = '{}'""".format(key)
            sql_insert = """insert into samc_cts.dbo.tnm_cntr ({}) values (%s, %s, %s, %s, %s, %s, %s, %s)""".format(cols)
            sql_update = """update samc_cts.dbo.tnm_master set cntr_chk_yn = 'Y' where tnm_key = '{}'""".format(key)
            curs.execute(sql_delete)
            print(new_cntrs)
            curs.executemany(sql_insert, tuple(new_cntrs))
            curs.execute(sql_update)
            conn.commit()
            new_cntrs  = []
        else:
            sql_update_false = """update samc_cts.dbo.tnm_master set cntr_chk_yn = 'N' where tnm_key = '{}'""".format(key)
            curs.execute(sql_update_false)
            conn.commit()
    conn.close()


def make_mail_data(res,damdangja,cond):
    conn = connectDb.connect_Db2()
    curs = conn.cursor()
    cust_code = res[1]
    ####메일 주소 수신 업체별 등록된 담당자 모두에게 메일 송신.
    ####통관 시스템에 있는 담당자에게만 송신 할 수 있는 기능 추가 --2022-08-16
    #### 통관시스템에 있는 담당자에게만 송신 하기 위한 옵션 구성 (tnm_cust1 --> 통관 시스템 담당자에게만 전송)
    sql_damdang_option = """select msg_sndtodamdang from samc_cts.dbo.tnm_cust1 where cust_code = '{}'""".format(cust_code)
    curs.execute(sql_damdang_option)
    res_damdng = curs.fetchone()
    if res_damdng[0] == 'Y':
        sql = """select damdangja,mails from samc_cts.dbo.tnm_cust2 where cust_code = '{}' and mail_snd_yn = 'Y' and damdangja = '{}'""".format(cust_code,damdangja)
    else:
        sql = """select damdangja,mails from samc_cts.dbo.tnm_cust2 where cust_code = '{}' and mail_snd_yn = 'Y'""".format(cust_code)
    curs.execute(sql)
    res_madd = curs.fetchall()
    #받는 사람
    if res_madd:
        for x in range(len(res_madd)):
            if res_madd[x][1]:
                if x == 0:
                    to = res_madd[x][1]
                else:
                    to = to + ';' + res_madd[x][1]
                print('발송메일주소',to)
        ############### 물류기한 템플릿 문구 추가 (유상서비스업체만 해당 - samc_cts.dbo.tnm_cust1 -- > paid_yn == 'Y')
        sql_paid = """select paid_yn from samc_cts.dbo.tnm_cust1 where cust_code = '{}'""".format(cust_code)
        curs.execute(sql_paid)
        paid = curs.fetchone()

        if paid[0] == 'Y' and cond == '3': # paid_yn 대상이 아니고, 물류기한(cond:3) 안내 메일이면, cond=5 적용 ---> 기존 text 형식 메일
            cond = '5'
        if cust_code == '013Y' and cond == 3:  ## 업체가 트렉스타의 경우 메일 본문에 해외거래처 추가 (물류기한 관리 - 박민정과장 요청)
            cond = '3A'
        elif cust_code == '013Y' and cond == 5:
            cond = '5A'
        sql_mails = """select gbn_txt,text from samc_cts.dbo.mail_templates where code = '{}'""".format(cond)
        curs.execute(sql_mails)
        resm = curs.fetchone()
        subject = resm[0]
        subject2 = res[-1] # cond 별 필드 개수가 달라서 mno를 항상 맨 마지막에 나열하도록 함
        if cond == '1': #tnm_key,cust_code,cust_name,bl,impo_singo_no,mrn,iphng_banip_storage_cd,iphng_banip_storage,trans_banip_storage_cd,trans_banip_storage,banchul_gihan,impo_damdangja,impo_ok_date,mno
            tnm_key = res[0]
            subject = subject + "(" + str(subject2) + ")"
            cust_name = res[2]
            bl = res[3]
            singo_no = res[4]
            mrn = res[5]
            if res[8]:
                jangchi_cd = res[8]
                jangchi_name = res[9]
            else:
                jangchi_cd = res[6]
                jangchi_name = res[7]
            banchul_gihan = reformat_date(res[10])
            ok_date = reformat_date(res[12])
            body = resm[1].format(cust_name,bl,singo_no,mrn,jangchi_name + '('+ jangchi_cd +')',ok_date,banchul_gihan,banchul_gihan)
            content_type = 'text'
            type = '반출기한(자동)'
        elif cond == '2': #tnm_key,cust_code,cust_name,bl,mrn,iphng_storage_cd,iphng_banip_storage,trans_banip_storage_cd,trans_banip_storage,import_declaration_gihan
            tnm_key = res[0]
            subject = subject + "(" + str(subject2) + ")"
            cust_name = res[2]
            bl = res[3]
            mrn = res[4]
            if res[5]:
                jangchi_cd = res[5]
                jangchi_name = res[6]
            else:
                jangchi_cd = res[7]
                jangchi_name = res[8]
            singo_gihan = reformat_date(res[9])
            body = resm[1].format(cust_name,bl,mrn,jangchi_name + '('+jangchi_cd+')',singo_gihan,singo_gihan)
            content_type = 'text'
            type = '신고기한(자동)'
        elif cond == '3' or cond == '5' or cond == '3A' or cond == '5A':
            tnm_key = res[0]
            subject = subject + "(" + str(subject2) + ")"
            cust_name = res[2]
            bl = res[3]
            if not res[4] or not res[5] or not res[6]: #dem ,det, sto 중 하나만 없어도 메일 발신 금지
                return
            dem = res[4]
            dem = reformat_date(dem)
            sto = res[5]
            sto = reformat_date(sto)
            det = res[6]
            det = reformat_date(det)
            ata = res[7]
            ata = reformat_date(ata)

            #########################해외거래처 정보 업데이트
            sql_exporter = """select Impo_gonggub_sangho from ncustoms.dbo.impo1 where impo_bl_no = '{}'""".format(
                bl)
            curs.execute(sql_exporter)
            try:
                exporter = curs.fetchone()[0]
            except:
                exporter = ''

            if cond == '3' or cond == '3A': #일반업체
                content_type = 'html'
                styles = """<style type="text/css">

                        body {
                          font-family:[Malgun Gothic];
                          font-size:10pt;
                        }
                        </style>"""
                if cond == '3A':
                    body = resm[1].format(styles,cust_name, bl, ata, dem, sto, det,exporter)
                else:
                    body = resm[1].format(styles, cust_name, bl, ata, dem, sto, det)
            elif cond == '5' or cond == '5A':# cond == '5' --> 유상서비스 대상업체
                content_type = 'text'
                if cond == '5A':
                    body = resm[1].format(cust_name, bl, ata, dem, sto, det,exporter)
                else:
                    body = resm[1].format(cust_name, bl, ata, dem, sto, det)
            type = '물류기한(자동)'
        cc = ''
        bcc = ''
        now = datetime.now()
        now = datetime.strftime(now, '%Y%m%d%H%M%S')
        #mails = {'to': to, 'userName': '관세법인 에스에이엠씨', 'subject': subject, 'body': body, 'contentType': 'text'}
        body = body.replace('\r','')
        body = body.replace('\n','\\n')
        sql_insert_mailmng = """If Not Exists(select ref_no,type from dsnsmsg.dbo.mailmng where ref_no = '{}' and  type = '{}')
                                    begin
                                    insert into dsnsmsg.dbo.mailmng (ref_no,mail_to,cc,bcc,usernm,subject,body,content_type,attatchment_yn,send_yn,snd_time1,type) 
                                    values {}
                                    end""".format(tnm_key,type,(tnm_key,to,cc,bcc,'관세법인 에스에이엠씨',subject,body,content_type,'N','N',now,type))
        curs.execute(sql_insert_mailmng)
        conn.commit()
        conn.close()

            #return mails


def reformat_date(tdate):
    if len(tdate) == 8:
        tdate = tdate[:4] + "-" + tdate[4:6] + "-" + tdate[6:8]
    elif len(tdate) > 8:
        tdate = tdate[:4] + "-" + tdate[4:6] + "-" + tdate[6:8] + ' ' + tdate[8:10] + ':' + tdate[10:12] + ':' + tdate[12:14]
    return tdate


def mail_kakao_data():
    ### 메일 보내기 ###
    conn = connectDb.connect_Db2()
    curs = conn.cursor()
    ### 1. 메일 전송 대상 기한 파악
    today = datetime.today()
    # 1.     반출기한 도래전 5일전 안내메일 발송 (전량 반출되지 않을 경우에도 메일 발송될수있게 부탁드립니다.) # 10일전 추가 --> 10일전 5일전
    for i in (5,1):
        d_day = timedelta(days=i)
        d_day = today + d_day
        d_day = datetime.strftime(d_day, '%Y%m%d')
        sql1 = """select tnm_key,cust_code,cust_name,bl,impo_singo_no,mrn,iphng_banip_storage_cd,iphng_banip_storage,trans_banip_storage_cd,trans_banip_storage,banchul_gihan,impo_damdangja,impo_ok_date,mno 
                from samc_cts.dbo.tnm_master where banchul_gihan = '{}' and update_cargo_complete != 'Y'""".format(d_day)
        curs.execute(sql1)
        res1 = curs.fetchall()
        for result in res1:
            key = result[0]
            damdangja = result[11]
            make_mail_data(result, damdangja,cond='1')

    # 2.     수입신고기한 도래전 15일전 안내메일 발송 --> 15일,5일,1일
    for i in (15,5,1):
        d_day = timedelta(days=i)
        d_day = today + d_day
        d_day = datetime.strftime(d_day, '%Y%m%d')
        sql2 = """select tnm_key,cust_code,cust_name,bl,mrn,iphng_banip_storage_cd,iphng_banip_storage,trans_banip_storage_cd,trans_banip_storage,import_declaration_gihan,impo_damdangja,mno 
                from samc_cts.dbo.tnm_master where import_declaration_gihan = '{}'
                and impo_ok_date = ''""".format(d_day)
        curs.execute(sql2)
        res2 = curs.fetchall()
        for result in res2:
            key = result[0]
            damdangja = result[10]
            make_mail_data(result, damdangja, cond='2')


    # 3.     DEM/ STO F/T 도래전 5일전 미반출시 안내메일 발송 --> 5일, 2일
    for i in (5,2):
        d_day = timedelta(days=i)
        d_day = today + d_day
        d_day = datetime.strftime(d_day, '%Y%m%d')
        ##mno 필드 항상 마지막에 나열
        sql3 = """select tnm_key,cust_code,cust_name,bl,dem_ft,sto_ft,det_ft,ata,impo_damdangja,mno 
                    from (select tnm_key,cust_code,cust_name,bl,dem_ft,sto_ft,det_ft,ata,impo_damdangja,mno from samc_cts.dbo.tnm_master where update_cargo_complete != 'Y') as tt
                    where tnm_key in 
                                (select tnm_key from (select * from samc_cts.dbo.tnm_master where det_ft not like '%%반출일%%') as b
                                where dem_ft = '{}' or sto_ft = '{}') 
                    or tnm_key in (
                                select tnm_key from samc_cts.dbo.tnm_master
                                where dem_ft = '{}' or sto_ft = '{}')""".format(d_day, d_day, d_day,d_day,d_day)

        ## 반출일로 부터 라는 문구와 20220101 10:00:00 형식의 텍스트가 혼재되어 쿼리가 더러워 졌다.
        try:
            curs.execute(sql3)
            res3 = curs.fetchall()
        except:
            mails = {'to': 'jnoo74@gmail.com', 'cc': 'njw@clsam.com', 'bcc': '', 'userName': '',
                     'subject': 'AIDMS 물류기한 산정 쿼리 오류발생',
                     'body': "AIDMS 물류기한 산정 쿼리 오류발생 \n " + sql3,
                     'contentType': 'text'}
            senders = api_For_Worksmobile()
            status = senders.send_mail(mails)
        for result in res3:
            sto = result[5]
            if sto == '' or not sto: #sto_ft 기재 안되어 있으면 메일 보내지 말기...
                continue
            key = result[0]
            damdangja = result[8]
            make_mail_data(result, damdangja, cond='3')


def update_tokens():
    key = winreg.HKEY_CURRENT_USER
    key_value = r"SOFTWARE\Tks\Ssks\Keys"
    key_value2 = r"SOFTWARE\GNU\XviD\Clis"

    reg = winreg.OpenKey(key, key_value, 0, winreg.KEY_ALL_ACCESS)
    refresh_token, type = winreg.QueryValueEx(reg, "rkys")

    reg = winreg.OpenKey(key, key_value2, 0, winreg.KEY_ALL_ACCESS)
    client_id, type = winreg.QueryValueEx(reg, 'ids')
    client_secret, type = winreg.QueryValueEx(reg, 'sds')

    url = 'https://auth.worksmobile.com/oauth2/v2.0/token'
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    grant_type = "refresh_token"
    data = {"refresh_token": refresh_token,
            "grant_type": grant_type,
            "client_id": client_id,
            "client_secret": client_secret}

    resp = requests.post(url, data=data, headers=headers)
    ttoken = resp.json()
    token = ttoken['access_token']
    akey = 'akys'  # access_token 저장

    reg = winreg.OpenKey(key, key_value, 0, winreg.KEY_ALL_ACCESS)
    winreg.SetValueEx(reg, akey, 0, REG_SZ, token)


def sending_mails(mails,tnm_key):
    conn = connectDb.connect_Db2()
    curs = conn.cursor()
    now = datetime.now()
    now = datetime.strftime(now,'%H%M%S')
    ###메일 전송은 레지스트리에서 변수 넣고 전송될 수 있도록 처리합시다.
    ###저녁 6시 이후에 레지스트리 송신 유무 N변경. 오전 첫실행시 송신유무 N 이면 전송 이후 Y 변경.
    senders = api_For_Worksmobile()
    status = senders.send_mail(mails)
    if status == 202:
        now = datetime.now()
        now = datetime.strftime(now,'%Y%m%d%H%M%S')
        sql = """update samc_cts.dbo.tnm_master set mailsnd_yn = 'Y' where tnm_key = '{}'""".format(tnm_key)
        curs.execute(sql)
        conn.commit()


def send_manual_mails():
    conn = connectDb.connect_Db2()
    curs = conn.cursor()
    sql = """select ref_no,mail_to,cc,bcc,usernm,subject,body,content_type,attatchment_yn from dsnsmsg.dbo.mailmng where send_yn = 'N'"""
    curs.execute(sql)
    res = curs.fetchall()
    if res:
        attatchs = []
        for i in res:
            if i[-1] == 'Y' and i[0] not in attatchs:
                attatchs.append(i[0])
        if attatchs:
            if len(attatchs) == 1:
                sql_attac = """select ref_no,filename,filetype,data from dsnsmsg.dbo.mailmng_attatch where ref_no = {}""".format(attatchs[0])
            else:
                sql_attac = """select ref_no,filename,filetype,data from dsnsmsg.dbo.mailmng_attatch where ref_no in {}""".format(tuple(attatchs))
            curs.execute(sql_attac)
            res_att = curs.fetchall()
            dics = []
            for i in range(len(res)):
                tnm_key = res[i][0]
                if res[i][8] == 'Y':
                    attatchments = []
                    for ii in range(len(res_att)):
                        if tnm_key == res_att[ii][0]:
                            filename = res_att[ii][1]
                            filetype = res_att[ii][2]
                            data = res_att[ii][3]
                            temp_dic = {'filename':filename,'fileType':filetype,'data':data}
                            attatchments.append(temp_dic)
                    body = res[i][6]
                    body = body.split('\\n')
                    bodys = ''
                    for ii in body:
                        bodys = bodys + ii + '\n'
                    reg = r'^[a-zA-Z0-9+-_.]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
                    p = re.compile(reg)
                    m = p.search(res[i][1])
                    if m:
                        mailto = m.group()
                    else:
                        continue
                    mails = {'to':mailto,'cc':res[i][2],'bcc':res[i][3],'userName':res[i][4],'subject':res[i][5],'body':bodys,'contentType':res[i][7],"attachments":attatchments}
                    senders = api_For_Worksmobile()
                    status = senders.send_mail(mails)
                    print(status)
        else:
            for i in range(len(res)):
                tnm_key = res[i][0]
                body = res[i][6]
                body = body.split('\\\\n')
                bodys = ''
                for ii in body:
                    ii = ii.replace("[", "'")
                    ii = ii.replace("]", "'")
                    bodys = bodys + ii + '\n'
                reg = r'^[a-zA-Z0-9+-_.]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
                p = re.compile(reg)
                m = p.search(res[i][1])
                if m:
                    mailto = m.group()
                else:
                    continue
                mails = {'to': mailto, 'cc': res[i][2], 'bcc': res[i][3], 'userName': res[i][4], 'subject': res[i][5],
                         'body': bodys, 'contentType': res[i][7]}
                #mails = {'to': 'jnoo74@gmail.com', 'cc': '', 'bcc': '', 'userName': '',
                 #'subject': '관세법인 에스에이엠씨 메일 리프레시 토큰 갱신 알림',
                 #'body': "관세법인 에스에이엠씨 메일 네이버웍스 모바일을 통한 메일 API 리프레시 토큰 갱신 만료일이 " + reflash_token_expire + "일 남았습니다.", 'contentType': 'text'}
                senders = api_For_Worksmobile()
                status = senders.send_mail(mails)

                if status == 202:
                    now = datetime.now()
                    now = datetime.strftime(now, '%Y%m%d%H%M%S')
                    sql = """update dsnsmsg.dbo.mailmng set send_yn = 'Y',snd_time2 = '{}' where ref_no = '{}'""".format(now,tnm_key)
                    curs.execute(sql)
                    conn.commit()

        conn.close()


def update_freetime():
    conn = connectDb.connect_Db2()
    #### 기초데이타 만들기
    sql = """select a.ata,a.mrn,a.bl,a.depart_cd,a.dem_ft,a.det_ft,a.sto_ft,b.cust_code, b.cust_name from samc_cts.dbo.tnm_submst a 
                join samc_cts.dbo.tnm_master b
                on a.tnm_key = b.tnm_key
                where a.dem_ft is not null or a.dem_ft != ''"""
    df = pd.read_sql(sql,con=conn)
    df.fillna('',inplace = True)
    df = df[(df['ata'] != '')&(df['mrn'] != '')&(df['ata'] != '미정')&(df['dem_ft'] != '')&(df['ata'].notnull())]
    df['mrn2'] = df['mrn'].apply(lambda x: x[2:6])
    for idx, row in df.iterrows():
        day1 = row['ata']
        day2 = row['dem_ft']
        try:
            day1 = datetime.strptime(day1, '%Y%m%d')
            day2 = datetime.strptime(day2, '%Y%m%d')
            diffs = day2 - day1
            diffs = diffs.days
            df.loc[idx, 'diffs'] = diffs
        except:
            continue
    df['len_mrn'] = df['mrn'].apply(lambda x: len(x))
    now = datetime.now()
    month3 = now - relativedelta(month=3)
    month3 = month3.strftime('%Y%m%d')
    df = df[df['ata'] > month3]
    df_std = df.groupby(['mrn2','cust_code','depart_cd','len_mrn'])[['diffs']].std() # df_Std  에 표준편차값을 두고 나중에 표준편차 4보다 작은것만 분리
    df = df.groupby(['mrn2','cust_code','depart_cd','len_mrn'])[['diffs']].min() # df 에는 선사,거래처,적재항 별로 그룹핑하여, 날짜 텀중 최소 기간을 기재
    df_std.reset_index(inplace = True)
    df_std['diffs_term'] = df_std['diffs']
    df_std['diffs_term'].fillna(0,inplace=True)
    df_std = df_std[(df_std['diffs_term'] < 4)&(df_std['diffs_term'] > -1)] #표준편차 4이하의 건만 기초자료로 축적
    df_std.drop(['diffs'],axis=1, inplace=True)
    df = pd.merge(df,df_std, how = 'left',on = ['mrn2','cust_code','depart_cd'])

    ###### demft 누락건 입력하기
    tdate = now - timedelta(days=10)
    tdate = tdate.strftime('%Y%m%d')
    sql = """select a.ata,a.cust_code, b.mrn,a.depart_cd from samc_cts.dbo.tnm_master a join (select tnm_key,ata,mrn,dem_ft from samc_cts.dbo.tnm_submst
                where ata >= '{}') b
                on a.tnm_key = b.tnm_key 
				join (select cust_code from samc_cts.dbo.tnm_cust1 where paid_yn is NULL or paid_yn = '') c
				on a.cust_code = c.cust_code
				where b.dem_ft is NULL or b.dem_ft = ''""".format(tdate)
    df2 = pd.read_sql(sql,con=conn)
    df2['mrn_2'] = df2['mrn'].apply(lambda x: x[2:6])
    df2['len_mrn'] = df2['mrn'].apply(lambda x: len(x))
    df = pd.merge(df,df2, how = 'inner', left_on = ['mrn2','cust_code','depart_cd','len_mrn'], right_on = ['mrn_2','cust_code','depart_cd','len_mrn'])
    for idx,row in df.iterrows():
        ata = row['ata']
        ata = datetime.strptime(ata, '%Y%m%d')
        days = row['diffs']
        diffsdays = timedelta(days=int(str(days).replace('.0',''))) # 타임델타 사용해서 계산할 기간 datetime 형식으로 변환
        t_date = ata + diffsdays  # 날짜 계산
        t_date = t_date.strftime('%Y%m%d') # datetime 문자형으로 변호나
        cust_code = row['cust_code']
        mrn = row['mrn']
        sql1 = """update samc_cts.dbo.tnm_master set dem_ft = '{}', det_ft = '{}' 
                    where cust_code = '{}' and mrn = '{}' and area = '02'""".format(t_date,t_date,cust_code,mrn)
        sql2 = """update samc_cts.dbo.tnm_submst set dem_ft = '{}', det_ft = '{}' 
                            where tnm_key in (select tnm_key from samc_cts.dbo.tnm_master where cust_code = '{}' and mrn = '{}' and area = '02')""".format(t_date, t_date, cust_code, mrn)
        curs = conn.cursor()
        curs.execute(sql1)
        curs.execute(sql2)
    conn.commit()

now = datetime.now()
now = datetime.strftime(now,'%H%M%S')

### 통관 데이타 가저오기
now_ms = now[2:]
if now_ms >= '1000' and now_ms <= '1500': # 10분에서 20분 사이는 가지고 오지 않는다.
    pass
else:
    for i in range(3):
        cust_cd = get_cust(i)
        getdata_class = import_bl.get_DataFromNcustoms()
        getdata_class.query(cust_cd,i)

### 관세청 수입화물 진행정보 API call 대상 취합
conn = connectDb.connect_Db2()
curs = conn.cursor()
now = now[2:]
# select  업데이트 필요데이타  수입신고 수리일자 없는 건들 모두 select
sql = """select bl,tnm_key,year,area from samc_cts.dbo.tnm_master where update_cargo_complete != 'Y'
                """
curs.execute(sql)
res = curs.fetchall()
conn.commit()
conn.close()

if res:
    now = datetime.now()
    now = datetime.strftime(now, '%H%M%S')
    bl = list(res)
    if now < '190000':
        now_ms = now[2:]
        if now_ms >= '1000' and now_ms <= '5200':

            get_api = api_call.getInfo_api_importCargo()
            lst = get_api.tracking_importCargo1(bl)

            ### API  수신 정보 update. --보세구역, 반출입 일자 , 중량, 화물관리번호등.....
            print('수입화물진행정보 업데이트')
            apiinfo_update_tnm(lst)
            ### 컨테이너 정보 확인 #####
            print('컨테이너 정보 확인')
            chk_cntr_inf()
            ### 2023-01-16 --> 분할 수입신고건의 경우(BL분할 아님) 첫번째 신고건이 수리되었을 경우 두번째 신고건에 대한 신고지연 가산세 안내 메일 발송되지 않는 문제 있음.

### Freetime 자동 기재
update_freetime() ### 보류.....


### 월납건 징수형태 43,44 납부기한 update
for i in range(3):
    napbu_gihan_update(i)

if now > '090000' and now < '091000':
    heelae = HEE_LAE_remind_mails()
    heelae.begin()

#### 메일 전송 준비 ######
if now > '085000' and now < '190000':
    #update_tokens()
    mail_kakao_data()

send_manual_mails()



