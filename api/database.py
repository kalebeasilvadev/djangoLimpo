import psycopg2
import psycopg2.extras 
from api.models import Config

class conexao():

    def __init__(self,db=None,user=None,host=None,port=None,password=None):
        if host:
            self.dbname = db
            self.user = user
            self.host = host
            self.port = port
            self.password = password
        else:
            config = Config.objects.all().first() 
            if config:
                self.dbname='ialIntegra'
                self.user ='postgres'
                self.host = config.host_app 
                self.port = config.porta_app
                self.password= 'cabulano@@'
            else:
                self.dbname='ialIntegra'
                self.user ='postgres'
                self.host = 'serversincronia.ddns.net' 
                self.port = '42124'
                self.password= 'cabulano@@'

    def get_connection(self):
        try:     
            db_connect = psycopg2.connect("dbname="+self.dbname+" user="+self.user+" host="+self.host+" port="+self.port+" password="+self.password)
            db_connect.set_client_encoding('latin1') 
            return db_connect
        except:
            return False
        
    def get_connectionJson(self):
        try:
            db_connect = psycopg2.connect("dbname="+self.dbname+" user="+self.user+" host="+self.host+" port="+self.port+" password="+self.password)
            db_connect.set_client_encoding('latin1') 
            conn = db_connect.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            return conn
        except:
            return False