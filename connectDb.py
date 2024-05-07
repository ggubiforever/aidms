import pymssql
import pymysql

def connect_Db():
    ipadd = '210.217.154.130' #본사 서버 라이브
    #ipadd = '127.0.0.1' #테스트용
    conn = pymssql.connect(server=ipadd, user='sa',port = 1433,
                           password='kcbapasswd',charset = 'UTF8')
    return conn


def connect_Db2(): #부산 서버 통관
    ipadd = '203.233.239.194' #부산 서버 라이브
    #ipadd = '127.0.0.1' #테스트용
    conn = pymssql.connect(server=ipadd, user='sa',port = 1433,
                           password='Ncomuser1',charset = 'UTF8')
    return conn


def connect_Db3(): #인천 서버 통관 'UTF8'
    ipadd = '210.217.155.2' #인천서버
    #ipadd = '127.0.0.1' #테스트용
    conn = pymysql.connect(host=ipadd, user='kcba',port = 3306,
                           passwd='kcbapasswd', db='ncustoms', charset = 'euckr')
    return conn


def connect_Db_ttks(): #인천 서버 통관 'UTF8'
    ipadd = "203.233.239.194"
    #ipadd = '127.0.0.1' #테스트용
    conn = pymysql.connect(host=ipadd, user='root',port = 32705,
                           passwd='^^sam16006^^', db='ttks', charset = 'utf8')
    return conn
