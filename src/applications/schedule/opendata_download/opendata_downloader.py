if __name__ == '__main__':
    import sys
    try:
        sys.path.append('/app/')
    except:
        sys.path.append('../../../')
import requests, gc, os, json, shutil, traceback
from settings.environment      import app
from lib.csv2json              import csv2json_func

def open_data_download_function():
    import time
    t = time.time()
    # 下載open data，並將檔案存到 [檔案名稱].tmp 這個位置
    for file_label, file_info in app.config['OPEN_DATA_INFO'].items():
        tmp_filepath = '{}.tmp'.format(file_info['FILE_PATH'])
        print('Start download file to {}'.format(tmp_filepath.split('/')[-1]))

        download_status = True
        while download_status:
            try:
                with requests.get(file_info['DOWNLOAD_LINK'], stream=True) as r:
                    r.raise_for_status()
                    with open(tmp_filepath, 'wb') as f:
                        for chunk in r.iter_content(chunk_size=512): 
                            if chunk:
                                f.write(chunk)
                break
            except:
                print(traceback.format_exc())
                download_status = False
        if not download_status:
            print('下載檔案至{}失敗'.format(file_info['FILE_PATH']))
            if os.path.exists(tmp_filepath):
                os.remove(tmp_filepath)
            continue

        if file_label=='IMPORTS_EXPORTS':
            # 進出口廠商登記資料下載後是CSV，故要轉換
            csv2json_func(tmp_filepath, tmp_filepath)
        else:
            f = open(tmp_filepath, 'r')
            file_content = f.read()
            f.close()
            f = open(tmp_filepath, 'w')
            f.write(json.dumps(json.loads(file_content), ensure_ascii=False, indent=4))
            f.close()
            del(file_content)

        # 將檔案從 [檔案名稱].tmp 改為 [檔案名稱]
        if os.path.exists(file_info['FILE_PATH']):
            f = open(file_info['FILE_PATH'], 'rb')
            original_file_size = len(f.read())
            f.close()
            f = open(tmp_filepath, 'rb')
            new_file_size = len(f.read())
            f.close()
            # 如果下載的檔案大小，小於原本檔案大小的一半，就會判定新下載的檔案有問題，寧願用舊的資料也不可覆蓋掉舊的資料
            if new_file_size<(original_file_size/2):
                print('{} 資料有誤，略過覆蓋並刪除tmp檔'.format(tmp_filepath))
                os.remove(tmp_filepath)
                continue
        print('Move file from {} to {}'.format(tmp_filepath, file_info['FILE_PATH']))
        shutil.move(tmp_filepath, file_info['FILE_PATH'])
        gc.collect()
    print('下載檔案共耗費{}秒'.format(round(time.time()-t, 5)))

if __name__ == '__main__':
    open_data_download_function()
