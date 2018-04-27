#!/usr/bin/python

__author__ = 'Danny Chrastil'
__email__ = 'danny.chrastil@gmail.com'
__description__ = 'Python Requests doesnt handle LinkedIn authentication well. This uses urllib instead'
__version__ = '0.3'

from http import cookiejar

import os
from urllib import request, parse
import sys
import config
from bs4 import BeautifulSoup


def linked_in():
    global opener
    cookie_filename = "cookies.txt"

    # Simulate browser with cookies enabled
    cj = cookiejar.MozillaCookieJar(cookie_filename)
    if os.access(cookie_filename, os.F_OK):
        cj.load()

    # Load Proxy settings
    if len(config.proxylist) > 0:
        # print "[Status] Setting up proxy (%s)" % config.proxylist[0]
        proxy_handler = request.ProxyHandler({'https': config.proxylist[0]})
        opener = request.build_opener(
            proxy_handler,
            request.HTTPRedirectHandler(),
            request.HTTPHandler(debuglevel=0),
            request.HTTPSHandler(debuglevel=0),
            request.HTTPCookieProcessor(cj)
        )
    else:
        opener = request.build_opener(
            request.HTTPRedirectHandler(),
            request.HTTPHandler(debuglevel=0),
            request.HTTPSHandler(debuglevel=0),
            request.HTTPCookieProcessor(cj)
        )

    # Get CSRF Token
    print("[Status] Obtaining a CSRF token")
    html = load_page("https://www.linkedin.com/")
    soup = BeautifulSoup(html, "html.parser")
    csrf = soup.find(id="loginCsrfParam-login")['value']
    # print csrf
    # Authenticate
    login_data = parse.urlencode({
        'session_key': config.linkedin['username'],
        'session_password': config.linkedin['password'],
        'loginCsrfParam': csrf,
    })
    # print "[Status] Authenticating to Linkedin"
    html = load_page("https://www.linkedin.com/uas/login-submit", login_data)
    soup = BeautifulSoup(html, "html.parser")
    try:
        print(cj._cookies['.www.linkedin.com']['/']['li_at'].value)
    except:
        print("error")
    cj.save()
    os.remove(cookie_filename)


def load_page(url, data=None):
    try:
        response = opener.open(url)
    except:
        print("\n[URLError] Your IP may have been temporarily blocked.")

    try:
        if data is not None:
            response = opener.open(url, data)
        else:
            response = opener.open(url)
        # return response.headers.get('Set-Cookie')
        return ''.join(response.readlines())
    except:
        # If URL doesn't load for ANY reason, try again...
        # Quick and dirty solution for 404 returns because of network problems
        # However, this could infinite loop if there's an actual problem
        print(" [Notice] Exception hit")
        sys.exit(0)


linked_in()
