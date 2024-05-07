#### T&M 수입신고 데이타 자동 가져오는 기능
#### T&M 알림톡, 메일 자동 전송기능

import connectDb
import get_today
import day_calc
import datetime
import pandas as pd

class get_DataFromNcustoms:

    def query(self, cust_cd,idx):
        self.idx = idx
        conn = connectDb.connect_Db2()
        curs = conn.cursor()
        cols = ['tnm_key','bl','impo_ok_date','year','jingsu_code','napbu_date','update_cargo_complete','cust_name','mailsnd_yn','mno','cust_code','kakao_alim_yn','cntr_chk_yn','area','ata','impo_damdangja']
        ncols = ','.join(cols)
        tstr = ','.join(['%s']*len(cols))
        #### 신고서에서 가져오는 쿼리 <부산>

        today = get_today.get_date()
        tdate = day_calc.get_date(today, -7)
        searching_date = datetime.datetime.strftime(tdate, '%Y%m%d')
        now = datetime.datetime.now()
        bf30m = now - datetime.timedelta(minutes=5)
        bf30m = datetime.datetime.strftime(bf30m, '%H%M%S')
        year = today[:4]
        values = self.add_values(searching_date, bf30m, year, cust_cd,False)
        if values:
            for x in range(len(values)):
                sql_insert = """If Not Exists(select bl from samc_cts.dbo.tnm_master where bl = '{}')
                                                                                            Begin
                                                                                            insert into samc_cts.dbo.tnm_master ({}) values {}
                                                                                            End""".format(values[x][1],ncols, values[x])
                curs.execute(sql_insert)
                conn.commit()

        if values:
            for x in range(len(values)):
                sql_insert = """If Not Exists(select bl from samc_cts.dbo.tnm_master where bl = '{}')
                                                                                                   Begin
                                                                                                   insert into samc_cts.dbo.tnm_master ({}) values {}
                                                                                                   End""".format(
                    values[x][1], ncols, values[x])
                curs.execute(sql_insert)
                conn.commit()

        ## 일괄복사 직후 수정전 데이타(잘못된 데이타 가져 온경우)
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
        curs2 = conn2.cursor()
        #sql1 = """select a.tnm_key,a.bl,b.impo_key,b.impo_bl_no
        #            from samc_cts.dbo.tnm_master a inner join ncustoms.dbo.impo1 b on a.tnm_key = b.impo_key
        #            where a.bl <> b.impo_bl_no""" ### BL이 입력된 후 변경된 경우를 대비해서 이 쿼리를 사용하였으나, 인천지사 mysql을 읽어와야 하는 경우가 생긴 이후엔 아래와 같이 처리
        #curs.execute(sql1)
        #res = curs.fetchall()
        sql1 = """select tnm_key from samc_cts.dbo.tnm_master where impo_ok_date = '' and area = '{}'""".format(area)
        curs.execute(sql1)
        res = curs.fetchall()
        lst_key = []
        for i in range(len(res)):
            key = res[i][0]
            lst_key.append(key)
        if lst_key:
            if len(lst_key) == 1:
                sql2 = """select impo_bl_no,impo_key from {}impo1 where impo_key = {}""".format(db_owner,lst_key[0])
            else:
                sql2 = """select impo_bl_no,impo_key from {}impo1 where impo_key in {}""".format(db_owner,tuple(lst_key))
            curs2.execute(sql2)
            res2 = curs2.fetchall()
            sql3 = """update samc_cts.dbo.tnm_master set bl = %s where tnm_key = %s and area = '{}'""".format(area)
            curs.executemany(sql3,res2)
            conn.commit()



        #### 관리번호 빠진건 자동업데이트
        tdate = day_calc.get_date(today,-31)
        searching_date = datetime.datetime.strftime(tdate,'%Y%m%d')
        sql_get_key = """select tnm_key,bl from samc_cts.dbo.tnm_master where mno = '' and ata > '{}'""".format(searching_date)
        curs.execute(sql_get_key)
        res = curs.fetchall()
        lst_key = []
        for xx in res:
            lst_key.append(xx[0])
        sql_ncustoms = """select impo_file_no1,impo_key from {}impo1 where impo_key in {}""".format(db_owner,tuple(lst_key))
        curs2.execute(sql_ncustoms)
        update_values = curs2.fetchall()
        #for x in res:
        #    update_values = []
        #    if x[0] != '':
        #        update_values.append(x)
        sql_update = """update samc_cts.dbo.tnm_master set mno = %s where tnm_key = %s"""
        if update_values:
            curs.executemany(sql_update,update_values)
        conn.commit()
        conn.close()



    def add_values(self,searching_date,bf30m,year,cust_cd,keys):
        conn = connectDb.connect_Db2()
        today = get_today.get_date()
        idx = self.idx
        if idx == 0:
            db_owner = 'ncustoms.kcba.'
            conn = connectDb.connect_Db()
            area = '01'
        elif idx == 1:
            db_owner = 'ncustoms.dbo.'
            conn = connectDb.connect_Db2()
            area = '02'
        elif idx == 2:
            db_owner = ''
            conn = connectDb.connect_Db3()
            area = '03'
        curs = conn.cursor()
        if keys:
            if len(keys) == 1:
                sql_select = """select impo_key,impo_bl_no,impo_ok_date,Impo_jingsu_type, impo_napse_sangho,impo_file_no1,impo_napse_code, from {}impo1 where 
                               impo_key = '{}' and impo_bl_no != ''""".format(db_owner,keys[0])
            else:
                sql_select = """select impo_key,impo_bl_no,impo_ok_date,Impo_jingsu_type, impo_napse_sangho,impo_file_no1,impo_napse_code from {}impo1 where 
                               impo_key in {} and impo_bl_no != ''""".format(db_owner,tuple(keys))
        else:
            if cust_cd:
                #### ADDDTTIME 이 공란일때를 대비해서 임시방편으로 업데이트 치는 쿼리 추가 '2022-08-10'
                tyear = today[:4]
                sql_upadd = """update {}impo1 set AddDtTime = '{}' where impo_napse_code in {} and impo_year = '{}' and AddDtTime is NULL""".format(db_owner,today+'000000',cust_cd,tyear) #20220810181427
                curs.execute(sql_upadd)
                conn.commit()
                if len(cust_cd) > 1:
                    sql_select = """select impo_key,impo_bl_no,impo_ok_date,Impo_jingsu_type, impo_napse_sangho,impo_file_no1,impo_napse_code,impo_damdangja from {}impo1 where 
                                       impo_napse_code in {} and AddDtTime > '{}' and AddDtTime < '{}' and impo_bl_no != ''""".format(db_owner,cust_cd,
                                                                                                                 searching_date + '000000',
                                                                                                             today + bf30m)

                else:
                    sql_select = """select impo_key,impo_bl_no,impo_ok_date,Impo_jingsu_type, impo_napse_sangho,impo_file_no1,impo_napse_code,impo_damdangja from {}impo1 where 
                                       impo_napse_code = '{}' and AddDtTime > '{}' and AddDtTime < '{}' and impo_bl_no != ''""".format(db_owner,cust_cd[0],
                                                                                                                 searching_date + '000000',
                                                                                                                 today + bf30m)
            else:
                return False
        curs.execute(sql_select)
        res = curs.fetchall()
        returned_values = []
        for x in res:
            values = []
            tnm_key = x[1] # 신고서 impo_key  에서 BL로 주키 변경 2022.08.03
            bl = x[1]
            jingsu = x[3]
            cust_name = x[4]
            update_cargo_complete = 'N'
            mno = x[5]
            try:
                mno = mno.encode('ISO-8859-1').decode('cp949')
            except:
                pass
            cust_code = x[6]
            try:
                cust_name = cust_name.encode('ISO-8859-1').decode('cp949')
            except:
                pass
            impo_damdangja = x[7]
            try:
                impo_damdangja = impo_damdangja.encode('ISO-8859-1').decode('cp949')
            except:
                pass
            if jingsu == '11':
                napbu_dt = day_calc.get_date(today, 10)
                napbu_dt = datetime.datetime.strftime(napbu_dt, '%Y%m%d')
            elif jingsu in ('13', '14'):
                napbu_dt = day_calc.get_date(today, 15)
                napbu_dt = datetime.datetime.strftime(napbu_dt, '%Y%m%d')
            elif jingsu == '43':
                napbu_dt = ''
            values.append(tnm_key)
            values.append(bl)
            values.append('')  # 수입신고수리일은 '' 처리
            values.append(year)
            values.append(jingsu)
            values.append(napbu_dt)
            values.append(update_cargo_complete)
            values.append(cust_name)
            values.append('N')
            values.append(mno)
            values.append(cust_code)
            values.append('N')
            values.append('')
            values.append(area)
            values.append('미정')
            values.append(impo_damdangja)
            values = tuple(values)
            print('BL:' + bl + "이 추가됩니다.")
            returned_values.append(values)

        return tuple(returned_values)






