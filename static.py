# -*- coding: utf-8 -*-
"""
:copyright: Nokia Shanghai Bell
:author: Yulin Xian
:contact: yulin.xian@nokia-sbell.com
:maintainer: None
:contact: None
"""


class Static:
    def __init__(self, source, rule):
        self.source = source
        self.rule = rule

    def get_pr_id(self):
        pr_id=[]
        for row in self.source:
            pr_id.append(row['Problem ID'])
        return pr_id

    def search(self, areas, which_rule):
        result = False
        result_list = []
        keywords = which_rule.split(',')
        for row in self.source:
            for area in areas:
                for kw in keywords:
                    if kw in row[area]:
                        result = True
                        break
                if result:
                    break
            result_list.append(result)
            result = False
        return result_list

    def iscustomerpr(self):
        return self.search(['Title','Description','Additional'],self.rule.customer_keyword_white)
