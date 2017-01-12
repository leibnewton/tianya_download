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

def IsValidContent(content): # filter out invalid ones
    if len(content) < 100:  # filter out  too short ones
        return False
    fstSeg = content[:40]
    if u'作者：' in fstSeg and u'回复日期：' in fstSeg:
        return False
    return True

def getContentFromDiv(contents):
    s = "".join(contents).strip()
    return s + (os.linesep + os.linesep) if IsValidContent(s) else ""
    
def getFloorFromDiv(contents):
    s = ''.join(contents).strip()
    parts = s.split('|')
    floor = '-'.join([item.strip() for item in parts if u'楼' in item])
    decostr = '_-_' * 12
    return '%s %s %s%s' % (decostr, floor, decostr, os.linesep)
    
def readHtml(soup,fp,authname):
    pageContent = ""
    item = soup.find(name='div', attrs={'class':'bbs-content clearfix'})
    if item != None:
        pageContent += getContentFromDiv(item.strings)

    items = soup.findAll(name='div', attrs={'class':'atl-item'})
    for item in items:
        userItem = item.find(name='a', attrs={'class':'js-vip-check'})
        if userItem == None or userItem.contents[0] != authname:
            continue
        
        contentItem = item.find(name='div', attrs={'class':'bbs-content'})
        contentPart  = getContentFromDiv(contentItem.strings)
        if contentPart:
            floorItem = item.find(name='div', attrs={'class':'atl-reply'})
            floorPart = getFloorFromDiv(floorItem.strings)
            pageContent += floorPart + contentPart
    
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
        fp.flush()
        print 'PAGE#%d OK' % p
        url = getNextPage(soup)
        if url == 'OVER' :
            break
        p = p + 1
       
    print '*** Article completely fetched. ***'
    fp.close()
    if title:
        newname = title+".txt"
        if os.path.isfile(newname):
            os.remove(newname)
        os.rename(filename, newname)
        filename = newname
    print os.linesep, 'File name is: [%s]' % filename

if __name__ == '__main__':
    getHtml('http://bbs.tianya.cn/post-free-2071655-1.shtml')
