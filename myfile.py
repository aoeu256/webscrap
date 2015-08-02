from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.proxy import *
from selenium.common.exceptions import NoSuchElementException
from threading import Thread, Lock
from time import sleep
from urllib import request
from random import random
from queue import Queue
import json
import psutil

optionlines = [v for v in open('options.txt').readlines()]
options = [i.split('=') for i in optionlines]
opt = {i[0].strip():eval(i[1]) for i in options}


site = opt['site']
nprocess = opt['nprocess']
delay = opt['delay']


print(opt)

browsers = []

doneIPlock = Lock()
consoleLock = Lock()
webdriver.DesiredCapabilities.CHROME['chrome.switches'] = ['disable-images']

def ezBrows(type='Chrome'):
	chromeOptions = webdriver.ChromeOptions()
	prefs = {"profile.managed_default_content_settings.images":2}
	chromeOptions.add_experimental_option("prefs",prefs)
	return webdriver.Chrome(chrome_options=chromeOptions)

def tprint(*args):
	global consoleLock
	with consoleLock:
		print(*args)

class IPManager:
	def __init__(self):
		self.name = 'ips.txt'
		self.get = lambda: json.load(open(self.name))
		self.ips = set(self.get())
		#self.ips = set()
		self.doneIP = json.load(open('done.txt'))
		self.available = self.ips - set(self.doneIP.keys())
		self.q = Queue()
		for i in self.available:
			self.q.put(i)

	#def newips(self, ips):
		#oldips = self.available
		#allips = oldips.union(set(ips))
		#json.dump(list(allips), open(self.name, 'w'))
		#return allips
	def gatherip(self):
		while True:
			sleep(10*60)
			browser = ezBrows('Chrome')
			browser.get('http://www.gatherproxy.com')
			# attrs = 'prx', 'type!='Transparent", country, port, tmres, time
			WebDriverWait(browser, 3).until(lambda d: d.find_elements_by_css_selector('.proxy-list'))
			prxips = [i.get_attribute('prx') for i in browser.find_elements_by_css_selector('.proxy')]

			browser.close()
			newips = set(prxips)-self.available
			self.available |= newips
			tprint('Added', newips, 'new ips!')
			for i in newips:
				self.q.put(i)

	def ipthread(self):
		ipth = Thread(target=self.gatherip, daemon=True)
		ipth.start()
	def finishIP(self, ip):
		self.doneIP[ip] = True
		json.dump(self.doneIP, open('done.txt','w'))

ips = IPManager()
ips.ipthread()
print('available IPS =',len(ips.available))        

#elm = browser.find_element_by_id('proxylisttable')
##    ip = []
##    info = ''
##
##    shownEntries = lambda: browser.find_elements_by_id('proxylisttable_info')[0].text
##    def checkNext():
##        info = shownEntries()
##        numbers = [i for i in info.split() if i.isdigit()]
##        print ('numbers is', numbers)
##        return numbers[1] != numbers[2]
##
##    searchSite = 'yahoo' in site or 'google' in site
##    def searchAble(d):
##        elt = [i for i in d if i in ['proxy', 'anonymous', 'transparent']][0]
##        ind = d.index(elt)+1
##        return d[ind] == 'yes'
##    
##    while checkNext():
##        entries = ((i.text, i.text.split()) for i in elm.find_elements_by_css_selector('tr')[2:])
##        
##        if searchSite:
##            ip += [dat[0]+':'+dat[1] for text, dat in entries if searchAble(dat)]
##        else:
##            ip += [dat[0]+':'+dat[1] for text, dat in entries if True]
##
##        browser.find_element_by_id('proxylisttable_next').click()
##        WebDriverWait(browser, 10).until(lambda d: shownEntries() != info)

keywords = lambda: open('keywords.txt', encoding='shiftjis').read().split('\n')

#browsers = [webdriver.PhantomJS() for i in range(nprocess)]
#browseri = 0

def nextbrowser():
	global browseri
	curb = browseri
	browseri = (browseri+1) % len(browsers)
	return browsers[curb]

def loadSite(proxy, browser, n={'bi':0}):
	n['bi'] += 1
	#site = ''.join(['http://',proxy,'/http://yahoo.co.jp'])
	threadn = n['bi']
	while True:
		tprint('trying', site, proxy, 'thread#=', threadn)
		if False:
			webdriver.DesiredCapabilities.PHANTOMJS['proxy']={
			  "httpProxy":proxy,
			  "ftpProxy":proxy,
			  "sslProxy":proxy,
			  "noProxy":None,
			  "proxyType":"MANUAL",
			  "autodetect":False
			}
			webdriver.DesiredCapabilities.PHANTOMJS['phantomjs.page.settings.userAgent'] = 'Mozilla/5.0 (Linux; U; Android 2.3.3; en-us; LG-LU3000 Build/GRI40) AppleWebKit/533.1 (KHTML, like Gecko) Version/4.0 Mobile Safari/533.1';
		browser = webdriver.PhantomJS()
		browsers.append(browser)
		#sleep(delay*random())
		try:
			browser.get(site)
			for keyword in keywords():
				elem = browser.find_element_by_name('p') # Find the search box
				elem.send_keys(keyword + Keys.RETURN)
				WebDriverWait(browser, 3).until(lambda d: d.find_element_by_id('WS2m'))
				tprint('found WS2M', threadn, proxy)
		except Exception as e:
			tprint('Error', threadn, proxy, e)

		browser.quit()
		with doneIPlock:
			global ips
			ips.finishIP(proxy)

def nextThread(browser = None):
	proxy = ips.q.get()
	ips.q.task_done()
	th = Thread(target=lambda:loadSite(proxy, browser))
	th.start()

print('starting processes')

for i in range(nprocess):
 	nextThread()

def closeAll():
	for p in psutil.process_iter():
		 if 'phantom' in i.name().lower(): p.kill()