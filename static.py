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
import datetime, time

class Static:
    def __init__(self, source, rule):
        self.source = source
        self.rule = rule
        titles = ['PR_ID','CustomerImpact','BBU','RRU','Category','Opendays','ReportCW','CloseCW','CrossCount','Duplicated','AttachPR','TestState','Severity','Top','Release','Comments']
        self.result=pd.DataFrame(columns=titles)

    def get_pr_id(self):
        return self.source['Problem ID']

    def search(self, areas, which_rule):
        result = False
        result_list = []
        if which_rule:
            keywords = which_rule.split(',')
            for index, row in self.source.iterrows():
                for area in areas:
                    for kw in keywords:
                        row_area = row[area]
                        if type(row_area) == float or type(row_area) == int:
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
        else:
            result_list = [False] * self.source.iloc[:,0].size
        return result_list

    def is_customer_pr(self):
        result = pd.DataFrame()
        result_list = []
        comments_list = []
        result['pr_black'] = self.search(['Problem ID'],self.rule.customer_pronto_black)
        result['pr_white'] = self.search(['Problem ID'],self.rule.customer_pronto_white)
        result['feature_black'] = self.search(['Title','Description','Feature'],self.rule.customer_feature_black)
        result['feature_white'] = self.search(['Title','Description','Feature'],self.rule.customer_feature_white)
        result['kw_black'] = self.search(['Title','Description','Additional'],self.rule.customer_keyword_black)
        result['kw_white'] = self.search(['Title','Description','Additional'],self.rule.customer_keyword_white)
        result['customer_top_fault'] = self.search(['Title','Description'],self.rule.customer_top_fault)
        result['customer_care_func'] = self.search(['Title','Description'],self.rule.customer_care_function)
        for index, row in result.iterrows():
            comments = []
            if row['pr_black'] or row['feature_black'] or row['kw_black']:
                result_list.append(False)
                if row['pr_black']:
                    comments.append('PR black')
                if row['feature_black']:
                    comments.append('Feature black')
                if row['kw_black']:
                    comments.append('KW black')
                comments_list.append(','.join(comments))
            elif row['pr_white'] or row['feature_white'] or row['kw_white'] or row['customer_top_fault'] or row['customer_care_func']:
                result_list.append(True)
                if row['pr_white']:
                    comments.append('PR white')
                if row['feature_white']:
                    comments.append('Feature white')
                if row['kw_white']:
                    comments.append('KW white')
                if row['customer_top_fault']:
                    comments.append('Top fault')
                if row['customer_care_func']:
                    comments.append('Customer care func')
                comments_list.append(','.join(comments))
            else:
                result_list.append(False)
                comments_list.append(np.nan)
        return result_list, comments_list

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

    def to_date_time(self, date_time):
        if date_time and date_time != '< empty >':
            if type(date_time) == datetime.datetime:
                return time.strftime('%Y-%m-%d %H:%M:%S',date_time.timetuple())
            elif type(date_time) == unicode:
                return time.strftime('%Y-%m-%d %H:%M:%S',time.strptime(date_time.encode("utf-8"), '%d.%m.%Y'))
            elif type(date_time) == str:
                return time.strftime('%Y-%m-%d %H:%M:%S',time.strptime(date_time,'%d.%m.%Y'))
            else:
                return str(date_time)
        else:
            return np.nan  #Null


    def get_cw(self):
        rpcw_list = []
        clcw_list = []
        open_list=[]
        for index, row in self.source.iterrows():
            report_day = row['Reported Date']
            close_day = row['State Changed to Closed']
            rd = self.to_date_time(report_day)
            rpcw_list.append(str(pd.Timestamp(self.to_date_time(report_day)).year) + '_CW' + str(pd.Timestamp(self.to_date_time(report_day)).weekofyear))
            if row['State'] == 'Closed' and self.to_date_time(close_day):
                cd = self.to_date_time(close_day)
                if cd:
                    clcw_list.append(str(pd.Timestamp(self.to_date_time(close_day)).year) + '_CW' + str(
                        pd.Timestamp(self.to_date_time(close_day)).weekofyear))
                    open_list.append((pd.to_datetime(cd) - pd.to_datetime(rd)).days)
                else:
                    clcw_list.append(np.nan)
                    open_list.append((datetime.datetime.now() - pd.to_datetime(rd)).days)
            else:
                clcw_list.append(np.nan)
                open_list.append((datetime.datetime.now() - pd.to_datetime(rd)).days)
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

    def duplicated(self):
        result_list = []
        fault_data = self.source['Fault ID']
        result_bin = fault_data.duplicated()
        for index, result in enumerate(result_bin):
        #     print 'duindex=',index
        #     if result:
            result_list.append(np.nan)
        #     else:
        #         fid = self.source['Fault ID'][index]
        #         pid = self.source['Problem ID'][index]
        #         duplicatedfault = []
        #         for index, row in self.source.iterrows():
        #             if row['Fault ID'] == fid and row['Problem ID'] != pid:
        #                 duplicatedfault.append(row['Problem ID'])
        #         if duplicatedfault:
        #             result_list.append(','.join(duplicatedfault))
        #         else:
        #             result_list.append(np.nan)
        return result_bin, result_list

    def crosscount_teststat(self):
        cross_list = []
        teststat_list = []
        for index, row in self.source.iterrows():
            release = row['Release']
            target_release = row['Target Release']
            if 'FL' in target_release and 'TL' in target_release:
                cross_list.append('FT')
                teststat_list_temp = []
                for index, trelease in enumerate(target_release.split(',')):
                    if trelease[0:1] == release[0:1]:
                        teststat = row['Correction State'].split(',')[index]
                        if teststat == "Testing Not Needed" or teststat == "Needless" or teststat == "Tested":
                            teststat_list_temp.append(trelease[0:1])
                if teststat_list_temp:
                    teststat_list.append(''.join(teststat_list_temp))
                else:
                    teststat_list.append(np.nan)
            elif row['Group in Charge'] in self.rule.ftcomsc:
                cross_list.append('FT')
                teststat_list_temp = []
                for index, trelease in enumerate(target_release.split(',')):
                    if trelease[0:1] == release[0:1]:
                        teststat = row['Correction State'].split(',')[index]
                        if teststat == "Testing Not Needed" or teststat == "Needless" or teststat == "Tested":
                            teststat_list_temp.append(trelease[0:1])
                if teststat_list_temp:
                    teststat_list.append(''.join(teststat_list_temp))
                else:
                    teststat_list.append(np.nan)
            elif 'TL' in target_release:
                cross_list.append('T')
                teststat_list_temp = []
                for index, trelease in enumerate(target_release.split(',')):
                    if 'T' in release:
                        teststat = row['Correction State'].split(',')[index]
                        if teststat == "Testing Not Needed" or teststat == "Needless" or teststat == "Tested":
                            teststat_list_temp.append('T')
                if teststat_list_temp:
                    teststat_list.append(''.join(teststat_list_temp))
                else:
                    teststat_list.append(np.nan)
            elif 'FL' in target_release:
                cross_list.append('F')
                teststat_list_temp = []
                for index, trelease in enumerate(target_release.split(',')):
                    if 'F' in release:
                        teststat = row['Correction State'].split(',')[index]
                        if teststat == "Testing Not Needed" or teststat == "Needless" or teststat == "Tested":
                            teststat_list_temp.append('F')
                if teststat_list_temp:
                    teststat_list.append(''.join(teststat_list_temp))
                else:
                    teststat_list.append(np.nan)
            else:
                cross_list.append(np.nan)
                teststat_list.append(np.nan)
        return cross_list, teststat_list

    def static(self):
        self.result['PR_ID'] = self.get_pr_id()
        self.result['CustomerImpact'], self.result['Comments'] = self.is_customer_pr()
        self.result['BBU'] = self.get_bbu()
        self.result['RRU'] = self.get_rru()
        self.result['Category'] = self.get_category()
        self.result['ReportCW'],self.result['CloseCW'],self.result['Opendays'] = self.get_cw()
        self.result['Top'] = self.is_top()
        self.result['Release'],self.result['Severity'] = self.get_release_severity()
        self.result['Duplicated'],self.result['AttachPR'] = self.duplicated()
        self.result['CrossCount'],self.result['TestState'] = self.crosscount_teststat()
        return self.result
