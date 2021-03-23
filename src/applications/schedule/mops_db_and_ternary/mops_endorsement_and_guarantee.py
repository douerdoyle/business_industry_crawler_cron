if __name__ == '__main__':
    import sys
    try:
        sys.path.append('/app/')
    except:
        sys.path.append('../../../')

# 這個程式碼是在櫥裡公開資訊觀測站的「背書保證與資金貸放餘額明細」
import time, requests, json, traceback, re
from pprint                    import pprint
from datetime                  import datetime
from copy                      import deepcopy
from dateutil.relativedelta    import relativedelta
from lib.func_tool             import kilo_string_to_int, RequestForMiltipleTimes
from lib.kg_api_tools          import get_kg_id, get_entity_info, get_entity_id, get_relation_info, add_kg_relation, update_kg_relation
from lib.gmail_sender          import GmailSender
from settings.environment      import db, app
from models.MOPS               import MOPS_Web, MOPS_EndorsementGuaranteeEndorsement, MOPS_EndorsementGuaranteeGuarantee, MOPS_EndorsementGuaranteeHostBranch
from sqlalchemy                import desc
from models.SHARE_TABLE        import get_CrawlerTriggerTime_trigger_time, update_CrawlerTriggerTime_trigger_time, CompanyData

# sleep_time = 4 # 花費秒數：52.38414168357849
# sleep_time = 3 # 花費秒數：39.26571297645569
# sleep_time = 2 # 花費秒數：26.565808296203613
sleep_time = 1 # 花費秒數：15.121716022491455
# sleep_time = 0 # 花費秒數：6.173640966415405

string_int_dict = {
    '有':1,
    '無':0
}
months_ago = 6
check_list = ['之公司不存在', '該公司不需申報', '公開發行公司不繼續公開發行', '第二上市(櫃)公司免申報本項資訊', '資料庫中查無需求資料', '該公司並未申報本項資料']

def add_update_kg_relation(company_entity_info_for_func, query_time_for_func, relation_text_for_func, entity_b_text_for_func):
    last_month_end_time = (query_time_for_func - relativedelta(seconds=1)).strftime('%Y-%m-%d %H:%M:%S')
    from_entity_id = company_entity_info_for_func['entity']['entity_id'][app.config['KGNAME2KGID']['公司背書保證與資金貸放餘額資訊-{}年'.format(query_time_for_func.year)]]
    relation_info  = get_relation_info(from_entity_id, relation_text_for_func)
    relation_dict = {}
    if relation_info['data']:
        for data in relation_info['data']:
            if not data['end_time'] or (data['end_time'] and datetime.strptime(data['end_time'], '%Y-%m-%d %H:%M:%S')>=query_time_for_func):
                relation_dict = data
                break
    to_entity_id   = get_entity_id(app.config['KGNAME2KGID']['公司背書保證與資金貸放餘額資訊-{}年'.format(query_time_for_func.year)], entity_b_text_for_func, '檢視結果', auto_add=True)
    if relation_dict and relation_dict['to_entity']!=to_entity_id:
        input_json = {
            'id'         : relation_dict['id'],
            'end_time'   : (query_time_for_func - relativedelta(seconds=1)).strftime('%Y-%m-%d %H:%M:%S')
        }
        update_kg_relation(input_json)
        # 設為空字典，這樣才會建立新的
        relation_dict = {}
    elif query_time_for_func.month==12:
        input_json = {
            'id'         : relation_dict['id'],
            'end_time'   : '{}-{}-31 23:59:59'.format(query_time_for_func.year, query_time_for_func.month)
        }
        update_kg_relation(input_json)

    # 如果relation_dict是空的，代表最新（end_time為null）的背書保證不存在，故要建立之
    if not relation_dict:
        add_kg_relation_input_json = {
            'kg_id':app.config['KGNAME2KGID']['公司背書保證與資金貸放餘額資訊-{}年'.format(query_time_for_func.year)],
            'data_list':[
                {
                    'entity_from': company_entity_info_for_func['entity']['entity_id'][app.config['KGNAME2KGID']['公司背書保證與資金貸放餘額資訊-{}年'.format(query_time_for_func.year)]],
                    'relations'  :[
                        {
                            'entity_to'    : to_entity_id,
                            'relation_text': relation_text_for_func,
                            'start_time'   : query_time_for_func.strftime('%Y-%m-%d %H:%M:%S'),
                            'end_time'     : None,
                            'weight'       : 1
                        }
                    ]
                }
            ]
        }
        add_kg_relation(add_kg_relation_input_json)

