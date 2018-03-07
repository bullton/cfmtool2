# -*- coding: utf-8 -*

from flask import Flask,render_template,url_for,request,redirect,session,flash, send_file, send_from_directory
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash,check_password_hash
import config
from models import User, Source, Rule, Static_Data
from static import Static
from exts import db
from decorators import login_require
from sqlalchemy import desc
from collections import OrderedDict
import os, datetime, platform, re, xlrd, time, random
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from _mysql import DataError
import _mysql_exceptions

app = Flask(__name__)
app.config.from_object(config)
# fileupload config
UPLOAD_FOLDER='uploadfolder'
EXPORT_FOLDER='export'
FIGURE_FOLDER='static/figure'
ALLOWED_EXTENSIONS = set(['xls', 'xlsx'])
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['EXPORT_FOLDER'] = EXPORT_FOLDER
app.config['FIGURE_FOLDER'] = FIGURE_FOLDER
basedir = os.path.abspath(os.path.dirname(__file__))
db.init_app(app)


def allowed_file(filename):                                  
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


def static_bbu_severity(df_data, xdd, iscustomer):
    df_bbu_severity = pd.DataFrame(columns=['FSMF', 'Airscale', 'Others', 'Subtotal', 'OpenDays'],index=['A - Critical', 'B - Major', 'C - Minor'])
    for index, row in df_bbu_severity.iterrows():
        subtotal = 0
        for col in df_bbu_severity.columns:
            if col in ['FSMF','Airscale','Others']:
                if xdd == 'FDD':
                    if iscustomer:
                        count = df_data[(df_data['CustomerImpact'] == True) & (df_data['BBU'].isin(col.split())) & (df_data['Severity'] == index) & (df_data['CrossCount'].isin(['F','FT']))].count()['CustomerImpact']
                        df_bbu_severity[col][index] = count
                    else:
                        count = \
                            df_data[(df_data['BBU'].isin(col.split())) & (df_data['Severity'] == index) & (df_data['CrossCount'].isin(['F','FT']))].count()['CustomerImpact']
                        df_bbu_severity[col][index] = count
                else:
                    if iscustomer:
                        count = \
                            df_data[(df_data['CustomerImpact'] == True) & (df_data['BBU'].isin(col.split())) & (df_data['Severity'] == index) & (df_data['CrossCount'].isin(['T','FT']))].count()['CustomerImpact']
                        df_bbu_severity[col][index] = count
                    else:
                        count = \
                            df_data[(df_data['BBU'].isin(col.split())) & (df_data['Severity'] == index) & (df_data['CrossCount'].isin(['T','FT']))].count()['CustomerImpact']
                        df_bbu_severity[col][index] = count
        if xdd == 'FDD':
            if iscustomer:
                sum_opendays_severity = df_data[(df_data['CustomerImpact'] == True) & (df_data['Severity'] == index)].sum()['Opendays']
                subtotal = df_data[(df_data['CustomerImpact'] == True) & (df_data['Severity'] == index) & (df_data['CrossCount'].isin(['F','FT']))].count()['CustomerImpact']
            else:
                sum_opendays_severity = df_data[(df_data['Severity'] == index)].sum()['Opendays']
                subtotal = df_data[(df_data['Severity'] == index) & (df_data['CrossCount'].isin(['F','FT']))].count()['CustomerImpact']
        else:
            if iscustomer:
                sum_opendays_severity = df_data[(df_data['CustomerImpact'] == True) & (df_data['Severity'] == index)].sum()['Opendays']
                subtotal = df_data[(df_data['CustomerImpact'] == True) & (df_data['Severity'] == index) & (df_data['CrossCount'].isin(['T','FT']))].count()['CustomerImpact']
            else:
                sum_opendays_severity = df_data[(df_data['Severity'] == index)].sum()['Opendays']
                subtotal = df_data[(df_data['Severity'] == index) & (df_data['CrossCount'].isin(['T','FT']))].count()['CustomerImpact']
        df_bbu_severity['Subtotal'][index] = subtotal
        df_bbu_severity['OpenDays'][index] = sum_opendays_severity / subtotal
    return df_bbu_severity


