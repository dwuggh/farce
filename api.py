
# header contains token, added by /api/user/login
# /api/user/login
{
  "ticket": "ST-eab13ae3ebad4f04ba0540e496568358",
  "wxId": "oMJsE5chAqLEbONpcsz2vYzkzLu8"
    }


# duno what it did
# /api/app/appointment/time/quantum/get/1
{}

# query
"/api/app/sport/place/getAppointmentInfo"
{
  "gymnasiumId": "1",
  "dateStr": "2022-04-29",
  "timeQuantumId": 3
    }

"/api/app/appointment/record/submit"
{
    "gymnasiumId": 1,
    # 几号场
    "sportPlaceId": 2,
    # should be like "11:00-12:30"
    "timeQuantum": "11:00-12:30",
    "timeQuantumId": 1,
    # 似乎就是名字
    "appointmentUserName": '丘处机',
    "appointmentPeopleNumber": 1,
    "appointmentDay": '2022-04-29',
    "phone": "11111111111"
}




# an element of timelist
{
      "createBy": "admin",
      "createTime": 1606878871000,
      "delFlag": "0",
      "gymnasiumId": 1,
      "id": 3,
      "sort": 0,
      "timeQuantum": "08:00-09:30",
      "updateBy": "admin",
      "updateTime": 1607163286000
    },

