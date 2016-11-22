import sys
import json
import requests
from bs4 import BeautifulSoup

#
# Python module for parsing and analyzing DBLP contents
# Now, DBLP has a well-defined search API, but it appears to be limited in the sense that
# I cannot, for example, easily pull out an entire venue.  To that end, I need to do the following
# Either A) Download the xml db for the DBLP which isn't huge but is still nontrivial to run through
#        B) Get the capability to parse the DBLP
# End result -- B; we have a congery of HTML, XML and json parsing going on in here.  Yay.
#
#

DBLP_BASE ='http://dblp.org/search'
DBLP_PUB = DBLP_BASE + '/publ/api'
DBLP_AUTHOR = DBLP_BASE + '/author/api'
DBLP_VENUE = DBLP_BASE + '/venue/api'

class Venue(object):
    # Venues are particular conferences
    
    def __str__(self):
        return "%4s|%10s|%80s|%50s|%50s" % ( self.score, self.id,
                                             self.venue, self.url, self.type)
    def __init__(self, v_url, v_type, v_venue, v_id, v_score):
        self.url = v_url
        self.type = v_type
        self.venue = v_venue
        self.id = v_id
        self.score = v_score
        
def gen_dblp_query(url, qstring, format='json',
                   hits = 10, firsthit = 0,
                   maxterms = 10):
    result = '%s?q="%s"&format=%s' % (url,qstring,format)
    return result

def search_venues(search_string):
    a = requests.get(gen_dblp_query(DBLP_VENUE, search_string))
    if a.status_code == 200:
        values = json.loads(a.text)
        v_list = []
        
        if values['result'].has_key('hits'):
            for v in values['result']['hits']['hit']:
                v_list.append(Venue(v['info']['url'],
                                    v['info']['type'],
                                    v['info']['venue'],
                                    v['@id'],
                                    v['@score']))
            return v_list
    else:
        return None

def fetch_conference_list(conference_url):
    """
    Fetches a dblp conference list page and provides output
    """   
    a = requests.get(conference_url)
    if a.status_code == 200:
        parsed_page = BeautifulSoup(a.text, 'html.parser')
        publications = parsed_page.findAll('ul','publ-list')
        for entry in publications:
            conferences = entry.findAll('li', 'entry editor')
            for event in conferences:
                location = event.find('link')
                print location
                data = event.find('div','data')[0]
                # Data at this point, should be a singleton
                spans = data.findAll('span')
                print spans
def fetch_conference_page(conference_url, year):
    conference_page_url = conference_url + "%04d.html" % year
    
if __name__ == '__main__':
    command = sys.argv[1]
    argument = sys.argv[2]
    if command == 'search':
        result = search_venues(argument)
        for i in result:
            print i
    elif command == 'fetch':
        fetch_conference_list(argument)
