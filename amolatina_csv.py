#!/usr/bin/env python
# -*- coding: utf-8 -*-

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options as Options
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
import time
import requests
import json
from datetime import date
import mysql.connector
import subprocess
import sys
import logging
import csv
import os

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO, filename=f"{os.path.abspath(os.path.dirname(__file__))}/debug.log", datefmt='%m/%d/%Y %I:%M:%S %p'
)

logger = logging.getLogger(__name__)
logger.info("Iniciando servicio!")

class Scraping(object):
	
	def __init__( self, user_agency, password_agency, datefrom=f'{date.today().month if not date.today().month  < 10 else "0"+str(date.today().month)}/{date.today().day if not date.today().day  < 10 else "0"+str(date.today().day)}/{date.today().year}' if len(sys.argv)==1 else sys.argv[1] ):
		# self.host="127.0.0.1"
		self.host="10.156.80.115"
		self.user="root"
		self.password="12345678"
		self.database="scraping"

		self.user_agency = user_agency
		self.password_agency = password_agency

		self.today = datefrom
		self.timeGeneral = 3
		self.timeMax=8
		self.PATH=os.path.abspath(os.path.dirname(__file__))
		
		# Google Chrome
		self.options = Options()
		prefs={'download.default_directory':self.PATH}
		self.options.add_experimental_option('prefs',prefs)
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
		password = self.driver.find_element(By.XPATH, '/html/body/div[1]/div/div[2]/div/div/section[1]/div/div[1]/div/div/div/div[2]/div/div/div[1]/div/form/div[2]/label/div/label/input')
		email.send_keys(self.user_agency)
		password.send_keys(self.password_agency)
		button = self.driver.find_element(By.XPATH, '/html/body/div[1]/div/div[2]/div/div/section[1]/div/div[1]/div/div/div/div[2]/div/div/div[1]/div/form/button')
		button.click()

	def diamonds(self):
		time.sleep(self.timeMax)
		buttonMenu = self.driver.find_element(By.XPATH, '/html/body/div[4]/div/div[1]/div/div/header/div[1]/div/div[1]/section/ul/li[10]/div')
		buttonMenu.click()
		time.sleep(self.timeGeneral)
		buttonDiamonds = self.driver.find_element(By.XPATH,'/html/body/div[4]/div/div[1]/div/div/header/div[1]/div/div[1]/section/ul/li[10]/div/div/div/div[1]/div/ul/li[7]/a')
		buttonDiamonds.click()

	def dateFrom(self):
		datepickerFrom = self.driver.find_element(By.XPATH, '/html/body/div[4]/div/div[2]/div/div/div/div/div/div/div[2]/div[1]/div/div[1]/div/div[1]/div[1]/div[1]/input')
		datepickerFrom.clear()
		datepickerFrom.send_keys(self.today)
		datepickerFrom.click()

		datepickerTo = self.driver.find_element(By.XPATH, '/html/body/div[4]/div/div[2]/div/div/div/div/div/div/div[2]/div[1]/div/div[1]/div/div[1]/div[1]/div[3]/input')
		datepickerTo.clear()
		datepickerTo.send_keys(self.today)
		datepickerTo.click()

	def showButtonRed(self):
		redButton = self.driver.find_element(By.XPATH, '/html/body/div[4]/div/div[2]/div/div/div/div/div/div/div[2]/div[1]/div/div[1]/button')
		redButton.click()
		time.sleep(self.timeMax)

	def current_time(self):
		current_time = time.strftime("%H:%M:%S", time.localtime())
		return current_time
	
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

	def download_csv(self):
		if os.path.exists(f"{self.PATH}/affiliate-partner-diamonds.csv"):
			os.remove(f"{self.PATH}/affiliate-partner-diamonds.csv")
		else:
			logger.info(f"El archivo {self.PATH}/affiliate-partner-diamonds.csv no existe!")
		
		download = self.driver.find_element(By.XPATH, '/html/body/div[4]/div/div[2]/div/div/div/div/div/div/div[2]/div[1]/div/span')
		download.click()
		logger.info(f"Descargando archivo affiliate-partner-diamonds.csv")

	def load_csv(self):
		while not os.path.exists(f"{self.PATH}/affiliate-partner-diamonds.csv"):
			time.sleep(self.timeGeneral)
		
		logger.info(f"Iniciada inserción en diamonds Time = {self.current_time()}")
		with open(f'{self.PATH}/affiliate-partner-diamonds.csv', mode='r') as csv_file:
			csv_reader = csv.reader(csv_file, delimiter=',')
			diamonds=[]

			for row in csv_reader:
				diamonds.append([row[0], row[1].split("(")[0], row[2].split("(")[0], row[3], row[4], row[5]])
			
			diamonds.pop(0)
			diamonds.pop(0)
			diamonds.pop()

		try:
			cursor=self.connect()
			# sql = f"TRUNCATE TABLE diamonds"
			sql = f"DELETE FROM diamonds WHERE diamond_date like '{date.today().year}-{date.today().month}-{date.today().day}%'"
			cursor.execute(sql)
			self.db.commit()
		except Exception as e:
			raise e
		
		logger.info(f"Inicia el INSERT de los {len(diamonds)} registros")
		for row in diamonds:
			diamondCuratorId=row[1]
			diamondMemberFromId=row[2]
			diamondMemberToId=row[3]
			ServiceName=row[4]
			Amount=row[5]
			agency=self.user_agency

			try:
				sql = "INSERT INTO diamonds (diamond_date, curator_id, member_from_id, member_to_id, serviceName, amount, agency) VALUES (SYSDATE(), %s, %s, %s, %s, %s, %s)"
				values = (diamondCuratorId, diamondMemberFromId, diamondMemberToId, ServiceName, Amount, agency)
				cursor.execute(sql, values)
			except Exception as e:
				raise e

		self.db.commit()
		self.close_connection()
		logger.info(f"Finalizada inserción en diamonds Time = {self.current_time()}")

	def insertPeoples(self):
		logger.info(f"Inicia inserción en peoples Time = {self.current_time()}")
		cursor=self.connect()
		sql = """SELECT p.api_id from
		(
			select DISTINCT(d.member_from_id) as id from diamonds d WHERE d.member_from_id != 0 union 
			select DISTINCT(d.member_to_id) as id from diamonds d WHERE d.member_to_id != 0
		) a left join peoples p on(a.id=p.api_id) where p.api_id != ''"""
		cursor.execute(sql)
		rows=cursor.fetchall()
		self.close_connection()
		
		members=[x[0] for x in rows if x[0] != '']

		if len(members)==0:
			sql = """SELECT DISTINCT(d.member_from_id) as id from diamonds d WHERE d.member_from_id != 0 union 
			select DISTINCT(d.member_to_id) as id from diamonds d WHERE d.member_to_id != 0"""
		else:
			sql = f"""SELECT 
			d.id
			from
			(
			select DISTINCT(d.member_from_id) as id from diamonds d WHERE d.member_from_id != 0 union 
			select DISTINCT(d.member_to_id) as id from diamonds d WHERE d.member_to_id != 0
			) d WHERE d.id not in {tuple(members)}"""
		
		cursor=self.connect()
		cursor.execute(sql)
		rows=cursor.fetchall()
		self.close_connection()

		members=[x[0] for x in rows if x[0] != '']
		# logger.info(members[:])

		for id in members:
			for i in range(0,10):
				try:
					if i==0:
						api=f'https://api.amolatina.com/users/{id}'
						response = requests.get(api)
					else:
						api=f'https://api{i}.amolatina.com/users/{id}'
						response = requests.get(api)

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
					break
				except Exception as e:
					logger.error(f"El id {id} no se encuentra en la API {api}")
					continue
		self.db.commit()
		self.close_connection()
		logger.info(f"Finalizada la inserción en peoples Time = {self.current_time()}")
		logger.info(f"############################################## {self.current_time()} ##############################################")
		logger.info("")

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
		app.download_csv()
		app.load_csv()
		# app.insertPeoples()
		app.quit()

		try:
			command="pgrep chrome | xargs kill -9 >/dev/null  2>/dev/null"
			result=subprocess.check_output(command, shell=True)
		except Exception as e:
			pass
	break 