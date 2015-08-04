from contextlib import suppress
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
import re

optionlines = [v for v in open('options.txt').readlines()]
options = [i.split('=') for i in optionlines]
opt = {i[0].strip():eval(i[1]) for i in options}

site, nprocess, delay = opt['site'], opt['nprocess'], opt['delay']

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
		self.proxysites = open('proxy_sites.txt').read().split('\n')
		for i in self.available:
			self.q.put(i)

	#def newips(self, ips):
		#oldips = self.available
		#allips = oldips.union(set(ips))
		#json.dump(list(allips), open(self.name, 'w'))
		#return allips

	def gatherFrom(self, name, brow=None):
		d = brow or webdriver.PhantomJS()

		d.get(name)
		#if name == 'http://www.proxynova.com/proxy-server-list/elite-proxies/':
		#	#attrs = 'prx', 'type!='Transparent", country, port, tmres, time
		#	with suppress(AttributeError): d.close()
		#	return [i.get_attribute('prx') for i in browser.find_elements_by_css_selector('.proxy')]

		txt = d.page_source
		allips = [ips for (ips, _) in re.findall(r'(([0-9]{1,3}\.){3}[0-9]{1,3}\:[0-9]+)', txt)]
		if allips:
			with suppress(AttributeError): d.close()
			return allips

		for i in d.find_elements_by_css_selector('tr'):
			try:
				ip = re.search(r'([0-9]{1,3}\.){3}[0-9]{1,3}', i.text)
				port = re.search(r'\s([0-9]{2,5})\s', i.text)
				allips.append(ip.group()+':'+port.groups()[0])
			except Exception as e:
				pass

		with suppress(AttributeError): d.close()
		return allips

	def gatherip(self):
		proxyi = 0
		while True:
			# browser = ezBrows('Chrome')
			# browser.get('http://www.gatherproxy.com')
			# # attrs = 'prx', 'type!='Transparent", country, port, tmres, time
			# WebDriverWait(browser, 3).until(lambda d: d.find_elements_by_css_selector('.proxy-list'))
			# prxips = [i.get_attribute('prx') for i in browser.find_elements_by_css_selector('.proxy')]
			#
			# browser.close()
			prxname = self.proxysites[proxyi]
			prxips = self.gatherFrom(prxname)
			proxyi = (proxyi + 1) % len(self.proxysites)
			newips = set(prxips)-self.available
			self.available |= newips
			tprint('Added', newips, 'new proxies from', prxname)
			for i in newips:
				self.q.put(i)
			sleep(30)

	def ipthread(self):
		ipth = Thread(target=self.gatherip)
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

def loadSite(n, browser=None):
	#site = ''.join(['http://',proxy,'/http://yahoo.co.jp'])
	while True:
		proxy = ips.q.get()
		tprint('trying', site, proxy, 'thread#=', n)
		if True:
			webdriver.DesiredCapabilities.PHANTOMJS['proxy']={
			  "httpProxy":proxy,
			  "ftpProxy":proxy,
			  "sslProxy":proxy,
			  "noProxy":None,
			  "proxyType":"MANUAL",
			  "autodetect":False
			}
			#webdriver.DesiredCapabilities.PHANTOMJS['phantomjs.page.settings.userAgent'] = 'Mozilla/5.0 (Linux; U; Android 2.3.3; en-us; LG-LU3000 Build/GRI40) AppleWebKit/533.1 (KHTML, like Gecko) Version/4.0 Mobile Safari/533.1';
		browser = None
		try:
			browser = webdriver.PhantomJS()
			sleep(delay*random())
			browser.get(site)
			for keyword in keywords():
				WebDriverWait(browser, 5).until(lambda d: d.find_element_by_name('p'))
				elem = browser.find_element_by_name('p') # Find the search box
				elem.send_keys(keyword + Keys.RETURN)
				WebDriverWait(browser, 5).until(lambda d: d.find_element_by_id('WS2m'))
				tprint('Thread#',n,proxy,'sucessfully executed search')
		except Exception as e:
			tprint('Thread#', n, proxy, 'is skipped.', e)

		if browser is not None:
			with suppress(AttributeError):
				browser.quit()

		with doneIPlock:
			global ips
			ips.finishIP(proxy)

print('starting processes')

for i in range(nprocess):
	th = Thread(target=lambda:loadSite(i))
	th.start()

# def closeAll():
# 	import psutil
# 	for p in psutil.process_iter():
# 		 if 'phantom' in i.name().lower(): p.kill()