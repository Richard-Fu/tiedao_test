
# -*- coding:utf-8 -*-
import requests
from bs4 import BeautifulSoup
import bs4
from selenium import webdriver
from time import sleep
import time
from PIL import Image
from hashlib import md5
from chaojiying import Chaojiying_Client
import datetime
import os
import json
import pymongo

MONGO_URL = 'localhost'
MONGO_DB = 'python'
MONGE_COLLECTION = 'rooms'
MONGE_FIND = 'week'
client = pymongo.MongoClient(MONGO_URL)
db = client[MONGO_DB]

def save_to_monge(result):
	"""
	保存到 mongeDb
	
	:param result: 结果
	"""
	try:
		if db[MONGE_COLLECTION].insert(result):
			print('存储成功')
	except Exception:
		print('存储失败')

def find_from_monge():
	try:
		item = db[MONGE_FIND].find_one({'title':'week'})
		return item
	except Exception:
		print('失败')

class Login(object): 

	def __init__(self):
		
	
		options=webdriver.ChromeOptions()
		options.add_argument('--headless')
		options.add_argument('--disable-gpu')
		options.add_argument('--ignore-certificate-errors')
		options.add_argument("--disable-gpu")
		self.driver=webdriver.Chrome(options=options)
		self.driver.maximize_window()
		self.driver.set_window_size('1920','1080') #设置浏览器宽480，高800　
		self.driver.get('http://tiedao.vatuu.com/service/login.html?returnUrl=return')
		cookie = self.driver.get_cookies()
		print(type(cookie))
		print(cookie[0]['value'])
		self.cookie = cookie[0]['value']
		print(type(self.cookie))
		self.headers = {
				'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
				'Accept-Encoding': 'gzip, deflate',
				'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
				'Connection': 'keep-alive',
				'Cookie': self.cookie,
				'Host': 'tiedao.vatuu.com',
				'Upgrade-Insecure-Requests': '1',
				'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 \
					(KHTML, like Gecko)Chrome/72.0.3626.121 Safari/537.36'
			}
		print(self.headers)
		self.url = 'http://tiedao.vatuu.com/vatuu/StudentScoreInfoAction?setAction=studentScoreQuery&viewType=\
			studentScore&orderType=submitDate&orderValue=desc'
		self.chaojiying = Chaojiying_Client('richardfu', '355aizijibaC', '898943')	
	# 时间格式进行格式化
	def time_format(self):
		current_time = time.strftime('%Y%m%d%H%M%S', time.localtime(time.time()))
		return current_time
	def cut(self):
		
		path = os.path.dirname(os.path.abspath(__file__))
		# 截取全屏
		self.driver.save_screenshot(path+"/img/full.png")
		# 要截屏的目标元素
		element = self.driver.find_element_by_id("randomPhoto")
		print(element.location)
		print(element.size)
		# 获取element的顶点坐标
		xPiont = element.location['x']
		yPiont = element.location['y']
		# 获取element的宽、高
		element_width = xPiont + element.size['width']
		element_height = yPiont + element.size['height']
	 
		picture = Image.open(path+"/img/full.png")
	 
		'''
		crop()--  一个显式的参数：一个4元组
		Image.crop(box=None):图像返回一个矩形区域,box是一个四元组 限定所述左，上，右，和下像素坐标
		参数：box--裁剪矩形，作为（左，上，右，下）-tuple;返回类型：Image；返回：一个Image对象
		所以你应该重写它：
		img.crop((414,122,650,338))
		#        ^    4-tuple    ^
		'''
		picture = picture.crop((xPiont, yPiont, element_width-30, element_height))
		src = path + "/img/"+self.time_format()+".png"
		picture.save(src)
		im = open(src, 'rb').read()													
		ran =  self.chaojiying.PostPic(im, 1902)
		print(ran)
		return ran
	
	
		
	def login(self):
		rant = self.cut()
		time.sleep(2)
		ran_id = rant['pic_id']
		ran = rant['pic_str']
		print(type(rant),rant)
		user = self.driver.find_element_by_id('username')
		passwor = self.driver.find_element_by_id('password')
		ranstring = self.driver.find_element_by_id('ranstring')
		confirm = self.driver.find_element_by_id('submit2')
		# name = input("请输入:username")
		# password = input("请输入:password")
		# ran = input("请输入:验证码")
		# user.send_keys(name)
		# passwor.send_keys(password)
		user.send_keys('20163707')
		passwor.send_keys('355aizijibaV')
		print(type(ran),ran)
		ranstring.send_keys(ran)
		confirm.click()
		time.sleep(2)
		url = 'http://tiedao.vatuu.com/vatuu/PublicInfoQueryAction?setAction=queryStudent'
		url_return = 'http://tiedao.vatuu.com:80/service/login.html?returnUrl=return'
		soup = get_soup(url,{'JSESSIONID':self.cookie})
		a = soup.find('a')['href']
		print(a)
		print(url_return)
		if a == url_return:
			self.chaojiying.ReportError(ran_id)
			print('重新登陆！！！')
			return 1
		return 0
		
