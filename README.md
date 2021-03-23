# business_industry_crawler_cron
使用 docker-compose，建立的 商工登記、公開資訊觀測站以及 Open Data 爬蟲 Container<br>
爬蟲爬取時，會同時進行資料清洗<br>

# 說明
docker-compose 檔案內有設定 Container 可使用的 CPU 與 Memory 上限<br>
本程式會去爬取商工登記上的公司相關資訊，查詢方式會是使用存在 MySQL 中的統編至商工登記頁面查詢該公司是否存在；如果存在，爬取其內容並做資料清洗存入 MySQL 中，不存在則略過之<br>
公開資訊觀測站爬蟲則是會去爬取重大資訊、與關係人進銷貨、背書保證與資金貸放、簡明綜合損益表（三年與四季）以及簡明資產負債表（三年與四季）等資訊，並將做資料清洗後存入 MySQL 中<br>