def static_cat(df_data, xdd, use_rule, iscustomer):
    cat_list = use_rule.category_tag.split(',')
    df_static_cat = pd.DataFrame(columns=cat_list,index=[''])
    for col in df_static_cat.columns:
        if xdd == 'FDD' and iscustomer:
            count = \
                df_data[(df_data['CustomerImpact'] == True) & (df_data['CrossCount'].isin(['F','FT'])) & (df_data['Category']==col)].count()['CustomerImpact']
            df_static_cat[col][''] = count
        elif xdd == 'FDD' and not iscustomer:
            count = \
                df_data[(df_data['CrossCount'].isin(['F','FT'])) & (df_data['Category']==col)].count()['CustomerImpact']
            df_static_cat[col][''] = count
        elif xdd == 'TDD' and iscustomer:
            count = \
                df_data[(df_data['CustomerImpact'] == True) & (df_data['CrossCount'].isin(['T','FT'])) & (df_data['Category']==col)].count()['CustomerImpact']
            df_static_cat[col][''] = count
        else:
            count = \
                df_data[(df_data['CrossCount'].isin(['T','FT'])) & (df_data['Category']==col)].count()['CustomerImpact']
            df_static_cat[col][''] = count
    return df_static_cat


def static_bar_severity(data, title):
    ind = np.arange(3)
    width = 0.3
    FSMF = data['FSMF']
    Airscale = data['Airscale']
    Others = data['Others']
    Sum = data['Subtotal']
    print max(Sum)

    figure_path = os.path.join(basedir, app.config['FIGURE_FOLDER'])
    unix_time = int(time.time())
    filename = str(unix_time) + str(random.randint(1000,9999)) + '.png'
    fullpath = os.path.join(figure_path, filename)

    p1 = plt.bar(ind, FSMF, width, color='r')
    p2 = plt.bar(ind, Airscale, width, color='b', bottom=FSMF)
    cum = list(map(sum, zip(list(FSMF), list(Airscale))))
    p3 = plt.bar(ind, Others, width, color='g', bottom=cum)

    plt.ylabel('Pronto QTY')
    plt.title(title)
    plt.xticks(ind + width / 2., ('Critical', 'Major', 'Minor'))
    plt.yticks(np.arange(0, max(Sum), 100))
    plt.legend((p1[0], p2[0], p3[0]), ('FSMF', 'Airscale', 'Others'), loc=2, frameon='false')
    plt.tick_params(top='off', bottom='off', right='off')
    plt.grid(axis='y', linestyle='-')
    plt.savefig(fullpath)
    plt.close('all')
    return filename


rulekey1 = OrderedDict([('customer_feature_white','customer_feature_white'),('customer_top_fault','customer_top_fault'),('customer_bbu','customer_bbu'),('customer_keyword_white','customer_keyword_white'),('category_tag','category_tag'),('uuf_filter','uuf_filter'),('kpi_filter','kpi_filter'),('ca_filter','ca_filter'),('oamstab_filter','oamstab_filter'),('pet_filter','pet_filter'),('func_filter','func_filter'),('customer_pronto_white','customer_pronto_white'),('r4bbu','r4bbu')])
rulekey2 = OrderedDict([('customer_feature_black','customer_feature_black'),('customer_care_function','customer_care_function'),('customer_rru','customer_rru'),('customer_keyword_black','customer_keyword_black'),('category_search_field','category_search_field'),('uuf_exclusion','uuf_exclusion'),('kpi_exclusion','kpi_exclusion'),('ca_exclusion','ca_exclusion'),('oamstab_exclusion','oamstab_exclusion'),('pet_exclusion','pet_exclusion'),('func_exclusion','func_exclusion'),('customer_pronto_black','customer_pronto_black'),('r3bbu','r3bbu'),('ftcomsc','ftcomsc')])


