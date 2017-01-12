#_*_coding:utf-8-*-
import os, sys
import urllib2
import traceback
import codecs
from bs4 import BeautifulSoup

class TianyaFetcher(object):
    def __init__(self):
        self.article_authname = ''
        self.article_title = ''
        
    def openSoup(self, url,code):
        print 'fetching [%s] ...' % url,
        sys.stdout.flush()
        page = urllib2.urlopen(url)
        content = page.read()
        print ' success, size %d' % len(content)
        for newline in ['<br>\n', '<br>\r\n', '<br>', '<BR>']:
            content = content.replace(newline, os.linesep)
        soup = BeautifulSoup(content,'lxml',from_encoding=code)
        return soup

    def IsValidContent(self, content): # filter out invalid ones
        if len(content) < 400:  # filter out  too short ones
            return False
        fstSeg = content[:40]
        if u'作者：' in fstSeg or u'日期：' in fstSeg:
            return False
        fstSeg = fstSeg.lstrip()
        if fstSeg[0] == u'@':
            return False
        return True

    def getContentFromDiv(self, contents):
        s = "".join(contents).strip()
        return s + (os.linesep + os.linesep) if self.IsValidContent(s) else ""
        
    def getFloorFromDiv(self, contents):
        s = ''.join(contents).strip()
        parts = s.split('|')
        floor = '-'.join([item.strip() for item in parts if u'楼' in item])
        decostr = '_-_' * 12
        return '%s %s %s%s' % (decostr, floor, decostr, os.linesep)
        
    def parseHtml(self, soup):
        pageContent = ""
        item = soup.find(name='div', attrs={'class':'bbs-content clearfix'})
        if item != None:
            pageContent += self.getContentFromDiv(item.strings)

        items = soup.findAll(name='div', attrs={'class':'atl-item'})
        for item in items:
            userItem = item.find(name='a', attrs={'class':'js-vip-check'})
            if userItem == None or userItem.contents[0] != self.article_authname:
                continue
            
            contentItem = item.find(name='div', attrs={'class':'bbs-content'})
            contentPart  = self.getContentFromDiv(contentItem.strings)
            if contentPart:
                floorItem = item.find(name='div', attrs={'class':'atl-reply'})
                floorPart = self.getFloorFromDiv(floorItem.strings)
                pageContent += floorPart + contentPart
        return pageContent
        
    def getPageIndex(self, url):
        i1 = url.rindex('-')
        i2 = url.rindex('.')
        return url[i1+1:i2]

    def getPage(self, url, fp):
        soup = None
        while not soup:
            try:
                soup = self.openSoup(url,'utf-8')
            except Exception, ex:
                print ' failed for "%s", retry' % ex.args
        if not self.article_authname:
            self.article_authname, self.article_title = self.getAuthor(soup)
        pageContent = self.parseHtml(soup)
        if pageContent:
            p = self.getPageIndex(url)
            fp.write(self.getPageLine(p))
            fp.write(pageContent)
            fp.flush()
            print '    -> Page#%s Finished.' % p
        return self.getNextPage(soup)
       
    def getNextPage(self, soup):
        nextlink = soup.find(name="a",attrs={"class":"js-keyboard-next"})
        return "http://bbs.tianya.cn"+nextlink["href"] if nextlink else ''
        
    def getAuthor(self, soup):
        div = soup.find(name='div', id="post_head")
        link = div.find(name="a",attrs={"class":"js-vip-check"})
        title = div.find(name='h1')
        return (link["uname"], title.text.strip())

    def makeFilename(self, url):
        return url[url.rindex("/")+1:].replace("shtml","txt")

    def getPageLine(self, page):
        decostr = '===' * 8
        return u'%s 第 %s 页 %s%s' % (decostr, page, decostr, os.linesep)
        
    def getHtml(self, url, count = sys.maxint):
        filename = self.makeFilename(url)
        p = 1
        fp = codecs.open(filename,'w','utf-8')
        while url and p < count:
            url = self.getPage(url, fp)
            p = p + 1

        print '*** Article completely fetched. ***'
        fp.close()
        if self.article_title:
            newname = self.article_title+".txt"
            if os.path.isfile(newname):
                os.remove(newname)
            os.rename(filename, newname)
            filename = newname
        print os.linesep, 'File name is: [%s]' % filename

if __name__ == '__main__':
    tianya = TianyaFetcher()
    tianya.getHtml('http://bbs.tianya.cn/post-free-2071655-1.shtml' if len(sys.argv) < 2 else sys.argv[1])
