from bs4 import BeautifulSoup
#import urllib.request
#import urllib.robotparser
import requests
from urllib.request import urlopen
from urllib.parse import urljoin
from concurrent.futures import ThreadPoolExecutor
import lxml
import re

#athletics
#moodle
class Worm:
    #key - current page's url, value - set of all the urls linked on current page
    web = {}
    frontier = []
    #rr is robot rules
    rr = {}

    def __init__(self, start):
        #self.robot_rules(start, (start + "/robots.txt"))
        self.start_crawl(start)

    def unit_test(self):
        soup = BeautifulSoup(urlopen("https://cs.brynmawr.edu/Courses/cs330/spring2020/Lab10.pdf").read(), "lxml")
        for link in soup.find_all('a'):
            link = urljoin(urlwithSlsh, link.get('href'))
            print(link)

    def crawl(self, url):
        try:
            current = urlopen(url).read()
        except Exception as e:
            #print(e)
            return
        soup = BeautifulSoup(current, "lxml")#parse tree

        urls = set()
        urlwSlsh = ""
        if url.endswith("/"):
            urlwSlsh = url
            url = url[:-1]
        else:
            urlwSlsh = url + "/"

        for link in soup.find_all('a'):
            link = urljoin(urlwSlsh, link.get('href'))
            #print(link)
            if re.search("^https://moodle.brynmawr.edu+.*$", link):
            #if re.search("^https://www.brynmawr.edu/academics+.*$", link):
                hashfound = link.find("#")
                if hashfound != -1:
                    if link.find("#!") != -1:
                        continue
                    else:
                        link = link[:hashfound]
                if link.endswith("/"):
                    link = link[:-1]
                urls.add(link)

        self.web[url] = urls

        newlinks = 0
        for u in urls:
            if u not in self.web:
                #check against robot rules
                if u in self.rr:
                    print("robot violation:", u)
                    continue
                #open each "viable" link if possible, discard??? if not
                try:
                    requests.get(u, timeout= 360)#timeout time 6 minutes
                except requests.RequestException:
                    print("failed request get:", u)
                    continue
                self.frontier.insert(0, u)
                newlinks = newlinks + 1
        #print("new links encountered:", newlinks)
        print(newlinks)

    #start is starting url
    def start_crawl(self, start):
        self.pool = ThreadPoolExecutor(max_workers=100)#100
        self.frontier.append(start)

        cntr = 0
        while len(self.frontier) != 0:
        #while cntr != 1500:
            current = self.frontier.pop()
            #print("cntr:", cntr)
            #print(current)
            #print(len(self.frontier))
            self.pool.submit(self.crawl(current))
            cntr = cntr + 1
            #print()
        self.print_links()

    def print_links(self):
        f = open("web_crawler_moodle.txt", "a+")
        for key, value in self.web.items() :
            f.write("%s" % key)
        f.close()



    def robot_rules(self, start, robot_url):
        data = urlopen(robot_url)
        for line in data:
            toks = line.decode().split(' ')
            toks = [str.rstrip() for str in toks]
            while '' in toks:
                toks.remove('')
            if len(toks) == 1:
                disallow = start + toks[0]
                if disallow.endswith("/"):
                    disallow = disallow[:-1]
                self.rr[disallow] = "Oh no"
            elif len(toks) == 0:
                continue
            elif toks[0] == "Disallow:":
                disallow = start + toks[1]
                if disallow.endswith("/"):
                    disallow = disallow[:-1]
                self.rr[start + toks[1]] = "Oh no"
            else:
                continue



if __name__ == "__main__":
    myWorm = Worm("https://moodle.brynmawr.edu")
    #ourWorm = Worm("https://www.brynmawr.edu/academics")
