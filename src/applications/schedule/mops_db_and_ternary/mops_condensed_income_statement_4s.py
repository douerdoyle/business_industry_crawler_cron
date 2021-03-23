if __name__ == '__main__':
    import sys
    try:
        sys.path.append('/app/')
    except:
        sys.path.append('../../../')

# 這個程式碼是在櫥裡公開資訊觀測站的「簡明綜合損益表(四季)」
import time, requests, json, traceback
from pprint                    import pprint
from datetime                  import datetime
from copy                      import deepcopy
from dateutil.relativedelta    import relativedelta
from lib.func_tool             import kilo_string_to_int, RequestForMiltipleTimes
from settings.environment      import db, app
from models.MOPS               import MOPS_Web, MOPS_CondensedIncomeStatement4S
from models.SHARE_TABLE        import get_CrawlerTriggerTime_trigger_time, update_CrawlerTriggerTime_trigger_time, CompanyData
from lib.gmail_sender          import GmailSender

sleep_time = 2

start_time_dict = {
    '第一季':'{}-01-01 00:00:00',
    '前二季':'{}-01-01 00:00:00',
    '前三季':'{}-01-01 00:00:00',
    '前四季':'{}-01-01 00:00:00',
}
end_time_dict = {
    '第一季':'{}-03-31 23:59:59',
    '前二季':'{}-06-30 23:59:59',
    '前三季':'{}-09-30 23:59:59',
    '前四季':'{}-12-31 23:59:59',
}

