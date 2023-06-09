#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Mar 20 09:46:42 2023

@author: pierre
"""

# import requests
import os
import pandas as pd
import sys
# print(sys.version)
# print(sys.path)

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException

import subprocess as s

import time
from datetime import datetime

import smtplib
from email.message import EmailMessage


#%%
# FUNCTIONS

def extract_time(text:str):
    return text[text.find('(')+2 : text.find(':')+3], pd.to_datetime(text[text.find('(')+2 : text.find(',')])



#%%
# PARAMETERS

before = pd.to_datetime('2023/08/15')   # latest
after = pd.to_datetime('2023/07/06')    # earliest

save_dir = '/media/terror/code/projects/osteoto/'
dump = 'notified.txt'
os.chdir(save_dir)

passwd = os.getenv('DSRT_PWD')
email_from = os.getenv('DSRT_EMAIL')
email_to = os.getenv('NOTIF_EMAIL')

version = 'alpha 002'


#%%
def run():
    print(version)
    previous_dump = False
    if os.path.exists(dump):
        previous_dump = True
        with open(dump, "r") as file:
            contents = file.read()
            already_notified = contents.split("\n")

    
    url = "https://www.ubiclic.com/osteopathie/gresy-sur-aix/paulin-vincent-osteopathe"
    
    
    # Get firefox to run in the background
    options = webdriver.FirefoxOptions()
    options.add_argument('--headless')
    driver = webdriver.Firefox(options=options)

    driver.get(url)
    time.sleep(1)
    try:
        select = Select(driver.find_element('id', 'owebagdispoprelmotif'))
    except NoSuchElementException:
        # there is a better way, wiht inbuilt waitfor function
        # from selenium.webdriver.common.by import By
        # from selenium.webdriver.support.ui import WebDriverWait
        # from selenium.webdriver.support import expected_conditions as EC
        
        # WebDriverWait(driver,5).until(EC.visibility_of_element_located((By.CSS_SELECTOR,'[name=firstF]')))
        # driver.switch_to.frame(driver.find_element_by_css_selector('[name=firstF]'))
        # WebDriverWait(driver,5).until(EC.visibility_of_element_located((By.ID,'id'))).send_keys('abc')
        
        driver.get(url)
        time.sleep(8)
        select = Select(driver.find_element('id', 'owebagdispoprelmotif'))

    select.select_by_visible_text('Consultation M. Paulin Vincent')
    time.sleep(1)
    soup = BeautifulSoup(driver.page_source, 'html5lib')
    
    found = False
    found_slots = []
    # check first available
    ddispo_first = soup.find_all('a', class_='heure_dispo')
    for slot in ddispo_first:
        t_time, d_time = extract_time(slot.attrs['onclick'])
        if d_time < before:
            if d_time > after:
                if previous_dump:
                    if t_time not in already_notified:
                        found = True
                        found_slots.append(t_time)
                else:
                    found = True
                    found_slots.append(t_time)
                
    if not found:    
        # try the next available week
        driver.find_element(by='xpath', value='//*[@id="a_suiv"]').click()
        time.sleep(.5)
        soup = BeautifulSoup(driver.page_source, 'html5lib')
        ddispo_next = soup.find_all('a', class_='heure_dispo')
        for slot in ddispo_next:
            t_time, d_time = extract_time(slot.attrs['onclick'])
            if d_time < before:
                if d_time > after:
                    if previous_dump:
                        if t_time not in already_notified:
                            found = True
                            # send notif email
                            found_slots.append(t_time)
                    else: 
                        found = True
                        found_slots.append(t_time)

    driver.close()
    
    if found:
        #send email with list of times
        if os.path.exists(dump):
            found_slots = already_notified + found_slots
        with open(dump, "w") as file:
            file.writelines("\n".join(found_slots))
        
        s.call(['notify-send', 'Available time!!!', 'osteo'])
        # Set up the message
        msg = EmailMessage()
        msg['Subject'] = 'Available time for Paulin'
        msg['From'] = email_from
        msg['To'] = email_to
        msg.set_content(f'Found something!\n    {found_slots}')

        # Connect to the Disroot SMTP server using TLS
        with smtplib.SMTP_SSL('disroot.org', 465) as smtp:
            smtp.login(email_from, passwd)
            smtp.send_message(msg)




        print(f"FOUND SLOTS:\n    {found_slots}")
    else:
        print(f'nothing available between {after} and {before}')
    print(f"Checked at {datetime.now().strftime('%H:%M:%S %d/%m/%Y')}")

    
    #%%



#%%
# TODO (dev)
# add cron job
# send email with links when new slots
# optimize so that 1 run bundles all the available time, and send 1 email, not 1 email for each available time
