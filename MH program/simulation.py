# -*- coding: utf-8 -*-
"""
Created on Mon Jul 20 20:55:15 2020

@author: yeves
"""

import pandas as pd
from pathlib import Path

class Simulator(object):
    
    def __init__(self, voltagePath: str, tempPath: str):
        self._voltageDf = pd.read_csv(Path(voltagePath))
        self._tempDf = pd.read_csv(Path(tempPath))
    
    def getOutput(self):
        output = [[] for i in range(len(self._voltageDf.columns.tolist()) - 1)]
        for i in range(1, len(self._voltageDf.columns.tolist())):
            output[i - 1].append((self._voltageDf.iloc[:, 0].values.tolist(),
                                  self._voltageDf.iloc[:, i].values.tolist()))
        temp = self._tempDf.iloc[:, 1].values.tolist()
        time = self._tempDf.iloc[:, 0].values.tolist()
        
        while (len(time) < len(output[0][0][0])):
            time.append(0.0)
            temp.append(0.0)
        
        output.append([(time, temp)])
        return output
        