def get_soup(url,cookies=''):
	if cookies:
		html = get_html(url,cookies)
		soup = BeautifulSoup(html, 'lxml')
		return soup
	else:
		html = get_html(url,'')
		soup = BeautifulSoup(html, 'lxml')
		
		return soup	
		
def html_utf(content):
	html=content
	html_doc=str(html,'utf-8') #html_doc=html.decode("utf-8","ignore")
	return html_doc	
def get_html(url,cookies):
	try:
		r = requests.get(url, timeout=5, cookies=cookies)
		r.raise_for_status()
		return html_utf(r.content)
	except:
		return "ERROR"	
def score(url,cookie):
	# print(get_html(url,{'JSESSIONID':cookie}))
	soup = get_soup(url,{'JSESSIONID':cookie})
	table = soup.find('table', attrs={'id':'table3'})
	trs = table.find_all('tr')
	contents = []
	for tr in trs:
		ths = tr.find_all('th')
		if ths:
			for th in ths:
				print(th.string.strip(),' | ',end='')
			print('')
		else:
			content = []
			tds = tr.find_all('td')
			for td in tds:
				if td.string is None:
					pass
				else:
					str = td.string.strip()
					content.append(str)
					print(str,' | ',end='')
			contents.append(content)
			print('')
	for con in contents:
		for c in con:
			print(c,'||',end='')
		print('')	

def course(url,cookie):
	soup = get_soup(url,{'JSESSIONID':cookie})
	table = soup.find('table',attrs={'class':'table_border'})
	trs = table.find_all('tr')
	contents = []
	for tr in trs:
		tds = tr.find_all('td')
		for td in tds:
			res = td.find_all(text=True)
			strs = ''
			for s in res:
				strs+=s
			# print(strs)
			contents.append(strs)
			print('+++++++++++++++++++++++++++++')
	'''
	classList 按时间顺序排好的课程
	'''
	classList = []			
	for i in range(1,8):
		for j in range(1,13):
			content = '星期'+str(i)+'：第'+str(j)+'节：'+contents[j*8+i]
			print(content)
			classList.append(content)
	
def init_week():
	try:
		item = db[MONGE_FIND].insert({'title':'week','week':5,'day':5})
		return item
	except Exception:
		print('失败')
	
