import json
from datetime                    import datetime
from uuid                        import uuid1
from sqlalchemy                  import Column, Integer, String, SmallInteger, Date, DateTime, Text, BigInteger, JSON, Float, TIMESTAMP, text
from sqlalchemy.dialects.mysql   import TINYINT
from settings.environment        import app, db

class MOPS_Web(db.Model):
    __tablename__ = 'mops_web'
    id            = Column('id',       String(36), primary_key=True)
    name          = Column('name',     String(45))
    web_url       = Column('web_url',  Text)
    def __init__(self, name=None, web_url=None):
        self.id       = str(uuid1())
        self.name     = name
        self.web_url  = web_url

# 「背書保證與資金貸放餘額明細」的是否有資金貸放餘額、本公司與子公司間有無背書保證資訊
class MOPS_EndorsementGuaranteeEndorsement(db.Model):
    __tablename__ = 'mops_endorsement_guarantee_endorsement'
    id            = Column('id'          ,  String(36), primary_key=True, nullable=False)
    president_no  = Column('president_no',  String(10))
    stock_symbol  = Column('stock_symbol',  String(8))
    data_type     = Column('data_type',     Text)
    status        = Column('status',        TINYINT)
    this_month    = Column('this_month',    BigInteger)
    last_month    = Column('last_month',    BigInteger)
    limit         = Column('limit',         BigInteger)
    start_time    = Column('start_time',    DateTime)
    end_time      = Column('end_time',      DateTime)
    update_time   = Column('update_time',   TIMESTAMP, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'), nullable=False)
    create_time   = Column('create_time',   TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'), nullable=False)

    def __init__(self, president_no, stock_symbol, data_type, status, this_month, last_month, limit, 
                start_time=None, end_time=None
                ):
        self.id            = '{}'.format(uuid1())
        self.president_no  = president_no
        self.stock_symbol  = stock_symbol
        self.data_type     = data_type
        self.status        = status
        self.this_month    = this_month
        self.last_month    = last_month
        self.limit         = limit
        self.start_time    = start_time
        self.end_time      = end_time

# 「背書保證與資金貸放餘額明細」的是否有背書保證資訊
class MOPS_EndorsementGuaranteeGuarantee(db.Model):
    __tablename__ = 'mops_endorsement_guarantee_guarantee'
    id            = Column('id'          ,  String(36), primary_key=True, nullable=False)
    president_no  = Column('president_no',  String(10))
    stock_symbol  = Column('stock_symbol',  String(8))
    data_type     = Column('data_type',     Text)
    status        = Column('status',        TINYINT)
    this_month    = Column('this_month',    BigInteger)
    accumulation  = Column('accumulation',  BigInteger)
    limit         = Column('limit',         BigInteger)
    start_time    = Column('start_time',    DateTime)
    end_time      = Column('end_time',      DateTime)
    update_time   = Column('update_time',   TIMESTAMP, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'), nullable=False)
    create_time   = Column('create_time',   TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'), nullable=False)
    def __init__(self, president_no, stock_symbol, data_type, status, this_month, accumulation, limit, 
                start_time=None, end_time=None
                ):
        self.id            = '{}'.format(uuid1())
        self.president_no  = president_no
        self.stock_symbol  = stock_symbol
        self.data_type     = data_type
        self.status        = status
        self.this_month    = this_month
        self.accumulation  = accumulation
        self.limit         = limit
        self.start_time    = start_time
        self.end_time      = end_time

# 「背書保證與資金貸放餘額明細」的本公司與子公司間有無背書保證資訊
class MOPS_EndorsementGuaranteeHostBranch(db.Model):
    __tablename__ = 'mops_endorsement_guarantee_host_branch'
    id            = Column('id'          , String(36), primary_key=True, nullable=False)
    president_no  = Column('president_no', String(10))
    stock_symbol  = Column('stock_symbol', String(8))
    status        = Column('status',       TINYINT)
    host2branch   = Column('host2branch',  BigInteger)
    branch2host   = Column('branch2host',  BigInteger)
    start_time    = Column('start_time',    DateTime)
    end_time      = Column('end_time',      DateTime)
    update_time   = Column('update_time',   TIMESTAMP, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'), nullable=False)
    create_time   = Column('create_time',   TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'), nullable=False)
    def __init__(self, president_no, stock_symbol, status, host2branch, branch2host, 
                start_time=None, end_time=None
                ):
        self.id            = '{}'.format(uuid1())
        self.president_no  = president_no
        self.stock_symbol  = stock_symbol
        self.status        = status
        self.host2branch   = host2branch
        self.branch2host   = branch2host
        self.start_time    = start_time
        self.end_time      = end_time

# 「與關係人取得處分資產、進貨銷貨、應收及應付款項相關資訊」的進銷貨
class MOPS_StakeholderAssetPurchaseSales(db.Model):
    __tablename__  = 'mops_stakeholder_asset_purchase_sales'
    id             = Column('id',           String(36), primary_key=True)
    president_no   = Column('president_no', String(10))
    stock_symbol   = Column('stock_symbol', String(8))
    category       = Column('category',     String(2))
    data_type      = Column('data_type',    String(2))
    name           = Column('name',         Text)
    frame_data_1   = Column('frame_data_1', BigInteger)
    frame_data_2   = Column('frame_data_2', Float)
    frame_data_3   = Column('frame_data_3', BigInteger)
    frame_data_4   = Column('frame_data_4', Float)
    start_time     = Column('start_time',    DateTime)
    end_time       = Column('end_time',      DateTime)
    update_time    = Column('update_time',   TIMESTAMP, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'), nullable=False)
    create_time    = Column('create_time',   TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'), nullable=False)
    def __init__(self, president_no, 
                        stock_symbol, 
                        category, 
                        data_type, 
                        name, 
                        frame_data_1, 
                        frame_data_2, 
                        frame_data_3, 
                        frame_data_4, 
                        start_time=None, end_time=None
                ):
        self.id           = '{}'.format(uuid1())
        self.president_no = president_no
        self.stock_symbol = stock_symbol
        self.category     = category
        self.data_type    = data_type
        self.name         = name
        self.frame_data_1 = frame_data_1
        self.frame_data_2 = frame_data_2
        self.frame_data_3 = frame_data_3
        self.frame_data_4 = frame_data_4
        self.start_time    = start_time
        self.end_time      = end_time

# 「與關係人取得處分資產、進貨銷貨、應收及應付款項相關資訊」的應收應付款
class MOPS_StakeholderAssetPaymentReceipt(db.Model):
    __tablename__  = 'mops_stakeholder_asset_payment_receipt'
    id             = Column('id',           String(36), primary_key=True)
    president_no   = Column('president_no', String(10))
    stock_symbol   = Column('stock_symbol', String(8))
    category       = Column('category',     String(2))
    data_type      = Column('data_type',    String(3))
    name           = Column('name',         Text)
    frame_data_1   = Column('frame_data_1', BigInteger)
    frame_data_2   = Column('frame_data_2', BigInteger)
    frame_data_3   = Column('frame_data_3', Float)
    start_time    = Column('start_time',    DateTime)
    end_time      = Column('end_time',      DateTime)
    update_time   = Column('update_time',   TIMESTAMP, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'), nullable=False)
    create_time   = Column('create_time',   TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'), nullable=False)
    def __init__(self, president_no, 
                        stock_symbol, 
                        category, 
                        data_type, 
                        name, 
                        frame_data_1, 
                        frame_data_2, 
                        frame_data_3, 
                        start_time=None, end_time=None
                ):
        self.id           = '{}'.format(uuid1())
        self.president_no = president_no
        self.stock_symbol = stock_symbol
        self.category     = category
        self.data_type    = data_type
        self.name         = name
        self.frame_data_1 = frame_data_1
        self.frame_data_2 = frame_data_2
        self.frame_data_3 = frame_data_3
        self.start_time    = start_time
        self.end_time      = end_time

# 「與關係人取得處分資產、進貨銷貨、應收及應付款項相關資訊」的取得處分資產
class MOPS_StakeholderAssetAsset(db.Model):
    __tablename__  = 'mops_stakeholder_asset_asset'
    id             = Column('id',           String(36), primary_key=True)
    president_no   = Column('president_no', String(10))
    stock_symbol   = Column('stock_symbol', String(8))
    category       = Column('category',     String(2))
    data_type      = Column('data_type',    String(4))
    name           = Column('name',         Text)
    frame_data_1   = Column('frame_data_1', Text)
    frame_data_2   = Column('frame_data_2', BigInteger)
    frame_data_3   = Column('frame_data_3', BigInteger)
    frame_data_4   = Column('frame_data_4', BigInteger)
    frame_data_5   = Column('frame_data_5', BigInteger)
    frame_data_6   = Column('frame_data_6', BigInteger)
    start_time    = Column('start_time',    DateTime)
    end_time      = Column('end_time',      DateTime)
    update_time   = Column('update_time',   TIMESTAMP, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'), nullable=False)
    create_time   = Column('create_time',   TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'), nullable=False)
    def __init__(self, president_no, 
                        stock_symbol, 
                        category, 
                        data_type, 
                        name, 
                        frame_data_1, 
                        frame_data_2=None, 
                        frame_data_3=None, 
                        frame_data_4=None, 
                        frame_data_5=None,
                        frame_data_6=None,  
                        start_time=None, end_time=None
                ):
        self.id           = '{}'.format(uuid1())
        self.president_no = president_no
        self.stock_symbol = stock_symbol
        self.category     = category
        self.data_type    = data_type
        self.name         = name
        self.frame_data_1 = frame_data_1
        self.frame_data_2 = frame_data_2
        self.frame_data_3 = frame_data_3
        self.frame_data_4 = frame_data_4
        self.frame_data_5 = frame_data_5
        self.frame_data_6 = frame_data_6
        self.start_time    = start_time
        self.end_time      = end_time

# 重大資訊
class MOPS_ImportantInformation(db.Model):
    __tablename__ = 'mops_important_information'
    id            = Column('id',           String(36), primary_key=True, nullable=False)
    president_no  = Column('president_no', String(10))
    stock_symbol  = Column('stock_symbol', String(8))
    category      = Column('category',     String(4))
    short_name    = Column('short_name',   Text)
    serial        = Column('serial',       SmallInteger)
    title         = Column('title',        Text)
    start_time    = Column('start_time',    DateTime)
    end_time      = Column('end_time',      DateTime)
    update_time   = Column('update_time',   TIMESTAMP, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'), nullable=False)
    create_time   = Column('create_time',   TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'), nullable=False)
    def __init__(self, president_no, stock_symbol, category, short_name, serial, title, 
                start_time=None, end_time=None
                ):
        self.id           = str(uuid1())
        self.president_no = president_no
        self.stock_symbol = stock_symbol
        self.category     = category
        self.short_name   = short_name
        self.serial       = serial
        self.title        = title
        self.start_time   = start_time
        self.end_time     = end_time

# 簡明綜合損益表(三年)
class MOPS_CondensedIncomeStatement3Y(db.Model):
    __tablename__ = 'mops_condensed_income_statement_3y'
    id            = Column('id'          , String(36), primary_key=True, nullable=False)
    president_no  = Column('president_no', String(10))
    stock_symbol  = Column('stock_symbol', String(8))
    year          = Column('year',         SmallInteger)
    frame_data    = Column('frame_data',   JSON)
    start_time    = Column('start_time',   DateTime)
    end_time      = Column('end_time',     DateTime)
    update_time   = Column('update_time',  TIMESTAMP, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'), nullable=False)
    create_time   = Column('create_time',  TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'), nullable=False)
    def __init__(self, president_no, stock_symbol, year, frame_data, 
                start_time=None, end_time=None
                ):
        self.id           = '{}'.format(uuid1())
        self.president_no = president_no
        self.stock_symbol = stock_symbol
        self.year         = year
        self.frame_data   = frame_data
        self.start_time   = start_time
        self.end_time     = end_time

# 簡明綜合損益表(四季)
class MOPS_CondensedIncomeStatement4S(db.Model):
    __tablename__ = 'mops_condensed_income_statement_4s'
    id            = Column('id'          , String(36), primary_key=True, nullable=False)
    president_no  = Column('president_no', String(10))
    stock_symbol  = Column('stock_symbol', String(8))
    year          = Column('year',         SmallInteger)
    data_type     = Column('data_type',    String(3))
    frame_data    = Column('frame_data',   JSON)
    start_time    = Column('start_time',    DateTime)
    end_time      = Column('end_time',      DateTime)
    update_time   = Column('update_time',   TIMESTAMP, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'), nullable=False)
    create_time   = Column('create_time',   TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'), nullable=False)
    def __init__(self, president_no, stock_symbol, year, data_type, frame_data, 
                start_time=None, end_time=None
                ):
        self.id           = '{}'.format(uuid1())
        self.president_no = president_no
        self.stock_symbol = stock_symbol
        self.year         = year
        self.data_type    = data_type
        self.frame_data   = frame_data
        self.start_time    = start_time
        self.end_time      = end_time

# 簡明資產負債表(三年)
class MOPS_BalanceSheet3Y(db.Model):
    __tablename__ = 'mops_balance_sheet_3y'
    id            = Column('id'          , String(36), primary_key=True, nullable=False)
    president_no  = Column('president_no', String(10))
    stock_symbol  = Column('stock_symbol', String(8))
    year          = Column('year',         SmallInteger)
    frame_data    = Column('frame_data',   JSON)
    start_time    = Column('start_time',    DateTime)
    end_time      = Column('end_time',      DateTime)
    update_time   = Column('update_time',   TIMESTAMP, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'), nullable=False)
    create_time   = Column('create_time',   TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'), nullable=False)
    def __init__(self, president_no, stock_symbol, year, frame_data, 
                start_time=None, end_time=None
                ):
        self.id           = '{}'.format(uuid1())
        self.president_no = president_no
        self.stock_symbol = stock_symbol
        self.year         = year
        self.frame_data   = frame_data
        self.start_time    = start_time
        self.end_time      = end_time

# 簡明資產負債表(四季)
class MOPS_BalanceSheet4S(db.Model):
    __tablename__ = 'mops_balance_sheet_4s'
    id            = Column('id'          , String(36), primary_key=True, nullable=False)
    president_no  = Column('president_no', String(10))
    stock_symbol  = Column('stock_symbol', String(8))
    year          = Column('year',         SmallInteger)
    data_type     = Column('data_type',    String(3))
    frame_data    = Column('frame_data',   JSON)
    start_time    = Column('start_time',    DateTime)
    end_time      = Column('end_time',      DateTime)
    update_time   = Column('update_time',   TIMESTAMP, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'), nullable=False)
    create_time   = Column('create_time',   TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'), nullable=False)
    def __init__(self, president_no, stock_symbol, year, data_type, frame_data, 
                start_time=None, end_time=None, 
                ):
        self.id           = '{}'.format(uuid1())
        self.president_no = president_no
        self.stock_symbol = stock_symbol
        self.year         = year
        self.data_type    = data_type
        self.frame_data   = frame_data
        self.start_time    = start_time
        self.end_time      = end_time