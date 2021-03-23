import sys, re, os, json, logging, requests
from requests.auth     import HTTPBasicAuth
from datetime          import datetime
from flask             import Flask
from flask_wtf.csrf    import CSRFProtect
from flask_sqlalchemy  import SQLAlchemy
from sqlalchemy.exc    import OperationalError

csrf = CSRFProtect()
app  = Flask(__name__)
csrf.init_app(app)

class Config(object):
    DEBUG      = False
    TESTING    = False
    SECRET_KEY = ''
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    EXPIRATION                     = 3600

    CIRCLE_SYMBOL = u"\U0001F785"

    DB_SETTINGS = {
        'DB_SCHEMA':'mysql+pymysql',
        'DB_NAME'  :'',
        'USER_NAME':'',
        'USER_PWD' :'',
        'CHARSET'  :'utf8mb4'
    }

    SHARED_HEADERS = {
        'Accept'         : 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'en,zh-TW;q=0.9,zh;q=0.8,en-US;q=0.7',
        'Cache-Control'  : 'max-age=0',
        'Connection'     : 'Close',
        'Connection'     : 'keep-alive',
        'Sec-Fetch-Dest' : 'document',
        'Sec-Fetch-Mode' : 'navigate',
        'Sec-Fetch-Site' : 'same-origin',
        'Sec-Fetch-User' : '?1',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent'     : 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.83 Safari/537.36',
    }

    ILLEGEL_PRESIDENT_NO_LIST = [None, '', '00000000']
    OPEN_DATA_INFO = {
        'LISTED_COMPANY_1':{ # 上市
            'FILE_PATH':'./data/上市公司基本資料.json',
            'DOWNLOAD_LINK':'https://quality.data.gov.tw/dq_download_json.php?nid=18419&md5_url=9791ec942cbcb925635aa5612ae95588'
        },
        'LISTED_COMPANY_2':{ # 上櫃
            'FILE_PATH':'./data/上櫃公司基本資料.json',
            'DOWNLOAD_LINK':'https://quality.data.gov.tw/dq_download_json.php?nid=25036&md5_url=1aae8254db1d14b0d113dd93f2265d06'
        },
        'LISTED_COMPANY_3':{
            'FILE_PATH':'./data/興櫃公司基本資料.json',
            'DOWNLOAD_LINK':'https://quality.data.gov.tw/dq_download_json.php?nid=28568&md5_url=7c1850be92ee9191486528d32244b751'
        },
        'LISTED_COMPANY_4':{
            'FILE_PATH':'./data/公發公司基本資料.json',
            'DOWNLOAD_LINK':'https://quality.data.gov.tw/dq_download_json.php?nid=28567&md5_url=1ef93c02be75c48ec6d8ba8f600c1fbd'
        },
        'IMPORTS_EXPORTS':{
            'FILE_PATH':'./data/出進口廠商登記資料.json',
            'DOWNLOAD_LINK':'https://fbfh.trade.gov.tw/fb/web/downloadCompanyDataf.jsp'
        },
        'DIR_SUP_SHARES_1':{
            'FILE_PATH':'./data/上市公司董監事持股餘額明細資料.json',
            'DOWNLOAD_LINK':'https://quality.data.gov.tw/dq_download_json.php?nid=22811&md5_url=876f6b5fc4775ee7bc37a5a3c57a7fa6'
        },
        'DIR_SUP_SHARES_2':{
            'FILE_PATH':'./data/上櫃公司董監事持股餘額明細資料.json',
            'DOWNLOAD_LINK':'https://quality.data.gov.tw/dq_download_json.php?nid=22812&md5_url=219d2e336cbb012db8e5b24c80fa49c6'
        },
        'DIR_SUP_SHARES_3':{
            'FILE_PATH':'./data/興櫃公司董監事持股餘額明細資料.json',
            'DOWNLOAD_LINK':'https://quality.data.gov.tw/dq_download_json.php?nid=107015&md5_url=13fb78f9552e75bc401035e350ed4710'
        },
        'DIR_SUP_SHARES_4':{
            'FILE_PATH':'./data/公發公司董監事持股餘額明細資料.json',
            'DOWNLOAD_LINK':'https://quality.data.gov.tw/dq_download_json.php?nid=104212&md5_url=9fd0e7aa3b93d304bfbffa58f863be92'
        },
        'LISTED_BIG_SHAREHOLDER_1':{
            'FILE_PATH':'./data/上市公司持股逾10%大股東名單.json',
            'DOWNLOAD_LINK':'https://quality.data.gov.tw/dq_download_json.php?nid=18422&md5_url=c066fbc9ac0df01415bec7973837d93e'
        },
        'LISTED_BIG_SHAREHOLDER_2':{
            'FILE_PATH':'./data/上櫃公司持股逾10%大股東名單.json',
            'DOWNLOAD_LINK':'https://quality.data.gov.tw/dq_download_json.php?nid=18423&md5_url=866be82c67213417cedd791a9268e4ad'
        },
        'TAX_REGISTRY':{
            'FILE_PATH':'./data/全國營業(稅籍)登記資料集.json',
            'DOWNLOAD_LINK':'https://quality.data.gov.tw/dq_download_json.php?nid=9400&md5_url=67531944cf6b13df7b9563b4cd472221'
        },
    }

    CRAWL_INFO = {
        'GCIS':{
            'HOST':'https://findbiz.nat.gov.tw/'
            },
        'MOPS':{
            'HOST':'https://mops.twse.com.tw/'
            }
        }
    
    CRAWL_INFO['GCIS']['QUERY_URL'] = '{}fts/query/'.format(CRAWL_INFO['GCIS']['HOST'])
    CRAWL_INFO['GCIS']['QUERY_LIST'] = '{}QueryList/queryList.do'.format(CRAWL_INFO['GCIS']['QUERY_URL'])
    CRAWL_INFO['GCIS']['QUERY_INIT_URL'] = '{}QueryBar/queryInit.do'.format(CRAWL_INFO['GCIS']['QUERY_URL'])
    CRAWL_INFO['GCIS']['CMPY_URL'] = '{}QueryCmpyDetail/queryCmpyDetail.do'.format(CRAWL_INFO['GCIS']['QUERY_URL'])
    CRAWL_INFO['GCIS']['BUSM_URL'] = '{}QueryBusmDetail/queryBusmDetail.do'.format(CRAWL_INFO['GCIS']['QUERY_URL'])
    CRAWL_INFO['GCIS']['BRCMPY_URL'] = '{}QueryBrCmpyDetail/queryBrCmpyDetail.do'.format(CRAWL_INFO['GCIS']['QUERY_URL'])
    CRAWL_INFO['GCIS']['FACT_URL'] = '{}QueryFactDetail/queryFactDetail.do'.format(CRAWL_INFO['GCIS']['QUERY_URL'])
    CRAWL_INFO['GCIS']['LMTD_URL'] = '{}QueryLmtdDetail/queryLmtdDetail.do'.format(CRAWL_INFO['GCIS']['QUERY_URL'])

    CRAWL_INFO['GCIS']['QUERY_URL_COMPARSION'] = {
        'cmpy':CRAWL_INFO['GCIS']['CMPY_URL'],
        'busm':CRAWL_INFO['GCIS']['BUSM_URL'],
        'brcmpy':CRAWL_INFO['GCIS']['BRCMPY_URL'],
        'fact':CRAWL_INFO['GCIS']['FACT_URL'],
        'lmtd':CRAWL_INFO['GCIS']['LMTD_URL']
    }

    KG_INFORMATION = {
        'KG_ACCOUNT' : '',
        'KG_PASSWORD': ''
    }

    GOOGLE_SENDER_CONF = {
        'FROM_ADDRESS':'',
        'FROM_ADDRESS_PSW':'',
        'SMTP_SERVER':'smtp.gmail.com',
        'SMTP_PORT':'587'
    }
    ILLEGAL_NAME_LIST = [None, '董事', '暫缺', '撤銷','從缺', '缺額', '懸缺', '補選', '委任關係不存在','懸缺暫不補選', '死', '留缺', '辭任', '解任', '待改派']

