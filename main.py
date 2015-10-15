import webapp2
import jinja2
import os
import logging
import urllib
from google.appengine.api import users
from google.appengine.ext import ndb
import json
import csv
import re


JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

class Thesis(ndb.Model):
    created_by = ndb.KeyProperty(indexed=True)
    created_date = ndb.DateTimeProperty(auto_now_add=True)
    author_id = ndb.StringProperty(indexed=True)
    title = ndb.StringProperty(indexed=True)
    subtitle = ndb.StringProperty()
    adviser_key = ndb.KeyProperty(indexed=True)
    abstract = ndb.TextProperty()
    section = ndb.IntegerProperty()
    year = ndb.IntegerProperty()
    student_keys = ndb.KeyProperty(kind='Student',repeated=True)

class Student(ndb.Model):
    first_name = ndb.StringProperty(indexed=True)
    last_name = ndb.StringProperty(indexed=True)
    email = ndb.StringProperty(indexed=True)
    middle_name = ndb.StringProperty(indexed=True,default='')
    phone_num = ndb.StringProperty(indexed=True)
    student_num = ndb.StringProperty(indexed=True)
    birthdate = ndb.StringProperty()
    picture = ndb.StringProperty(indexed=True)
    year_graduated = ndb.IntegerProperty(indexed=True)

class User(ndb.Model):
    email = ndb.StringProperty(indexed=True)
    first_name = ndb.StringProperty(indexed=True)
    last_name = ndb.StringProperty(indexed=True)
    phone_num = ndb.StringProperty(indexed=True)
    date = ndb.DateTimeProperty(auto_now_add=True)
    authority = ndb.StringProperty(indexed=False)
    identity = ndb.StringProperty(indexed=False)

class Faculty(ndb.Model):
    position = ndb.StringProperty(indexed=True)
    first_name = ndb.StringProperty(indexed=True,default='')
    middle_name = ndb.StringProperty(indexed=True)
    last_name = ndb.StringProperty(indexed=True,default='')
    email = ndb.StringProperty(indexed=True)
    phone_number = ndb.StringProperty(indexed=True)
    birthdate = ndb.StringProperty(indexed=True)
    picture = ndb.StringProperty(indexed=True)

    @classmethod
    def get_by_key(cls, keyname):
        try:
            return ndb.Key(cls, keyname).get()
        except Exception:
            return None

class Department(ndb.Model):
    name = ndb.StringProperty(indexed=True)
    college_key = ndb.KeyProperty(indexed=True)

class College(ndb.Model):
    name = ndb.StringProperty(indexed=True)
    university_key = ndb.KeyProperty(indexed=True)

class University(ndb.Model):
    name = ndb.StringProperty(indexed=True)
    initials = ndb.StringProperty(indexed=True)
    address = ndb.StringProperty(indexed=True)

class ImportHandler(webapp2.RequestHandler):
    def get(self):

        csvfile = 'PUPCOEThesisList.csv'

        if csvfile:
            f = csv.reader(open(csvfile , 'r'),skipinitialspace=True)
            counter = 1
            for row in f:
                # logging.info(counter)
                thesis = Thesis()
                th = Thesis.query(Thesis.title == row[4]).fetch()
                # know if thesis title already in database
                if not th:
                    if len(row[7]) > 2:
                        adviser_name = row[7] # 'Rodolfo Talan'
                        x = adviser_name.split(' ')
                        adv_fname = x[0]
                        adv_lname = x[1]
                        adviser_keyname = adviser_name.strip().replace(' ', '').lower()
                        adviser = Faculty.get_by_key(adviser_keyname)
                        if adviser is None:
                            adviser = Faculty(key=ndb.Key(Faculty, adviser_keyname), first_name=adv_fname, last_name=adv_lname)
                            thesis.adviser_key = adviser.put()
                        else:
                            thesis.adviser_key = adviser.key
                    else:
                        adv_fname = 'Anonymous'
                        adviser = Faculty(first_name = adv_fname, last_name = adv_lname)
                        thesis.adviser_key = adviser.put()
                    
                    for i in range(8,13):
                        stud = Student()
                        if row[i]:
                            stud_name = row[i].title().split(' ')
                            size = len(stud_name)
                            if size >= 1:
                                stud.first_name = stud_name[0]
                            if size >= 2:
                                stud.middle_name = stud_name[1]
                            if size >= 3:
                                stud.last_name = stud_name[2]
                            thesis.student_keys.append(stud.put())

                    university = University(name = row[0])
                    university.put()
                    college = College(name = row[1], university_key = university.key)
                    college.put()
                    department = Department(name = row[2], college_key = college.key)
                    thesis.department_key = department.put()

                    thesis.year = int(row[3])
                    thesis.title = row[4]
                    thesis.abstract = row[5]
                    thesis.section = int(row[6])

                    # user = users.get_current_user()
                    # user_key = ndb.Key('User',user.user_id())

                    # thesis.created_by = user_key
                    thesis.put()

                    adv_fname = ''
                    adv_lname = ''
                    counter=counter+1
            self.response.write('CSV imported successfully')
        else:
            self.response.write(error)