@app.route('/')
@app.route('/index/')
@login_require
def index():
    user_id = session.get('user_id')
    sourcefilelist = Source.query.filter(Source.owner_id == user_id).order_by(desc(Source.id)).all()
    userrulelist = Rule.query.filter(Rule.owner_id == user_id).order_by(desc(Rule.id)).all()
    return render_template('index.html', sources = sourcefilelist, userrules=userrulelist)


@app.route('/data/',methods=['GET','POST'])
@login_require
def data():
    if request.method == 'GET':
        pass
    else:
        user_id = session.get('user_id')
        source_path = request.form.get('selectsource')
        select_rule = request.form.get('selectrule')
        data = pd.read_excel(source_path)
        if 'Unnamed' in ','.join(data.columns):
            data = pd.read_excel(source_path, skiprows = range(0, 6))
        # titles = ['PR_ID','CustomerImpact','BBU','RRU','Category','Opendays','ReportCW','CloseCW','CrossCount','Duplicated','AttachPR','TestState','Severity','Top','Release','Comments']
        stat = pd.DataFrame()
        rule = Rule.query.filter(Rule.id == select_rule).first()
        static = Static(data, rule)
        stat = static.static()
        stat_orderdict = stat.to_dict(into=OrderedDict)
        static_data = Static_Data(data=str(stat_orderdict))
        user = User.query.filter(User.id == user_id).first()
        static_data.owner = user
        static_data.use_rule = rule
        db.session.add(static_data)
        db.session.commit()
        # qqqqq = Static_Data.query.order_by(desc(Static_Data.id)).first()
        # ccc = pd.DataFrame(eval(qqqqq.data.replace('nan','np.nan')))
        return render_template('data.html',stat=stat)


@app.route('/statics/')
@login_require
def statics():
    user_id = session.get('user_id')
    static_data = Static_Data.query.filter(Static_Data.owner_id == user_id).order_by(desc(Static_Data.id)).first()
    use_rule = Rule.query.filter(Rule.id == static_data.use_rule_id).first()
    data = pd.DataFrame(eval(static_data.data.replace('nan','np.nan')))
    # df_fdd_customer_bbu = pd.DataFrame(columns=['FSMF','Airscale','Others','Subtotal','OpenDays'],index=['A - Critical','B - Major','C - Minor'])
    df_tdd_customer_bbu = pd.DataFrame(columns=['UUF','KPI','CA','OAM Stab','PET Stab','Func'])
    df_fdd_bbu = pd.DataFrame()
    df_tdd_bbu = pd.DataFrame()
    df_top_pr = pd.DataFrame()
    df_top_blocker = pd.DataFrame()
    df_dedicate_finding = pd.DataFrame()
    stats=[]
    stats_title=[]
    stats_figure=[]
    # FDD cBBU
    #for index, row in df_fdd_customer_bbu.iterrows():
    #    subtotal = 0
    #    for col in df_fdd_customer_bbu.columns:
    #        if col in ['FSMF','Airscale','Others']:
    #            count = \
    #                data[(data['CustomerImpact']==True) & (data['BBU'].isin(col.split())) & (data['Severity']==index) & (data['CrossCount'].isin(['F']))].count()['CustomerImpact']
    #            df_fdd_customer_bbu[col][index] = count
    #    sum_opendays_severity = data[(data['CustomerImpact'] == True) & (data['Severity'] == index)].sum()['Opendays']
    #    subtotal = data[(data['CustomerImpact'] == True) & (data['Severity'] == index)].count()['CustomerImpact']
    #    df_fdd_customer_bbu['Subtotal'][index] = subtotal
    #    df_fdd_customer_bbu['OpenDays'][index] = sum_opendays_severity / subtotal
    #    print index, sum_opendays_severity, subtotal
    stats.append(static_bbu_severity(data,'FDD',True))
    stats_figure.append(static_bar_severity(stats[0], 'FDD - ' + use_rule.customer))
    time.sleep(2)
    stats.append(static_bbu_severity(data, 'TDD', True))
    stats_figure.append(static_bar_severity(stats[1], 'TDD - ' + use_rule.customer))
    stats.append(static_cat(data,'FDD',use_rule,True))
    stats.append(static_cat(data, 'TDD', use_rule, True))

    stats.append(static_bbu_severity(data, 'FDD', False))
    stats_figure.append(static_bar_severity(stats[4], 'FDD - ' + use_rule.release))
    stats.append(static_bbu_severity(data, 'TDD', False))
    stats_figure.append(static_bar_severity(stats[5], 'TDD - ' + use_rule.release))
    stats.append(static_cat(data, 'FDD', use_rule, False))
    stats.append(static_cat(data, 'TDD', use_rule, False))

    stats_title.append('FDD - ' + use_rule.customer)
    stats_title.append('TDD - ' + use_rule.customer)
    stats_title.append('FDD - Category - ' + use_rule.customer)
    stats_title.append('TDD - Category - ' + use_rule.customer)
    stats_title.append('FDD - ' + use_rule.release)
    stats_title.append('TDD - ' + use_rule.release)
    stats_title.append('FDD - Category - ' + use_rule.release)
    stats_title.append('TDD - Category - ' + use_rule.release)
    print stats_figure
    return render_template('statics.html',stats=stats,enumerate=enumerate,stats_title=stats_title,stats_figure=stats_figure)