def room(url,cookie,class_num):
	'''
	首先构建表单
	'''
	
	room_object = {}
	d=datetime.datetime.now()

	class_num = class_num
	# week = input('请输入周数：')
	# week = '5'
	# day_num = d.weekday()+1
	item = find_from_monge()
	week = item['week']
	day_num = item['day']
	room_object['week'] = week
	room_object['day'] = day_num
	print(day_num)
	# class_num = input('请输入：\
	# 1：第一二节\
	# 2：第三四节\
	# 3：整个上午\
	# 4：第六七节\
	# 5：第八九节\
	# 6：整个下午\
	# 7：晚自习')
	day_num = pow(2,day_num-1)
	week = pow(2,week-1)

	day_time = ''
	
	if class_num == '1':
		day_time='0000000000011'
	elif class_num == '2':
		day_time='0000000001100'
	elif class_num == '3':
		day_time='0000000001111'
	elif class_num == '4':
		day_time='0000001100000'
	elif class_num == '5':
		day_time='0000110000000'
	elif class_num == '6':
		day_time='0000111100000'
	elif class_num == '7':
		day_time='0110000000000'
	param = {'setAction': 'classroomQuery',
			'PageAction': 'Query',
			'day_time_text': day_time,
			'school_area_code': '1',
			'building': '',
			'week_no': str(week),
			'day_no': str(int(day_num)),
			'B1': '查询'
		}
	cookie_copy = 'JSESSIONID='+cookie
	print(param)
	
	headers = {
				'Connection': 'keep-alive',
				'Cache-Control': 'max-age=0',
				'Origin': 'http://tiedao.vatuu.com',
				'Upgrade-Insecure-Requests': '1',
				'Content-Type': 'application/x-www-form-urlencoded',
				'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 \
					(KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36',
				'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,\
					image/apng,*/*;q=0.8',
				'Referer': 'http://tiedao.vatuu.com/vatuu/CourseAction',
				'Accept-Encoding': 'gzip, deflate',
				'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
				'Cookie':  cookie_copy
			}
	r = requests.post(url,data=param,headers=headers)
	soup = BeautifulSoup(html_utf(r.content), 'lxml')
	table = soup.find('table',attrs={'class':'table_gray'})
	trs = table.find_all('tr')
	items = []
	for tr in trs:
		
		ths = tr.find_all('th')
		if ths:
			for th in ths:
				print(th.string.strip(),' | ',end='')
			print('')
		else:
			content = []
			tds = tr.find_all('td')
			for td in tds:
				res = td.find_all(text=True)
				strs = ''
				item = []
				for s in res:
					s = s.strip('\n')
					strs+=s
				strs = strs.strip()
				print(strs,' || ',end='')
				content.append(strs)
			items.append(content)
		print('+++++++++++++++++++++++++++++')
	for item in items:
		if not item[3].find('基'):
			item[3] = item[3].replace('基','基教')
			print(item[3],11)
		elif not item[3].find('土'):
			item[3] = item[3].replace('土','土木')
			print(item[3],22)
		else:
			print(item[3])
			
		
	room_object['class_num'] = class_num
	room_object['classes'] = items
	save_to_monge(room_object)
	
def when_week():
	d = datetime.datetime.now()
	item = find_from_monge()
	week = item['week']
	day = item['day']
	day_num = d.weekday()+1
	# day_num = 1
	if day == 7 and day_num == 1:
		db[MONGE_FIND].update_one({'title':'week'},{'$set':{'week':week+1,'day':day_num}})
	if day_num > day:
		db[MONGE_FIND].update_one({'title':'week'},{'$set':{'day':day_num}})
	
				

if __name__ == '__main__':
	
	# init_week()
	when_week()
	login = Login()
	for i in range(1,8):
		login1 = Login()
		if login1.login():
			continue
		else:
			login = login1
			break
	
	
	room_url = 'http://tiedao.vatuu.com/vatuu/CourseAction'
	for i in range(1,8):
		room(room_url,login.cookie,str(i))
	
	# course_url = 'http://tiedao.vatuu.com/vatuu/CourseAction?setAction=userCourseScheduleTable\
		# &viewType=studentQueryCourseList&selectTableType=ThisTerm&queryType=student'
	# score(login.url,login.cookie)
	# course(course_url,login.cookie)
	
	
"""
登陆功能完善，比如验证码错误，密码错误等。
找出需要的url，并整理好返回数据
"""