class MainPage(webapp2.RequestHandler):
    def get(self):

        user = users.get_current_user()
        url = users.create_logout_url(self.request.uri)
        url_linktext = 'Logout'
        template_data = {
            'user': user,
            'url': url,
            'url_linktext': url_linktext,
        }
        if user:
            template = JINJA_ENVIRONMENT.get_template('main_page.html')
            self.response.write(template.render(template_data))
        else:
            self.redirect('/login');

class LoginPage(webapp2.RequestHandler):
    def get(self):

        user = users.get_current_user()
        template_data = {
            'login' : users.create_login_url(self.request.uri),
            'register' : users.create_login_url(self.request.uri)
        }
        if user:
            self.redirect('/register')
        else:
            template = JINJA_ENVIRONMENT.get_template('index.html')
            self.response.write(template.render(template_data))

class RegisterPage(webapp2.RequestHandler):
    def get(self):
        loginUser = users.get_current_user()

        if loginUser:
            user_key = ndb.Key('User',loginUser.user_id())
            user = user_key.get()
            if user:
                self.redirect('/')
            else:
                template = JINJA_ENVIRONMENT.get_template('register.html')
                logout_url = users.create_logout_url('/login')
                template_data = {
                    'logout_url' : logout_url
                }
                self.response.write(template.render(template_data))
        else:
            login_url = users.create_login_url('/register')
            self.redirect(login_url)

    def post(self):
        loginUser = users.get_current_user()
        fname = self.request.get('first_name')
        lname = self.request.get('last_name')
        pnum = self.request.get('phone_num')
        email = loginUser.email()
        user_id = loginUser.user_id()
        user = User(id = user_id, email=email,first_name=fname,last_name = lname,phone_num = pnum)
        
        u = User.query(User.first_name == fname).fetch()
        if u:
            for user in u:
                if user.cr_last_name == lname:
                    self.response.headers['Content-Type'] = 'application/json'
                    response = {
                        'status':'Name have already been taken',
                    }
                    self.response.out.write(json.dumps(response))
                    return


        faculty_email = Faculty.query(Faculty.email == email).get()
        if faculty_email:
            authority = 'faculty'
        else:
            authority = 'reader'
        user = User(id = user_id, email = email, first_name = fname , last_name = lname, phone_num = pnum, authority = authority)
        logging.info(authority)
        user.put()
        
        self.response.headers['Content-Type'] = 'application/json'
        response = {
            'result':'OK',
            }
        self.response.out.write(json.dumps(response))
        self.redirect('/')

class DetailPage(webapp2.RequestHandler):
    def get(self,th_id):
        thes =  Thesis.get_by_id(int(th_id))
        thesis = thes.key.get()
        logging.info(thesis)
        user = users.get_current_user()
        url = users.create_logout_url(self.request.uri)
        url_linktext = 'Logout'
        template_data = {
            'user': user,
            'url': url,
            'url_linktext': url_linktext,
            'thesis': thesis
        }
        if user:
            template = JINJA_ENVIRONMENT.get_template('thesis_info.html')
            self.response.write(template.render(template_data))
        else:
            self.redirect('/');

