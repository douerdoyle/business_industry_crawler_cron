from sqlalchemy                  import Column, String, DateTime, Text, text, TIMESTAMP
from settings.environment        import db
from uuid                        import uuid1

class BIG_SHAREHOLDER(db.Model):
    __tablename__ = 'big_shareholder'
    id            = Column('id',           String(36), primary_key=True)
    president_no  = Column('president_no', String(10))
    stock_symbol  = Column('stock_symbol', String(8))
    sh_name       = Column('shareholder_name', Text)
    sh_type       = Column('sh_type',      String(10))
    start_time    = Column('start_time',   DateTime)
    end_time      = Column('end_time',     DateTime)
    update_time   = Column('update_time',  TIMESTAMP, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'), nullable=False)
    create_time   = Column('create_time',  TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'), nullable=False)

    def __init__(self, president_no, stock_symbol, sh_name, sh_type, start_time, end_time=None):
        self.id           = '{}'.format(uuid1())
        self.president_no = president_no
        self.stock_symbol = stock_symbol
        self.sh_name      = sh_name
        self.sh_type      = sh_type
        self.start_time   = start_time
        self.end_time     = end_time
    
    def json(self):
        return(
            {
                'id':self.id,
                'president_no':self.president_no,
                'stock_symbol':self.stock_symbol,
                'sh_name':self.sh_name,
                'sh_type':self.sh_type,
                'start_time':self.start_time.strftime('%Y-%m-%d %H:%M:%S'),
                'end_time':self.end_time.strftime('%Y-%m-%d %H:%M:%S') if self.end_time else None
            }
        )