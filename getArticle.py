#_*_coding:utf-8-*-
import urllib2
import traceback
import codecs
from BeautifulSoup import BeautifulSoup

def openSoup(url,code):
    page = urllib2.urlopen(url)
    soup = BeautifulSoup(page,fromEncoding=code)#,fromEncoding="gb2312"
    #soup = BeautifulSoup(page,code)
    return soup

def getContentFromDiv(contents):
    s = ""
    for content in contents:
        try:
            s += content
        except:
            pass
    
    s = s.lstrip().rstrip()
    if len(s) < 50:
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
   
def getNextPage(soup,pno):
    nextlink = soup.find(name="a",attrs={"class":"js-keyboard-next"})
    if nextlink != None:
        return "http://bbs.tianya.cn"+nextlink["href"]
    else:
        return 'OVER'
    
def getAuthor(soup):
    div = soup.find(name='div', id="post_head")
    link = div.find(name="a",attrs={"class":"js-vip-check"})
    return link["uname"]

def makeFilename(url):
    return url[url.rindex("/"):][1:].replace("shtml","txt")

def getHtml(url):
    filename = makeFilename(url)
    
    p = 1
    fp = codecs.open(filename,'w','utf-8')
    while True:
        soup = openSoup(url,'utf-8')
        authname = getAuthor(soup)
        readHtml(soup,fp,authname)
        url = getNextPage(soup,p+1)
        if url == 'OVER' :
            break
        print 'PAGE '+str(p)+' OK'
        p = p + 1
       
    print 'It\'s Over'
    fp.close()

if __name__ == '__main__':
    getHtml('http://bbs.tianya.cn/post-worldlook-1219340-1.shtml')
