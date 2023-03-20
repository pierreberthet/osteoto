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



import time
from datetime import datetime

#%%
def run():
    
    #%%
    url = "https://www.ubiclic.com/osteopathie/gresy-sur-aix/paulin-vincent-osteopathe"
    
    
    # Get firefox to run in the background
    options = webdriver.FirefoxOptions()
    options.add_argument('--headless')
    driver = webdriver.Firefox(options=options)

    driver.get(url)
    time.sleep(1)
    
    select = Select(driver.find_element('id', 'owebagdispoprelmotif'))

    select.select_by_visible_text('Consultation M. Paulin Vincent')
    time.sleep(1)
    soup = BeautifulSoup(driver.page_source, 'html5lib')
    
    # FIRST
    ddispo_first = soup.find_all('a', class_='heure_dispo')
    
    
    # NEXT
    button = driver.find_element(by='xpath', value='//*[@id="a_suiv"]').click()
    time.sleep(.5)
    soup = BeautifulSoup(driver.page_source, 'html5lib')
    ddispo_next = soup.find_all('a', class_='heure_dispo')
    # click button
    # driver.execute_script("arguments[0].click();", button)

    
    driver.close()
    #%%
    
    # Find all job listings on the page
    # ddispo = soup.find_all('td', class_='ddispos')

    
    
    # get current job offers
    current = dict()
    for job in job_listings:
        current[job['href']] = {'title': job.find('div', class_='JobList_titleColumn__3oZrC').text, 
                            'business': job.find('div', class_='JobList_secondaryColumnSm__Ac1BT').text,
                            'location': [loc.text for loc in job.find('div', class_='JobList_locationsColumn__xrHQC')],
                            'date': datetime.now().strftime('%d/%m/%Y')}
     
    current = pd.DataFrame.from_dict(current, orient='index')
    current['date'] = pd.to_datetime(current.date, format="%d/%m/%Y")
    
    found_new = False
    # Read the old job listings from a file, if it exists
    if os.path.exists(previous_jobs):
        previous = pd.read_csv(previous_jobs, index_col=0)
        # first print the ones not listed anymore
        for pi in previous.index:
            if pi not in current.index:
                print(f"REMOVED: {previous.loc[pi, 'title']}      ---    {pi}\n")
        # then print the new ones
        for ci in current.index:
            if ci not in previous.index:
                found_new = True
                print(f"!!! NEW !!!:    {current.loc[ci,'title']}   ---   {current.loc[ci,'business']}\
        \n{current.loc[ci,'location']}\n{current.loc[ci,'date']}\
        \n{ci}\n")
        if not found_new:
            print('no new jobs listed')
        
    else: 
        for ci in current.index:
            print(f"!!! NEW !!!:    {current.loc[ci,'title']}   ---   {current.loc[ci,'business']}\
    \n{current.loc[ci,'location']}\n{current.loc[ci,'date']}\
    \n{ci}\n")
    
    # now we save the current as previous
    current.to_csv(previous_jobs)
    
    print(f"Checked at {datetime.now().strftime('%H:%M:%S %d/%m/%Y')}")
    return


#%%
# TODO (dev)
# add cron job
# send email with links when new jobs
