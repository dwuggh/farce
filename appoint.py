from requests_futures.sessions import FuturesSession
from concurrent.futures import ThreadPoolExecutor
import requests
from bs4 import BeautifulSoup
import datetime
import pickle
import time

def get_date_str(offset=0):
    now = datetime.datetime.now()
    delta = datetime.timedelta(days=offset)
    t = now + delta
    return t.strftime('%Y-%m-%d')

# id=3 --> 08:00-9:30
def time_id_to_segment(id):
    if id < 3 or id > 11:
        return None
    dt = datetime.timedelta(hours=1.5)
    start = datetime.datetime.combine(datetime.datetime.today(),  datetime.time(8))
    start = start + dt * (id - 3)
    end = start + dt
    return start.strftime('%H:%M') + "-" + end.strftime('%H:%M')


class Appointer(object):

    def __init__(self, stuid, password, wxId):
        self.stuid = stuid
        self.password = password
        self.wxId = wxId
        self.name =''
        self.phone =''
        self.session = requests.Session()
        # futuresSession
        self.sf = FuturesSession()

    def update_info(self, name, phone):
        self.name = name
        self.phone = phone

    def load_session(self):
        with open('./session.pickle', 'rb') as f:
            self.session.cookies.update(pickle.load(f))

    def dump_session(self):
        with open('./session.pickle', 'wb') as f:
            pickle.dump(self.session.cookies, f)

    def login(self):
        url = "https://passport.ustc.edu.cn/login?service=https://cgyy.ustc.edu.cn/validateLogin.html"
        session = self.session
        session.headers.update({
            'x-requested-with': 'com.tencent.mm',
            'user-agent': 'Mozilla/5.0 (Linux; Android 7.0; Google Nexus 5X Build/NBD92Y; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/74.0.3729.186 Mobile Safari/537.36 MMWEBID/2579 MicroMessenger/8.0.2.1860(0x28000236) Process/appbrand0 WeChat/arm32 Weixin NetType/WIFI Language/zh_CN ABI/arm32 miniProgram',
        })
        resp1 = session.get(url)

        data = resp1.text.encode('ascii', 'ignore').decode('utf-8', 'ignore')
        soup = BeautifulSoup(data, 'html.parser')
        CAS_LT = soup.find("input", id="CAS_LT")['value']
        
        session.cookies.set('lang', 'zh')

        data = {
            'model': 'uplogin.jsp',
            'CAS_LT': CAS_LT,
            'service': 'https://cgyy.ustc.edu.cn/validateLogin.html',
            'username': self.stuid,
            'password': str(self.password),
            'warn': '',
            'showCode': '',
            'button': '',
        }

        headers = {
            'origin': 'https://passport.ustc.edu.cn',
            'referer': 'https://passport.ustc.edu.cn/login?service=https://cgyy.ustc.edu.cn/validateLogin.html'
        }
        resp = session.post('https://passport.ustc.edu.cn/login', data=data, headers=headers)
        validate_url = resp.url

        # get ticket
        self.ticket = validate_url.split('ticket=')[-1]
        # print(self.ticket)

        mplogin_url = "https://cgyy.ustc.edu.cn/api/user/login"
        resp = session.post(mplogin_url, json={
            "ticket": self.ticket,
            "wxId": self.wxId
        }, headers={
            "referer": "https://servicewechat.com/wxf0984b113dd8ac45/20/page-frame.html",
        })

        self.data = resp.json()["data"]
        # print(self.data)
        self.session.headers.update({"token": self.data["token"]})
        self.sf = FuturesSession(session=self.session, executor=ThreadPoolExecutor(max_workers=30))


    def get_time_list(self):
        resp = self.post("app/appointment/time/quantum/get/1", json={})
        return resp.json()
        

    def get_appointment_list(self, time_id, date_offset=0):
        resp = self.post("app/sport/place/getAppointmentInfo", json={
            
            "gymnasiumId": "1",
            "dateStr": get_date_str(date_offset),
            "timeQuantumId": time_id
        })
        data = resp.json()["data"]
        return data
        # TODO reduce by useType(=1 means occupied), map to id here


    def submit(self, time_id, sport_place_id, date):
        payload = {
            "gymnasiumId": 1,
            # 几号场
            "sportPlaceId": sport_place_id,
            "timeQuantum": time_id_to_segment(time_id),
            "timeQuantumId": time_id,
            "appointmentUserName": self.name,
            "appointmentPeopleNumber": 1,
            "appointmentDay": date,
            "phone": self.phone
        }
        # print(payload)
        resp_future = self.post_async('app/appointment/record/submit', json=payload)
        # result_code = int(resp.json()['code'])
        # # result_msg = resp.json()['msg']
        # if result_code == 400:
        #     pass
        return resp_future
        

    def post(self, url, *args, **kwargs):
        actual_url = "https://cgyy.ustc.edu.cn/api/" + url
        return self.session.post(actual_url, *args, **kwargs)

    def post_async(self, url, *args, **kwargs):
        actual_url = "https://cgyy.ustc.edu.cn/api/" + url
        return self.sf.post(actual_url, *args, **kwargs)
    '''
    time_id:
    3  --> 08:00-09:30
    4  --> 09:30-11:00
    5  --> 11:00-12:30
    6  --> 12:30-14:00
    7  --> 14:00-15:30
    8  --> 15:30-17:00
    9  --> 17:00-18:30
    10 --> 18:30-20:00
    11 --> 20:00-21:30

    place_id: 1 - 14
    '''
    def appoint_definite(self, time_id, place_id):
        self.submit(time_id, place_id, get_date_str(1))


if __name__ == '__main__':
    import data
    a = Appointer(data.stuid, data.password, data.wxId)
    a.login()
    # a.dump_session()
    # a.load_session()
    a.update_info(data.name, data.phone)

    def process_resp(fut):
        resp = fut.result()
        # result_code = int(resp.json()['code'])
        # result_msg = resp.json()['msg']
        # if result_code == 400:
        #     pass
        msg = resp.json()
        print(msg)
        return msg

    # print(a.get_time_list())
    # print(a.get_appointment_list(5))
    # NOTE took 0.03s for one request in eduroam
    tommorow = get_date_str(1)

    t = datetime.datetime.combine(datetime.datetime.today(),  datetime.time(22))
    t = time.mktime(t.timetuple())
    time.sleep(t - time.time() - data.prepone)

    t0 = time.time()
    
    rs = []
    for j in range(data.reps):
        for t in data.time_id:
            rs.extend([a.submit(t, i, tommorow) for i in range(1, 15)])

    for r in rs:
        process_resp(r)

