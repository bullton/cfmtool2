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

class Static:
    def __init__(self, source, rule):
        self.source = source
        self.rule = rule
        titles = ['PR_ID','CustomerImpact','BBU','RRU','Category','Opendays','ReportCW','CloseCW','CrossCount','Duplicated','AttachPR','TestState','Severity','Top','Release']
        self.result=pd.DataFrame(columns=titles)
        print self.rule

    def get_pr_id(self):
        return self.source['Problem ID']

    def search(self, areas, which_rule, title):
        result = False
        result_list=[]
        keywords = which_rule.split(',')
        for index, row in self.source.iterrows():
            for area in areas:
                for kw in keywords:
                    if kw in row[area]:
                        print 'kw=',kw,'row=',row[area]
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
        return self.search(['Title','Description','Additional'],self.rule.customer_keyword_white, 'BBU')

    def static(self):
        self.result['PR_ID']=self.get_pr_id()
        self.result['CustomerImpact']=self.iscustomerpr()
        return self.result
