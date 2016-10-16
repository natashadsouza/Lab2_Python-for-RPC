import logging
import spyne

logging.basicConfig(level=logging.DEBUG)

from spyne import Application, rpc, ServiceBase, \
    Integer, Unicode, AnyDict

from spyne import Iterable
from spyne import json
import spyne.protocol.http
from spyne.protocol.json import JsonDocument
from spyne.model.primitive import String
from spyne.model.complex import *
from spyne import srpc
from spyne.server.wsgi import WsgiApplication
from spyne.protocol.http import HttpRpc
import simplejson as json
import urllib2
import datetime
import re
import operator
from operator import itemgetter


class CrimeCheckService(ServiceBase):
    @rpc(float, float, float, _returns=AnyDict)
    def checkcrime(ctx, lat, lon, radius):
        crime_rec = "https://api.spotcrime.com/crimes.json?lat=%s&lon=%s&radius=%s&key=." % (lat, lon, radius)

        url_call = urllib2.urlopen(crime_rec)
        data_rec = json.load(url_call)
        crimes = data_rec['crimes']
        total_data = data_rec['crimes'] 
        crime_count = len(total_data)

        street_array = {} 
        dict_crime = {} 
        scary_streets = [] 
        time_array = {'t1': 0, 't2': 0, 't3': 0, 't4': 0, 't5': 0, 't6': 0, 't7': 0, 't8': 0}

        for crime in data_rec['crimes']:

            crime_type = crime['type']
            if not crime_type in dict_crime:
                dict_crime[crime_type] = 1
            else:
                dict_crime[crime_type] += 1

            datecheck = crime['date']
            #crime_time = CrimeCheckService.check_crimeTime(datecheck)
            #crime_time = datetime.datetime.strptime(datecheck, "%m/%d/%y %I:%M %p")
            crime_time = CrimeCheckService.check_crimeTime(datecheck)
            CrimeCheckService.street_check(crime['address'], street_array)
            CrimeCheckService.crimeOccur_time(crime_time, time_array)
        street_arrayFinal = dict(sorted(street_array.items(), key=operator.itemgetter(1), reverse=True)[:3])

        for key in street_arrayFinal:
            scary_streets.append(key)

        t1 = time_array['t1']
        t2 = time_array['t2']
        t3 = time_array['t3']
        t4 = time_array['t4']
        t5 = time_array['t5']
        t6 = time_array['t6']
        t7 = time_array['t7']
        t8 = time_array['t8']
        time_counter = {'12:01am-3am': t1, '3:01am-6:00am': t2, '6:01am-9:00am': t3, '9:01am-12noon': t4,
                        '12:01pm-3pm': t5, '3:01pm-6pm': t6, '6:01pm-9pm': t7, '9:01pm-12midnight': t8}
        time_check = {'total_crime': crime_count, 'the_most_dangerous_streets': scary_streets,
                      'crime_type_count': dict_crime,
                      'event_time_count': time_counter}
        return time_check
    @staticmethod
    def check_crimeTime(datecheck):
        date = datetime.datetime.strptime(datecheck, "%m/%d/%y %I:%M %p")
        time = date.time()
        return date

    @staticmethod
    def street_check(address, street_array):
        checker = re.search(r'([\d\w\s]+OF) & ([\w\s\d]+ST)', address, re.IGNORECASE)  # check this out
        if checker:
            st = checker.group(1)
            if not st in street_array:
                street_array[st] = 1
            else:
                street_array[st] = street_array[st] = 1
            return street_array

        checker1 = re.search(r'([\d\w\s]+ST) & ([\w\s\d]+ST)', address, re.IGNORECASE)
        if checker1:
            check_street1 = checker1.group(1)
            check_street2 = checker1.group(2)

            if not check_street1 in street_array:
                street_array[check_street1] = 1
            else:
                street_array[check_street1] += 1

            if not check_street2 in street_array:
                street_array[check_street2] = 1
            else:
                street_array[check_street2] += 1
            return street_array

        checker2 = re.search(r'([\d\w\s]+OF) & ([\w\s\d]+BL)', address, re.IGNORECASE)
        if checker2:
            st = checker2.group(1)
            if not st in street_array:
                street_array[st] = 1
            else:
                street_array[st] += 1
            return street_array

        checker3 = re.search(r'([\d\w\s]+OF) & ([\w\s\d]+AV)', address, re.IGNORECASE)
        if checker3:
            st = checker3.group(1)
            if not st in street_array:
                street_array[st] = 1
            else:
                street_array[st] = street_array[st] + 1
            return street_array

    @staticmethod
    def crimeOccur_time(crime_time, time_array):
        d = crime_time.day
        m = crime_time.month
        y = crime_time.year
        dt1 = datetime.datetime(y, m, d, 00, 01, 00)
        dt2 = datetime.datetime(y, m, d, 03, 00, 00)

        if dt1 <= crime_time <= dt2:
            time_array['t1'] += 1
            return time_array

        dt1 = datetime.datetime(y, m, d, 03, 01, 00)
        dt2 = datetime.datetime(y, m, d, 06, 00, 00)

        if dt1 <= crime_time <= dt2:
            time_array['t2'] += 1
            return time_array

        dt1 = datetime.datetime(y, m, d, 06, 01, 00)
        dt2 = datetime.datetime(y, m, d, 9, 00, 00)

        if dt1 <= crime_time <= dt2:
            time_array['t3'] += 1
            return time_array

        dt1 = datetime.datetime(y, m, d, 9, 01, 00)
        dt2 = datetime.datetime(y, m, d, 12, 00, 00)

        if dt1 <= crime_time <= dt2:
            time_array['t4'] += 1
            return time_array

        dt1 = datetime.datetime(y, m, d, 12, 01, 00)
        dt2 = datetime.datetime(y, m, d, 15, 00, 00)

        if dt1 <= crime_time <= dt2:
            time_array['t5'] = time_array['t5'] + 1
            return time_array

        dt1 = datetime.datetime(y, m, d, 15, 01, 00)
        dt2 = datetime.datetime(y, m, d, 18, 00, 00)

        if dt1 <= crime_time <= dt2:
            time_array['t6'] = time_array['t6'] + 1
            return time_array

        dt1 = datetime.datetime(y, m, d, 18, 01, 00)
        dt2 = datetime.datetime(y, m, d, 21, 00, 00)

        if dt1 <= crime_time <= dt2:
            time_array['t7'] = time_array['t7'] + 1
            return time_array

        time_array['t8'] = time_array['t8'] + 1
        return time_array


application = Application([CrimeCheckService],
                          tns='spyne.examples.lab2',
                          in_protocol=HttpRpc(validator='soft'),
                          out_protocol=JsonDocument()
                          )

if __name__ == '__main__':
    # You can use any Wsgi server. Here, we chose
    # Python's built-in wsgi server but you're not
    # supposed to use it in production.
    from wsgiref.simple_server import make_server

    wsgi_app = WsgiApplication(application)
    server = make_server('0.0.0.0', 8000, wsgi_app)
    server.serve_forever()