@app.route('/export/')
@login_require
def export():
    user_id = session.get('user_id')
    static_data = Static_Data.query.filter(Static_Data.owner_id == user_id).order_by(desc(Static_Data.id)).first()
    data = pd.DataFrame(eval(static_data.data.replace('nan', 'np.nan')))
    export_path = os.path.join(basedir, app.config['EXPORT_FOLDER'])
    unix_time = int(time.time())
    filename = str(unix_time) + '.xls'
    fullpath = os.path.join(export_path,filename)
    data.to_excel(fullpath)
    return send_from_directory(export_path, filename, as_attachment=True)

@app.route('/trend/')
@login_require
def trend():
    user_id = session.get('user_id')
    static_data = Static_Data.query.filter(Static_Data.owner_id == user_id).order_by(desc(Static_Data.id)).first()
    data = pd.DataFrame(eval(static_data.data.replace('nan','np.nan')))
    return render_template('trend.html',stat=data)


@app.route('/newrule/',methods=['GET','POST'])
@login_require
def newrule():
    user_id = session.get('user_id')
    if request.method == 'GET':
        userrulelist = Rule.query.order_by(desc(Rule.id)).all()
        return render_template('newrule.html', key1 = rulekey1, key2 = rulekey2, userrules = userrulelist)
    else:
        rulename = request.form.get('rulename')
        customer = request.form.get('customer')
        release = request.form.get('release')
        customer_feature_white = request.form.get('customer_feature_white')
        customer_feature_black = request.form.get('customer_feature_black')
        customer_top_fault = request.form.get('customer_top_fault')
        customer_care_function = request.form.get('customer_care_function')
        customer_bbu = request.form.get('customer_bbu')
        customer_rru = request.form.get('customer_rru')
        customer_keyword_white = request.form.get('customer_keyword_white')
        customer_keyword_black = request.form.get('customer_keyword_black')
        category_tag = request.form.get('category_tag')
        category_search_field = request.form.get('category_search_field')
        uuf_filter = request.form.get('uuf_filter')
        uuf_exclusion = request.form.get('uuf_exclusion')
        kpi_filter = request.form.get('kpi_filter')
        kpi_exclusion = request.form.get('kpi_exclusion')
        ca_filter = request.form.get('ca_filter')
        ca_exclusion = request.form.get('ca_exclusion')
        oamstab_filter = request.form.get('oamstab_filter')
        oamstab_exclusion = request.form.get('oamstab_exclusion')
        pet_filter = request.form.get('pet_filter')
        pet_exclusion = request.form.get('pet_exclusion')
        func_filter = request.form.get('func_filter')
        func_exclusion = request.form.get('func_exclusion')
        customer_pronto_white = request.form.get('customer_pronto_white')
        customer_pronto_black = request.form.get('customer_pronto_black')
        r4bbu = request.form.get('r4bbu')
        r3bbu = request.form.get('r3bbu')
        ftcomsc = request.form.get('func_exclusion')

        rule = Rule.query.filter(Rule.rulename == rulename).first()
        if rule:
            flash('Rule is already exist, please try another rule name!','danger')
            return redirect(url_for('newrule'))
        else:
            rule = Rule(rulename=rulename,customer=customer,release=release,customer_feature_white=customer_feature_white, customer_feature_black=customer_feature_black, customer_top_fault=customer_top_fault, customer_care_function=customer_care_function, uuf_filter=uuf_filter, uuf_exclusion=uuf_exclusion, kpi_filter=kpi_filter, kpi_exclusion=kpi_exclusion, ca_filter=ca_filter, ca_exclusion=ca_exclusion, oamstab_filter=oamstab_filter, oamstab_exclusion=oamstab_exclusion, pet_filter=pet_filter, pet_exclusion=pet_exclusion, func_filter=func_filter, func_exclusion=func_exclusion, category_search_field=category_search_field, category_tag=category_tag, customer_rru=customer_rru, customer_bbu=customer_bbu, customer_keyword_white=customer_keyword_white, customer_keyword_black=customer_keyword_black, customer_pronto_white=customer_pronto_white, customer_pronto_black=customer_pronto_black, r4bbu=r4bbu, r3bbu=r3bbu, ftcomsc=ftcomsc)
            user = User.query.filter(User.id == user_id).first()
            rule.owner = user
            db.session.add(rule)
            db.session.commit()
            flash('Rule is already sucessfully added!', 'success')
            return redirect(url_for('newrule'))


