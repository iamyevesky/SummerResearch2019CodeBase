# -*- coding: utf-8 -*-
"""
Created on Thu Jun 27 21:42:06 2019

@author: yeves
"""

import csv

with open('C:\\Users\\yeves\\Desktop\\eggs.csv', 'w', newline = '') as csvfile:
    headers = ['Time','Voltage(CH1)','Voltage(CH2)']
    writer = csv.DictWriter(csvfile, fieldnames = headers)
    writer.writeheader()
    writer.writerow({'Time' : '0.00','Voltage(CH1)' : '23.45','Voltage(CH2)' : '19.56'})