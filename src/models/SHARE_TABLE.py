import hashlib
from datetime                    import datetime
from sqlalchemy                  import Column, String, DateTime, Text, text, TIMESTAMP
from sqlalchemy.dialects.mysql   import TINYINT
from settings.environment        import app, db
from uuid                        import uuid1

class MOPS_CompanyCompare(db.Model):
    __tablename__ = 'mops_company_compare'
    id            = Column('id',        String(32), primary_key=True)
    re_name       = Column('re_name',   Text)
    example       = Column('example',   Text)
    full_name     = Column('full_name', Text)
    def __init__(self, id, re_name=None, example=None, full_name=None):
        self.id        = id
        self.re_name   = re_name
        self.example   = example
        self.full_name = full_name

class CrawlerTriggerTime(db.Model):
    __tablename__ = 'crawler_trigger_time'
    crawler_name  = Column('crawler_name', String(45), primary_key=True)
    trigger_time  = Column('trigger_time', DateTime)
    update_time   = Column('update_time',  TIMESTAMP, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'), nullable=False)
    create_time   = Column('create_time',  TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'), nullable=False)
    def __init__(self, crawler_name, trigger_time):
        self.crawler_name = crawler_name
        self.trigger_time = trigger_time

class CompanySymbolStock(db.Model):
    __tablename__ = 'company_stock_symbol'
    stock_symbol  = Column('stock_symbol',  String(8), primary_key=True)
    president_no  = Column('president_no',  String(10))
    company_name  = Column('company_name',  Text)
    category      = Column('category',      String(2))
    status        = Column('status',        TINYINT) # 1代表該公司依然處於上市、上櫃、興櫃、公發的狀態 0代表該公司已經下市下櫃
    add_by        = Column('add_by',        TINYINT,   default=1) # 0代表由爬蟲爬進DB 1代表由人手動存進DB
    update_time   = Column('update_time',   TIMESTAMP, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'), nullable=False)
    create_time   = Column('create_time',   TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'), nullable=False)
    def __init__(self, stock_symbol, president_no, company_name, category, status, add_by):
        self.stock_symbol = stock_symbol
        self.president_no = president_no
        self.company_name = company_name
        self.category     = category
        self.status       = status
        self.add_by       = add_by

class CompanyData(db.Model):
    __tablename__ = 'company_data'
    tax_id      = Column('tax_id',      String(10), primary_key=True)
    ho_tax_id   = Column('ho_tax_id',   String(10))
    name        = Column('name',        String(100))
    create_time = Column('create_time', TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'), nullable=False)
    status      = Column('status',      TINYINT)

def get_CrawlerTriggerTime_trigger_time(crawler_name):
    db_result = CrawlerTriggerTime.query.filter(CrawlerTriggerTime.crawler_name==crawler_name).first()
    if db_result:
        return(db_result.trigger_time)
    else:
        return(None)

def update_CrawlerTriggerTime_trigger_time(crawler_name, trigger_time):
    db_result = CrawlerTriggerTime.query.filter(CrawlerTriggerTime.crawler_name==crawler_name).first()
    if not db_result:
        dictionary = {
            'crawler_name':crawler_name,
            'trigger_time':trigger_time
        }
        db.session.add(CrawlerTriggerTime(**dictionary))
    else:
        db_result.trigger_time = trigger_time
        db.session.add(db_result)
    db.session.commit()
