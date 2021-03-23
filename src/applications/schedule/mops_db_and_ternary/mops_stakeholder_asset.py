if __name__ == '__main__':
    import sys
    try:
        sys.path.append('/app/')
    except:
        sys.path.append('../../../')

# 這個程式碼是在櫥裡公開資訊觀測站的「與關係人取得處分資產、進貨銷貨、應收及應付款項相關資訊」
import time, requests, json, traceback, re
from pprint                    import pprint
from datetime                  import datetime
from copy                      import deepcopy
from dateutil.relativedelta    import relativedelta
from lib.func_tool             import kilo_string_to_int, string_to_folat, RequestForMiltipleTimes, strQ2B, check_rename_rule, string2md5
from lib.kg_api_tools          import get_kg_id, get_entity_info, get_entity_id, get_relation_info, add_kg_relation, update_kg_relation, add_entity
from lib.mops_regexp           import re_name_func, full_name_func
from lib.gmail_sender          import GmailSender
from settings.environment      import db, app
from models.MOPS               import MOPS_Web, MOPS_StakeholderAssetPurchaseSales, MOPS_StakeholderAssetPaymentReceipt, MOPS_StakeholderAssetAsset
from models.GCIS               import GCIS_DirectorSupervisor, GCIS_Manager
from models.SHARE_TABLE        import get_CrawlerTriggerTime_trigger_time, update_CrawlerTriggerTime_trigger_time, MOPS_CompanyCompare

def add_update_kg_relation(kg_id_for_func, company_entity_info_for_func, query_time_for_func, relation_text_for_func, entity_b_text_for_func, human_name_dict):
    last_month_end_time = (query_time_for_func - relativedelta(seconds=1)).strftime('%Y-%m-%d %H:%M:%S')
    from_entity_id = company_entity_info_for_func['entity']['entity_id'][kg_id_for_func]

    if entity_b_text_for_func in human_name_dict:
        concept_b = '人名'
    else:
        concept_b = '公司名稱'

    to_entity_id   = get_entity_id(kg_id_for_func, entity_b_text_for_func, concept_b, auto_add=True)
    relation_info  = get_relation_info(from_entity_id, relation_text_for_func, to_entity=to_entity_id, offset=0, limit=100)

    if relation_info['data']:
        relation_dict = relation_info['data'][0]
    else:
        relation_dict = {}
    if relation_dict:
        input_json = {
            'id'         : relation_dict['id'],
            'end_time'   : (query_time_for_func + relativedelta(months=1) - relativedelta(seconds=1)).strftime('%Y-%m-%d %H:%M:%S')
        }
        update_kg_relation(input_json)
    else:
        add_kg_relation_input_json = {
            'kg_id':kg_id_for_func,
            'data_list':[
                {
                    'entity_from': company_entity_info_for_func['entity']['entity_id'][kg_id_for_func],
                    'relations'  :[
                        {
                            'entity_to'    : get_entity_id(kg_id_for_func, entity_b_text_for_func, '檢視結果', auto_add=True),
                            'relation_text': relation_text_for_func,
                            'start_time'   : query_time_for_func.strftime('%Y-%m-%d %H:%M:%S'),
                            'end_time'     : (query_time_for_func + relativedelta(months=1) - relativedelta(seconds=1)).strftime('%Y-%m-%d %H:%M:%S'),
                            'weight'       : 1
                        }
                    ]
                }
            ]
        }
        add_kg_relation(add_kg_relation_input_json)

def format_data_func_1(input_dict):
    dictionary = {}
    dictionary['frame_data_1'] = input_dict['本月進貨金額']
    for key_string in ['占本月合併報表進貨金額百分比', '占本月進貨金額百分比']:
        if key_string in input_dict:
            dictionary['frame_data_2'] = input_dict[key_string]
    dictionary['frame_data_3'] = input_dict['本年累計進貨金額']
    for key_string in ['占本年合併報表累計進貨金額百分比', '占本年累計進貨金額百分比']:
        if key_string in input_dict:
            dictionary['frame_data_4'] = input_dict[key_string]
    return(dictionary)

def format_data_func_2(input_dict):
    dictionary = {}
    dictionary['frame_data_1'] = input_dict['本月銷貨金額']
    for key_string in ['占本月合併報表銷貨金額百分比', '占本月銷貨金額百分比']:
        if key_string in input_dict:
            dictionary['frame_data_2'] = input_dict[key_string]
    dictionary['frame_data_3'] = input_dict['本年累計銷貨金額']
    for key_string in ['占本年合併報表累計銷貨金額百分比', '占本年累計銷貨金額百分比']:
        if key_string in input_dict:
            dictionary['frame_data_4'] = input_dict[key_string]
    return(dictionary)

