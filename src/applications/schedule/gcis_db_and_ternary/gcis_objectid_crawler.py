if __name__ == '__main__':
    import sys
    try:
        sys.path.append('/app/')
    except:
        sys.path.append('../../../')
import os, json, time, gc, traceback, base64, psutil
from copy                 import deepcopy
from lib.gcis_ternary     import OpenData2Dict
from models.GCIS          import GCIS_ObjectID
from lib.gcis_web_crawler import gcis_crawler_class
from lib.gmail_sender     import GmailSender
from lib.func_tool        import RequestForMiltipleTimes
from models.SHARE_TABLE   import get_CrawlerTriggerTime_trigger_time, update_CrawlerTriggerTime_trigger_time, CompanyData
from sqlalchemy           import or_
from settings.environment import db, app

def check_same_process_still_running(script_name_func):
    pid_list = []
    for process in psutil.process_iter():
        # 檢查pid是否存在、是否以python執行、python執行的檔案是否為該排程
        try:
            process_command = ' '.join(process.cmdline())
        except:
            continue
        if psutil.pid_exists(process.pid) and 'python' in process_command.lower() and script_name_func in process_command:
            pid_list.append(process.pid)
    # 代表包含這個程式在內，有兩個以上相同的排程正在運行
    return(True if pid_list and os.getpid()>min(pid_list) else False)

def gcis_objectId_adder():
    main_name = os.path.basename(__file__)
    try:
        GCIS_Class = gcis_crawler_class()
        GCIS_Class.remove_useless_proxy(GCIS_Class.get_proxy_dict_list())

        opendataclass = OpenData2Dict()
        president_no_list = list(opendataclass.get_dict('listed_company_dict').keys())
        president_no_list.extend([x.tax_id for x in CompanyData.query.filter(CompanyData.ho_tax_id==None).all()])
        if not president_no_list:
            raise Exception('{}: president_no_list 是空的'.format(main_name))

        print('{}: 將統編列表內，尚未匯入的統編匯入'.format(main_name))

        progress = 0
        offset = 0
        limit = 10000
        while True:
            president_no_list_tmp = president_no_list[offset:(offset+limit)]
            if not president_no_list_tmp:
                break
            offset+=limit
            conds = [GCIS_ObjectID.president_no==president_no for president_no in president_no_list_tmp]
            db_president_no_dict = {db_result.president_no:True for db_result in GCIS_ObjectID.query.with_entities(GCIS_ObjectID.president_no).filter(or_(*conds)).all()}

            for iiindex, president_no in enumerate(president_no_list_tmp):
                iiindex+=offset
                progress_tmp = int(iiindex/len(president_no_list)*100)
                if progress_tmp!=progress:
                    progress = deepcopy(progress_tmp)
                    print('{}: 進度 {}%'.format(main_name, progress))
                if president_no not in db_president_no_dict:
                    db.session.add(GCIS_ObjectID(president_no=president_no))
        GCIS_ObjectID.query.filter(GCIS_ObjectID.exist==None).update({'params':None})
        db.session.commit()

        gcis_headers = deepcopy(app.config['SHARED_HEADERS'])
        gcis_headers['Referer'] = 'https://findbiz.nat.gov.tw/fts/query/QueryList/queryList.do'
        gcis_headers['Origin']  = 'https://findbiz.nat.gov.tw'
        gcis_headers['Host']    = 'findbiz.nat.gov.tw'

        if check_same_process_still_running(main_name):
            print('{}: 尚有其他相同的程式執行中'.format(main_name))
            return

        print('{}: 開始透過查詢，獲得公司Bankey'.format(main_name))
        while True:
            db_result = GCIS_ObjectID.query.filter(GCIS_ObjectID.exist==None).first()
            if not db_result:
                print('{}: 無需要獲得Bankey的項目'.format(main_name))
                break
            print('----------')
            print(db_result.president_no)
            while True:
                status, params = GCIS_Class.gcis_search_list_crawler(db_result)
                break
            print(status, params)
    except:
        print(traceback.format_exc())
        # ggg = GmailSender('{}出現錯誤'.format(main_name), 'douerchiang@iii.org.tw', traceback.format_exc())
        # ggg.send_email()
if __name__ == '__main__':
    gcis_objectId_adder()
