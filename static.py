# -*- coding: utf-8 -*-
"""
:copyright: Nokia Shanghai Bell
:author: Yulin Xian
:contact: yulin.xian@nokia-sbell.com
:maintainer: None
:contact: None
"""
import pandas as pd
import numpy as np
import datetime

class Static:
    def __init__(self, source, rule):
        self.source = source
        self.rule = rule
        titles = ['PR_ID','CustomerImpact','BBU','RRU','Category','Opendays','ReportCW','CloseCW','CrossCount','Duplicated','AttachPR','TestState','Severity','Top','Release']
        self.result=pd.DataFrame(columns=titles)
        # print self.source

    def get_pr_id(self):
        return self.source['Problem ID']

    def search(self, areas, which_rule, title):
        result = False
        result_list = []
        keywords = which_rule.split(',')
        for index, row in self.source.iterrows():
            for area in areas:
                for kw in keywords:
                    row_area = row[area]
                    if type(row_area) == float:
                        row_area = str(row_area)
                    else:
                        pass
                    if kw in row_area:
                        result = True
                        break
                if result:
                    break
            result_list.append(result)
            result = False
        return result_list

    def iscustomerpr(self):
        return self.search(['Title','Description','Additional'],self.rule.customer_keyword_white, 'PR_ID')

    def get_bbu(self):
        bbutype = []
        bbutypelist = []
        r4result = self.search(['Test Subphase','Title','Description'],self.rule.r4bbu, 'BBU')
        r3result = self.search(['Test Subphase','Title','Description'],self.rule.r3bbu, 'BBU')
        for i in range(len(r4result)):
            if r4result[i]:
                bbutypelist.append('Airscale')
            if r3result[i]:
                bbutypelist.append('FSMF')
            if bbutypelist:
                pass
            else:
                bbutypelist.append('OTHERS')
            bbutype.append(','.join(bbutypelist))
            bbutypelist[:]=[]
        return bbutype

    def get_cw(self):
        rpcw_list = []
        clcw_list = []
        for index, row in self.source.iterrows():
            rpcw_list.append(str(row['Reported Date'].year) + '_CW' + str(row['Reported Date'].weekofyear))
            if row['State'] == 'Closed':
                close_day = row['State Changed to Closed']
                if type(close_day) == datetime.datetime:
                    clcw_list.append(str(pd.Timestamp(close_day).year) + '_CW' + str(pd.Timestamp(close_day).weekofyear))
                else:
                    clcw_list.append(
                        str(close_day.year) + '_CW' + str(close_day.weekofyear))
            else:
                clcw_list.append(np.nan)
        return rpcw_list,clcw_list

    def static(self):
        self.result['PR_ID'] = self.get_pr_id()
        self.result['CustomerImpact'] = self.iscustomerpr()
        self.result['BBU'] = self.get_bbu()
        self.result['ReportCW'],self.result['CloseCW'] = self.get_cw()
        return self.result
