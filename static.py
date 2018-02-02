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

    def search(self, areas, which_rule):
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
        return self.search(['Title','Description','Additional'],self.rule.customer_keyword_white)

    def get_bbu(self):
        bbutype = []
        bbutypelist = []
        r4result = self.search(['Test Subphase','Title','Description'],self.rule.r4bbu)
        r3result = self.search(['Test Subphase','Title','Description'],self.rule.r3bbu)
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

    def get_rru(self):
        rrutype = []
        for i in range(len(self.source)):
            rrutype.append([])
        for rru in self.rule.customer_rru.split(','):
            rruresult = self.search(['Test Subphase','Title','Description'],rru)
            for i in range(len(rruresult)):
                if rruresult[i]:
                    print rru
                    rrutype[i].append(rru)
        for i in range(len(self.source)):
            if rrutype[i]:
                rrutype[i] = ','.join(rrutype[i])
            else:
                rrutype[i] = np.nan
        return rrutype

    def get_category(self):
        df = pd.DataFrame()
        cate_list=[]
        category_tag = self.rule.category_tag.split(',')
        for category in category_tag:
            df[category] = self.search(['Title','Description'],category)
        for index, row in df.iterrows():
            cate_list.append([])
            for category in category_tag:
                if row[category]:
                    cate_list[index] = category
                    break
        for i in range(len(self.source)):
            if cate_list[i]:
                pass
            else:
                cate_list[i] = np.nan
        return cate_list

    def get_cw(self):
        rpcw_list = []
        clcw_list = []
        open_list=[]
        for index, row in self.source.iterrows():
            report_day = row['Reported Date']
            rpcw_list.append(str(row['Reported Date'].year) + '_CW' + str(row['Reported Date'].weekofyear))
            if row['State'] == 'Closed':
                close_day = row['State Changed to Closed']
                if type(close_day) == datetime.datetime:
                    clcw_list.append(str(pd.Timestamp(close_day).year) + '_CW' + str(pd.Timestamp(close_day).weekofyear))
                    open_list.append((close_day - pd.to_datetime(report_day)).days)
                else:
                    clcw_list.append(str(close_day.year) + '_CW' + str(close_day.weekofyear))
                    open_list.append((pd.to_datetime(close_day) - pd.to_datetime(report_day)).days)
            else:
                clcw_list.append(np.nan)
                open_list.append((datetime.datetime.now() - pd.to_datetime(report_day)).days)
        return rpcw_list,clcw_list,open_list

    def is_top(self):
        return self.search(['Top Importance','Title'],'TOP,Top,top')

    def get_release_severity(self):
        release_list = []
        severity_list = []
        for index, row in self.source.iterrows():
            release_list.append(row['Release'])
            severity_list.append(row['Severity'])
        return release_list,severity_list


    def static(self):
        self.result['PR_ID'] = self.get_pr_id()
        self.result['CustomerImpact'] = self.iscustomerpr()
        self.result['BBU'] = self.get_bbu()
        self.result['RRU'] = self.get_rru()
        self.result['Category'] = self.get_category()
        self.result['ReportCW'],self.result['CloseCW'],self.result['Opendays'] = self.get_cw()
        self.result['Top'] = self.is_top()
        self.result['Release'],self.result['Severity'] = self.get_release_severity()
        return self.result
