if __name__ == '__main__':
    import sys
    try:
        sys.path.append('/app/')
    except:
        sys.path.append('../../../')

# 這個程式碼是在櫥裡公開資訊觀測站的「重大訊息主旨全文檢索」
import time, requests, json, traceback, re
from pprint                    import pprint
from datetime                  import datetime
from copy                      import deepcopy
from sqlalchemy                import desc
from dateutil.relativedelta    import relativedelta
from lib.func_tool             import RequestForMiltipleTimes, strQ2B
from lib.kg_api_tools          import get_entity_info, get_entity_id, add_kg_relation, get_kg_id
from lib.gmail_sender          import GmailSender
from settings.environment      import db, app
from models.MOPS               import MOPS_Web, MOPS_ImportantInformation
from models.SHARE_TABLE        import get_CrawlerTriggerTime_trigger_time, update_CrawlerTriggerTime_trigger_time, CompanyData

sleep_time = 1

# 每個月月初（一號），啟動爬蟲，只要抓主旨、日期，近半年的資訊即可
# 爬取的網址為 https://mops.twse.com.tw/mops/web/t51sb10_q1
def mops_important_information_func():
    main_name = '重大訊息主旨全文檢索'
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

        pre_no_stk_symbol_dict = {}
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
                    continue
                pre_no_stk_symbol_dict[dictionary['公司代號']] = dictionary

        KIND_dict = {
            'L':'上市', 
            'O':'上櫃', 
            'R':'興櫃', 
            'C':'公發'
        }

        params_template = {
            'encodeURIComponent': '1',
            'firstin'   : 'true',
            'Stp'       : '4',
            'go'        : 'false',
            'r1'        : '1',
            'Condition2': '1',
            # 'begin_day' : '1',
            # 'end_day'   : '31',
            'Orderby'   : '1' # 從新到舊
        }
        url = '{}/ajax_{}'.format('/'.join(web_url.split('/')[:-1]), web_url.split('/')[-1].split('_')[0])
        db_result = MOPS_ImportantInformation.query.order_by(desc(MOPS_ImportantInformation.start_time)).first()
        if db_result:
            query_time = datetime.strptime(db_result.start_time.strftime('%Y-%m-%d 00:00:00'), '%Y-%m-%d %H:%M:%S') - relativedelta(days=3)
        else:
            query_time = datetime.strptime(datetime.now().strftime('%Y-%m-%d 00:00:00'), '%Y-%m-%d %H:%M:%S') - relativedelta(days=3)

        db_info_dict = {}
        for db_result in MOPS_ImportantInformation.query.filter(MOPS_ImportantInformation.start_time>=query_time).all():
            if db_result.start_time not in db_info_dict:
                db_info_dict[db_result.start_time] = {}
            if db_result.stock_symbol not in db_info_dict[db_result.start_time]:
                db_info_dict[db_result.start_time][db_result.stock_symbol] = {}
            if db_result.serial not in db_info_dict[db_result.start_time][db_result.stock_symbol]:
                db_info_dict[db_result.start_time][db_result.stock_symbol][db_result.serial] = True
        while query_time<=trigger_time:
            for KIND, KIND_TYPE in KIND_dict.items():
                print('「重大訊息主旨全文檢索」執行中，爬取目標: {}，日期: {}'.format(KIND_TYPE, query_time.strftime('%Y-%m-%d %H:%M:%S')))
                tmp_params = deepcopy(params_template)
                # tmp_params['CODE']   = '31' if KIND=='L' else ''
                tmp_params['KIND']   = KIND
                tmp_params['year']   = '{}'.format(query_time.year-1911)
                tmp_params['month1'] = '{}'.format(query_time.month)
                tmp_params['begin_day'] = '{}'.format(query_time.day)
                tmp_params['end_day'] = '{}'.format(query_time.day)

                ReqCrawler = RequestForMiltipleTimes(url, headers, tmp_params, sleep_time=sleep_time, request_timeout=120, n_max=3)
                if not ReqCrawler or '查無所需資料' in ReqCrawler.get_source():
                    continue
                elif 'sql錯誤,原因是:java.sql.SQLException:' in ReqCrawler.get_source():
                    print('-'*20)
                    print('爬蟲帶的參數錯誤，請修正')
                    print(ReqCrawler.get_source())
                    print('-'*20)
                    break
                try:
                    table = ReqCrawler.get_tags(0, 'table', align='center', class_='hasBorder')
                    title_list = []
                    for title in [x.text for x in table[0].find_all('th')]:
                        if title in title_list:
                            break
                        title_list.append(title)
                    td_list = [x.text for x in table[0].find_all('td')]
                except Exception as e:
                    continue
                for index in range(0, len(td_list), len(title_list)):
                    infomation_list = td_list[index+2].strip().split('/')
                    db_dictionary = {
                        'president_no':pre_no_stk_symbol_dict[td_list[index].strip()]['營利事業統一編號'] if td_list[index].strip() in pre_no_stk_symbol_dict else None,
                        'stock_symbol':td_list[index].strip(),
                        'category'    :KIND_TYPE,
                        'short_name'  :td_list[index+1].strip(),
                        'start_time'  :query_time,
                        'end_time'    :query_time + relativedelta(days=1) - relativedelta(seconds=1),
                        'serial'      :int(td_list[index+3].strip()),
                        'title'       :td_list[index+4].strip()
                    }
                    
                    # 如果查詢時間已存在於DB，檢查是否已經有存資料
                    if query_time in db_info_dict and db_dictionary['stock_symbol'] in db_info_dict[query_time] and db_dictionary['serial'] in db_info_dict[query_time][db_dictionary['stock_symbol']]:
                        continue
                    db.session.add(MOPS_ImportantInformation(**db_dictionary))

                    # 這是串接KG的函式
                    if db_dictionary['stock_symbol'] in pre_no_stk_symbol_dict:
                        company_name = re.sub(u'台灣', '臺灣', strQ2B(pre_no_stk_symbol_dict[db_dictionary['stock_symbol']]['公司名稱']))
                    elif db_dictionary['president_no']:
                        db_result = CompanyData.query.filter(CompanyData.tax_id==db_dictionary['president_no']).first()
                        if db_result:
                            company_name = re.sub(u'台灣', '臺灣', strQ2B(db_result.name))
                        else:
                            company_name = None
                    else:
                        company_name = None
                    if '公司重大資訊-{}年'.format(query_time.year) not in app.config['KGNAME2KGID']:
                        app.config['KGNAME2KGID']['公司重大資訊-{}年'.format(query_time.year)] = get_kg_id('公司重大資訊-{}年'.format(query_time.year))
                    if company_name:
                        add_kg_relation_input_json = {
                            'insert':1,
                            'kg_id':app.config['KGNAME2KGID']['公司重大資訊-{}年'.format(query_time.year)],
                            'data_list':[
                                {
                                    'entity_from': get_entity_id(app.config['KGNAME2KGID']['公司重大資訊-{}年'.format(query_time.year)], company_name, '公司名稱', auto_add=True),
                                    'relations'  :[
                                        {
                                            'entity_to'    : get_entity_id(app.config['KGNAME2KGID']['公司重大資訊-{}年'.format(query_time.year)], db_dictionary['title'], '訊息主旨', auto_add=True),
                                            'relation_text': query_time.strftime('%Y-%m-%d'),
                                            'start_time'   : query_time.strftime('%Y-%m-%d %H:%M:%S'),
                                            'end_time'     : (query_time + relativedelta(days=1) - relativedelta(seconds=1)).strftime('%Y-%m-%d %H:%M:%S'),
                                            'weight'       : 1
                                        }
                                    ]
                                }
                            ]
                        }
                        add_kg_relation(add_kg_relation_input_json)
                db.session.commit()
            query_time+=relativedelta(days=1)
    except:
        ggg = GmailSender('{}出現錯誤'.format(main_name), 'douerchiang@iii.org.tw', traceback.format_exc())
        ggg.send_email()
    db.session.rollback()
if __name__ == '__main__':
    mops_important_information_func()