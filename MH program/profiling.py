# -*- coding: utf-8 -*-
"""
Created on Wed Sep  2 11:27:03 2020

@author: yeves
"""

import tempsScopeAndVNALabviewMHProgramMultiprocessing
import tempsScopeAndVNALabviewMHProgramThreading

main1 = tempsScopeAndVNALabviewMHProgramMultiprocessing.mainForAmbrell
main2 = tempsScopeAndVNALabviewMHProgramThreading.mainForAmbrell

if __name__ == "__main__":
    import timeit
    print(timeit.timeit("main1(10000. 100000, 3, 2, 0, '', '', 0, 0)", setup="from __main__ import test", number=100))
    print(timeit.timeit("main2(10000. 100000, 3, 2, 0, '', '', 0, 0)", setup="from __main__ import test", number=100))