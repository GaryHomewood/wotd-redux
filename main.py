from lxml import html
from lxml.cssselect import CSSSelector
import requests
import datetime
from flask import Flask
from flask import render_template
from flask import jsonify
from flask import Markup

word_html = html.fromstring(requests.get('http://dictionary.reference.com/wordoftheday').text)
word = (word_html.xpath('(//*[@class="wotd-wrapper wotd-requested wotd-today"]//@data-word)'))[0]
definition_list_items = (word_html.xpath('(//*[@class="definition-box"]/ol)[1]/li'))
usages = word_html.xpath('//*[@data-word="' + word + '"]/div[2]/div[2]/div/blockquote/span')

# get as html to preserve em tags
origin = (html.tostring(word_html.cssselect('div.origin-content')[0])).decode('utf-8')
# remove multiple spaces
origin = ' '.join(origin.split())

# get pronounciation and word type from the detail page
word_detail_html = html.fromstring(requests.get('http://dictionary.reference.com/browse/' + word).text)
pronounciation = html.tostring((word_detail_html.cssselect('h1 + span + div')[0])[1]).decode('utf-8')
word_metadata = word_detail_html.cssselect('header')[1].cssselect('span')
word_type = word_metadata[1].text_content()

# populate a dictionary with the word definitions, keyed on word type (noun, verb, etc)
definitions = {}
definition_list = []
for definition in definition_list_items:
	definition_list.append(definition.text_content())

definitions[word_type] = definition_list

# populate a dictionary of quotes
quotes = []
sources = []
for usage in usages:
	if usage.attrib.get("class") == None:
		quotes.append(usage.text_content())
	elif usage.attrib.get("class") == "author":
		sources.append(usage.text_content())

quote_list = []
i = 0
for quote in quotes:
	q = {
		'quote': quote,
		'source': sources[i]
			}
	quote_list.append(q)
	i = i + 1

word_date = datetime.date.today().isoformat()

app = Flask(__name__)

@app.route("/")
def main():
    return render_template("index.html", word = word,
										pronounciation = pronounciation,
										definitions = definitions,
										quotes = quote_list,
										origin = origin)

@app.route("/data")
def data():
		return jsonify(	word = word,
										word_date = word_date,
										pronounciation = pronounciation,
										definitions = definitions,
										quotes = quote_list,
										origin = origin)

if __name__ == "__main__":
	app.run()
