#!/usr/bin/python
import ast
import codecs
import os
import sys

import utils


class GeoSearchClass(object):
    """Create a geo search with data validation

    For examples of usages, see geotweets.py

    Usage:
    g = GeoSearchClass()
    g.latitude =37.7821
    g.longitude =-122.4093
    g.radius =3
    g.search_term="#SF"
    g.result_type='mixed'
    g.count = 15

    Simple example:
    g = GeoSearchClass()
    g.search()
    g.print_search_results()

    OR to properly initialize:
    g = GeoSearchClass(params_filename, consumer_key_and_secret_filename)

    To initialize the geosearchclass with a parameter file and the
    consumer key and secret file:
    g = GeoSearchClass(params_filename,consumer_key_and_secret_filename)
    and use:
    g.search()
    g.print_search_results()
    """

    def __init__(self, params_file='params.txt',
                 keys_file="consumerkeyandsecret",
                 api=None):
        if params_file:
            self.set_params_from_file(params_file)
        else:
            self.use_default_params()
        self.keys_file = keys_file
        if api:
            self.api = api
            self.credits_retrieved = True
        # elif self.get_creds(keys_file):
        #     self.credits_retrieved = True
        else:
            self.credits_retrieved = False

    def use_default_params(self):
        self._search_term = None
        self._result_type = "mixed"
        self._count = 15
        self._latitude = 37.7821
        self._longitude = -122.4093
        self._radius = 3
        self._geo_string = None
        self.search_results = None

    def set_params_from_file(self, filename):
        with codecs.open(filename, encoding='utf-8', mode='rU') as f:
            params = dict()
            params.update(ast.literal_eval(f.read()))
        for key in params.keys():
            print key + ' : ' + str(params[key])
        self._latitude = params['latitude']
        self._longitude = params['longitude']
        self._radius = params['radius']
        self._search_term = params['search_term']
        self._result_type = params['result_type']
        self._count = params['count']
        self.tweet_text = params['tweet_text']

    def search(self):
        '''Perform a geolocated search using the class attributes
        'search_term', 'result_type', 'count', and 'geo_string'.

        Requires an api object as returned by the tweepy module.

        USAGE:
        search_results = search(api)
        
        See: http://docs.tweepy.org/en/v3.5.0/api.html#API.search
        '''
        if not self.credits_retrieved:
            (self.api, __) = utils.get_credentials(self.keys_file, True)
            self.credits_retrieved = True
        geo_string = getattr(self, "geo_string")
        if self._geo_string is None:
            raise Exception("initialize geo string")
        search_results = self.api.search(q=self._search_term,
                                         geocode=geo_string,
                                         result_type=self._result_type,
                                         count=self._count)
        self.search_results = search_results
        return self.search_results

    def print_search_results(self):
        '''Pretty prints the list of SearchResult objects returned using the
        api.search method.

        The results are formated and give some info about the tweet.

        '''

        # printSROInfo()   #This is for SRO object investigation
        search_results = self.search_results
        print "Actual number of tweets returned from Twitter: " + str(len(
            search_results))

        for sr in search_results:
            print
            print '@' + sr.user.screen_name
            if sr.geo:
                print 'coordinates = ' + str((sr.geo)['coordinates'])
            print "created_at = " + str(sr.created_at)
            print "tweet id: " + str(sr.id)
            print "retweet_count = " + str(
                sr.retweet_count) + "favorite_count = " + str(
                    sr.favorite_count)
            print sr.text

    def write_search_results(self, output_file=u'output.txt'):
        '''Writes search results to output file, defaults to "output.txt".


        USAGE:
        write_results( output_file = 'output.txt')


        Details: It uses unicode encoding to capture all of the
        possible tweet characters. It gets the filesystemencoding for
        each OS.

        '''
        search_results = self.search_results
        tweet_text = u''
        for sr in search_results:
            coords = u''
            if sr.geo:
                coords = u'     coordinates = ' + str((sr.geo)['coordinates'])
            s = u'\n\n\n@' + sr.user.screen_name + coords + u' : \n' + sr.text

            tweet_text = tweet_text + s

        # print tweet_text
        # print "tweet text type = " + str(type(tweet_text))
        fileSystemEncoding = sys.getfilesystemencoding()
        # OUTPUT_FILE = os.path.expanduser(u'./output.txt')
        OUTPUT_FILE = os.path.expanduser(u'./' + output_file)
        # with codecs.open(OUTPUT_FILE, encoding='utf-8', mode="w") as f:
        with codecs.open(OUTPUT_FILE,
                         encoding=fileSystemEncoding,
                         mode="w") as f:
            f.write(tweet_text)
        return

    def json_search_results(self, output_file='search_results.json'):
        '''Writes search results as json to output file 'search_results.json


        USAGE:
        json_search_results( output_file = 'search_results.json')


        Details: It uses unicode encoding to capture all of the
        possible tweet characters. It gets the filesystemencoding for
        each OS.

        '''
        import json
        print 'writing results to file {}'.format(output_file)
        fileSystemEncoding = sys.getfilesystemencoding()
        # OUTPUT_FILE = os.path.expanduser(u'./output.txt')
        OUTPUT_FILE = os.path.expanduser(u'./' + output_file)
        # with codecs.open(OUTPUT_FILE, encoding='utf-8', mode="w") as f:
        with codecs.open(OUTPUT_FILE,
                         encoding=fileSystemEncoding,
                         mode="w") as f:
            for sr in self.search_results:
                j = json.dumps(sr._json, indent=1)
                f.write(j)
        return

    def _print_SRO_info(self):
        '''
        This gives a verbose amount of info about the SearchResult object

        USAGE:
        print_SRO_info()
        '''
        search_results = self.search_results
        print '\n\n\n\n'
        print 'The methods of each SearchResult object :'
        print dir(search_results[0])
        print '\n\n\n\n'
        print 'The methods of each User object in a SRO:'
        print dir(search_results[0].user)
        print '\n\n\n\n'
        print 'Example of the first SRO object:'
        sr1 = search_results[0]
        print sr1.created_at
        # print sr1.retweets
        print sr1.retweet_count
        # print sr1.favorite
        # print sr1.favorited
        print sr1.favorite_count

    @property
    def count(self):
        "Number of results to return"
        return self._count

    @count.setter
    def count(self, value):
        if isinstance(value, basestring):
            value = float(value)
        if isinstance(value, (float, int)):
            if not (value > 0 and value < 101 and value == int(value)):
                raise ValueError(
                    "count is '" + str(value) +
                    "' but count must be an integer and 0 < count < 101")
        self._count = value

    @property
    def result_type(self):
        "Type of results to return: mixed, popular or recent"
        return self._result_type

    @result_type.setter
    def result_type(self, rt):
        if not (rt == "mixed" or rt == "popular" or rt == "recent"):
            raise ValueError(
                "result_type must be 'mixed', 'recent', or 'popular' NOT '" +
                str(rt) + "'")
        self._result_type = rt

    @property
    def latitude(self):
        "90 > Latitude > -90"
        return self._latitude

    @latitude.setter
    def latitude(self, value):
        if (value == ''):
            raise ValueError("You must put in a value")
        value = float(value)
        if not (value > -90.0 and value < 90.0):
            raise ValueError("latitude must be in bounds: 90.0>latitude>-90.0")
        self._latitude = value

    @property
    def longitude(self):
        "180 > Longitude > -180"
        return self._longitude

    @longitude.setter
    def longitude(self, value):
        if (value == ''):
            raise ValueError("You must put in a value")
        value = float(value)
        if not (value > -180.0 and value < 180.0):
            raise ValueError(
                "longitude must be in bounds: 180.0>longitude>-180.0")
        self._longitude = value

    @property
    def radius(self):
        "Radius of search, must be >0"
        return self._radius

    @radius.setter
    def radius(self, value):
        if (value == ''):
            raise ValueError("You must put in a value")
        value = float(value)
        if not (value > 0):
            raise ValueError("radius must be > 0.0 miles")
        self._radius = value

    @property
    def geo_string(self):
        "Formats the geo string using latitude, longitude and radius"
        self._geo_string = str(self._latitude) + "," + \
            str(self._longitude) + "," + str(self._radius) + "mi"
        return self._geo_string


def att_test(obj, atr, val_list):
    '''
    Perform a unit test on attributes of a class

    USAGE:
    att_test(this_object, attribute_name_as_string, values_to_test_as_list)
    '''
    print "\n\nTesting " + atr + " validation"
    for val in val_list:
        try:
            print "trying to set attribute to " + str(val)
            setattr(obj, atr, val)
        except ValueError as e:
            print e


def main():
    c = GeoSearchClass()

    print c.__doc__
    print c.__dict__
    # att_test(c, "count", [1,35, 101, -1, 3.5, "hello", "15"])
    # att_test(c, "result_type", ["mixed","popular","recent","other",15, " mIxEd"])
    # att_test(c,"latitude",[0, -90, 90, 300, "-50", "hello", 1.3])
    # att_test(c,"longitude",[0, -180, 180, 300, "-100", "hello", 1.3])
    # att_test(c,"radius",[0, -1, 10, 100, 1000])
    print "\n\ncurrent geo_string " + c.geo_string
    print c.result_type


if __name__ == '__main__':
    main()
