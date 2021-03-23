if __name__ == '__main__':
    import sys
    try:
        sys.path.append('/app/')
    except:
        sys.path.append('../../../')

# 這個程式碼是在櫥裡公開資訊觀測站的「簡明資產負債表(三年)」
import time, requests, json, traceback
from pprint                    import pprint
from datetime                  import datetime
from copy                      import deepcopy
from dateutil.relativedelta    import relativedelta
from sqlalchemy                import desc
from lib.func_tool             import kilo_string_to_int, RequestForMiltipleTimes
from settings.environment      import db, app
from models.MOPS               import MOPS_Web, MOPS_BalanceSheet3Y
from models.SHARE_TABLE        import get_CrawlerTriggerTime_trigger_time, update_CrawlerTriggerTime_trigger_time
from lib.gmail_sender          import GmailSender

sleep_time = 2

# 每年啟動爬蟲一次
# 爬取的網址為 https://mops.twse.com.tw/mops/web/t163sb17
def mops_balance_sheet_3y_func():
    main_name = '簡明資產負債表(三年)'
    try:
        trigger_time = datetime.now()
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
                stk_symbol_pre_no_dict[dictionary['公司代號']] = dictionary['營利事業統一編號'] if dictionary['營利事業統一編號'] not in app.config['ILLEGEL_PRESIDENT_NO_LIST'] else None

        # 取得已經爬過的舊資料
        # 假設時間為2020年年初，查詢2317（鴻海），公開資訊觀測站尚無鴻海2019年的資料，只會回傳2016~2018三年的資料，故舊資料會向前取三年
        # 新上市上櫃的公司，即使無前幾年的資料，公開資訊觀測站依然會顯示該年度的欄位
        url = '{}/ajax_{}'.format('/'.join(web_url.split('/')[:-1]), web_url.split('/')[-1].split('_')[0])
        for stock_symbol, president_no in stk_symbol_pre_no_dict.items():
            print('「簡明資產負債表(三年)」執行中，統編：{}、公司代碼：{}'.format(president_no, stock_symbol))
            db_year_list = [x.year for x in MOPS_BalanceSheet3Y.query.filter(MOPS_BalanceSheet3Y.president_no==president_no, MOPS_BalanceSheet3Y.stock_symbol==stock_symbol).order_by(desc(MOPS_BalanceSheet3Y.year)).all()]
            if db_year_list and ((db_year_list[0]+1)==trigger_time.year):
                continue
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
                'isnew'    : 'true',
                'co_id'    : stock_symbol
            }
            ReqCrawler = RequestForMiltipleTimes(url, headers, tmp_params, sleep_time=1)
            if not ReqCrawler or '查無所需資料' in ReqCrawler.get_source():
                continue
            web_year_list = ReqCrawler.get_text_by_tag(0, 'th', class_='tblHead')

            # 會有需要用另一個方式requests才能取得資料的公司，如星展銀行 5875
            if len(web_year_list)==3 and web_year_list[0]=='公司代號' and web_year_list[1]=='公司名稱' and not web_year_list[2]:
                tmp_params = {
                    'encodeURIComponent': '1',
                    'co_id'    : stock_symbol,
                    'TYPEK'    : 'pub',
                    'step'     : '2',
                    'year'     : '{}'.format(trigger_time.year),
                    'isnew'    : 'true',
                    'firstin'  : '1'                
                }
                ReqCrawler = RequestForMiltipleTimes(url, headers, tmp_params)
                if not ReqCrawler or '查無所需資料' in ReqCrawler.get_source():
                    time.sleep(sleep_time)
                    continue
                web_year_list = ReqCrawler.get_text_by_tag(0, 'th', class_='tblHead')

            year_list = []
            for string in web_year_list:
                if not string:
                    continue
                year_list.append(int(string.replace('年', ''))+1911)
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
                for i in range(0, len(even_list), len(year_list)):
                    tmp_list = []
                    for iii in range(0, len(year_list)):
                        tmp_list.append(even_list[i+iii])
                    frame_list.append(tmp_list)
                    try:
                        tmp_list = []
                        for iii in range(0, len(year_list)):
                            tmp_list.append(odd_list[i+iii])
                        frame_list.append(tmp_list)
                    except:
                        break
            except:
                continue
            for year_index, year in enumerate(year_list):
                if year in db_year_list:
                    continue
                db_year_list.append(year)
                db_dictionary = {
                    'president_no': president_no,
                    'stock_symbol': stock_symbol,
                    'year'        : year,
                    'frame_data'  : {},
                    'start_time'  : '{}-01-01 00:00:00'.format(year),
                    'end_time'    : '{}-12-31 23:59:59'.format(year)
                }
                for index, title in enumerate(title_list):
                    if index>=len(frame_list):
                        break
                    db_dictionary['frame_data'][title] = kilo_string_to_int(frame_list[index][year_index]) if frame_list[index][year_index]!='-' else None
                db.session.add(MOPS_BalanceSheet3Y(**db_dictionary))
            db.session.commit()
    except Exception as e:
        f = open('/app/applications/schedule/error_log-{}.log'.format(main_name), 'w')
        f.write(traceback.format_exc())
        f.close()
if __name__ == '__main__':
    mops_balance_sheet_3y_func()