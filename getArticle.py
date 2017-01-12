#_*_coding:utf-8-*-
import os
import urllib2
import traceback
import codecs
from bs4 import BeautifulSoup

def openSoup(url,code):
    page = urllib2.urlopen(url)
    content = page.read()
    print '[%s] fetched, size %d' % (url, len(content))
    content = content.replace('<br>', os.linesep).replace('<BR>', os.linesep)
    soup = BeautifulSoup(content,'lxml',from_encoding=code)
    return soup

def getContentFromDiv(contents):
    s = ""
    for content in contents:
        try:
            s += content
        except:
            pass
    
    s = s.lstrip().rstrip()
    if len(s) < 50: # filter out short ones
        return ""
    else:
        return "    "+s+"\r\n"+"\r\n"

def readHtml(soup,fp,authname):
    pageContent = ""
    item = soup.find(name='div', attrs={'class':'bbs-content clearfix'})
    if item != None:
        pageContent += getContentFromDiv(item.contents)

    items = soup.findAll(name='div', attrs={'class':'atl-item'})
    for item in items:
        userItem = item.find(name='a', attrs={'class':'js-vip-check'})
        if userItem == None or userItem.contents[0] != authname:
            continue

        contentItem = item.find(name='div', attrs={'class':'bbs-content'})
        pageContent += getContentFromDiv(contentItem.contents)
    
    fp.write(pageContent)
   
def getNextPage(soup):
    nextlink = soup.find(name="a",attrs={"class":"js-keyboard-next"})
    if nextlink != None:
        return "http://bbs.tianya.cn"+nextlink["href"]
    else:
        return 'OVER'
    
def getAuthor(soup):
    div = soup.find(name='div', id="post_head")
    link = div.find(name="a",attrs={"class":"js-vip-check"})
    title = div.find(name='h1')
    return (link["uname"], title.text.strip())

def makeFilename(url):
    return url[url.rindex("/")+1:].replace("shtml","txt")

def getHtml(url):
    filename = makeFilename(url)
    
    p = 1
    fp = codecs.open(filename,'w','utf-8')
    title = ''
    while True:
        soup = openSoup(url,'utf-8')
        authname, title = getAuthor(soup)
        readHtml(soup,fp,authname)
        print 'PAGE#%d OK' % p
        url = getNextPage(soup)
        if url == 'OVER' :
            break
        p = p + 1
       
    print '*** Article completely fetched. ***'
    fp.close()
    if title: os.rename(filename, title+".txt")

if __name__ == '__main__':
    getHtml('http://bbs.tianya.cn/post-free-2071655-1.shtml')