# 爬取的網址為 https://mops.twse.com.tw/mops/web/t163sb17
def mops_condensed_income_statement_4s_func():
    main_name = '簡明綜合損益表(四季)'
    try:
        trigger_time = datetime.now()
        last_trigger_time = get_CrawlerTriggerTime_trigger_time(main_name)
        update_CrawlerTriggerTime_trigger_time(main_name, trigger_time)

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
                stk_symbol_pre_no_dict[dictionary['公司代號']] = dictionary['營利事業統一編號'] if dictionary['營利事業統一編號'] not in app.config['ILLEGEL_PRESIDENT_NO_LIST'] else None
        # 取得已經爬過的舊資料
        # 假設時間為2020年年初，查詢2317（鴻海），公開資訊觀測站尚無鴻海2019年的資料，只會回傳2016~2018三年的資料，故舊資料會向前曲四年
        # 新上市上櫃的公司，即使無前幾年的資料，公開資訊觀測站依然會顯示該年度的欄位
        old_data_dict = {}
        for db_result in MOPS_CondensedIncomeStatement4S.query.filter(MOPS_CondensedIncomeStatement4S.year>=(crawl_time.year-1)).all():
            if db_result.stock_symbol not in old_data_dict:
                old_data_dict[db_result.stock_symbol] = {}
            if db_result.year not in old_data_dict[db_result.stock_symbol]:
                old_data_dict[db_result.stock_symbol][db_result.year] = []
            old_data_dict[db_result.stock_symbol][db_result.year].append(db_result.data_type)
        #########################
        url = '{}/ajax_{}'.format('/'.join(web_url.split('/')[:-1]), web_url.split('/')[-1].split('_')[0])
        ##########正序###############
        for stock_symbol, president_no in stk_symbol_pre_no_dict.items():
            for i in range (0, 2):
                year = (crawl_time.year-i)
                print('「簡明綜合損益表(四季)」執行中，統編：{}、公司代碼：{}、年份：{}'.format(president_no, stock_symbol, year))
                tmp_params = {
                    'encodeURIComponent': '1',
                    'step'     : '1',
                    'firstin'  : '1',
                    'off'      : '1',
                    'queryName': 'co_id',
                    't05st29_c_ifrs': 'N',
                    't05st30_c_ifrs': 'N',
                    'inpuType' : 'co_id',
                    'TYPEK'    : 'all',
                    'isnew'    : 'false',
                    'co_id'    : stock_symbol,
                    'year'     : str(year-1911)
                }
                ReqCrawler = RequestForMiltipleTimes(url, headers, tmp_params, sleep_time=sleep_time)
                if not ReqCrawler:
                    continue
                skip_status = False
                for key_string in ['查無所需資料', '之公司不存在！', '查無最新資訊']:
                    if key_string in ReqCrawler.get_source():
                        skip_status = True
                if skip_status:
                    time.sleep(sleep_time)
                    continue

                web_data_type_list = ReqCrawler.get_text_by_tag(0, 'th', class_='tblHead')

                # 會有需要用另一個方式requests才能取得資料的公司，如星展銀行 5875
                if len(web_data_type_list)==3 and web_data_type_list[0]=='公司代號' and web_data_type_list[1]=='公司名稱' and not web_data_type_list[2]:
                    tmp_params = {
                        'encodeURIComponent': '1',
                        'co_id'    : stock_symbol,
                        'TYPEK'    : 'pub',
                        'step'     : '2',
                        'year'     : '{}'.format(crawl_time.year),
                        'isnew'    : 'true',
                        'firstin'  : '1'                
                    }
                    ReqCrawler = RequestForMiltipleTimes(url, headers, tmp_params)
                    web_data_type_list = ReqCrawler.get_text_by_tag(0, 'th', class_='tblHead')
                data_type_list = []
                for string in web_data_type_list:
                    if not string:
                        continue
                    data_type_list.append(string.strip())
                title_list = []
                title_odd_list = ReqCrawler.get_text_by_tag(0, 'th', class_='odd')
                for index, item in enumerate(ReqCrawler.get_text_by_tag(0, 'th', class_='even')):
                    title_list.append(item)
                    try:
                        title_list.append(title_odd_list[index])
                    except:
                        break
                even_list = ReqCrawler.get_text_by_tag(0, 'td', class_='even')
                odd_list  = ReqCrawler.get_text_by_tag(0, 'td', class_='odd')
                frame_list = []
                try:
                    for i in range(0, len(even_list), len(data_type_list)):
                        tmp_list = []
                        for iii in range(0, len(data_type_list)):
                            tmp_list.append(even_list[i+iii])
                        frame_list.append(tmp_list)
                        try:
                            tmp_list = []
                            for iii in range(0, len(data_type_list)):
                                tmp_list.append(odd_list[i+iii])
                            frame_list.append(tmp_list)
                        except:
                            break
                except Exception as e:
                    continue
                data_type_this_year = [x.data_type for x in MOPS_CondensedIncomeStatement4S.query.filter(MOPS_CondensedIncomeStatement4S.stock_symbol==stock_symbol, MOPS_CondensedIncomeStatement4S.year==year).all()]
                for data_type_index, data_type in enumerate(data_type_list):
                    db_dictionary = {
                        'president_no': president_no,
                        'stock_symbol': stock_symbol,
                        'year'        : year,
                        'data_type'   : data_type,
                        'frame_data'  : {},
                        'start_time'  : start_time_dict[data_type].format(year),
                        'end_time'    : end_time_dict[data_type].format(year)
                    }
                    for index, title in enumerate(title_list):
                        if index>=len(frame_list):
                            break
                        db_dictionary['frame_data'][title] = kilo_string_to_int(frame_list[index][data_type_index]) if frame_list[index][data_type_index]!='-' else None
                    if data_type in data_type_this_year:
                        MOPS_CondensedIncomeStatement4S.query.filter(MOPS_CondensedIncomeStatement4S.stock_symbol==stock_symbol, 
                                                        MOPS_CondensedIncomeStatement4S.year==year,
                                                        MOPS_CondensedIncomeStatement4S.data_type==data_type).update(db_dictionary)
                    else:
                        db.session.add(MOPS_CondensedIncomeStatement4S(**db_dictionary))
                db.session.commit()
    except:
        msg = traceback.format_exc()
        print(msg)
        ggg = GmailSender('{}出現錯誤'.format(main_name), 'douerchiang@iii.org.tw', msg)
        ggg.send_email()

if __name__ == '__main__':
    mops_condensed_income_statement_4s_func()