""" Flask app to extract word of the day
"""
import datetime
import requests

from lxml import html
from flask import Flask
from flask import render_template
from flask import jsonify
from flask_scss import Scss

class Parser():
    """ Parser to extract word of the day and associated metadata
    """
    word_html = ''
    word = ''
    pronunciation = ''
    word_type = ''

    def __init__(self):
        word_url = 'http://dictionary.reference.com/wordoftheday'
        self.word_html = html.fromstring(requests.get(word_url).text)

        word_xpath = '(//*[@class="wotd-wrapper wotd-requested wotd-today"]//@data-word)'
        self.word = (self.word_html.xpath(word_xpath))[0]

        # get pronounciation and word type from the detail page
        word_detail_url = 'http://dictionary.reference.com/browse/' + self.word
        word_detail_html = html.fromstring(requests.get(word_detail_url).text)

        pronunciation_container = word_detail_html.cssselect('h3 + div')
        if not pronunciation_container:
            # no alternative spelling
            pronunciation_container = word_detail_html.cssselect('h1 + span + div')

        self.pronunciation = html.tostring((pronunciation_container[0])[1]).decode('utf-8')

        word_metadata = word_detail_html.cssselect('header')[1].cssselect('span')
        self.word_type = word_metadata[1].text_content()

    def get_definitions(self):
        """ populate a dictionary with the word definitions, keyed on word type (noun, verb, etc)
        """
        definition_list_items = (self.word_html.xpath('(//*[@class="definition-box"]/ol)[1]/li'))
        definitions = {}
        definition_list = []
        for definition in definition_list_items:
            definition_list.append(definition.text_content())

        definitions[self.word_type] = definition_list
        return definitions

    def get_quotes(self):
        """ populate a dictionary of quotes
        """
        quote_list = []
        quotes = []
        sources = []
        usages_xpath = '//*[@data-word="' + self.word + '"]/div[2]/div[2]/div/blockquote/span'
        usages = self.word_html.xpath(usages_xpath)

        for usage in usages:
            if usage.attrib.get("class") is None:
                quotes.append(usage.text_content())
            elif usage.attrib.get("class") == "author":
                sources.append(usage.text_content())
                i = 0

        for quote in quotes:
            blockquote = {
                'quote': quote,
                'source': sources[i]
                }
            quote_list.append(blockquote)
            i = i + 1

        return quote_list

    def get_origin(self):
        """ get as html to preserve em tags, and remove multiple spaces
        """
        origin = (html.tostring(self.word_html.cssselect('div.origin-content')[0])).decode('utf-8')
        return ' '.join(origin.split())

PARSER = Parser()
APP = Flask(__name__)
Scss(APP, static_dir='static/stylesheets', asset_dir='assets/scss')

@APP.route("/")
def main():
    """ word of the day page
    """
    return render_template("index.html", word=PARSER.word,
                           pronunciation=PARSER.pronunciation,
                           definitions=PARSER.get_definitions(),
                           quotes=PARSER.get_quotes(),
                           origin=PARSER.get_origin())

@APP.route("/data")
def data():
    """ word of the day as json
    """
    return jsonify(word=PARSER.word,
                   word_date=datetime.date.today().isoformat(),
                   pronunciation=PARSER.pronunciation,
                   definitions=PARSER.get_definitions(),
                   quotes=PARSER.get_quotes(),
                   origin=PARSER.get_origin())

if __name__ == "__main__":
    APP.run()