class ThesisListAll(webapp2.RequestHandler):
    def get(self):

        thesis = Thesis.query().order(-Thesis.created_date).fetch()
        logging.info(thesis)
        user = users.get_current_user()
        url = users.create_logout_url(self.request.uri)
        url_linktext = 'Logout'
        template_data = {
            'user': user,
            'url': url,
            'url_linktext': url_linktext,
            'thesis': thesis
        }
        if user:
            template = JINJA_ENVIRONMENT.get_template('thesis_list.html')
            self.response.write(template.render(template_data))
        else:
            self.redirect('/');

class ThesisYear11(webapp2.RequestHandler):
    def get(self):

        thes1 = Thesis.query(Thesis.year==2011)
        logging.info(thes1)
        user = users.get_current_user()
        url = users.create_logout_url(self.request.uri)
        url_linktext = 'Logout'
        template_data = {
            'user': user,
            'url': url,
            'url_linktext': url_linktext,
            'thesis': thes1
        }
        if user:
            template = JINJA_ENVIRONMENT.get_template('thesis_list.html')
            self.response.write(template.render(template_data))
        else:
            self.redirect('/');

class ThesisYear12(webapp2.RequestHandler):
    def get(self):

        thes2 = Thesis.query(Thesis.year==2012)
        logging.info(thes2)
        user = users.get_current_user()
        url = users.create_logout_url(self.request.uri)
        url_linktext = 'Logout'
        template_data = {
            'user': user,
            'url': url,
            'url_linktext': url_linktext,
            'thesis': thes2
        }
        if user:
            template = JINJA_ENVIRONMENT.get_template('thesis_list.html')
            self.response.write(template.render(template_data))
        else:
            self.redirect('/');

class ThesisYear13(webapp2.RequestHandler):
    def get(self):

        thes3 = Thesis.query(Thesis.year==2013)
        logging.info(thes3)
        user = users.get_current_user()
        url = users.create_logout_url(self.request.uri)
        url_linktext = 'Logout'
        template_data = {
            'user': user,
            'url': url,
            'url_linktext': url_linktext,
            'thesis': thes3
        }
        if user:
            template = JINJA_ENVIRONMENT.get_template('thesis_list.html')
            self.response.write(template.render(template_data))
        else:
            self.redirect('/');

class ThesisYear14(webapp2.RequestHandler):
    def get(self):

        thes4 = Thesis.query(Thesis.year==2014)
        logging.info(thes4)
        user = users.get_current_user()
        url = users.create_logout_url(self.request.uri)
        url_linktext = 'Logout'
        template_data = {
            'user': user,
            'url': url,
            'url_linktext': url_linktext,
            'thesis': thes4
        }
        if user:
            template = JINJA_ENVIRONMENT.get_template('thesis_list.html')
            self.response.write(template.render(template_data))
        else:
            self.redirect('/');

class ThesisYear15(webapp2.RequestHandler):
    def get(self):

        thes5 = Thesis.query(Thesis.year==2015)
        logging.info(thes5)
        user = users.get_current_user()
        url = users.create_logout_url(self.request.uri)
        url_linktext = 'Logout'
        template_data = {
            'user': user,
            'url': url,
            'url_linktext': url_linktext,
            'thesis': thes5
        }
        if user:
            template = JINJA_ENVIRONMENT.get_template('thesis_list.html')
            self.response.write(template.render(template_data))
        else:
            self.redirect('/');