def format_data_func_3(input_dict):
    dictionary = {}
    for key_string in ['本月應收款增減金額']:
        if key_string in input_dict:
            dictionary['frame_data_1'] = input_dict[key_string]
    for key_string in ['本年累計應收款金額']:
        if key_string in input_dict:
            dictionary['frame_data_2'] = input_dict[key_string]
    for key_string in ['占本年合併報表累計該科目百分比', '占本年累計該科目百分比']:
        if key_string in input_dict:
            dictionary['frame_data_3'] = input_dict[key_string]
    return(dictionary)

def format_data_func_4(input_dict):
    dictionary = {}
    for key_string in ['本月應付款增減金額']:
        if key_string in input_dict:
            dictionary['frame_data_1'] = input_dict[key_string]
    for key_string in ['本年累計應付款金額']:
        if key_string in input_dict:
            dictionary['frame_data_2'] = input_dict[key_string]
    for key_string in ['占本年合併報表累計該科目百分比', '占本年累計該科目百分比']:
        if key_string in input_dict:
            dictionary['frame_data_3'] = input_dict[key_string]
    return(dictionary)

def format_data_func_5(input_dict):
    dictionary = {}
    for key_string in ['取得資產項目']:
        if key_string in input_dict:
            dictionary['frame_data_1'] = input_dict[key_string]
    for key_string in ['本月取得資產金額']:
        if key_string in input_dict:
            dictionary['frame_data_3'] = input_dict[key_string]
    for key_string in ['本年累計取得資產金額']:
        if key_string in input_dict:
            dictionary['frame_data_4'] = input_dict[key_string]
    return(dictionary)

def format_data_func_6(input_dict):
    dictionary = {}
    for key_string in ['處分資產項目']:
        if key_string in input_dict:
            dictionary['frame_data_1'] = input_dict[key_string]
    for key_string in ['本月處分資產帳面金額']:
        if key_string in input_dict:
            dictionary['frame_data_2'] = input_dict[key_string]
    for key_string in ['本月處分資產交易金額']:
        if key_string in input_dict:
            dictionary['frame_data_3'] = input_dict[key_string]
    for key_string in ['本年累計處分資產交易金額']:
        if key_string in input_dict:
            dictionary['frame_data_4'] = input_dict[key_string]
    for key_string in ['本月處分資產損益']:
        if key_string in input_dict:
            dictionary['frame_data_5'] = input_dict[key_string]
    for key_string in ['本年累計處分資產損益']:
        if key_string in input_dict:
            dictionary['frame_data_6'] = input_dict[key_string]
    return(dictionary)

format_data_dict = {
    '進貨':format_data_func_1,
    '銷貨':format_data_func_2,
    '應收款':format_data_func_3,
    '應付款':format_data_func_4,
    '取得資產':format_data_func_5,
    '處分資產':format_data_func_6
}

step_category_dict = {
    '上市':'sii',
    '上櫃':'otc'
}
invalid_string_list = ['單位：新台幣仟元；％', '單位：新台幣仟元']

table_dictionary = {
    '進貨':MOPS_StakeholderAssetPurchaseSales,
    '銷貨':MOPS_StakeholderAssetPurchaseSales,
    '應收款':MOPS_StakeholderAssetPaymentReceipt,
    '應付款':MOPS_StakeholderAssetPaymentReceipt,
    '取得資產':MOPS_StakeholderAssetAsset,
    '處分資產':MOPS_StakeholderAssetAsset
}

illegal_name_list = ['', '0', '-', '無', '合計']

sleep_time = 1
months_ago = 6
check_list = ['之公司不存在', '該公司不需申報', '公開發行公司不繼續公開發行', '第二上市(櫃)公司免申報本項資訊', '資料庫中查無需求資料', '該公司並未申報本項資料']