@app.route('/editrule/',methods=['GET','POST'])
@login_require
def editrule():
    user_id = session.get('user_id')
    rule = {'rulename':'rulename','release':'release','customer':'customer'}
    userrulelist = Rule.query.filter(Rule.owner_id == user_id).order_by(desc(Rule.id)).all()
    if request.method == 'GET':
        return render_template('editrule.html', key1 = rulekey1, key2 = rulekey2, userrules = userrulelist)
    else:
        rulename = request.form.get('rulename')
        customer = request.form.get('customer')
        release = request.form.get('release')
        customer_feature_white = request.form.get('customer_feature_white')
        customer_feature_black = request.form.get('customer_feature_black')
        customer_top_fault = request.form.get('customer_top_fault')
        customer_care_function = request.form.get('customer_care_function')
        customer_bbu = request.form.get('customer_bbu')
        customer_rru = request.form.get('customer_rru')
        customer_keyword_white = request.form.get('customer_keyword_white')
        customer_keyword_black = request.form.get('customer_keyword_black')
        category_tag = request.form.get('category_tag')
        category_search_field = request.form.get('category_search_field')
        uuf_filter = request.form.get('uuf_filter').decode("utf-8")
        uuf_exclusion = request.form.get('uuf_exclusion')
        kpi_filter = request.form.get('kpi_filter')
        kpi_exclusion = request.form.get('kpi_exclusion')
        ca_filter = request.form.get('ca_filter')
        ca_exclusion = request.form.get('ca_exclusion')
        oamstab_filter = request.form.get('oamstab_filter')
        oamstab_exclusion = request.form.get('oamstab_exclusion')
        pet_filter = request.form.get('pet_filter')
        pet_exclusion = request.form.get('pet_exclusion')
        func_filter = request.form.get('func_filter')
        func_exclusion = request.form.get('func_exclusion')
        customer_pronto_white = request.form.get('customer_pronto_white')
        customer_pronto_black = request.form.get('customer_pronto_black')
        r4bbu = request.form.get('r4bbu')
        r3bbu = request.form.get('r3bbu')
        ftcomsc = request.form.get('func_exclusion')
        id = request.form.get('ruleid')

        rule = Rule.query.filter(Rule.id == id).first()
        if rule:
            checkrulename = Rule.query.filter(Rule.rulename == rulename).first()
            if checkrulename and checkrulename.id != int(id):
                flash('Rule name could not be duplicated!', 'danger')
                return redirect(url_for('editrule'))
            else:
                rule.rulename = rulename
                rule.release = release
                rule.customer = customer
                rule.customer_feature_white = customer_feature_white
                rule.customer_feature_black = customer_feature_black
                rule.customer_top_fault = customer_top_fault
                rule.customer_care_function = customer_care_function
                rule.uuf_filter = uuf_filter
                rule.uuf_exclusion = uuf_exclusion
                rule.kpi_filter = kpi_filter
                rule.kpi_exclusion = kpi_exclusion
                rule.ca_filter = ca_filter
                rule.ca_exclusion = ca_exclusion
                rule.oamstab_filter = oamstab_filter
                rule.oamstab_exclusion = oamstab_exclusion
                rule.pet_filter = pet_filter
                rule.pet_exclusion = pet_exclusion
                rule.func_filter = func_filter
                rule.func_exclusion = func_exclusion
                rule.category_search_field = category_search_field
                rule.category_tag = category_tag
                rule.customer_rru = customer_rru
                rule.customer_bbu = customer_bbu
                rule.customer_keyword_white = customer_keyword_white
                rule.customer_keyword_black = customer_keyword_black
                rule.customer_pronto_white = customer_pronto_white
                rule.customer_pronto_black = customer_pronto_black
                rule.r4bbu = r4bbu
                rule.r3bbu = r3bbu
                rule.ftcomsc = ftcomsc
                db.session.commit()
                rule = Rule.query.filter(Rule.id == id).first()
                key1 = OrderedDict()
                key2 = OrderedDict()
                for k in rulekey1.keys():
                    key1[k] = vars(rule)[k]
                for k in rulekey2.keys():
                    key2[k] = vars(rule)[k]
                # return redirect(url_for('editrule'))
                flash('Rule is already sucessfully edited!', 'success')
                return render_template('editrule.html',key1 = key1, key2 = key2, userrules = userrulelist, ruleid=id, rule=rule)
        else:
            flash('A Null rule cannot be edited' , 'danger')
            return render_template('editrule.html', key1 = rulekey1, key2 = rulekey2, userrules = userrulelist)


