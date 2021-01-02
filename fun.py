from datetime import datetime
import pytz

record_ex = {'recordId':'123', 'title':'上課','start_date':'2021-01-30', 'start_section':1, 'end_date':'2021-01-30', 'end_section':10,
'roomName':'TR313', 'building':'研揚大樓(TR)', 'participant':['茶是一種蔬菜湯','茶葉蛋',
'神棍局局長']}

record_ex2 = {'recordId':'456', 'title':'創業', 'start_date':'2021-02-01', 'start_section':1, 'end_date':'2021-02-03', 'end_section':10,
'roomName':'TR411', 'building':'研揚大樓(TR)', 'participant':['勞工',
'CEO','CTO','PM']}

records = [record_ex, record_ex2]

def get_current_time():
    taipei = pytz.timezone('Asia/Taipei')
    return datetime.strftime(datetime.now(taipei), "%Y-%m-%d")

def authentication(email:str, password:str):
    """
    check user iuformation
    """
    if email == None or password == None:
        return False
    return True

def search():
    return True

def get_record(id):
    for record in records:
        if record['recordId'] == id:
            return record