# 爬取的網址為 https://mops.twse.com.tw/mops/web/t05st11
def mops_endorsement_and_guarantee_func():
    main_name = '背書保證與資金貸放餘額明細'
    trigger_time = datetime.now()
    try:
        last_trigger_time = get_CrawlerTriggerTime_trigger_time(main_name)
        update_CrawlerTriggerTime_trigger_time(main_name, trigger_time)

        db_result = MOPS_Web.query.filter(MOPS_Web.name==main_name).first()
        if not db_result:
            print('「{}」找不到資料庫中的網址資料'.format(main_name))
            return
        web_url = db_result.web_url
        headers = app.config['SHARED_HEADERS']
        headers.update({
            'Host'   :'mops.twse.com.tw',
            'Origin' :app.config['CRAWL_INFO']['MOPS']['HOST'],
            'Referer':web_url
            })
        stk_symbol_pre_no_dict = {}
        for LABEL, INFO in app.config['OPEN_DATA_INFO'].items():
            if 'LISTED_COMPANY' not in LABEL:
                continue
            try:
                f = open(app.config['OPEN_DATA_INFO'][LABEL]['FILE_PATH'], 'r')
            except:
                f = open('../../../{}'.format(app.config['OPEN_DATA_INFO'][LABEL]['FILE_PATH']), 'r')
            dictionary_list = json.loads(f.read())
            f.close()
            for dictionary in dictionary_list:
                if dictionary['營利事業統一編號'] in app.config['ILLEGEL_PRESIDENT_NO_LIST']:
                    stk_symbol_pre_no_dict[dictionary['公司代號']] = None
                stk_symbol_pre_no_dict[dictionary['公司代號']] = dictionary

        url = '{}/ajax_{}'.format('/'.join(web_url.split('/')[:-1]), web_url.split('/')[-1])

        db_result = MOPS_EndorsementGuaranteeEndorsement.query.order_by(desc(MOPS_EndorsementGuaranteeEndorsement.start_time)).first()
        if db_result:
            earliest_date = db_result.start_time - relativedelta(months=6)
        else:
            earliest_date = datetime.strptime('1986-12-01 00:00:00', '%Y-%m-%d %H:%M:%S')

        stock_symbol_list = list(stk_symbol_pre_no_dict.keys())
        stock_symbol_list.sort()

        params_template = {
            'encodeURIComponent': '1',
            'step': '1',
            'firstin': '1',
            'off': '1',
            'queryName': 'co_id',
            'inpuType': 'co_id',
            'TYPEK': 'all',
            'isnew': 'false'
        }
        for stock_symbol in stock_symbol_list:
            president_no = stk_symbol_pre_no_dict[stock_symbol]['營利事業統一編號']
            query_time = deepcopy(earliest_date)
            db_start_time_list = list(set([x.start_time for x in MOPS_EndorsementGuaranteeEndorsement.query.filter(
                                    MOPS_EndorsementGuaranteeEndorsement.stock_symbol==stock_symbol, 
                                    MOPS_EndorsementGuaranteeEndorsement.start_time>=query_time).all()]))
            while query_time<(trigger_time-relativedelta(months=1)):
                print('「背書保證與資金貸放餘額明細」執行中，統編：{}、公司代碼：{}、時間: {}'.format(president_no, stock_symbol, query_time))
                if '公司背書保證與資金貸放餘額資訊-{}年'.format(query_time.year) not in app.config['KGNAME2KGID']:
                    app.config['KGNAME2KGID']['公司背書保證與資金貸放餘額資訊-{}年'.format(query_time.year)] = get_kg_id('公司背書保證與資金貸放餘額資訊-{}年'.format(query_time.year), kg_domain='商業')
                if query_time in db_start_time_list:
                    query_time+=relativedelta(months=1)
                    continue
                tmp_params = deepcopy(params_template)
                tmp_params['co_id'] = stock_symbol
                tmp_params['year']  = '{}'.format(query_time.year-1911)
                tmp_params['month'] = '{}'.format(query_time.month)
                ReqCrawler = RequestForMiltipleTimes(url, headers, tmp_params, sleep_time=sleep_time, n_max=10, check_target='MOPS')
                if not ReqCrawler:
                    break

                skip_status = False
                for key_string in check_list:
                    if key_string in ReqCrawler.get_source():
                        db.session.rollback()
                        skip_status = True
                        break
                if skip_status:
                    break

                add2db_dictionary_template = {
                    'president_no':president_no,
                    'stock_symbol':stock_symbol,
                    'start_time'  :query_time.strftime('%Y-%m-%d %H:%M:%S'),
                    'end_time'    :(query_time + relativedelta(months=1) - relativedelta(seconds=1)).strftime('%Y-%m-%d %H:%M:%S')
                }

                company_name = re.sub(u'台灣', '臺灣', stk_symbol_pre_no_dict[stock_symbol]['公司名稱'])
                # 這是串接KG的函式
                company_entity_info = get_entity_info(app.config['KGNAME2KGID']['公司背書保證與資金貸放餘額資訊-{}年'.format(query_time.year)], company_name)
                # 如果三元沒有該公司資料，建立之
                if app.config['KGNAME2KGID']['公司背書保證與資金貸放餘額資訊-{}年'.format(query_time.year)] not in company_entity_info['entity']['entity_id']:
                    company_entity_info['entity']['entity_id'][app.config['KGNAME2KGID']['公司背書保證與資金貸放餘額資訊-{}年'.format(query_time.year)]] = get_entity_id(app.config['KGNAME2KGID']['公司背書保證與資金貸放餘額資訊-{}年'.format(query_time.year)], company_name, '公司名稱', auto_add=True)

                # 處理表格ㄧ第一行
                add2db_dictionary = deepcopy(add2db_dictionary_template)
                add2db_dictionary['data_type'] = '本公司'
                add2db_dictionary['status'] = string_int_dict[ReqCrawler.get_text_by_tag(0, 'font', color="red")[0].strip()]
                add2db_dictionary['this_month'] = kilo_string_to_int(ReqCrawler.get_text_by_tag(0, 'td', align="right",   class_="odd")[0])
                add2db_dictionary['last_month'] = kilo_string_to_int(ReqCrawler.get_text_by_tag(0, 'td', align="right",   class_="odd")[1])
                add2db_dictionary['limit'] = kilo_string_to_int(ReqCrawler.get_text_by_tag(0, 'td', align="right",   class_="odd")[2])
                db.session.add(MOPS_EndorsementGuaranteeEndorsement(**add2db_dictionary))
                relation_text = '{}資金貸放餘額'.format(add2db_dictionary['data_type'])
                entity_b_text = format(add2db_dictionary['this_month']) if add2db_dictionary['this_month'] else '無'
                # 這是串接KG的函式
                add_update_kg_relation(company_entity_info, query_time, relation_text, entity_b_text)

                # 處理表格ㄧ第二行
                add2db_dictionary = deepcopy(add2db_dictionary_template)
                add2db_dictionary['data_type'] = '各子公司'
                add2db_dictionary['status'] = string_int_dict[ReqCrawler.get_text_by_tag(0, 'font', color="red")[1].strip()]
                add2db_dictionary['this_month'] = kilo_string_to_int(ReqCrawler.get_text_by_tag(0, 'td', align="right",   class_="even")[0])
                add2db_dictionary['last_month'] = kilo_string_to_int(ReqCrawler.get_text_by_tag(0, 'td', align="right",   class_="even")[1])
                add2db_dictionary['limit'] = kilo_string_to_int(ReqCrawler.get_text_by_tag(0, 'td', align="right",   class_="even")[2])
                db.session.add(MOPS_EndorsementGuaranteeEndorsement(**add2db_dictionary))
                relation_text = '{}資金貸放餘額'.format(add2db_dictionary['data_type'])
                entity_b_text = format(add2db_dictionary['this_month']) if add2db_dictionary['this_month'] else '無'
                # 這是串接KG的函式
                add_update_kg_relation(company_entity_info, query_time, relation_text, entity_b_text)

                # 處理表格二第一行
                add2db_dictionary = deepcopy(add2db_dictionary_template)
                add2db_dictionary['data_type'] = '本公司'
                add2db_dictionary['status'] = string_int_dict[ReqCrawler.get_text_by_tag(0, 'font', color="red")[2].strip()]
                add2db_dictionary['this_month'] = kilo_string_to_int(ReqCrawler.get_text_by_tag(0, 'td', align="right", class_="odd")[3])
                add2db_dictionary['accumulation'] = kilo_string_to_int(ReqCrawler.get_text_by_tag(0, 'td', align="right", class_="odd")[4])
                add2db_dictionary['limit'] = kilo_string_to_int(ReqCrawler.get_text_by_tag(0, 'td', align="right", class_="odd")[5])
                db.session.add(MOPS_EndorsementGuaranteeGuarantee(**add2db_dictionary))
                relation_text = '{}背書保證餘額資訊'.format(add2db_dictionary['data_type'])
                entity_b_text = format(add2db_dictionary['this_month']) if add2db_dictionary['this_month'] else '無'
                # 這是串接KG的函式
                add_update_kg_relation(company_entity_info, query_time, relation_text, entity_b_text)

                # 處理表格二第二行
                add2db_dictionary = deepcopy(add2db_dictionary_template)
                add2db_dictionary['data_type'] = '各子公司'
                add2db_dictionary['status'] = string_int_dict[ReqCrawler.get_text_by_tag(0, 'font', color="red")[3].strip()]
                add2db_dictionary['this_month'] = kilo_string_to_int(ReqCrawler.get_text_by_tag(0, 'td', align="right", class_="even")[3])
                add2db_dictionary['accumulation'] = kilo_string_to_int(ReqCrawler.get_text_by_tag(0, 'td', align="right", class_="even")[4])
                add2db_dictionary['limit'] = kilo_string_to_int(ReqCrawler.get_text_by_tag(0, 'td', align="right", class_="even")[5])
                db.session.add(MOPS_EndorsementGuaranteeGuarantee(**add2db_dictionary))
                relation_text = '{}背書保證餘額資訊'.format(add2db_dictionary['data_type'])
                entity_b_text = format(add2db_dictionary['this_month']) if add2db_dictionary['this_month'] else '無'
                # 這是串接KG的函式
                add_update_kg_relation(company_entity_info, query_time, relation_text, entity_b_text)

                # 處理表格四第一行
                add2db_dictionary = deepcopy(add2db_dictionary_template)
                add2db_dictionary['data_type'] = '本公司對大陸地區'
                add2db_dictionary['status'] = string_int_dict[ReqCrawler.get_text_by_tag(0, 'font', color="red")[5].strip()]
                add2db_dictionary['this_month'] = kilo_string_to_int(ReqCrawler.get_text_by_tag(0, 'td', align="right", class_="odd")[6])
                add2db_dictionary['accumulation'] = kilo_string_to_int(ReqCrawler.get_text_by_tag(0, 'td', align="right", class_="odd")[7])
                add2db_dictionary['limit'] = None
                db.session.add(MOPS_EndorsementGuaranteeGuarantee(**add2db_dictionary))
                relation_text = '{}背書保證餘額資訊'.format(add2db_dictionary['data_type'])
                entity_b_text = format(add2db_dictionary['this_month']) if add2db_dictionary['this_month'] else '無'
                # 這是串接KG的函式
                add_update_kg_relation(company_entity_info, query_time, relation_text, entity_b_text)

                # 處理表格四第二行
                add2db_dictionary = deepcopy(add2db_dictionary_template)
                add2db_dictionary['data_type'] = '各子公司對大陸地區'
                add2db_dictionary['status'] = string_int_dict[ReqCrawler.get_text_by_tag(0, 'font', color="red")[6].strip()]
                add2db_dictionary['this_month'] = kilo_string_to_int(ReqCrawler.get_text_by_tag(0, 'td', align="right", class_="even")[6])
                add2db_dictionary['accumulation'] = kilo_string_to_int(ReqCrawler.get_text_by_tag(0, 'td', align="right", class_="even")[7])
                add2db_dictionary['limit'] = None
                db.session.add(MOPS_EndorsementGuaranteeGuarantee(**add2db_dictionary))
                relation_text = '{}背書保證餘額資訊'.format(add2db_dictionary['data_type'])
                entity_b_text = format(add2db_dictionary['this_month']) if add2db_dictionary['this_month'] else '無'
                # 這是串接KG的函式
                add_update_kg_relation(company_entity_info, query_time, relation_text, entity_b_text)

                # 處理表格三，第一行第二行
                add2db_dictionary = deepcopy(add2db_dictionary_template)
                add2db_dictionary['status'] = string_int_dict[ReqCrawler.get_text_by_tag(0, 'font', color="red")[4].strip()]
                add2db_dictionary['host2branch'] = kilo_string_to_int(ReqCrawler.get_text_by_tag(0, 'td', class_="lColor", style="text-align:right !important;")[0])
                add2db_dictionary['branch2host'] = kilo_string_to_int(ReqCrawler.get_text_by_tag(0, 'td', class_="lColor", style="text-align:right !important;")[1])
                db.session.add(MOPS_EndorsementGuaranteeHostBranch(**add2db_dictionary))
                query_time+=relativedelta(months=1)
            db.session.commit()
    except:
        ggg = GmailSender('{}出現錯誤'.format(main_name), 'douerchiang@iii.org.tw', traceback.format_exc())
        ggg.send_email()
if __name__ == '__main__':
    mops_endorsement_and_guarantee_func()