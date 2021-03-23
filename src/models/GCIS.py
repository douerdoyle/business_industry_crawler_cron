from datetime                    import datetime
from sqlalchemy                  import Column, Integer, String, SmallInteger, Date, DateTime, Text, update, text, BigInteger, JSON, TIMESTAMP
from sqlalchemy.dialects.mysql   import TINYINT
from settings.environment        import app, db
from uuid                        import uuid1

class GCIS_Company(db.Model):
    __tablename__            = 'gcis_company'
    id                       = Column('id',                       String(36), primary_key=True)
    president_no             = Column('president_no',             String(10), nullable=False)
    stock_symbol             = Column('stock_symbol',             String(8))
    company_name_short       = Column('company_name_short',       Text)
    business_current_status  = Column('business_current_status',  Text)
    equity_status            = Column('equity_status',            Text)
    company_name             = Column('company_name',             Text)
    company_name_eng         = Column('company_name_eng',         Text)
    capital_stock_amount     = Column('capital_stock_amount',     BigInteger)
    paid_In_capital_amount   = Column('paid_In_capital_amount',   BigInteger)
    responsible_name         = Column('responsible_name',         Text)
    company_location         = Column('company_location',         Text)
    register_organization    = Column('register_organization',    Text)
    company_setup_date       = Column('company_setup_date',       Date)
    change_of_approval_date  = Column('change_of_approval_date',  Date)
    multiple_special_shares1 = Column('multiple_special_shares1', Text)
    multiple_special_shares2 = Column('multiple_special_shares2', Text)
    multiple_special_shares3 = Column('multiple_special_shares3', Text)
    multiple_special_shares4 = Column('multiple_special_shares4', Text)
    cmp_business             = Column('cmp_business',             Text)
    start_time               = Column('start_time',               DateTime)
    end_time                 = Column('end_time',                 DateTime)
    update_time              = Column('update_time',              TIMESTAMP, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'), nullable=False)
    create_time              = Column('create_time',              TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'), nullable=False)
    def __init__(self, president_no,
                    stock_symbol=None,
                    company_name_short=None,
                    business_current_status=None, 
                    equity_status=None, 
                    company_name=None, 
                    company_name_eng=None, 
                    capital_stock_amount=None, 
                    paid_In_capital_amount=None, 
                    responsible_name=None, 
                    company_location=None, 
                    register_organization=None, 
                    company_setup_date=None, 
                    change_of_approval_date=None, 
                    multiple_special_shares1=None, 
                    multiple_special_shares2=None, 
                    multiple_special_shares3=None, 
                    multiple_special_shares4=None,
                    cmp_business=None, 
                    start_time=None,
                    end_time=None
                    ):
        self.id = '{}'.format(uuid1())
        self.president_no             = president_no
        self.stock_symbol             = stock_symbol
        self.company_name_short       = company_name_short
        self.business_current_status  = business_current_status
        self.equity_status            = equity_status
        self.company_name             = company_name
        self.company_name_eng         = company_name_eng
        self.capital_stock_amount     = capital_stock_amount
        self.paid_In_capital_amount   = paid_In_capital_amount
        self.responsible_name         = responsible_name
        self.company_location         = company_location
        self.register_organization    = register_organization
        self.company_setup_date       = company_setup_date
        self.change_of_approval_date  = change_of_approval_date
        self.multiple_special_shares1 = multiple_special_shares1
        self.multiple_special_shares2 = multiple_special_shares2
        self.multiple_special_shares3 = multiple_special_shares3
        self.multiple_special_shares4 = multiple_special_shares4
        self.cmp_business             = cmp_business
        self.start_time               = start_time
        self.end_time                 = end_time

class GCIS_DirectorSupervisor(db.Model):
    __tablename__      = 'gcis_director_and_supervisor'
    id                 = Column('id',                 String(36), primary_key=True)
    president_no       = Column('president_no',       String(10), nullable=False)
    stock_symbol       = Column('stock_symbol',       String(8))
    company_name_short = Column('company_name_short', Text)
    serial             = Column('serial',             SmallInteger)
    job_title          = Column('job_title',          Text)
    name               = Column('name',               Text)
    corporation        = Column('corporation',        Text)
    shares             = Column('shares',             BigInteger)
    start_time         = Column('start_time',         DateTime)
    end_time           = Column('end_time',           DateTime)
    update_time        = Column('update_time',        TIMESTAMP, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'), nullable=False)
    create_time        = Column('create_time',        TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'), nullable=False)
    def __init__(self, president_no,
                        stock_symbol=None,
                        company_name_short=None,
                        serial=None, 
                        job_title=None, 
                        name=None, 
                        corporation=None, 
                        shares=None, 
                        start_time=None,
                        end_time=None
                    ):
        self.id = '{}'.format(uuid1())
        self.president_no       = president_no
        self.stock_symbol       = stock_symbol
        self.company_name_short = company_name_short
        self.serial             = serial
        self.job_title          = job_title
        self.name               = name
        self.corporation        = corporation
        self.shares             = shares
        self.start_time         = start_time
        self.end_time           = end_time

class GCIS_Manager(db.Model):
    __tablename__      = 'gcis_manager'
    id                 = Column('id',                 String(36), primary_key=True)
    president_no       = Column('president_no',       String(10), nullable=False)
    stock_symbol       = Column('stock_symbol',       String(8))
    company_name_short = Column('company_name_short', Text)
    serial             = Column('serial',             SmallInteger)
    job_title          = Column('job_title',          Text)
    name               = Column('name',               Text)
    take_office_date   = Column('take_office_date',   Date)
    start_time         = Column('start_time',         DateTime)
    end_time           = Column('end_time',           DateTime)
    start_time         = Column('start_time',         DateTime)
    end_time           = Column('end_time',           DateTime)
    update_time        = Column('update_time',        TIMESTAMP, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'), nullable=False)
    create_time        = Column('create_time',        TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'), nullable=False)
    def __init__(self, president_no,
                        stock_symbol=None,
                        company_name_short=None,
                        serial=None, 
                        job_title=None,
                        name=None, 
                        take_office_date=None, 
                        start_time=None,
                        end_time=None
                    ):
        self.id = '{}'.format(uuid1())
        self.president_no       = president_no
        self.stock_symbol       = stock_symbol
        self.company_name_short = company_name_short
        self.serial             = serial
        self.job_title          = job_title
        self.name               = name
        self.take_office_date   = take_office_date
        self.start_time         = start_time
        self.end_time           = end_time

class GCIS_BranchOffice(db.Model):
    __tablename__           = 'gcis_branch_office'
    id                      = Column('id',                       String(36), primary_key=True)
    president_no            = Column('president_no',             String(10), nullable=False)
    stock_symbol            = Column('stock_symbol',            String(8))
    company_name_short      = Column('company_name_short',      Text)
    serial                  = Column('serial',                  SmallInteger)
    branch_president_no     = Column('branch_president_no',     String(10))
    company_name            = Column('company_name',            Text)
    equity_status           = Column('equity_status',           Text)
    company_setup_date      = Column('company_setup_date',      Date)
    change_of_approval_date = Column('change_of_approval_date', Date)
    start_time              = Column('start_time',   DateTime)
    end_time                = Column('end_time',     DateTime)
    start_time              = Column('start_time',         DateTime)
    end_time                = Column('end_time',           DateTime)
    update_time             = Column('update_time',        TIMESTAMP, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'), nullable=False)
    create_time             = Column('create_time',        TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'), nullable=False)
    def __init__(self, president_no,
                        stock_symbol=None,
                        company_name_short=None,
                        serial=None, 
                        branch_president_no=None,
                        company_name=None, 
                        equity_status=None, 
                        company_setup_date=None, 
                        change_of_approval_date=None, 
                        start_time=None,
                        end_time=None
                    ):
        self.id = '{}'.format(uuid1())
        self.president_no            = president_no
        self.stock_symbol            = stock_symbol
        self.company_name_short      = company_name_short
        self.serial                  = serial
        self.branch_president_no     = branch_president_no
        self.company_name            = company_name
        self.equity_status           = equity_status
        self.company_setup_date      = company_setup_date
        self.change_of_approval_date = change_of_approval_date
        self.start_time              = start_time
        self.end_time                = end_time

class GCIS_FinanceTaxation(db.Model):
    __tablename__      = 'gcis_finance_and_taxation'
    id                 = Column('id',               String(36), primary_key=True)
    president_no       = Column('president_no',     String(10), nullable=False)
    stock_symbol       = Column('stock_symbol',     String(9))
    company_name_short = Column('company_name_short', Text)
    cmp_business       = Column('cmp_business',     Text)
    receipt            = Column('receipt',          SmallInteger)
    business_address   = Column('business_address', Text)
    start_time         = Column('start_time',       DateTime)
    end_time           = Column('end_time',         DateTime)
    update_time        = Column('update_time',      TIMESTAMP, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'), nullable=False)
    create_time        = Column('create_time',      TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'), nullable=False)
    def __init__(self, president_no,
                        stock_symbol=None,
                        company_name_short=None,
                        cmp_business=None, 
                        receipt=None, 
                        business_address=None, 
                        start_time=None,
                        end_time=None
                    ):
        self.id = '{}'.format(uuid1())
        self.president_no       = president_no
        self.stock_symbol       = stock_symbol
        self.company_name_short = company_name_short
        self.cmp_business       = cmp_business
        self.receipt            = receipt
        self.business_address   = business_address
        self.start_time         = start_time
        self.end_time           = end_time

class GCIS_BureauOfForeignTrade(db.Model):
    __tablename__ = 'gcis_bureau_of_foreign_trade'
    id                      = Column('id',                      String(36), primary_key=True)
    president_no            = Column('president_no',            String(10), nullable=False)
    stock_symbol            = Column('stock_symbol',            String(8))
    company_name_short      = Column('company_name_short',      Text)
    company_setup_date      = Column('company_setup_date',      Date)
    change_of_approval_date = Column('change_of_approval_date', Date)
    company_chs_name        = Column('company_chs_name',        Text)
    company_eng_name        = Column('company_eng_name',        Text)
    address_chs             = Column('address_chs',             Text)
    address_eng             = Column('address_eng',             Text)
    tel                     = Column('tel',                     Text)
    import_status           = Column('import_status',           SmallInteger)
    export_status           = Column('export_status',           SmallInteger)
    start_time              = Column('start_time',              DateTime)
    end_time                = Column('end_time',                DateTime)
    update_time             = Column('update_time',             TIMESTAMP, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'), nullable=False)
    create_time             = Column('create_time',             TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'), nullable=False)
    def __init__(self, president_no,
                        stock_symbol=None,
                        company_name_short=None,
                        company_setup_date=None, 
                        change_of_approval_date=None, 
                        company_chs_name=None, 
                        company_eng_name=None, 
                        address_chs=None, 
                        address_eng=None, 
                        tel=None, 
                        import_status=None, 
                        export_status=None, 
                        start_time=None,
                        end_time=None
                    ):
        self.id = '{}'.format(uuid1())
        self.president_no            = president_no
        self.stock_symbol            = stock_symbol
        self.company_name_short      = company_name_short
        self.company_setup_date      = company_setup_date
        self.change_of_approval_date = change_of_approval_date
        self.company_chs_name        = company_chs_name
        self.company_eng_name        = company_eng_name
        self.address_chs             = address_chs
        self.address_eng             = address_eng
        self.tel                     = tel
        self.import_status           = import_status
        self.export_status           = export_status
        self.start_time              = start_time
        self.end_time                = end_time

class GCIS_DPOCompany(db.Model):
    __tablename__      = 'gcis_dpo_company'
    id                 = Column('id',                 String(36), primary_key=True)
    president_no       = Column('president_no',       String(10), nullable=False)
    stock_symbol       = Column('stock_symbol',       String(8))
    company_name_short = Column('company_name_short', Text)
    company_name       = Column('company_name',       Text)
    company_industry   = Column('company_industry',   Text)
    marketing_category = Column('marketing_category', Text)
    start_time         = Column('start_time',         DateTime)
    end_time           = Column('end_time',           DateTime)
    update_time        = Column('update_time',        TIMESTAMP, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'), nullable=False)
    create_time        = Column('create_time',        TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'), nullable=False)
    def __init__(self, president_no,
                        stock_symbol=None, 
                        company_name_short=None, 
                        company_name=None, 
                        company_industry=None, 
                        marketing_category=None, 
                        start_time=None,
                        end_time=None
                    ):
        self.id = '{}'.format(uuid1())
        self.president_no       = president_no
        self.stock_symbol       = stock_symbol
        self.company_name_short = company_name_short
        self.company_name       = company_name
        self.company_industry   = company_industry
        self.marketing_category = marketing_category
        self.start_time         = start_time
        self.end_time           = end_time

class GCIS_IntellectualPropertyOffice(db.Model):
    __tablename__      = 'gcis_intellectual_property_office'
    id                 = Column('id',                 String(36), primary_key=True)
    president_no       = Column('president_no',       String(10), nullable=False)
    stock_symbol       = Column('stock_symbol',       String(8))
    company_name_short = Column('company_name_short', Text)
    trademark          = Column('trademark',          Text)
    start_time         = Column('start_time',         DateTime)
    end_time           = Column('end_time',           DateTime)
    update_time        = Column('update_time',        TIMESTAMP, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'), nullable=False)
    create_time        = Column('create_time',        TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'), nullable=False)
    def __init__(self, president_no,
                    stock_symbol=None,
                    company_name_short=None,
                    trademark=None, 
                    start_time=None,
                    end_time=None
                    ):
        self.id = '{}'.format(uuid1())
        self.president_no       = president_no
        self.stock_symbol       = stock_symbol
        self.company_name_short = company_name_short
        self.trademark          = trademark
        self.start_time         = start_time
        self.end_time           = end_time

class GCIS_ObjectID(db.Model):
    __tablename__ = 'gcis_detail_params'
    president_no  = Column('president_no', String(10), primary_key=True)
    type          = Column('type',         String(6))
    params        = Column('params',       JSON)
    is_alive      = Column('is_alive',     TINYINT)
    exist         = Column('exist',        TINYINT)
    update_time   = Column('update_time',  TIMESTAMP, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'), nullable=False)
    create_time   = Column('create_time',  TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'), nullable=False)
    def __init__(self, president_no, type=None, is_alive=None, params=None, exist=None):
        self.president_no = president_no
        self.type         = type
        self.params       = params
        self.is_alive     = is_alive
        self.exist        = exist