@app.route('/editrule/showedit/',methods=['GET','POST'])
@login_require
def showedit():
    user_id = session.get('user_id')
    ruleid = request.form.get('ruleid')
    rule = Rule.query.filter(Rule.id == ruleid).first()
    userrulelist = Rule.query.filter(Rule.owner_id == user_id).order_by(desc(Rule.id)).all()
    key1 = OrderedDict()
    key2 = OrderedDict()
    for k in rulekey1.keys():
        key1[k] = vars(rule)[k]
    for k in rulekey2.keys():
        key2[k] = vars(rule)[k]
    return render_template('editrule.html',key1 = key1, key2 = key2, userrules = userrulelist, ruleid=ruleid,rule=rule)


@app.route('/newrule/ref/',methods=['GET','POST'])
@login_require
def newref():
    user_id = session.get('user_id')
    ruleid = request.form.get('ruleid')
    rule = Rule.query.filter(Rule.id == ruleid).first()
    userrulelist = Rule.query.order_by(desc(Rule.id)).all()
    key1 = OrderedDict()
    key2 = OrderedDict()
    for k in rulekey1.keys():
        key1[k] = vars(rule)[k]
    for k in rulekey2.keys():
        key2[k] = vars(rule)[k]
    return render_template('newrule.html',key1 = key1, key2 = key2, userrules = userrulelist, ruleid=ruleid,rule=rule)


@app.route('/delrule/',methods=['GET','POST'])
@login_require
def delrule():
    user_id = session.get('user_id')
    rule = {'rulename': 'rulename', 'release': 'release', 'customer': 'customer'}
    userrulelist = Rule.query.filter(Rule.owner_id == user_id).order_by(desc(Rule.id)).all()
    if request.method == 'GET':
        return render_template('delrule.html', key1=rulekey1, key2=rulekey2, userrules=userrulelist)
    else:
        id = request.form.get('ruleid')
        rule = Rule.query.filter(Rule.id == id).first()
        if rule:
            db.session.delete(rule)
            db.session.commit()
            userrulelist = Rule.query.filter(Rule.owner_id == user_id).order_by(desc(Rule.id)).all()
            flash('Rule is already sucessfully deleted!', 'success')
            return render_template('delrule.html',key1 = rulekey1, key2 = rulekey2, userrules = userrulelist)
        else:
            flash('Rule is not exist!', 'danger')
            return redirect(url_for('editrule'))


