from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.proxy import *
from selenium.common.exceptions import NoSuchElementException

from urllib import request

from time import sleep
from random import *
import json

#browser = webdriver.Chrome()
#browser.get('http://www.us-proxy.org/')
#elm = browser.find_element_by_id('proxylisttable')

optionlines = [v for v in open('options.txt').readlines()]
options = [i.split('=') for i in optionlines]
opt = {i[0].strip():eval(i[1]) for i in options}
print(opt)

def getips():
    return eval(open('ips.txt').read())
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
##
##    with open('ips.txt', 'w') as f:
##        f.write(repr(ip))

delay = opt['delay']

keywords = open('keywords.txt').read().split('\n')
doneIP = json.load(open('done.txt'))
    
for proxy in getips():
    if proxy in doneIP:  continue

    PROXY = proxy
    
    webdriver.DesiredCapabilities.CHROME['proxy']={
        "httpProxy":PROXY,
        "ftpProxy":PROXY,
        "sslProxy":PROXY,
        "noProxy":None,
        "proxyType":"MANUAL",
        "autodetect":False
    }
    try:
        browser = webdriver.Chrome()
        site = 'http://yahoo.co.jp'
        browser.get(site)
        
        for keyword in keywords:
                elem = browser.find_element_by_name('p') # Find the search box
                elem.send_keys(keyword + Keys.RETURN)
                WebDriverWait(browser, 10).until(lambda d: d.find_elements_by_id('results'))
                
        browser.quit()
        sleep(delay*random())
        
    except Exception as e:
        print(e)
        browser.quit()
    doneIP[proxy] = True
    json.dump(doneIP, open('done.txt','w'))
        
