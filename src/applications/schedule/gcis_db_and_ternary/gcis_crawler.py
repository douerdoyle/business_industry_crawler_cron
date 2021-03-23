import sys
if __name__ == '__main__':
    try:
        sys.path.append('/app/')
    except:
        sys.path.append('../../../')
import os, traceback, base64, time, requests
from random                 import shuffle
from pprint                 import pprint
from datetime               import datetime, timedelta
from settings.environment   import app, db
from sqlalchemy             import desc, or_, func
from lib.func_tool          import RequestForMiltipleTimes, get_disj_param
from lib.gcis_ternary       import OpenData2Dict, get_gcis_detail, gcis_check_add2db
from lib.gcis_web_crawler   import gcis_crawler_class
from lib.gmail_sender       import GmailSender
from models.GCIS            import GCIS_Company, GCIS_ObjectID
from models.SHARE_TABLE     import get_CrawlerTriggerTime_trigger_time, update_CrawlerTriggerTime_trigger_time, CompanyData, CompanySymbolStock
from copy                   import deepcopy

crawler_info_dict = {
    'gcis_list_company':'GCIS上市上櫃公司',
    'gcis_normal_company':'GCIS一般公司',
    'gcis_new_company':'GCIS新公司',
    'customization':'客製化'
}

business_current_false_list = [
    '撤銷公司設立', 
    '廢止許可已清算完結', 
    '清理完結', 
    '解散', 
    '遷他縣市', 
    # 'null', 
    '命令停業', 
    '廢止', 
    '破產已清算完結', 
    '接管', 
    '撤銷許可', 
    '廢止認許', 
    '廢止登記', 
    '合併解散', 
    '解散已清算完結', 
    '撤銷認許已清算完結', 
    '撤回登記已清算完結', 
    '撤銷登記', 
    '歇業', 
    '列入廢止', 
    '撤銷設立登記', 
    '列入廢止中', 
    '撤回登記', 
    '廢止許可', 
    '終止破產', 
    '破產', 
    '破產程序終結(終止)', 
    '廢止已清算完結', 
    '撤銷已清算完結', 
    '清理', 
    '撤回認許', 
    '重整', 
    '破產程序終結(終止)清算中', 
    '核准設立,但已命令解散', 
    '撤回認許已清算完結', 
    '廢止認許已清算完結', 
    '核准停業', 
    '撤銷無需清算', 
    '撤銷', 
    # None, 
    '申覆(辯)期', 
    '撤銷認許', 
    '塗銷破產', 
    '歇業/撤銷', 
    '停業']

business_current_true_list = [
    '核准認許', 
    '核准許可報備', 
    '核准登記', 
    '核准報備', 
    '核准許可登記', 
    '核准設立', 
]

gcis_detail_type_dict = {
    'CMPY_URL':'cmpy',
    'BUSM_URL':'busm'
}

