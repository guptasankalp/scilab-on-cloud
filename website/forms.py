import MySQLdb
import random
import re
import ajax
from django import forms
from django.core.validators import validate_email
from __main__ import *
from dajax.core import Dajax
from django.utils import simplejson
from dajaxice.decorators import dajaxice_register
from dajaxice.utils import deserialize_form
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render 
from django.template.loader import render_to_string
from django.core.context_processors import csrf
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from django.db.models import Q
from soc.config import *
from django.http import HttpResponse
from django.template import Context
from django.template.loader import render_to_string, get_template
from django.core.mail import EmailMessage
from django.db import connection
conn = MySQLdb.connect(host= "127.0.0.1",
		user=DB_USER_DEFAULT,
		passwd=DB_PASS_DEFAULT,
		db=DB_NAME_DEFAULT)
x = conn.cursor()

issues = (
    ('', '-- Select Type of issue --'),
    (1, 'Blank Code / Incorrect code'),
    (2, 'Output error'),
    (3, 'Execution error'),
    (4, 'Missing example(s)'),
    (6, 'Blank output'),
    (7, 'Any other / General'),
)

ex_id =0
ch_id =0
bk_id =0
ct_id =0


@dajaxice_register
def codes(request, example_id):

    global ex_id
    global bk_id
    global ch_id
    global ct_id
    ex_id = example_id
    x.execute("""SELECT chapter_id FROM textbook_companion_example WHERE id = %s""", [ex_id]) #get the chapter id
    conn.commit()
    c_data = x.fetchone() 
    ch_id = int(c_data[0])   

    x.execute("""SELECT preference_id FROM textbook_companion_chapter WHERE id = %s""", [ch_id]) #get the preference id
    conn.commit()
    b_data = x.fetchone() 
    bk_id = int(b_data[0])    
		
    x.execute("""SELECT category FROM textbook_companion_preference WHERE approval_status = 1 AND id = %s""", [bk_id]) #get the category id
    conn.commit()
    t_data = x.fetchone() 
    ct_id = int(t_data[0])   

@dajaxice_register
def change_ch(request, chapter_id):

   global ex_id
    ex_id = 0	

@dajaxice_register
def change_bk(request, book_id):

    global ex_id
    ex_id = 0
	
@dajaxice_register
def change_ct(request, category_id):

    global ex_id
    ex_id = 0
	
@dajaxice_register
def email_one(request):

        subject = "Scilab on Cloud Comment Reply"
        to = [mail]
        from_email = EMAIL_HOST_USER 

        ctx = {
            'user': mail,
            'issue': comment
        }

        message = render_to_string('email/email_text.txt', ctx)

        EmailMessage(subject, message, to = to, from_email = from_email).send()

        return HttpResponse('email_one')


class BugForm(forms.Form):


    example = forms.CharField(widget = forms.HiddenInput(), required = False)
    issue = forms.CharField(widget = forms.Select(choices=issues))
    description = forms.CharField(widget = forms.Textarea)
    notify = forms.BooleanField(required = False, initial = True)
    email = forms.CharField(required = False)
    notify.widget.attrs['disabled'] = True

    def clean_email(self):

        email = self.cleaned_data.get('email', None)
        notify = True
	global mail
	mail = email
        if notify and not email:
            raise forms.ValidationError('Email id is required if you want to be notified.')
        elif notify:
            validate_email(email)
	   

    def clean(self):

        issue = self.cleaned_data.get('issue', None)
	description = self.cleaned_data.get('description',None)
        global comment
	comment = description

        if (issue and int(issue) != 7) and (ex_id == 0) and (not ex_id):
            raise forms.ValidationError("""
                Please select book, chapter and example.
                Or select the *Any other/General* issue type.
            """) 
	    
	else:
            x.execute(""" INSERT into scilab_cloud_comment(type, comment, email ,category, books, chapter, example) values (%s, %s, %s, %s, %s, %s, %s)""", (issue, comment, mail, ct_id, bk_id, ch_id, ex_id))   #insert new scilab cloud comment 
            conn.commit()
	

