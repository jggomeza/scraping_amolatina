from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options as Options
from selenium.webdriver.support.ui import Select
import time
import requests
import json
from datetime import date
import mysql.connector
import subprocess
import sys
import logging

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO, filename="debug.log", datefmt='%m/%d/%Y %I:%M:%S %p'
)

logger = logging.getLogger(__name__)
logger.info("Iniciando servicio!")
# logger.info()
# logger.error()
# logger.warning()
# logger.critical()

class Scraping(object):
	"""docstring for Scraping"""
	
	def __init__( self, user_agency, password_agency, datefrom=f'{date.today().month if not date.today().month  < 10 else "0"+str(date.today().month)}/{date.today().day if not date.today().day  < 10 else "0"+str(date.today().day)}/{date.today().year}' if len(sys.argv)==1 else sys.argv[1] ):
		# self.host="127.0.0.1"
		self.host="10.156.80.115"
		self.user="root"
		self.password="12345678"
		self.database="scraping"

		self.user_agency = user_agency
		self.password_agency = password_agency

		self.today = datefrom
		# print(self.today)
		self.timeGeneral = 3
		self.timeMax=8

		self.options = Options()
		self.options.add_argument("--headless")

	def main(self):
		self.website = "https://www.amolatina.com/"
		self.driver = webdriver.Chrome(options=self.options)
		# self.driver.maximize_window()
		self.driver.get(self.website)

	def login(self):
		time.sleep(self.timeGeneral)
		login_button = self.driver.find_element(By.XPATH, '/html/body/div[1]/div/div[2]/div/div/section[1]/div/div[1]/div/div/div/div[1]/button')
		login_button.click()
		time.sleep(self.timeGeneral)
		email = self.driver.find_element(By.XPATH, '/html/body/div[1]/div/div[2]/div/div/section[1]/div/div[1]/div/div/div/div[2]/div/div/div[1]/div/form/div[1]/label/div/label/input')
		time.sleep(self.timeGeneral)
		password = self.driver.find_element(By.XPATH, '/html/body/div[1]/div/div[2]/div/div/section[1]/div/div[1]/div/div/div/div[2]/div/div/div[1]/div/form/div[2]/label/div/label/input')
		time.sleep(self.timeGeneral)
		email.send_keys(self.user_agency)
		time.sleep(self.timeGeneral)
		password.send_keys(self.password_agency)
		time.sleep(self.timeGeneral)
		button = self.driver.find_element(By.XPATH, '/html/body/div[1]/div/div[2]/div/div/section[1]/div/div[1]/div/div/div/div[2]/div/div/div[1]/div/form/button')
		button.click()

	def diamonds(self):
		time.sleep(self.timeMax)
		buttonMenu = self.driver.find_element(By.XPATH, '/html/body/div[4]/div/div[1]/div/div/header/div[1]/div/div[1]/section/ul/li[10]/div')
		buttonMenu.click()
		time.sleep(self.timeGeneral)
		buttonDiamonds = self.driver.find_element(By.XPATH,'/html/body/div[4]/div/div[1]/div/div/header/div[1]/div/div[1]/section/ul/li[10]/div/div/div/div[1]/div/ul/li[7]/a')
		buttonDiamonds.click()
		time.sleep(self.timeGeneral)
		self.driver.execute_script("window.scrollTo(0, window.scrollY + 800)") 
		time.sleep(self.timeGeneral)

	def dateFrom(self):
		time.sleep(self.timeGeneral)
		datepicker = self.driver.find_element(By.XPATH, '/html/body/div[4]/div/div[2]/div/div/div/div/div/div/div[2]/div[1]/div/div[1]/div/div[1]/div[1]/div[1]/input')
		datepicker.clear()
		datepicker.send_keys(self.today)
		datepicker.click()

	def showButtonRed(self):
		redButton = self.driver.find_element(By.XPATH, '/html/body/div[4]/div/div[2]/div/div/div/div/div/div/div[2]/div[1]/div/div[1]/button')
		redButton.click()
		time.sleep(self.timeMax)

	def getDiamondTable(self):
		self.diamondTable = self.driver.find_element(By.XPATH,'/html/body/div[4]/div/div[2]/div/div/div/div/div/div/div[2]/div[1]/div/div[3]/table/tbody')
		self.rows = self.diamondTable.find_elements(By.TAG_NAME, "tr")

		self.total = self.driver.find_element(By.XPATH, '/html/body/div[4]/div/div[2]/div/div/div/div/div/div/div[2]/div[1]/div/div[3]/table/thead/tr[2]/th')
		self.total=float(self.total.text.split(" ")[1].replace(',',''))

		self.suma=0
		for row in self.rows:
			self.suma+=float(row.find_elements(By.TAG_NAME, "td")[5].text if not row.find_elements(By.TAG_NAME, "td")[5].text=="" else 0)

		logger.info(f"Tiempo de inicio = {self.current_time()}")

	def printValues(self):
		logger.info(f'{self.suma} < {self.total} rows = {len(self.rows)}')

	def current_time(self):
		current_time = time.strftime("%H:%M:%S", time.localtime())
		return current_time

	def getTotals(self):
		while self.suma < self.total:
			self.printValues()
			
			try:
				show_more = self.driver.find_element(By.XPATH, '/html/body/div[4]/div/div[2]/div/div/div/div/div/div/div[2]/div[1]/div/div[3]/button')
				show_more.click()
			except Exception as e:
				self.rows = self.diamondTable.find_elements(By.TAG_NAME, "tr")
			finally:
				self.rows = self.diamondTable.find_elements(By.TAG_NAME, "tr")
				self.total = self.driver.find_element(By.XPATH, '/html/body/div[4]/div/div[2]/div/div/div/div/div/div/div[2]/div[1]/div/div[3]/table/thead/tr[2]/th')
				self.total=float(self.total.text.split(" ")[1].replace(',',''))
				
				self.suma=0
				for row in self.rows:
					self.suma+=float(row.find_elements(By.TAG_NAME, "td")[5].text if not row.find_elements(By.TAG_NAME, "td")[5].text=="" else 0)

	def insertDiamonds(self):
		try:
			cursor=self.connect()
			sql = f"SELECT COUNT(id) FROM diamonds WHERE diamond_date like '{date.today().year}-{date.today().month}-{date.today().day}%'"
			cursor.execute(sql)
			ultimo=cursor.fetchone()[0]
			logger.info(f"Inicia el INSERT de los {len(self.rows)-ultimo} registros")

			for row in self.rows[ultimo:len(self.rows)]:
				# diamondDate = row.find_elements(By.TAG_NAME, "td")[0].text
				# diamondDate =  diamondDate if not '-' in diamondDate else diamondDate.split('-')[0].strip()
				# diamondDate = f"{diamondDate.split('/')[2]}/{diamondDate.split('/')[0]}/{diamondDate.split('/')[1]}"
				diamondDate = f'{date.today().year}-{date.today().month}-{date.today().day} 00:00:00.000'
				diamondCuratorId=row.find_elements(By.TAG_NAME, "td")[1].text
				diamondMemberFromId=row.find_elements(By.TAG_NAME, "td")[2].text
				diamondMemberToId=row.find_elements(By.TAG_NAME, "td")[3].text
				ServiceName=row.find_elements(By.TAG_NAME, "td")[4].text
				Amount=row.find_elements(By.TAG_NAME, "td")[5].text if not row.find_elements(By.TAG_NAME, "td")[5].text=="" else 0
				agency=self.user_agency

				# sql = "INSERT INTO diamonds (diamond_date, curator_id, member_from_id, member_to_id, serviceName, amount, agency) VALUES (%s, %s, %s, %s, %s, %s, %s)"
				sql = "INSERT INTO diamonds (diamond_date, curator_id, member_from_id, member_to_id, serviceName, amount, agency) VALUES (SYSDATE(), %s, %s, %s, %s, %s, %s)"
				# values = (diamondDate, diamondCuratorId, diamondMemberFromId, diamondMemberToId, ServiceName, Amount, agency)
				values = (diamondCuratorId, diamondMemberFromId, diamondMemberToId, ServiceName, Amount, agency)
				cursor.execute(sql, values)
				self.db.commit()
			
			self.close_connection()
		except Exception as e:
			raise e

		logger.info(f"Finalizada inserción en diamonds Time = {self.current_time()}")

	def insertPeoples(self):
		logger.info(f"Inicia inserción en peoples Time = {self.current_time()}")
		cursor=self.connect()
		sql = "select count(id), member_from_id from diamonds group by member_from_id"
		cursor.execute(sql)
		rows1=cursor.fetchall()

		sql = "select count(id), member_to_id from diamonds group by member_to_id"
		cursor.execute(sql)
		rows2=cursor.fetchall()
		self.close_connection()
		
		members=[x[1] for x in rows1 if x[1] != ''] + [x[1] for x in rows2 if x[1] != '']
		for id in members:
			try:
				response = requests.get(f'https://api.amolatina.com/users/{id}')
				data=response.json()
				api_id=data['id'] if 'id' in data.keys() else ''
				name=data['name'] if 'name' in data.keys() else ''
				gender=data['gender'] if 'gender' in data.keys() else ''
				birthday=data['birthday'].split("T")[0] if 'birthday' in data.keys() else '0000-00-00'
				country=data['country'] if 'country' in data.keys() else ''
				city=data['city'] if 'city' in data.keys() else ''
				avatar=data['thumbnail'] if 'thumbnail' in data.keys() else ''
				occupation=data['occupation'] if 'occupation' in data.keys() else ''
				eye=data['eye'] if 'eye' in data.keys() else ''
				hair=data['hair'] if 'hair' in data.keys() else ''
				about=data['about'] if 'about' in data.keys() else ''
				bodytype=data['bodytype'] if 'bodytype' in data.keys() else ''
				smoke=data['smoke'] if 'smoke' in data.keys() else ''
				drink=data['drink'] if 'drink' in data.keys() else ''
				education=data['education'] if 'education' in data.keys() else ''
				relationship=data['relationship'] if 'relationship' in data.keys() else ''

				cursor=self.connect()
				sql = "INSERT INTO peoples (api_id, name, gender, birthday, country, city, avatar, occupation, eye, hair, about, bodytype, smoke, drink, education, relationship ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
				values = (api_id, name, gender, birthday, country, city, avatar, occupation, eye, hair, about, bodytype, smoke, drink, education, relationship)
				cursor.execute(sql, values)
				self.db.commit()
				self.close_connection()
			except Exception as e:
				# print(id+" Fallo")
				# cursor=self.connect()
				# sql='SELECT IFNULL(MAX(id), 0)+1 FROM peoples'
				# cursor.execute(sql)

				# sql = f'ALTER TABLE peoples auto_increment = {cursor.fetchone()[0]}'
				# cursor.execute(sql)
				# self.close_connection()
				pass
		logger.info(f"Finalizada la inserción en peoples Time = {self.current_time()}")
		
	def quit(self):
		self.driver.quit()

	def connect(self):
		self.db = mysql.connector.connect(
		  host=self.host,
		  user=self.user,
		  password=self.password,
		  database=self.database
		)

		self.cursor = self.db.cursor()
		return self.cursor

	def close_connection(self):
		self.cursor.close()
		self.db.close()


agencys=[
	{'user': 'uaisleteam@gmail.com', 'password': 'Rojo**03'},
	# {'user': 'uaisleteam@gmail.com', 'password': 'Rojo**03'},
]

while True:
	for agency in agencys:
		user=agency['user']
		password=agency['password']
		app = Scraping(user, password)

		app.main()

		app.login()
		app.diamonds()
		app.dateFrom()
		app.showButtonRed()
		app.getDiamondTable()
		app.getTotals()
		app.printValues()
		app.insertDiamonds()

		app.insertPeoples()
		app.quit()

		try:
			command="pgrep chrome | xargs kill -9 >/dev/null  2>/dev/null"
			result=subprocess.check_output(command, shell=True)
		except Exception as e:
			pass
	# break 