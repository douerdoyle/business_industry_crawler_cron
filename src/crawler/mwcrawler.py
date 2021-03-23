if __name__ == "__main__":
    import sys
    sys.path.append('../')
import requests, random
from bs4 import BeautifulSoup
from bs4 import Comment
from crawler.util import *

class RequestsCrawler(object):
    def __init__(self, method, url, encode, headers, params=None, proxies=[{}], cookies=[{}], debug=None, timeout=60):
        self.timeout = timeout
        resource = self.request_func(url, encode, headers, params, proxies, cookies, debug)
        self.soup = BeautifulSoup(resource, "lxml")

    def request_func(self, url, encode, headers, params=None, proxies=[{}], cookies=[{}], debug=None):
        response = requests.get(url, headers=headers, params=params, proxies=random.choice(proxies), cookies=random.choice(cookies), timeout=self.timeout)
        response.close()
        response.encoding = encode
        resource = response.text
        return resource

    def get_soup(self):
        return self.soup

    def get_source(self):
        return self.soup.prettify()

    def get_tags(self, mode, *args, **kwargs):
        tag = []
        if mode==0:
            tag = self.soup.find_all(*args, **kwargs)
        elif mode==1:
            tag = [self.soup.find(*args, **kwargs)]
        return tag

    def get_text_by_tag(self, mode, *args, **kwargs):
        text = []
        if mode==0:
            tags = self.soup.find_all(*args, **kwargs)
            text =[get_tag_text(tag) for tag in tags]
        elif mode==1:
            tags = [self.soup.find(*args, **kwargs)]
            text =[get_tag_text(tag) for tag in tags]
        return text

    def get_attr_by_tag(self, mode, target_attr, *args, **kwargs):
        attrs = []
        if mode==0:
            tags = self.soup.find_all(*args, **kwargs)
            attrs =[get_tag_attr(tag, target_attr) for tag in tags]
        elif mode==1:
            tags = [self.soup.find(*args, **kwargs)]
            attrs =[get_tag_attr(tag, target_attr) for tag in tags]
        return attrs

    def get_comments(self):
        comments = []
        comments = self.soup.find_all(string=lambda text: isinstance(text, Comment))
        return comments
