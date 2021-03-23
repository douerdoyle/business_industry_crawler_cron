if __name__ == '__main__':
    import sys
    try:
        sys.path.append('/app/')
    except:
        sys.path.append('../../../')
import json, traceback, re
from pprint                 import pprint
from datetime               import datetime, timedelta
from dateutil.relativedelta import relativedelta
from sqlalchemy             import desc, or_
from lib.func_tool          import ternary_regular_expression, cjk_detect, strQ2B, name_or_company
from lib.mops_regexp        import full_name_func
from settings.environment   import db, app
from lib.gmail_sender       import GmailSender
from models.GCIS            import GCIS_BureauOfForeignTrade, GCIS_DPOCompany
from models.SHARE_TABLE     import CrawlerTriggerTime, CompanySymbolStock, update_CrawlerTriggerTime_trigger_time
from models.OPENDATA        import BIG_SHAREHOLDER
from copy                   import deepcopy
from lib.kg_api_tools       import get_kg_id, get_entity_info, add_entity, get_entity_id, get_relation_info, add_kg_relation, update_kg_relation, add_multiple_entity

def gcis_update_from_opendata_func():
    main_name = 'gcis_update_from_opendata'
    try:
        trigger_time = datetime.now()

        # 處理上市上櫃興櫃攻伐公司的統編與公司代號對應
        listed_company_dict = {}
        for key, value in app.config['OPEN_DATA_INFO'].items():
            if 'LISTED_COMPANY' not in key:
                continue
            try:
                f = open(value['FILE_PATH'], 'r')
            except:
                f = open('../../../{}'.format(value['FILE_PATH']), 'r')
            marketing_category = f.name.split('/')[-1][:2]
            listed_company_list = json.loads(f.read())
            f.close()
            for listed_company_index, listed_company in enumerate(listed_company_list):
                if listed_company['營利事業統一編號'] in app.config['ILLEGEL_PRESIDENT_NO_LIST'] and listed_company['營利事業統一編號'] in listed_company_dict:
                    continue
                listed_company_dict[listed_company['營利事業統一編號']] = listed_company
                try:
                    start_time_split_list = listed_company['出表日期'].split('/')
                    start_time_split_list[0] = '{}'.format(int(start_time_split_list[0])+1911)
                    start_time = datetime.strptime('/'.join(start_time_split_list), '%Y/%m/%d').strftime('%Y-%m-%d %H:%M:%S')
                except:
                    continue

                db_result = CompanySymbolStock.query.filter(CompanySymbolStock.stock_symbol==listed_company['公司代號']).first()
                if not db_result:
                    dictionary = {
                        'stock_symbol':listed_company['公司代號'], 
                        'president_no':listed_company['營利事業統一編號'], 
                        'company_name':listed_company['公司名稱'], 
                        'category'    :marketing_category,
                        'status'      :1,
                        'add_by'      :0
                    }
                    db.session.add(CompanySymbolStock(**dictionary))
                else:
                    db_result.status = 1
                    db_result.add_by = 0
                    db_result.update_time = datetime.now()
                    db.session.add(db_result)

                dictionary = {
                    'president_no'      :listed_company['營利事業統一編號'], 
                    'stock_symbol'      :listed_company['公司代號'], 
                    'company_name_short':listed_company['公司簡稱'], 
                    'company_name'      :listed_company['公司名稱'], 
                    'company_industry'  :listed_company['產業別'], 
                    'marketing_category':marketing_category,
                    'start_time'        :start_time
                }
                for key in list(dictionary.keys()):
                    if not dictionary[key]:
                        dictionary.pop(key)
                db_result = GCIS_DPOCompany.query.filter(GCIS_DPOCompany.president_no==listed_company['營利事業統一編號']).order_by(desc(GCIS_DPOCompany.start_time)).first()
                if not db_result:
                    db.session.add(GCIS_DPOCompany(**dictionary))
                elif db_result.start_time.strftime('%Y-%m-%d %H:%M:%S')!=start_time:
                    db_result.end_time = start_time
                    db.session.add(db_result)
                    db.session.add(GCIS_DPOCompany(**dictionary))
            db.session.commit()

        stock_symbol_list = []
        for key, value in app.config['OPEN_DATA_INFO'].items():
            if 'LISTED_COMPANY' not in key:
                continue
            try:
                f = open(value['FILE_PATH'], 'r')
            except:
                f = open('../../../{}'.format(value['FILE_PATH']), 'r')
            listed_company_list = json.loads(f.read())
            f.close()
            for listed_company_index, listed_company in enumerate(listed_company_list):
                if listed_company['營利事業統一編號'] in app.config['ILLEGEL_PRESIDENT_NO_LIST'] and listed_company['營利事業統一編號'] in listed_company_dict:
                    continue
                stock_symbol_list.append(listed_company['公司代號'])
        stock_symbol_list = list(set(stock_symbol_list))
        if stock_symbol_list:
            add_by_0_stock_symbol_list = [x.stock_symbol for x in CompanySymbolStock.query.filter(CompanySymbolStock.add_by==0).all()]
            conds = [CompanySymbolStock.stock_symbol==stock_symbol for stock_symbol in list(set(add_by_0_stock_symbol_list)-set(stock_symbol_list))]
            if conds:
                CompanySymbolStock.query.filter(CompanySymbolStock.add_by==0, or_(*conds)).update({'status':0})
                db.session.commit()

        # # 處理持股 10% 以上的大股東
        stock_symbol_president_no_dict = {}
        president_no_company_name_dict = {}
        for db_result in CompanySymbolStock.query.with_entities(CompanySymbolStock.stock_symbol, CompanySymbolStock.president_no, CompanySymbolStock.company_name).all():
            stock_symbol_president_no_dict[db_result.stock_symbol] = db_result.president_no
            president_no_company_name_dict[db_result.president_no] = db_result.company_name

        data_dict = {}
        for i in range(1, 3):
            f = open(app.config['OPEN_DATA_INFO']['LISTED_BIG_SHAREHOLDER_{}'.format(i)]['FILE_PATH'], 'r')
            sh_info_list = json.loads(f.read())
            f.close()
            for sh_info in sh_info_list:
                if sh_info['公司代號'] not in stock_symbol_president_no_dict:
                    continue
                if stock_symbol_president_no_dict[sh_info['公司代號']] not in data_dict:
                    data_dict[stock_symbol_president_no_dict[sh_info['公司代號']]] = sh_info

        tmp_list = data_dict[list(data_dict.keys())[0]]['出表日期'].split('/')
        tmp_list[0] = '{}'.format(int(tmp_list[0])+1911)
        start_time = datetime.strptime('{} 00:00:00'.format('-'.join(tmp_list)), '%Y-%m-%d %H:%M:%S')
        end_time = start_time-timedelta(seconds=1)

        db_data_dict = {}
        db_result_list = BIG_SHAREHOLDER.query.filter(BIG_SHAREHOLDER.end_time==None).all()
        for db_result in db_result_list:
            if db_result.president_no not in db_data_dict:
                db_data_dict[db_result.president_no] = {}
            if db_result.sh_name not in db_data_dict[db_result.president_no]:
                db_data_dict[db_result.president_no][db_result.sh_name] = {
                    'id':db_result.id,
                    'still':False
                }
        for president_no, sh_info in data_dict.items():
            sh_name = full_name_func(re.sub(u'台灣', '臺灣', strQ2B(sh_info['大股東名稱'])))
            if president_no in db_data_dict and sh_name in db_data_dict[president_no]:
                db_data_dict[president_no][sh_name]['still'] = True
            else:
                dictionary = {
                    'president_no':president_no,
                    'stock_symbol':sh_info['公司代號'],
                    'sh_name'     :sh_name,
                    'start_time'  :start_time,
                    'end_time'    :None
                }
                db_result = BIG_SHAREHOLDER.query.with_entities(BIG_SHAREHOLDER.sh_type).filter(BIG_SHAREHOLDER.sh_name==dictionary['sh_name']).first()
                dictionary['sh_type'] = db_result.sh_type if db_result else name_or_company(dictionary['sh_name'])
                adding = BIG_SHAREHOLDER(**dictionary)
                db.session.add(adding)

        id_list = []
        for president_no in db_data_dict.keys():
            stock_symbol_dict = db_data_dict[president_no]
            for stock_symbol, id_dict in stock_symbol_dict.items():
                if not id_dict['still']:
                    id_list.append(id_dict['id'])
        if id_list:
            for db_result in BIG_SHAREHOLDER.query.filter(or_(*[BIG_SHAREHOLDER.id==id for id in id_list])).all():
                db_result.end_time = end_time
                db.session.add(db_result)
        db.session.commit()

        # 這邊是串接KG
        # kg_id = get_kg_id('上市上櫃公司持股逾10%大股東')
        # relation_text = '大股東'
        # concept_comapany_name = '公司名稱'
        # entity_text_list = []
        # concept_text_list = []
        # entity_dict = {}
        # db_result_list = BIG_SHAREHOLDER.query.filter(BIG_SHAREHOLDER.update_time>=trigger_time).all()
        # # db_result_list = BIG_SHAREHOLDER.query.all()
        # if db_result_list:
        #     for db_result in db_result_list:
        #         if president_no_company_name_dict[db_result.president_no] not in entity_text_list:
        #             entity_text_list.append(president_no_company_name_dict[db_result.president_no])
        #             concept_text_list.append(concept_comapany_name)
        #         if db_result.sh_name not in entity_text_list:
        #             entity_text_list.append(db_result.sh_name)
        #             concept_text_list.append(db_result.sh_type)

        #     offset = 0
        #     limit = 50
        #     while offset<=len(entity_text_list):
        #         result_dict = add_multiple_entity(kg_id, entity_text_list[offset:offset+limit], concept_text_list[offset:offset+limit])
        #         offset+=limit
        #         for concept_text in result_dict.keys():
        #             if concept_text not in entity_dict:
        #                 entity_dict[concept_text] = {}
        #             entity_dict[concept_text].update(result_dict[concept_text])

        #     insert_list = []
        #     update_list = []
        #     for db_result in db_result_list:
        #         entity_from = entity_dict[concept_comapany_name][president_no_company_name_dict[db_result.president_no]]
        #         entity_to = entity_dict[db_result.sh_type][db_result.sh_name]
        #         relation_info = get_relation_info(entity_from, relation_text, entity_to)
        #         insert_status = True
        #         relation_id = None
        #         for relation_dict in relation_info['data']:
        #             if not relation_dict['end_time']:
        #                 insert_status = False
        #                 relation_id = relation_dict['id']
        #                 break
        #         if insert_status:
        #             insert_list.append(
        #                 {
        #                     'entity_from':entity_from,
        #                     'relations':[
        #                         {
        #                             'entity_to':entity_to,
        #                             'relation_text':relation_text,
        #                             'start_time':db_result.start_time.strftime('%Y-%m-%d %H:%M:%S'),
        #                             'end_time':db_result.end_time.strftime('%Y-%m-%d %H:%M:%S') if db_result.end_time else None,
        #                             'weight':1
        #                         }
        #                     ]
        #                 }
        #             )
        #             insert_list.append(
        #                 {
        #                     'entity_from':entity_to,
        #                     'relations':[
        #                         {
        #                             'entity_to':entity_from,
        #                             'relation_text':'{}of'.format(relation_text),
        #                             'start_time':db_result.start_time.strftime('%Y-%m-%d %H:%M:%S'),
        #                             'end_time':db_result.end_time.strftime('%Y-%m-%d %H:%M:%S') if db_result.end_time else None,
        #                             'weight':1
        #                         }
        #                     ]
        #                 }
        #             )    
        #         if relation_id:
        #             update_list.append(
        #                 {
        #                     'kg_id':kg_id,
        #                     'id':relation_id,
        #                     'end_time':end_time.strftime('%Y-%m-%d %H:%M:%S')
        #                 }
        #             )
        #     for input_json in update_list:
        #         update_kg_relation(input_json)

        #     offset = 0
        #     limit = 10
        #     while offset<len(insert_list):
        #         input_json_for_insert = {
        #             'kg_id':kg_id,
        #             'data_list':insert_list[offset:offset+limit],
        #             'insert':1
        #         }
        #         offset+=limit
        #         add_kg_relation(input_json_for_insert)

        # del(db_result_list, data_dict)

        # 國貿局資料
        imports_exports_dict = {}
        try:
            f = open(app.config['OPEN_DATA_INFO']['IMPORTS_EXPORTS']['FILE_PATH'], 'r')
        except:
            f = open('../../../{}'.format(app.config['OPEN_DATA_INFO']['IMPORTS_EXPORTS']['FILE_PATH']), 'r')
        imports_exports_list = json.loads(f.read())
        f.close()
        # print(len(imports_exports_list)) # 314212
        pre_no_key = '\ufeff統一編號' if '\ufeff統一編號' in imports_exports_list[0] else '統一編號'
        for index, imports_exports in enumerate(imports_exports_list):
            if imports_exports[pre_no_key] in app.config['ILLEGEL_PRESIDENT_NO_LIST']:
                continue
            dictionary = {
                'president_no':imports_exports[pre_no_key], 
                'stock_symbol':listed_company_dict[imports_exports[pre_no_key]]['公司代號'] if imports_exports[pre_no_key] in listed_company_dict and '公司代號' in listed_company_dict[imports_exports[pre_no_key]] else None,
                'company_name_short':listed_company_dict[imports_exports[pre_no_key]]['公司簡稱'] if imports_exports[pre_no_key] in listed_company_dict and '公司簡稱' in listed_company_dict[imports_exports[pre_no_key]] else None,
                'company_setup_date':'{}-{}-{} 00:00:00'.format((1911+int(imports_exports['原始登記日期'][0:3])), imports_exports['原始登記日期'][3:5], imports_exports['原始登記日期'][5:7]), 
                'change_of_approval_date':'{}-{}-{} 00:00:00'.format((1911+int(imports_exports['核發日期'][0:3])), imports_exports['核發日期'][3:5], imports_exports['核發日期'][5:7]), 
                'company_chs_name':imports_exports['廠商中文名稱'], 
                'company_eng_name':imports_exports['廠商英文名稱'], 
                'address_chs':imports_exports['中文營業地址'], 
                'address_eng':imports_exports['英文營業地址'], 
                'tel':imports_exports['電話號碼'], 
                'import_status':1 if imports_exports['進口資格']=='有' else 0, 
                'export_status':1 if imports_exports['進口資格']=='有' else 0.,
            }
            dictionary['start_time'] = dictionary['change_of_approval_date'] if dictionary.get('change_of_approval_date') else dictionary.get('company_setup_date')
            for key in list(dictionary.keys()):
                if not dictionary[key]:
                    dictionary.pop(key)
            db_result = GCIS_BureauOfForeignTrade.query.filter(GCIS_BureauOfForeignTrade.president_no==imports_exports[pre_no_key]).order_by(desc(GCIS_BureauOfForeignTrade.start_time)).first()
            if not db_result:
                db.session.add(GCIS_BureauOfForeignTrade(**dictionary))
            elif (not db_result.start_time and dictionary['start_time']) or (db_result.start_time and db_result.start_time.strftime('%Y-%m-%d %H:%M:%S')!=dictionary['start_time']):
                db_result.end_time = dictionary['start_time']
                db.session.add(db_result)
                db.session.add(GCIS_BureauOfForeignTrade(**dictionary))
            if index and index%1000==0:
                db.session.commit()
                print('gcis_bureau_of_foreign_trade index:{}'.format(index))
        db.session.commit()
    except Exception as e:
        print(traceback.format_exc())
        ggg = GmailSender('{}出現錯誤'.format(main_name), 'douerchiang@iii.org.tw', traceback.format_exc())
        ggg.send_email()

if __name__ == '__main__':
    gcis_update_from_opendata_func()