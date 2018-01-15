#!/usr/bin/python
# -*- coding: UTF-8 -*-

from PIL import Image
from shlex import split, quote
from unicodedata import normalize
from email import encoders
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from config import KINDLE_EMAIL,GMAIL_EMAIL,SMTP_HOST_NAME,SMTP_PORT,GMAIL_PASSWORD,MERCURY_API_KEY
from sys import exit
import smtplib
import os
import requests
import re
import subprocess
from bs4 import BeautifulSoup

directory = os.path.abspath(os.path.expanduser(os.curdir))


def parse_url(url):
    try:
        os.makedirs(directory, exist_ok=True)
    except OSError as e:
        exit()

    parse_url = 'https://mercury.postlight.com/parser?url=' + url
    data = requests.get(parse_url, headers={
                        'x-api-key': MERCURY_API_KEY}).json()
    if data is None:
        exit()
    return convert_html(data, directory)


def convert_html(data, directory):
    command = ''
    try:
        title = normalize('NFKD', data['title'])
    except:
        title = 'webpage'
    filename = os.path.join(directory, title.replace(" ", "_"))
    html_file = filename + ".html"
    mobi_file = filename + ".mobi"
    img_file = filename + ".png"

    command += ' --title {} '.format(quote(title))

    if data['lead_image_url'] is not None:

        img_url = data['lead_image_url']
        try:
            Image.open(requests.get(img_url, stream=True).raw).resize((1200, 1600),).save('{}'.format(img_file))
            command += ' --cover {} '.format(img_file)
        except:
            pass

    if data['excerpt'] is not None:
        excerpt = normalize('NFKD', data['excerpt'])
        command += ' --comments {} --output-profile kindle'.format(
            quote(excerpt))

    with open(os.path.join(directory, html_file), 'w') as template:
        clean_html = normalize('NFKD', data['content'])
        template.write(clean_html)

    try:
        build_line = 'ebook-convert ' + html_file + " " + mobi_file + command
        args = split(build_line)
        subprocess.call(args)
    except:
        exit()
    os.remove(html_file)
    os.remove(img_file)
    return send_email(mobi_file)

def setup_email(SMTP_PORT):
    try:
        smtpObj = smtplib.SMTP(SMTP_HOST_NAME, SMTP_PORT)
        if smtpObj.ehlo()[0]==250:
            try:
                smtpObj.starttls()
                smtpObj.login(GMAIL_EMAIL, GMAIL_PASSWORD)
                return smtpObj

            except smtplib.SMTPAuthenticationError:
                exit()
    except:
        exit()

def send_email(mobi_file):
    smtpObj = setup_email(SMTP_PORT)
    msg = MIMEMultipart()
    msg['From'] = GMAIL_EMAIL
    msg['To'] = KINDLE_EMAIL
    msg['Subject'] = "Convert"
    body = ""
    msg.attach(MIMEText(body, 'plain'))
    attachment = open(mobi_file, "rb")
    part = MIMEBase('application', 'octet-stream')
    part.set_payload((attachment).read())
    encoders.encode_base64(part)
    part.add_header('Content-Disposition', 'attachment', filename=mobi_file)
    msg.attach(part)
    text = msg.as_string()
    os.remove(mobi_file)

    try:
        smtpObj.sendmail(GMAIL_EMAIL, KINDLE_EMAIL, text)
    except:
        exit()
    return smtpObj.quit()

###########################################################

html_doc=requests.get('http://haber.sol.org.tr/anasayfa').text
regex = r"\<a href\=\"\/yazarlar\/([^\"]*)"
pages = re.findall(regex, html_doc)

for slink in pages:
    log_file = open(directory+'/newslogs.txt', 'r')
    old_news = log_file.readlines()

    link='http://haber.sol.org.tr/yazarlar/'+slink
    print (link)

    if link+'\n' in old_news:
        print ('old')
    else:
        print ('new')
        parse_url(link)
        log_file = open(directory + '/newslogs.txt', 'a')
        log_file.write(link+'\n')
