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
import datetime, time, json

class Static:
    def __init__(self, source, rule, parameter):
        self.source = source
        self.rule = rule
        self.parameter = parameter
        titles = ['PR_ID','Opendays','ReportCW','CloseCW','Duplicated','AttachPR','Severity','Top','Release','Comments']
        for eachrule in json.loads(self.rule.rules)['rule']:
            titles.append(eachrule['title'])
        self.result=pd.DataFrame(columns=titles)

    def get_pr_id(self):
        return self.source['Problem ID']

    def search(self, source, areas, which_rule): # source = dataframe
        result = False
        result_list = []
        if isinstance(which_rule, unicode):
            keywords = which_rule.split(',')
            for index, row in source.iterrows():
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
        elif isinstance(which_rule, pd.core.series.Series):
            for index, value in which_rule.iteritems():
                if value is not np.nan:
                    keywords = value.split(',')
                    for area in areas:
                        for kw in keywords:
                            source_area = source[area]
                            if type(source_area) == float or type(source_area) == int:
                                source_area = str(source_area)
                            else:
                                pass
                            if kw in source_area:
                                result = True
                                break
                        if result:
                            break
                    result_list.append(result)
                    result = False

        else:
            result_list = [False] * source.iloc[:,0].size
        return result_list


    def caculate_subpara(self, source, parameter, preresult, subpara, resultindex):
        subparaname = subpara['subparaname']
        expression = subpara['expression']
        parasubvalue = subpara['parasubvalue']
        if expression == '=':
            if json.loads(parameter.parameters).has_key(subpara['subparaname']):
                if parasubvalue == json.loads(parameter.parameters)[subpara['subparaname']]:
                    return True
                else:
                    return False
            elif subpara['subparaname'] in source.columns:
                if parasubvalue == source[subpara['subparaname']][resultindex]:
                    return True
                else:
                    return False
            else:
                if parasubvalue == preresult[subpara['subparaname']][resultindex]:
                    return True
                else:
                    return False
        elif expression == '!=':
            if json.loads(parameter.parameters).has_key(subpara['subparaname']):
                if parasubvalue != json.loads(parameter.parameters)[subpara['subparaname']]:
                    return True
                else:
                    return False
            else:
                if parasubvalue != preresult[subpara['subparaname']][resultindex]:
                    return True
                else:
                    return False
        elif expression == '>':
            if json.loads(parameter.parameters).has_key(subpara['subparaname']):
                if parasubvalue > json.loads(parameter.parameters)[subpara['subparaname']]:
                    return True
                else:
                    return False
            else:
                if parasubvalue > preresult[subpara['subparaname']][resultindex]:
                    return True
                else:
                    return False
        elif expression == 'include':
            print subpara
            if json.loads(parameter.parameters).has_key(subpara['subparaname']):
                if parasubvalue in json.loads(parameter.parameters)[subpara['subparaname']]:
                    return True
                else:
                    return False
            elif subpara['subparaname'] in source.columns:
                if parasubvalue in source[subpara['subparaname']][resultindex]:
                    return True
                else:
                    return False
            else:
                if parasubvalue in preresult[subpara['subparaname']][resultindex]:
                    return True
                else:
                    return False
        elif expression == 'exclude':
            if json.loads(parameter.parameters).has_key(subpara['subparaname']):
                if parasubvalue in json.loads(parameter.parameters)[subpara['subparaname']]:
                    return False
                else:
                    return True
            else:
                if parasubvalue in preresult[subpara['subparaname']][resultindex]:
                    return False
                else:
                    return True
        else:
            return


    def execute_rule(self, rule, parameter, preresult): # rule is each subrule, parameter is parameter from db
        resulttype = [[] for i in range(self.source.iloc[:,0].size)]
        for eachpara in rule['parameters']:
            result=[]
            if eachpara['condition']=='IN':
                if json.loads(parameter.parameters).has_key(eachpara['paraname']):
                    para = json.loads(parameter.parameters)[eachpara['paraname']]  # should add result here as para
                    result = self.search(self.source, eachpara['seachfield'], para)
                else:
                    para = preresult[eachpara['paraname']]
                    result = self.search(json.loads(parameter.parameters), eachpara['seachfield'], para)


                if eachpara['subparameter']:
                    for subpara in eachpara['subparameter']:
                        for i in range(len(result)):
                            if result[i]:

                                if subpara['subcondition'] == 'AND NOT':
                                    if self.caculate_subpara(self.source, parameter, preresult, subpara, i):
                                        result[i] = False
                                    else:
                                        pass
                                elif subpara['subcondition'] == 'AND':
                                    if self.caculate_subpara(self.source, parameter, preresult, subpara, i):
                                        pass
                                    else:
                                        result[i] = False
                                else:
                                    pass

                if eachpara['return'] == 'Self Define':
                    for i in range(len(result)):
                        if result[i] and eachpara['break'] == 'NA':
                            resulttype[i].append(eachpara['return value'])
                        elif result[i] and eachpara['break'] == 'Break' and resulttype[i]==[]:
                            resulttype[i].append(eachpara['return value'])
                        else:
                            pass
                elif eachpara['return'] == 'As Parameter':
                    if (len(para)==1):
                        for i in range(len(result)):
                            if result[i]:
                                resulttype[i].append(para)
                    else:
                        return self.get_mass_kw(eachpara['seachfield'],para.split(','))
                elif eachpara['return'] == 'True':
                    pass
                else:
                    pass

        for index, value in enumerate(resulttype):
            resulttype[index] = ','.join(value)
        return resulttype

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
                bbutypelist.append('Others')
            bbutype.append(','.join(bbutypelist))
            bbutypelist[:]=[]
        return bbutype

    def get_mass_kw(self, fields, keywords):
        rrutype = []
        for i in range(len(self.source)):
            rrutype.append([])
        for rru in keywords:
            rruresult = self.search(self.source, fields,rru)
            for i in range(len(rruresult)):
                if rruresult[i]:
                    rrutype[i].append(rru)
        for i in range(len(self.source)):
            if rrutype[i]:
                rrutype[i] = ','.join(rrutype[i])
            else:
                rrutype[i] = np.nan
        return rrutype   # array

    def get_category(self):
        df = pd.DataFrame()
        cate_list=[]
        category_tag = self.rule.category_tag.split(',')
        for category in category_tag:
            if category == 'UUF':
                df[category] = self.search(['Title','Description'],self.rule.uuf_filter)
            elif category == 'KPI':
                df[category] = self.search(['Title', 'Description'], self.rule.kpi_filter)
            elif category == 'CA':
                df[category] = self.search(['Title', 'Description'], self.rule.ca_filter)
            elif category == 'OAMStab':
                df[category] = self.search(['Title', 'Description'], self.rule.oamstab_filter)
            elif category == 'PETStab':
                df[category] = self.search(['Title', 'Description'], self.rule.pet_filter)
            elif category == 'Func':
                df[category] = self.search(['Title', 'Description'], self.rule.func_filter)


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
                cate_list[i] = 'Func'
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
        return self.search(self.source, ['Top Importance','Title'],'TOP,Top,top')

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
        self.result['ReportCW'],self.result['CloseCW'],self.result['Opendays'] = self.get_cw()
        self.result['Top'] = self.is_top()
        self.result['Release'],self.result['Severity'] = self.get_release_severity()
        self.result['Duplicated'],self.result['AttachPR'] = self.duplicated()
        #self.result['CrossCount'],self.result['TestState'] = self.crosscount_teststat()
        for eachrule in json.loads(self.rule.rules)['rule']:
            self.result[eachrule['title']] = self.execute_rule(eachrule, self.parameter, self.result)
        return self.result