class  CreateThesis(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        url = users.create_logout_url(self.request.uri)
        url_linktext = 'Logout'
        template_data = {
            'user': user,
            'url': url,
            'url_linktext': url_linktext
        }
        if user:
            template = JINJA_ENVIRONMENT.get_template('create_thesis.html')
            self.response.write(template.render(template_data))
        else:
            self.redirect('/');

    def post(self):

        dept=Department()
        dept.name = self.request.get('department')
        dept.put()
        thesis=Thesis()
        thesis.title = self.request.get('title')
        thesis.subtitle = self.request.get('subtitle')
        thesis.abstract = self.request.get('abstract')
        thesis.adviser = self.request.get('adviser')
        thesis.year = int(self.request.get('year'))
        thesis.section = int(self.request.get('section'))
        thesis.proponent1 = self.request.get('proponent1')
        thesis.proponent2 = self.request.get('proponent2')
        thesis.proponent3 = self.request.get('proponent3')
        thesis.proponent4 = self.request.get('proponent4')
        thesis.proponent5 = self.request.get('proponent5')
        # thesis.department_key = self.request.get('department_key')
        thesis.put()
        self.redirect('/thesis/create')

class  CreateFaculty(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        url = users.create_logout_url(self.request.uri)
        url_linktext = 'Logout'
        template_data = {
            'user': user,
            'url': url,
            'url_linktext': url_linktext
        }
        if user:
            template = JINJA_ENVIRONMENT.get_template('create_faculty.html')
            self.response.write(template.render(template_data))
        else:
            self.redirect('/');

    def post(self):

        dept=Department()
        dept.position = self.request.get('position')
        dept.fname = self.request.get('first_name')
        dept.mname = self.request.get('middle_name')
        dept.lname = self.request.get('last_name')
        dept.email = self.request.get('email')
        dept.pnum = int(self.request.get('phone_number'))
        dept.bday = self.request.get('birthdate')
        dept.picture = self.request.get('picture')
        dept.put()
        self.redirect('/faculty/create')

class  CreateStudent(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        url = users.create_logout_url(self.request.uri)
        url_linktext = 'Logout'
        template_data = {
            'user': user,
            'url': url,
            'url_linktext': url_linktext
        }
        if user:
            template = JINJA_ENVIRONMENT.get_template('create_student.html')
            self.response.write(template.render(template_data))
        else:
            self.redirect('/');

    def post(self):

        stud=Student()
        stud.fname = self.request.get('first_name')
        stud.mname = self.request.get('middle_name')
        stud.lname = self.request.get('last_name')
        stud.email = int(self.request.get('email'))
        stud.pnum = int(self.request.get('phone_number'))
        stud.studnum = self.request.get('student_num')
        stud.picture = self.request.get('picture')
        stud.put()
        self.redirect('/student/create')

class  CreateUniversity(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        url = users.create_logout_url(self.request.uri)
        url_linktext = 'Logout'
        template_data = {
            'user': user,
            'url': url,
            'url_linktext': url_linktext
        }
        if user:
            template = JINJA_ENVIRONMENT.get_template('create_university.html')
            self.response.write(template.render(template_data))
        else:
            self.redirect('/');

    def post(self):

        univ=University()
        univ.name = self.request.get('name')
        univ.initials = self.request.get('initials')
        univ.address = self.request.get('address')
        univ.put()
        self.redirect('/university/create')

class  CreateCollege(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        url = users.create_logout_url(self.request.uri)
        url_linktext = 'Logout'
        template_data = {
            'user': user,
            'url': url,
            'url_linktext': url_linktext
        }
        if user:
            template = JINJA_ENVIRONMENT.get_template('create_college.html')
            self.response.write(template.render(template_data))
        else:
            self.redirect('/');

    def post(self):

        co=College()
        co.name = self.request.get('name')
        co.put()
        self.redirect('/college/create')

class  CreateDepartment(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        url = users.create_logout_url(self.request.uri)
        url_linktext = 'Logout'
        template_data = {
            'user': user,
            'url': url,
            'url_linktext': url_linktext
        }
        if user:
            template = JINJA_ENVIRONMENT.get_template('create_department.html')
            self.response.write(template.render(template_data))
        else:
            self.redirect('/');

    def post(self):

        dep=Department()
        dep.name = self.request.get('name')
        dep.put()
        self.redirect('/department/create')

class  DeleteThesis(webapp2.RequestHandler):
    def get(self,th_id):
        d = Thesis.get_by_id(int(th_id))
        d.key.delete()
        self.redirect('/thesis/list/all')

class  DeleteStudent(webapp2.RequestHandler):
    def get(self,s_id):
        key_to_delete = ndb.Key('Student',int(s_id))
        th = Thesis.query(projection=[Thesis.student_keys]).fetch()
        for t in th:
            if key_to_delete in t.student_keys:
                thesis = t.key.get()
                idx = thesis.student_keys.index(key_to_delete)
                del thesis.student_keys[idx]
                thesis.put()
        s = key_to_delete.get()
        s.key.delete()
        self.redirect('/studen/list')

class  DeleteFaculty(webapp2.RequestHandler):
    def get(self,f_id):
        if f_id.isdigit():
            key_to_delete = ndb.Key('Faculty',int(f_id))
        else:
            key_to_delete = ndb.Key('Faculty',f_id)
        th = Thesis.query(projection=[Thesis.adviser_key]).fetch()
        for t in th:
            if key_to_delete == t.adviser_key:
                thesis = t.key.get()
                thesis.adviser_key = None
                thesis.put()
        f = key_to_delete.get()
        f.key.delete()
        self.redirect('/faculty/list')

class  DeleteCollege(webapp2.RequestHandler):
    def get(self,c_id):
        c = College.get_by_id(int(c_id))
        d = Department.query(Department.college_key == c.key).get()
        if d:
            d.college_key = None
        d.put()
        c.key.delete()

        self.redirect('/college/list')

class  DeleteUniversity(webapp2.RequestHandler):
    def get(self,u_id):
        u = University.get_by_id(int(u_id))
        c = College.query(College.university_key == u.key).get()
        if c:
            c.university_key = None
        c.put()
        u.key.delete()

        self.redirect('/university/list')

class  ThesisEdit(webapp2.RequestHandler):
    def get(self,th_id):
        s = Thesis.get_by_id(int(th_id))
        user = users.get_current_user()
        url = users.create_logout_url(self.request.uri)
        url_linktext = 'Logout'
        template_data = {
            'thesis': s,
            'user': user,
            'url': url,
            'url_linktext': url_linktext
        }
        template = JINJA_ENVIRONMENT.get_template('edit.html')
        self.response.write(template.render(template_data))
    def post(self,th_id):
        thesis = Thesis.get_by_id(int(th_id))
        thesis.title = self.request.get('title')
        thesis.abstract = self.request.get('abstract')
        thesis.adviser = self.request.get('adviser')
        thesis.year = self.request.get('year')
        thesis.section = self.request.get('section')
        hesis.proponent1 = self.request.get('proponent1')
        thesis.proponent2 = self.request.get('proponent2')
        thesis.proponent3 = self.request.get('proponent3')
        thesis.proponent4 = self.request.get('proponent4')
        thesis.proponent5 = self.request.get('proponent5')
        thesis.put()
        self.redirect('/')

class ListFaculty(webapp2.RequestHandler):
    def get(self):

        fac = Faculty.query().order(-Faculty.first_name).fetch()
        logging.info(fac)
        user = users.get_current_user()
        url = users.create_logout_url(self.request.uri)
        url_linktext = 'Logout'
        template_data = {
            'user': user,
            'url': url,
            'url_linktext': url_linktext,
            'faculty': fac
        }
        if user:
            template = JINJA_ENVIRONMENT.get_template('faculty_list.html')
            self.response.write(template.render(template_data))
        else:
            self.redirect('/');

class ListStudent(webapp2.RequestHandler):
    def get(self):

        st = Student.query().order(-Student.first_name).fetch()
        logging.info(st)
        user = users.get_current_user()
        url = users.create_logout_url(self.request.uri)
        url_linktext = 'Logout'
        template_data = {
            'user': user,
            'url': url,
            'url_linktext': url_linktext,
            'student': st
        }
        if user:
            template = JINJA_ENVIRONMENT.get_template('student_list.html')
            self.response.write(template.render(template_data))
        else:
            self.redirect('/');

class ListCollege(webapp2.RequestHandler):
    def get(self):

        c = College.query().order(-College.name).fetch()
        logging.info(c)
        user = users.get_current_user()
        url = users.create_logout_url(self.request.uri)
        url_linktext = 'Logout'
        template_data = {
            'user': user,
            'url': url,
            'url_linktext': url_linktext,
            'college': c
        }
        if user:
            template = JINJA_ENVIRONMENT.get_template('college_list.html')
            self.response.write(template.render(template_data))
        else:
            self.redirect('/');

class ListUniversity(webapp2.RequestHandler):
    def get(self):

        u = University.query().order(-University.name).fetch()
        logging.info(u)
        user = users.get_current_user()
        url = users.create_logout_url(self.request.uri)
        url_linktext = 'Logout'
        template_data = {
            'user': user,
            'url': url,
            'url_linktext': url_linktext,
            'university': u
        }
        if user:
            template = JINJA_ENVIRONMENT.get_template('university_list.html')
            self.response.write(template.render(template_data))
        else:
            self.redirect('/');

class APIHandlerPage(webapp2.RequestHandler):
    def get(self):
        thesis = Thesis.query().order(-Thesis.created_date).fetch()
        thesis_list = []

        for thes in thesis:
            creator = thes.author_id
            created_by = ndb.Key('User',creator)
            thesis_list.append({
                'self_id':thes.key.id(),
                'thesis_title':thes.title,
                'thesis_adviser':thes.adviser,
                'thesis_abstract':thes.abstract,
                'thesis_year':thes.year,
                'thesis_section':thes.section,
                'author_fname':created_by.get().first_name,
                'author_lname':created_by.get().last_name
                })

        response = {
            'result':'OK',
            'data':thesis_list
        }

        self.response.headers['Content-Type'] = 'application/json'
        self.response.out.write(json.dumps(response))

    def post(self):

        proponents = []
        if self.request.get('thesis_member1'):
            proponents.append(self.request.get('thesis_member1'))
        if self.request.get('thesis_member2'):
            proponents.append(self.request.get('thesis_member2'))
        if self.request.get('thesis_member3'):
            proponents.append(self.request.get('thesis_member3'))
        if self.request.get('thesis_membe4'):
            proponents.append(self.request.get('thesis_member4'))
        if self.request.get('thesis_member5'):
            proponents.append(self.request.get('thesis_member5'))

        user = users.get_current_user()
        thesis = Thesis()
        thesis.title = self.request.get('title')
        thesis.abstract = self.request.get('abstract')
        thesis.adviser = self.request.get('adviser')
        thesis.year = self.request.get('year')
        thesis.section = self.request.get('section')
        thesis.author_id = user.user_id()
        creator = thesis.author_id
        thesis.created_by = ndb.Key('User',creator)
        thesis.put()
        
        

        self.response.headers['Content-Type'] = 'application/json'
        response = {
            'result':'OK',
            'data':{
                'self_id':thesis.key.id(),
                'title':thesis.title,
                'adviser':student.adviser,
                'abstract':student.abstract,
                'year':thesis.year,
                'section':student.section,
                'author_fname':created_by.get().first_name,
                'author_lname':created_by.get().last_name
            }
        }
        self.response.out.write(json.dumps(response))


app = webapp2.WSGIApplication([
    ('/thesis/create', CreateThesis),
    ('/faculty/create', CreateFaculty),
    ('/student/create', CreateStudent),
    ('/university/create', CreateUniversity),
    ('/college/create', CreateCollege),
    ('/department/create', CreateDepartment),
    ('/thesis/delete/(.*)', DeleteThesis),
    ('/thesis/delete/(.*)', DeleteThesis),
    ('/student/delete/(.*)', DeleteStudent),
    ('/faculty/delete/(.*)', DeleteFaculty),
    ('/college/delete/(.*)', DeleteCollege),
    ('/university/delete/(.*)', DeleteUniversity),
    ('/thesis/edit/(.*)', ThesisEdit),
    ('/thesis/list/all', ThesisListAll),
    ('/thesis/list/2011', ThesisYear11),
    ('/thesis/list/2012', ThesisYear12),
    ('/thesis/list/2013', ThesisYear13),
    ('/thesis/list/2014', ThesisYear14),
    ('/thesis/list/2015', ThesisYear15),
    ('/faculty/list', ListFaculty),
    ('/student/list', ListStudent),
    ('/university/list', ListUniversity),
    ('/college/list', ListCollege),
    ('/api/handler', APIHandlerPage),
    ('/thesis/info/(.*)', DetailPage),
    ('/register', RegisterPage),
    ('/login', LoginPage),
    ('/', MainPage),
    # ('/csvimport', ImportHandler)
], debug=True)
