# Room reservation system
教室預訂系統
https://lulalatest.herokuapp.com

# physical
此project是以python flask框架製作並部屬在Heroku上的網頁，以此來讓整個系統可以透過網路連接。
database的部分使用Heroku的Add-ons中的clearDB服務
寫入google calendar使用google api的google calendar

重現這個project，需要建立一個Heroku的python專案，
並在Heroku的Add-ons使用clearDB的服務，並將clearDB提供的資訊填入connect.py中連接database的參數。
另外由於有使用到google calendar，因此還要另外申請一個網頁服務的google api，
並且將會用到的測試email與redirect URL加入API中，
最後將建立好的專案的OAuth 2.0 ID下載並更名為"credentials.json"
將project中的"credentials.json"取代掉。