@app.route('/delrule/ref/',methods=['GET','POST'])
@login_require
def delref():
    user_id = session.get('user_id')
    ruleid = request.form.get('ruleid')
    rule = Rule.query.filter(Rule.id == ruleid).first()
    userrulelist = Rule.query.filter(Rule.owner_id == user_id).order_by(desc(Rule.id)).all()
    key1 = OrderedDict()
    key2 = OrderedDict()
    for k in rulekey1.keys():
        key1[k] = vars(rule)[k]
    for k in rulekey2.keys():
        key2[k] = vars(rule)[k]
    return render_template('delrule.html',key1 = key1, key2 = key2, userrules = userrulelist, ruleid=ruleid,rule=rule)

@app.route('/login/',methods=['GET','POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    else:
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter(User.username == username).first()
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            session.permanent = True
            flash('You were successfully logged in')
            return redirect(url_for('index'))
        else:
            error = 'Invalid credentials'
            return render_template('login.html', error=error)


@app.route('/register/',methods=['GET','POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')
    else:
        email = request.form.get('email')
        username = request.form.get('username')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        user = User.query.filter(User.email == email).first()
        if user:
            flash('email is already registered!', 'danger')
            return redirect(url_for('register'))
        else:
            if password1 != password2:
                flash('Please confirm password!', 'danger')
                return redirect(url_for('register'))
            else:
                user = User(email=email, username=username, password=generate_password_hash(password1))
                db.session.add(user)
                db.session.commit()
                flash('Congratulations! You have successfully signed up! ', 'success')
                return redirect(url_for('login'))


@app.route('/logout/')
def logout():
    session.clear()
    return redirect(url_for('index'))


@app.route('/upload/', methods = ['POST'],strict_slashes=False)
def upload():
    uf = request.files['input-b1']
    file_dir=os.path.join(basedir,app.config['UPLOAD_FOLDER'])
    if not os.path.exists(file_dir):
        os.makedirs(file_dir)
    if uf and allowed_file(uf.filename):                       
        # size = len(uf.read())
        size = 1                               
        if size<51200000:          
            filename = secure_filename(uf.filename)
            # currentpath = os.path.abspath(os.path.dirname(__file__))
            # ossep = os.path.sep
            ext = filename.rsplit('.',1)[1]
            name = filename.rsplit('.',1)[0]
            unix_time = int(time.time())
            new_filename=name + '_' + str(unix_time)+'.'+ext
            # savepath = currentpath + ossep+'uploadfolder'+ ossep + filename
            savepath = os.path.join(file_dir,new_filename)
            # uf.save(savepath)
            uf.save(savepath)
            source = Source(path=savepath,filename=new_filename)
            user_id = session.get('user_id')
            user = User.query.filter(User.id == user_id).first()
            source.owner = user
            try:                                                
                db.session.add(source)
                db.session.commit()
            except Exception as reason:
                s=str(reason)                                    
                list = re.split(r'[()]+', s)                    
                flash(u'Upload Failed：(%s)(%%s)'%list[1]%list[3])
                return redirect(url_for('index'))
            else:
                flash(u'Upload Succ')
                return redirect(url_for('index'))
        else:
            flash(u'error:File size should less than 50M')
            return redirect(url_for('index'))
    else:
        flash(u'error:File type should be xls or xlsx')
        return redirect(url_for('index'))

@app.context_processor
def my_context_processor():
    user_id = session.get('user_id')
    if user_id:
        user = User.query.filter(User.id == user_id).first()
        if user:
            return {'user':user}
    return {}


if __name__ == '__main__':
    app.run(host='0.0.0.0',port=8080)
