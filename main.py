# !/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import webapp2
import jinja2
import os
import logging
import json
import urllib
import unicodedata


from google.appengine.api import urlfetch
from google.appengine.api import users
from google.appengine.ext import ndb

from google.appengine.ext import vendor

# from twilio.rest import TwilioRestClient
# import twilio


# Add any libraries installed in the "lib" folder.
vendor.add('lib')
# from twilio.rest.resources import SmsMessages
#
# import twilio
# import twilio.rest
import httplib2
import simplejson
import eventful

class Person(ndb.Model):
    name = ndb.StringProperty(required=True)
    userID = ndb.StringProperty(required=True)
    email = ndb.StringProperty()
    number = ndb.StringProperty() # change to int property later
    bio = ndb.TextProperty()
    # events = ndb.StructuredProperty(Event, repeated=True)



class Event(ndb.Model):
    name = ndb.StringProperty()
    place = ndb.StringProperty()
    description = ndb.TextProperty()
    address = ndb.StringProperty()
    city = ndb.StringProperty()
    region = ndb.StringProperty()
    zip_code = ndb.StringProperty()
    country = ndb.StringProperty()
    place_url = ndb.StringProperty()
    start_time = ndb.StringProperty()
    frequency = ndb.StringProperty()
    # location = ndb.StringProperty(required=True)
    lat_lon = ndb.FloatProperty(repeated=True)
    # pictures = ndb.BlobProperty(required=True, repeated=True)

    # people = ndb.StructuredProperty(Person, repeated=True)


class PersonEvent(ndb.Model):
    person = ndb.KeyProperty(Person)
    event = ndb.KeyProperty(Event)

class RomeoHandler(webapp2.RequestHandler):
    def get(self):
        template= jinja_environment.get_template('templates/romeo.html')
        self.response.write(template.render({'results': "no swag"}))


# Your Account Sid and Auth Token from twilio.com/user/account
# account_sid = "AC32a3c49700934481addd5ce1659f04d2"
# auth_token  = "{{ auth_token }}"
# account_sid = "ACa0a71e9219433e4b3d9f5edb40cf3d6f"
# auth_token = "ed61ec98d6b79a5580d0f5a67feda8e9"
# client = TwilioRestClient(account_sid, auth_token)
#
# message = client.messages.create(body="test",
#    to="+13057763642",    # Replace with your phone number
#    from_="+13057763642") # Replace with your Twilio number
# logging.info(message.sid)