# 爬取的網址為 https://mops.twse.com.tw/mops/web/t141sb02
def mops_stakeholder_asset_func():
    main_name = '與關係人取得處分資產、進貨銷貨、應收及應付款項相關資訊'
    try:
        trigger_time = datetime.now()
        last_trigger_time = get_CrawlerTriggerTime_trigger_time(main_name)
        update_CrawlerTriggerTime_trigger_time(main_name, trigger_time)

        human_name_dict = {}
        for db_table in GCIS_DirectorSupervisor, GCIS_Manager:
            for db_result in db_table.query.filter(db_table.name!=None, db_table.stock_symbol!=None).all():
                if db_result.name not in human_name_dict:
                    human_name_dict[db_result.name] = True

        data_type_kg_id = {}
        for kg_name_template in ['公司與關係人進貨資訊-{}年', '公司與關係人銷貨資訊-{}年', '公司與關係人應收資訊-{}年', '公司與關係人應付資訊-{}年']:
            kg_name = kg_name_template.format(trigger_time.year)
            if kg_name not in app.config['KGNAME2KGID']:
                app.config['KGNAME2KGID'][kg_name] = get_kg_id(kg_name, kg_domain='商業')
        data_type_kg_id = {
            trigger_time.year:{
                '進貨':app.config['KGNAME2KGID']['公司與關係人進貨資訊-{}年'.format(trigger_time.year)],
                '銷貨':app.config['KGNAME2KGID']['公司與關係人銷貨資訊-{}年'.format(trigger_time.year)],
                '應收款':app.config['KGNAME2KGID']['公司與關係人應收資訊-{}年'.format(trigger_time.year)],
                '應付款':app.config['KGNAME2KGID']['公司與關係人應付資訊-{}年'.format(trigger_time.year)]
            },
            (trigger_time-relativedelta(years=1)).year:{
                '進貨':app.config['KGNAME2KGID']['公司與關係人進貨資訊-{}年'.format((trigger_time-relativedelta(years=1)).year)],
                '銷貨':app.config['KGNAME2KGID']['公司與關係人銷貨資訊-{}年'.format((trigger_time-relativedelta(years=1)).year)],
                '應收款':app.config['KGNAME2KGID']['公司與關係人應收資訊-{}年'.format((trigger_time-relativedelta(years=1)).year)],
                '應付款':app.config['KGNAME2KGID']['公司與關係人應付資訊-{}年'.format((trigger_time-relativedelta(years=1)).year)]
            }
        }

        db_result = MOPS_Web.query.filter(MOPS_Web.name==main_name).first()
        if not db_result:
            print('「{}」找不到資料庫中的網址資料'.format(main_name))
            return
        crawl_time = datetime.now()
        web_url = db_result.web_url
        headers = app.config['SHARED_HEADERS']
        headers.update({
            'Host'   :'mops.twse.com.tw',
            'Origin' :app.config['CRAWL_INFO']['MOPS']['HOST'],
            'Referer':web_url
            })
        stk_symbol_pre_no_dict = {}

        # 先處理上市再處理上櫃
        for index in range(1, 3):
            try:
                f = open(app.config['OPEN_DATA_INFO']['LISTED_COMPANY_{}'.format(index)]['FILE_PATH'], 'r')
            except:
                f = open('../../../{}'.format(app.config['OPEN_DATA_INFO']['LISTED_COMPANY_{}'.format(index)]['FILE_PATH']), 'r')
            dictionary_list = json.loads(f.read())
            f.close()
            for dictionary in dictionary_list:
                if dictionary['營利事業統一編號'] in app.config['ILLEGEL_PRESIDENT_NO_LIST']:
                    continue
                dictionary['category'] = app.config['OPEN_DATA_INFO']['LISTED_COMPANY_{}'.format(index)]['FILE_PATH'].split('/')[-1][:2]
                stk_symbol_pre_no_dict[dictionary['公司代號']] = dictionary
        url = '{}/ajax_{}'.format('/'.join(web_url.split('/')[:-1]), web_url.split('/')[-1])

        if MOPS_StakeholderAssetPurchaseSales.query.first():
            earliest_date = datetime.strptime((trigger_time - relativedelta(months=6)).strftime('%Y-%m-01 00:00:00'), '%Y-%m-%d %H:%M:%S')
        else:
            earliest_date = datetime.strptime('1986-12-01 00:00:00', '%Y-%m-%d %H:%M:%S')

        stock_symbol_list = list(stk_symbol_pre_no_dict.keys())
        stock_symbol_list.sort()

        params_template = {
            'encodeURIComponent': '1',
            'step': '0',
            'firstin': '1',
            'off': '1',
            'queryName': 'co_id',
            'inpuType': 'co_id',
            'isnew': 'false',
        }

        for stock_symbol in stock_symbol_list:
            stock_symbol_info = stk_symbol_pre_no_dict[stock_symbol]
            president_no = stock_symbol_info['營利事業統一編號']
            query_time = deepcopy(earliest_date)

            db_start_time_list = []
            for table_class in [MOPS_StakeholderAssetPurchaseSales, MOPS_StakeholderAssetPaymentReceipt, MOPS_StakeholderAssetAsset]:
                db_start_time_list.extend([x.start_time for x in table_class.query.filter(table_class.stock_symbol==stock_symbol, table_class.start_time>=query_time).all()])
            db_start_time_list = list(set(db_start_time_list))

            company_name = re.sub(u'台灣', '臺灣', stk_symbol_pre_no_dict[stock_symbol]['公司名稱'])
            data_type_company_entity_info = {}
            for year in [trigger_time.year, (trigger_time-relativedelta(years=1)).year]:
                # 這是串接KG的函式
                data_type_company_entity_info[year] = {}
                company_entity_info_1 = get_entity_info(app.config['KGNAME2KGID']['公司與關係人進貨資訊-{}年'.format(year)], company_name)
                # 如果三元沒有該公司資料，建立之
                if app.config['KGNAME2KGID']['公司與關係人進貨資訊-{}年'.format(year)] not in company_entity_info_1['entity']['entity_id']:
                    concept_text = '公司名稱'
                    company_entity_info_1['entity']['entity_id'][app.config['KGNAME2KGID']['公司與關係人進貨資訊-{}年'.format(year)]] = get_entity_id(app.config['KGNAME2KGID']['公司與關係人進貨資訊-{}年'.format(year)], company_name, concept_text, auto_add=True)

                company_entity_info_2 = get_entity_info(app.config['KGNAME2KGID']['公司與關係人銷貨資訊-{}年'.format(year)], company_name)
                # 如果三元沒有該公司資料，建立之
                if app.config['KGNAME2KGID']['公司與關係人銷貨資訊-{}年'.format(year)] not in company_entity_info_2['entity']['entity_id']:
                    concept_text = '公司名稱'
                    company_entity_info_2['entity']['entity_id'][app.config['KGNAME2KGID']['公司與關係人銷貨資訊-{}年'.format(year)]] = get_entity_id(app.config['KGNAME2KGID']['公司與關係人銷貨資訊-{}年'.format(year)], company_name, concept_text, auto_add=True)

                company_entity_info_3 = get_entity_info(app.config['KGNAME2KGID']['公司與關係人應收資訊-{}年'.format(year)], company_name)
                # 如果三元沒有該公司資料，建立之
                if app.config['KGNAME2KGID']['公司與關係人應收資訊-{}年'.format(year)] not in company_entity_info_3['entity']['entity_id']:
                    concept_text = '公司名稱'
                    company_entity_info_3['entity']['entity_id'][app.config['KGNAME2KGID']['公司與關係人應收資訊-{}年'.format(year)]] = get_entity_id(app.config['KGNAME2KGID']['公司與關係人應收資訊-{}年'.format(year)], company_name, concept_text, auto_add=True)

                company_entity_info_4 = get_entity_info(app.config['KGNAME2KGID']['公司與關係人應付資訊-{}年'.format(year)], company_name)
                # 如果三元沒有該公司資料，建立之
                if app.config['KGNAME2KGID']['公司與關係人應付資訊-{}年'.format(year)] not in company_entity_info_4['entity']['entity_id']:
                    concept_text = '公司名稱'
                    company_entity_info_4['entity']['entity_id'][app.config['KGNAME2KGID']['公司與關係人應付資訊-{}年'.format(year)]] = get_entity_id(app.config['KGNAME2KGID']['公司與關係人應付資訊-{}年'.format(year)], company_name, concept_text, auto_add=True)

                data_type_company_entity_info[year]['進貨'] = company_entity_info_1
                data_type_company_entity_info[year]['銷貨'] = company_entity_info_2
                data_type_company_entity_info[year]['應收款'] = company_entity_info_3
                data_type_company_entity_info[year]['應付款'] = company_entity_info_4

            while query_time<(trigger_time-relativedelta(months=1)):
                if query_time in db_start_time_list:
                    query_time+=relativedelta(months=1)
                    continue
                print('「與關係人取得處分資產、進貨銷貨、應收及應付款項相關資訊」執行中，統編：{}、公司代碼：{}、時間: {}'.format(president_no, stock_symbol, query_time))
                tmp_params = deepcopy(params_template)
                tmp_params['TYPEK'] = step_category_dict[stock_symbol_info['category']]
                tmp_params['year']  = '{}'.format((query_time.year-1911))
                tmp_params['month'] = '{}{}'.format('0' if query_time.month<=9 else '', query_time.month)
                tmp_params['co_id'] = stock_symbol
                ReqCrawler = RequestForMiltipleTimes(url, headers, tmp_params, sleep_time=sleep_time, request_timeout=300)
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

                category_list = [x.text.replace('【', '').replace('】', '') for x in ReqCrawler.get_tags(0, 'td', align="left", colspan="3")]
                tables_list = ReqCrawler.get_tags(0, 'table', class_='hasBorder')
                if len(category_list)<len(tables_list):
                    for i in range(0, len(tables_list)-len(category_list)):
                        category_list.append(None)
                add2db_template_1 = {
                    'president_no':president_no,
                    'stock_symbol':stock_symbol,
                    'category'    :stock_symbol_info['category'],
                    'frame_data'  :{},
                    'start_time'  :query_time.strftime('%Y-%m-%d %H:%M:%S'),
                    'end_time'    :(query_time + relativedelta(months=1) - relativedelta(seconds=1)).strftime('%Y-%m-%d %H:%M:%S')
                }
                for tables_list_index, table in enumerate(tables_list):
                    add2db_template_2 = deepcopy(add2db_template_1)
                    add2db_template_2['data_type'] = category_list[tables_list_index]
                    table_title_list = [x.text for x in table.find_all('th')]
                    table_td_list = [x.text for x in table.find_all('td')]
                    for i_1 in range(0, len(table_td_list), len(table_title_list)):
                        add2db_dictionary = deepcopy(add2db_template_2)
                        for table_title_index, table_title in enumerate(table_title_list):
                            try:
                                add2db_dictionary['frame_data'][table_title] = table_td_list[i_1+table_title_index]
                            except Exception as e:
                                continue
                        add2db_dictionary['name'] = strQ2B(add2db_dictionary['frame_data'].pop('關係人名稱', None))
                        if add2db_dictionary['name'] in illegal_name_list or not add2db_dictionary['frame_data']:
                            continue
                        for k in add2db_dictionary['frame_data'].keys():
                            if '.' in add2db_dictionary['frame_data'][k]:
                                try:
                                    add2db_dictionary['frame_data'][k] = string_to_folat(add2db_dictionary['frame_data'][k])
                                except:
                                    pass
                            elif ',' in add2db_dictionary['frame_data'][k]:
                                try:
                                    add2db_dictionary['frame_data'][k] = kilo_string_to_int(add2db_dictionary['frame_data'][k])
                                except:
                                    pass
                            else:
                                try:
                                    add2db_dictionary['frame_data'][k] = kilo_string_to_int(add2db_dictionary['frame_data'][k])
                                except:
                                    pass
                        add2db_dictionary.update(format_data_dict[add2db_dictionary['data_type']](add2db_dictionary.pop('frame_data')))
                        db.session.add(table_dictionary[add2db_dictionary['data_type']](**add2db_dictionary))

                        re_name_tmp = re_name_func(add2db_dictionary['name'])
                        if not add2db_dictionary['frame_data_1'] \
                        or add2db_dictionary['data_type'] not in data_type_kg_id[query_time.year] \
                        or not check_rename_rule(re_name_tmp):
                            continue

                        mcc_db_result = MOPS_CompanyCompare.query.filter(MOPS_CompanyCompare.id==string2md5(re_name_tmp)).first()
                        if not mcc_db_result:
                            mcc_db_result = MOPS_CompanyCompare(
                                    id=string2md5(re_name_tmp),
                                    re_name=re_name_tmp,
                                    example=add2db_dictionary['name'],
                                    full_name=full_name_func(add2db_dictionary['name'])
                                    )
                            db.session.add(mcc_db_result)
                        # 這是串接KG的函式
                        add_update_kg_relation(data_type_kg_id[query_time.year][add2db_dictionary['data_type']], 
                                                data_type_company_entity_info[query_time.year][add2db_dictionary['data_type']], 
                                                query_time, 
                                                add2db_dictionary['data_type'], 
                                                mcc_db_result.full_name,
                                                human_name_dict)
                db.session.commit()
                query_time+=relativedelta(months=1)
    except Exception as e:
        ggg = GmailSender('{}出現錯誤'.format(main_name), 'douerchiang@iii.org.tw', traceback.format_exc())
        ggg.send_email()

if __name__ == '__main__':
    mops_stakeholder_asset_func()