def crawler_funciont(crawler_name):
    if crawler_name not in crawler_info_dict:
        err_message = '不支援的 crawler_name: {}, 將 crawler_name 改為 {}'.format(crawler_name, list(crawler_info_dict.keys())[0])
        print(err_message)
        crawler_name = list(crawler_info_dict.keys())[0]
    main_name = crawler_info_dict[crawler_name]
    try:
        trigger_time = datetime.now()
        update_CrawlerTriggerTime_trigger_time(crawler_name, trigger_time)

        # 處理並取得公司統編與職稱對應的dictionary、處理上市、上櫃、興櫃、公開發行董監事持股盈餘明細的OPEN DATA資料，取得職稱
        print('開始讀取Open Data')
        opendataclass = OpenData2Dict()

        print('取得自上次排程時間以來，未更新之「{}」統一編號列表'.format(main_name))
        # 上市上櫃公司
        tmp_list = list(opendataclass.get_dict('listed_company_dict').keys())
        if crawler_name=='gcis_list_company':
            president_no_list = deepcopy(tmp_list)
            if not president_no_list:
                print('president_no_list.(1)')
        # 新公司或商號
        elif crawler_name=='gcis_new_company':
            conds = [CompanyData.tax_id!=x for x in tmp_list]
            president_no_list = [x.tax_id for x in CompanyData.query.filter(CompanyData.ho_tax_id==None, CompanyData.create_time>=(datetime.strptime((datetime.now()-timedelta(days=1)).strftime('%Y-%m-%d 00:00:00'), '%Y-%m-%d %H:%M:%S')), CompanyData.status==1, or_(*conds)).order_by(desc(CompanyData.create_time)).all()]
            if not president_no_list:
                print('president_no_list.(2)')
        # 其他公司或商號
        elif crawler_name=='gcis_normal_company':
            conds = [CompanyData.tax_id!=x for x in tmp_list]
            president_no_list = [x.tax_id for x in CompanyData.query.filter(CompanyData.ho_tax_id==None, CompanyData.create_time<=(datetime.strptime((datetime.now()-timedelta(days=1)).strftime('%Y-%m-%d 00:00:00'), '%Y-%m-%d %H:%M:%S')), CompanyData.status==1, or_(*conds)).order_by(func.random()).all()]
            if not president_no_list:
                print('president_no_list.(3)')
        elif crawler_name=='customization':
            president_no_list = list(set([db_result.president_no for db_result in GCIS_Company.query.with_entities(GCIS_Company.president_no).all()])-set([db_result.tax_id for db_result in CompanyData.query.with_entities(CompanyData.tax_id).filter(CompanyData.status==0).all()]))
            shuffle(president_no_list)
            # president_no_list = ['71248003']
            if not president_no_list:
                print('president_no_list.(4)')
        del(tmp_list)

        gcis_headers = deepcopy(app.config['SHARED_HEADERS'])
        gcis_headers['Referer'] = 'https://findbiz.nat.gov.tw/fts/query/QueryList/queryList.do'

        gcc = gcis_crawler_class(os.path.basename(__file__))
        key_list = ['cmpyType'] if crawler_name=='gcis_list_company' else []
        print('開始執行{}程式'.format(main_name))
        # ##############################
        # iiiiindex = president_no_list.index('53003483')
        # president_no_list = deepcopy(president_no_list[iiiiindex:])

        # key_list = []
        # ##############################

        disj_string = get_disj_param()
        disj_gen_time = time.time()
        for president_no_index, president_no in enumerate(president_no_list):
            # ##############################
            # if president_no_index<82:
            #     continue
            # ##############################
            print('{}: 正在處理 {}, 進度 {}/{}({}%)'.format(main_name, president_no, president_no_index, len(president_no_list),round((president_no_index/len(president_no_list))*100, 3)))
            db.session.rollback()
            db.session.close()
            # ##############################
            # GCIS_ObjectID.query.filter(GCIS_ObjectID.president_no==president_no).delete()
            # db.session.commit()
            # ##############################
            gcis_obj_db_result = GCIS_ObjectID.query.filter(GCIS_ObjectID.president_no==president_no).first()
            if not gcis_obj_db_result:
                db.session.add(GCIS_ObjectID(**{'president_no':president_no}))
                db.session.commit()
                gcis_obj_db_result = GCIS_ObjectID.query.filter(GCIS_ObjectID.president_no==president_no).first()
            if gcis_obj_db_result.exist==0:
                print('已檢查過商工登記平台無法查詢到統編 {} ，略過之'.format(president_no))
                continue
            gcis_params = deepcopy(gcis_obj_db_result.params)
            if not gcis_obj_db_result.params:
                query_status, gcis_params = deepcopy(gcc.gcis_search_list_crawler(gcis_obj_db_result, key_list))
                if not query_status:
                    print('無法取得該筆公司於商工登記的參數, 略過之')
                    continue
                db.session.rollback()
                db.session.close()
                gcis_obj_db_result = GCIS_ObjectID.query.filter(GCIS_ObjectID.president_no==president_no).first()
            gcis_params['disj'] = disj_string

            DetailReqCrawler = RequestForMiltipleTimes(app.config['CRAWL_INFO']['GCIS']['QUERY_URL_COMPARSION'][gcis_obj_db_result.type], gcis_headers, gcis_params, request_timeout=120, check_target='GCIS')
            # 代表查詢用的臨時參數要換一個
            if DetailReqCrawler and '系統忙碌中、超出同時連線數，請您稍後再嘗試一次' in DetailReqCrawler.get_source():
                del(disj_string, disj_gen_time)
                disj_string = get_disj_param()
                disj_gen_time = time.time()
                DetailReqCrawler = RequestForMiltipleTimes(app.config['CRAWL_INFO']['GCIS']['QUERY_URL_COMPARSION'][gcis_obj_db_result.type], gcis_headers, gcis_params, request_timeout=120, check_target='GCIS')

            # 商工登記的主機無法連上
            if not DetailReqCrawler:
                continue
            if '很抱歉，您所輸入的需求有誤' in DetailReqCrawler.get_source():
                print('找不到此間公司，統編: {}，原因: {}'.format(president_no, '很抱歉，您所輸入的需求有誤'))
                continue
            elif '很抱歉，您所存取的網頁系統暫時無法回應' in DetailReqCrawler.get_source():
                print('找不到此間公司，統編: {}，原因: {}'.format(president_no, '很抱歉，您所存取的網頁系統暫時無法回應'))
                continue
            try:
                webresult2dict = get_gcis_detail(president_no, DetailReqCrawler, opendataclass=opendataclass)
                if not webresult2dict['gcis_company'].get('company_name'):
                    print('無法取得公司資訊')
                    continue
                gcis_check_add2db(opendataclass, president_no, webresult2dict)
                if gcis_obj_db_result.is_alive==None:
                    business_current_false_list, business_current_true_list
                    if webresult2dict['gcis_company'].get('business_current_status') in business_current_false_list:
                        gcis_obj_db_result.is_alive = 0
                    elif webresult2dict['gcis_company'].get('business_current_status') in business_current_true_list:
                        gcis_obj_db_result.is_alive = 1
                    if type(gcis_obj_db_result.is_alive) is int:
                        db.session.add(gcis_obj_db_result)
                        db.session.commit()
            except:
                err_msg = '\n'.join(
                    [
                        president_no,
                        traceback.format_exc(),
                        DetailReqCrawler.get_source()
                    ]
                )
                raise(Exception(err_msg))
                # err_msg = traceback.format_exc()
                # print(president_no)
                # print(err_msg)
                # ggg = GmailSender('{}出現錯誤'.format(main_name), 'douerchiang@iii.org.tw', '{}\n{}\n{}'.format(president_no, err_msg, DetailReqCrawler.get_source()))
                # ggg.send_email()
                # return
        print('done')
    except Exception as e:
        err_msg = traceback.format_exc()
        print(err_msg)
        ggg = GmailSender('{}出現錯誤'.format(main_name), 'douerchiang@iii.org.tw', err_msg)
        ggg.send_email()

if __name__ == "__main__":
    'gcis_list_company'
    'gcis_normal_company'
    'gcis_new_company'
    crawler_funciont(sys.argv[1] if len(sys.argv)>=2 else 'gcis_list_company')
