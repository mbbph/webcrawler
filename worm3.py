#Webcrawler for https://brynmawr.edu and its subdomains (moodle, digitalscholarship, techdocs.blogs)

from bs4 import BeautifulSoup
import requests
from urllib.request import urlopen
from urllib.parse import urljoin
from concurrent.futures import ThreadPoolExecutor
import lxml
import re

class Worm:
    web = {} #maps current page url to set of linked urls
    frontier = [] #queue holding urls to be crawled
    rr = {} #robot rules

    def __init__(self, start):
        self.start_crawl(start)

    #unit test to find all links on a single page
    def unit_test(self):
        soup = BeautifulSoup(urlopen("https://cs.brynmawr.edu/Courses/cs330/spring2020/Lab10.pdf").read(), "lxml")
        for link in soup.find_all('a'):
            link = urljoin(urlwithSlsh, link.get('href'))
            print(link)

    #crawls page at url and adds any new links found to queue
    def crawl(self, url):
        try:
            current = urlopen(url).read()
        except Exception as e:
            return
        soup = BeautifulSoup(current, "lxml")

        urls = set() #Stores unique links on a page
        urlwSlsh = ""

        #Normalize links
        if url.endswith("/"):
            urlwSlsh = url
            url = url[:-1]
        else:
            urlwSlsh = url + "/"

        for link in soup.find_all('a'):
            link = urljoin(urlwSlsh, link.get('href'))

            #check and process anchor links
            if re.search("^" + url + ".*$", link):
                hashfound = link.find("#")
                if hashfound != -1:
                    if link.find("#!") != -1:
                        continue
                    else:
                        link = link[:hashfound] #cut off anchor if exists
                if link.endswith("/"):
                    link = link[:-1]
                urls.add(link)

        self.web[url] = urls

        newlinks = 0
        for u in urls:
            #if u hasn't been encountered
            if u not in self.web:
                #check against robot rules
                if u in self.rr:
                    print("robot violation:", u)
                    continue
                #try to open each "viable" link
                try:
                    requests.get(u, timeout= 360) #timeout time 6 minutes
                except requests.RequestException:
                    print("failed to GET: ", u)
                    continue
                self.frontier.insert(0, u)
                newlinks = newlinks + 1
        print(newlinks)

    #start = starting url
    def start_crawl(self, start):
        self.robot_rules("https://www.brynmawr.edu", "https://www.brynmawr.edu/robots.txt")
        self.pool = ThreadPoolExecutor(max_workers=100)
        self.frontier.append(start)
        cntr = 0
        #while queue is not empty, create threads
        while len(self.frontier) != 0:
            current = self.frontier.pop() #get link
            self.pool.submit(self.crawl(current))
            cntr = cntr + 1
        self.print_links()

    #outputs all links found to file
    def print_links(self):
        f = open("web_crawler.txt", "a+")
        for key, value in self.web.items():
            f.write("%s" % key)
        f.close()

    #custom robot rules parser (built in parser wasn't working)
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
    myWorm = Worm("https://www.moodle.brynmawr.edu")