##### 正式機用設定
def FormalitySettings():
    app.config['KG_INFORMATION']['KG_URL'] = ''

    app.config['DB_SETTINGS']['IP']        = ''
    app.config['DB_SETTINGS']['PORT']      = '3306'

# 主機測試版
def DevSettings():
    app.config['KG_INFORMATION']['KG_URL'] = ''

    app.config['DB_SETTINGS']['IP']        = '10.0.1.81'
    app.config['DB_SETTINGS']['PORT']      = '3306'

#### 本機開發用設定
def LocalDevSettings():
    app.config['KG_INFORMATION']['KG_URL'] = ''
    app.config['DB_SETTINGS']['IP']       = ''
    app.config['DB_SETTINGS']['PORT']     = '3306'

def GeneralSettings():
    app.config['SQLALCHEMY_DATABASE_URI'] = '%(DB_SCHEMA)s://%(USER_NAME)s:%(USER_PWD)s@%(IP)s:%(PORT)s/%(DB_NAME)s?charset=%(CHARSET)s' % app.config['DB_SETTINGS']

    tmp_dict = {}
    config_tmp_filepath = '/app/settings/config_tmp.json'
    for key in ['KGNAME2KGID', 'KGName2KGDomain', 'KGID2KGName', 'KGID2KGDomain']:
        if key not in app.config:
            tmp_dict[key] = {}

    # 去CE的API拉KG資訊下來
    try:
        url = '{}project'.format(app.config['KG_INFORMATION']['KG_URL'])
        params = {
            'user_id':app.config['KG_INFORMATION']['KG_ACCOUNT'],
            'limit'  :100000000,
            'orderby':'name'
        }
        rsp = requests.get(url, params=params, auth=HTTPBasicAuth(app.config['KG_INFORMATION']['KG_ACCOUNT'], app.config['KG_INFORMATION']['KG_PASSWORD']))
        for data in rsp.json()['data']:
            tmp_dict['KGNAME2KGID'][data['name']] = data['id']
            tmp_dict['KGName2KGDomain'][data['name']] = data['domain']
            tmp_dict['KGID2KGName'][data['id']] = data['name']
            tmp_dict['KGID2KGDomain'][data['id']] = data['domain']
        content = json.dumps(tmp_dict, ensure_ascii=False, indent=4)
        f = open(config_tmp_filepath, 'w')
        f.write(content)
        f.close()
    except:
        # 無法連到CE的API，先從暫存讀取
        f = open(config_tmp_filepath, 'r')
        tmp_dict = json.loads(f.read())
        f.close()
    for key, value in tmp_dict.items():
        app.config[key] = value
    del(tmp_dict)

    app.config['KGNameTemplate'] = {}
    for kg_name in ['公司重大資訊', 
                    '公司與關係人進貨資訊',
                    '公司與關係人銷貨資訊',
                    '公司與關係人應收資訊',
                    '公司與關係人應付資訊']:
        app.config['KGNameTemplate'][kg_name] = '{}-{{}}年'.format(kg_name)

def scheduler_log():
    cron_log = logging.getLogger()
    log_fmt  = logging.Formatter('[%(levelname)s][%(asctime)s]%(message)s', '%Y-%m-%d %H:%M:%S') 
    handler  = logging.StreamHandler()
    handler.setFormatter(log_fmt)
    cron_log.setLevel(logging.WARNING)
    cron_log.addHandler(handler)

app.config.from_object('settings.environment.Config')
dynamic_settings = {
    'FORMALITY':FormalitySettings,
    'DEV'      :DevSettings,
    'LOCAL'    :LocalDevSettings,
    None       :LocalDevSettings
}

dynamic_settings[os.environ.get('API_PROPERTY')]()
GeneralSettings()

db = SQLAlchemy(app)
scheduler_log()

@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'POST, OPTIONS, GET, PATCH, DELETE, PUT')
    db.session.rollback()
    db.session.close()
    return(response)

@app.teardown_request
def teardown_request(exception):
    if exception:
        db.session.rollback()
    db.session.remove()