class MainHandler(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        template= jinja_environment.get_template('templates/sign_in.html')
        self.response.write(template.render({'user': user, 'logout_link': users.create_logout_url('/'), 'nickname': "DEFAULT" if not user else user.nickname(), 'login_link': users.create_login_url('/')}))
        people = Person.query()
        if user:
            for person in people:
                if person.userID == user.user_id():
                    self.redirect('/home')
                    return
        if user:
            self.redirect('/create_profile')

class Home(webapp2.RequestHandler):
    def get(self):

        # # deletes everything on datastore
        # people = Event.query()
        # for person in people:
        #     person.key.delete()
        # people = Person.query()
        # for person in people:
        #     person.key.delete()
        # people = PersonEvent.query()
        # for person in people:
        #     person.key.delete()


        user = users.get_current_user()
        if user:
            template= jinja_environment.get_template('templates/home.html')
            self.response.write(template.render({'user': user, 'logout_link': users.create_logout_url('/'), 'nickname': "DEFAULT" if not user else user.nickname(), 'login_link': users.create_login_url('/')}))
        else:
            not_signed_in_template= jinja_environment.get_template('templates/not_signed_in.html')
            self.response.write(not_signed_in_template.render())

    def post(self):
        user = users.get_current_user()
        template_data = {'user': user, 'logout_link': users.create_logout_url('/'), 'nickname': "DEFAULT" if not user else user.nickname(), 'login_link': users.create_login_url('/')}
        #!/usr/bin/env python
        api = eventful.API('P39qwcnBXLTHTnP3',cache=None)
        # api = eventful.API('test_key', cache=None)
        events = api.call('/events/search', q= self.request.get('query', default_value='music'), l=self.request.get('city', default_value='boston')) #later will be self.request.get('city')
        # logging.info(events)
        result_template= jinja_environment.get_template('templates/result.html')
        result=""
        if int(events['page_count']) > 0:

            for event in events['events']['event']:


                next_event = Event(name = event['title'],
                                    place = event['venue_name'],
                                    description= event['description'],
                                    address = event['venue_address'],
                                    city= event['city_name'],
                                    region = event['region_name'],
                                    zip_code= event['postal_code'],
                                    country = event['country_abbr'],
                                    place_url= event['venue_url'],
                                    start_time = event['start_time'],
                                    frequency= event['recur_string'],
                                    lat_lon = [float(event['latitude']), float(event['longitude'])]
                                    # pictures[0]= event['description'],
                                    )
                match = False
                name = next_event.name
                next_event = next_event.put()
                event_id = str(next_event.id())
                next_event = next_event.get()
                # start_time = next_event.start_time
                # all_events = Event.query()

                # for each_event in all_events:
                #     if name == each_event.name and start_time == each_event.start_time:
                #         match = True
                #         logging.info('this event exists already')
                # if not match:
                #     next_event = next_event.put()
                #     next_event = next_event.get()

                result+= "<a href='/event?id=" + event_id + "'>" + event['title'] + " at " + event['venue_name'] + "</a><br>" # "<a href='/event?id=%s> %s at %s</a><br>" % (event_id, event['title'], event['venue_name'])


            template_data['results'] = result
            self.response.write(result_template.render(template_data))
        else:
            self.response.write(result_template.render({"results": "None"}))

class AboutPage(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        if user:
            template_data = {'user': user, 'logout_link': users.create_logout_url('/'), 'nickname': "DEFAULT" if not user else user.nickname(), 'login_link': users.create_login_url('/')}
            template= jinja_environment.get_template('templates/about.html')
            self.response.write(template.render(template_data))
        else:
            not_signed_in_template= jinja_environment.get_template('templates/not_signed_in.html')
            self.response.write(not_signed_in_template.render())

'''class SavedHandler(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        if user:
            template= jinja_environment.get_template('templates/saved_events.html')
            self.response.write(template.render({'user': user, 'logout_link': users.create_logout_url('/'), 'nickname': "DEFAULT" if not user else user.nickname(), 'login_link': users.create_login_url('/')}))
        else:
            not_signed_in_template= jinja_environment.get_template('templates/not_signed_in.html')
            self.response.write(not_signed_in_template.render())'''
#####this is what we have

class FormHandler(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        if user:
            template = jinja_environment.get_template('templates/form.html')
            self.response.write(template.render({'user': user, 'logout_link': users.create_logout_url('/'), 'nickname': "DEFAULT" if not user else user.nickname(), 'login_link': users.create_login_url('/')}))
        else:
            not_signed_in_template= jinja_environment.get_template('templates/not_signed_in.html')
            self.response.write(not_signed_in_template.render())
    def post(self):
        logging.info("====================")
        user = users.get_current_user()
        template_data = {'user': user, 'logout_link': users.create_logout_url('/'), 'nickname': "DEFAULT" if not user else user.nickname(), 'login_link': users.create_login_url('/')}
        template = jinja_environment.get_template('templates/event.html')
        # if self.request.get('latitude') != "" and self.request.get('longitude') != "":
        #     next_event = Event(name = self.request.get('name'),
        #                         place = self.request.get('venue_name'),
        #                         description= self.request.get('description'),
        #                         address = self.request.get('venue_address'),
        #                         city= self.request.get('city_name'),
        #                         region = self.request.get('region_name'),
        #                         zip_code= self.request.get('postal_code'),
        #                         country = self.request.get('country_abbr'),
        #                         place_url= self.request.get('venue_url'),
        #                         start_time = self.request.get('start_time'),
        #                         frequency= self.request.get('recur_string'),
        #                         lat_lon = [float(self.request.get('latitude')), float(event['longitude'))]
        #                         # pictures[0]= event['description'],
        #                         )
        # else:
        next_event = Event(name = self.request.get('name'),
                            place = self.request.get('venue_name'),
                            description= self.request.get('description'),
                            address = self.request.get('venue_address'),
                            city= self.request.get('city_name'),
                            region = self.request.get('region_name'),
                            zip_code= self.request.get('postal_code'),
                            country = self.request.get('country_abbr'),
                            place_url= self.request.get('venue_url'),
                            start_time = self.request.get('start_time'),
                            frequency= self.request.get('recur_string'),
                            # pictures[0]= event['description'],
                            )
        # logging.info(self.request.get('name'))
        # logging.info(self.request.get('venue_name'))
        # logging.info(self.request.get('description'))
        # logging.info(self.request.get('venue_address'))
        # logging.info(self.request.get('city_name'))
        # logging.info(self.request.get('region_name'))
        # logging.info(self.request.get('postal_code'))
        # logging.info(self.request.get('country_abbr'))
        # logging.info(self.request.get('venue_url'))
        # logging.info(self.request.get('start_time'))
        # logging.info(self.request.get('recur_string'))

        template_data['name'] = next_event.name
        template_data['place'] = next_event.place
        template_data['description'] = next_event.description
        template_data['address'] = next_event.address
        template_data['city'] = next_event.city
        template_data['region'] = next_event.region
        template_data['zip_code'] = next_event.zip_code
        template_data['country'] = next_event.country
        template_data['start_time'] = next_event.start_time
        template_data['frequency'] = next_event.frequency

        match = False
        name = next_event.name
        next_event = next_event.put().get()
        event_id = str(next_event.key.id())
        # template_data['id']= str(next_event.id())()
        start_time = next_event.start_time
        all_events = Event.query()
        # for each_event in all_events:
        #     if name == each_event.name and start_time == each_event.start_time:
        #         match = True
        #         logging.info('this event exists already')
        # if not match:
        #     next_event = next_event.put()
        #     next_event = next_event.get()
        result = "<a href='/event?id=" + event_id + "'>" + next_event.name + " at " + next_event.place + "</a><br>" # "<a href='/event?id=%s> %s at %s</a><br>" % (event_id, event['title'], event['venue_name'])


        template_data['results'] = result
        redirect_site = '/event?id=' + event_id
        self.redirect(redirect_site)
        # self.response.write(template.render(template_data))


class MapHandler(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        template_data = {'user': user, 'logout_link': users.create_logout_url('/'), 'nickname': "DEFAULT" if not user else user.nickname(), 'login_link': users.create_login_url('/')}
        if user:
            events = Event.query()
            # locations = []
            latitudes = []
            longitudes = []

            names = []
            i = 0
            for event in events:
                latitudes.append(float(event.lat_lon[0]))
                longitudes.append(float(event.lat_lon[1]))
                names.append(event.name)
                i += 1

            template = jinja_environment.get_template('templates/map.html')
            combined = zip(set(names), set(latitudes), set(longitudes))
            template_data['zip'] = combined
            self.response.write(template.render(template_data))
        else:
            not_signed_in_template= jinja_environment.get_template('templates/not_signed_in.html')
            self.response.write(not_signed_in_template.render())





class ProfileHandler(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        template_data = {'user': user, 'logout_link': users.create_logout_url('/'), 'nickname': "DEFAULT" if not user else user.nickname(), 'login_link': users.create_login_url('/')}
        if user:
            template = jinja_environment.get_template('templates/my_profile.html')
            current_id = self.request.get('id')
            people = Person.query()
            # logging.info(people)
            for person in people:
                if person.userID == user.user_id():
                    template_data['name'] = person.name #unicodedata.normalize('NFKD', person.name).encode('ascii','ignore')
                    template_data['email'] = person.email
                    template_data['bio'] = person.bio
                    break
            if current_id != "":
                person_key = None

                for person in people:
                    logging.info(person.userID)
                    logging.info(current_id)
                    if person.userID == current_id:
                        logging.info("==============match boyz")
                        person_key = person.key
                        break
                if person_key:
                    person = person_key.get()
                    template_data['name'] = person.name #unicodedata.normalize('NFKD', person.name).encode('ascii','ignore')
                    template_data['email'] = person.email    #user.email()
                    template_data['bio'] = person.bio




            relationships = PersonEvent.query().fetch()
            template_data['results'] = ""
            for relationship in relationships:
                if relationship and relationship.person and relationship.person.get():

                    logging.info(relationship.person.get().name)
                    logging.info(template_data['name'])
                if relationship and relationship.person and relationship.person.get():
                    if relationship.person.get().name == template_data['name']:
                        event = relationship.event.get()
                        event_id = str(event.key.id())

                        template_data['results'] += "<a href='/event?id=" + event_id + "'>" + event.name + " at " + event.place + "</a><br>"

            self.response.write(template.render(template_data))

            # line below may never execute because user will always have a profile at this point
            # only uncomment line below if Google users get in without a TEH profile
            # self.response.write(template.render({'user': user, 'logout_link': users.create_logout_url('/'), 'nickname': "DEFAULT" if not user else user.nickname(), 'login_link': users.create_login_url('/')}))

        else:
            not_signed_in_template= jinja_environment.get_template('templates/not_signed_in.html')
            self.response.write(not_signed_in_template.render())

class CreateProfileHandler(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        template = jinja_environment.get_template('templates/profile_form.html')
        self.response.write(template.render({'user': user, 'logout_link': users.create_logout_url('/'), 'nickname': "DEFAULT" if not user else user.nickname(), 'login_link': users.create_login_url('/')}))
    def post(self):
        user = users.get_current_user()
        person = Person(name = self.request.get('person_name'), userID = user.user_id(), email = user.email(), number = self.request.get('number'), bio = self.request.get('bio'))
        person.put()
        self.redirect('/home')

class EventHandler(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        template = jinja_environment.get_template('templates/event.html')
        template_data = {'user': user, 'logout_link': users.create_logout_url('/'), 'nickname': "DEFAULT" if not user else user.nickname(), 'login_link': users.create_login_url('/')}
        event = Event.get_by_id(long(self.request.get('id')))

        # logging.info('---------')
        # logging.info(self.request.get('id'))
        # template_data['id'] = event.key.id()

        template_data['name'] = event.name
        template_data['place'] = event.place
        template_data['description'] = event.description
        template_data['address'] = event.address
        template_data['city'] = event.city
        template_data['region'] = event.region
        template_data['zip_code'] = event.zip_code
        template_data['country'] = event.country
        template_data['start_time'] = event.start_time
        template_data['frequency'] = event.frequency
        # location.href += "?id=" + str(self.request.get('id'))
        # if event.frequency == None:
        #     template_data['frequency'] = event.frequency

        # relationships = PersonEvent.query().fetch()
        # template_data['results'] = ""
        # for relationship in relationships:
        #     if relationship and relationship.person and relationship.person.get():
        #
        #         logging.info(relationship.person.get().name)
        #         logging.info(template_data['name'])
        #
        #         if relationship.event.id() == event.key.id():
        #         # if relationship.event.id() == template_data['name']:
        #             logging.info("there is a match fam!!!!")
        #         # if relationship.event.get().name == template_data['name']:
        #             person = relationship.person.get()
        #             person_id = str(person.userID)
        #
        #             # person_id = None
        #             # people = Person.query()
        #             # for person in people:
        #             #     if person.userID == user.user_id():
        #             #         person_id = str(user.user_id())
        #             #         break
        #
        #             template_data['results'] += "<a href='/my_profile?id=" + person_id + "'>" + person.name + "</a><br>"
        template_data['results'] = ""
        query = PersonEvent.query().fetch()

        for relationship in query:
            current_rel = relationship.event.get()
            if current_rel.name == event.name and current_rel.start_time == event.start_time:
                person = relationship.person.get()
                person_id = str(person.key.id())
                template_data['results'] += "<a href='/my_profile?id=" + person_id + "'>" + person.name + "</a><br>"

        self.response.write(template.render(template_data))


        #


    def post(self):
        user = users.get_current_user()
        people = Person.query().fetch()
        person_key = None

        # person_key = ndb.Key(Person, user.user_id())
        # person.key = Person(userID= user.user_id()).key

        for person in people:
            if person.userID == user.user_id():
                person_key = person.key
                break


        # event_key = Event.get_by_id(long(person_key.id())).key
        logging.info('=============')
        logging.info(self.request.get('id'))

        event_key = Event.get_by_id(long(self.request.get('id'))).key
        attender = PersonEvent(person = person_key, event = event_key)
        relationships = PersonEvent.query()
        logging.info(relationships)
        match = False
        for relationship in relationships:
            #
            # logging.info('person_key.id()')
            # logging.info(person_key.id())
            #
            # logging.info('relationship.person.id()')
            # logging.info(relationship.person.id())
            #
            # logging.info('person names') #lol
            # logging.info(person_key.get().name + " " + relationship.person.get().name)
            #
            # logging.info('event_key.id()')
            # logging.info(event_key.id())
            #
            # logging.info('relationship.event.id()')
            # logging.info(relationship.event.id())
            #
            # logging.info('event names')
            # logging.info(event_key.get().name + " " + relationship.event.get().name)

            if (person_key.id() == relationship.person.id() and event_key.get().name == relationship.event.get().name):
                match = True
                logging.info("there is a match in relationships! noswag")
        if not match:
            attender.put()
            logging.info("no relationship match swag")
        self.redirect('/my_profile')


routes = [
    ('/',MainHandler),
    ('/home', Home),
    ('/about', AboutPage),
    #('/saved', SavedHandler),
    ('/romeo', RomeoHandler),
    ('/map', MapHandler),
    ('/forms', FormHandler),
    ('/my_profile', ProfileHandler),
    ('/create_profile', CreateProfileHandler),
    ('/event', EventHandler)
]

app = webapp2.WSGIApplication(routes, debug=True)

jinja_environment= jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))
