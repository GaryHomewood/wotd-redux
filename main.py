from lxml import html
from lxml.cssselect import CSSSelector
import requests
import datetime
from flask import Flask
from flask import render_template
from flask import jsonify

wordHtml = html.fromstring(requests.get('http://dictionary.reference.com/wordoftheday').text)
word = (wordHtml.xpath('(//*[@class="wotd-wrapper wotd-requested wotd-today"]//@data-word)'))[0]
definitions = (wordHtml.xpath('(//*[@class="definition-box"]/ol)[1]/li'))
usages = wordHtml.xpath('//*[@data-word="' + word + '"]/div[2]/div[2]/div/blockquote/span')
origin = wordHtml.cssselect('div.origin-content')[0].text_content()

wordDetailHtml = html.fromstring(requests.get('http://dictionary.reference.com/browse/' + word).text)
pronounciation = wordDetailHtml.cssselect('span.pron.spellpron')[0].text_content()
wordType = wordDetailHtml.cssselect('div.def-list > section > header')[0].text_content()

# populate a dictionary with the word definitions, keyed on word type (noun, verb, etc)
definitionDictionary = {}
definitionList = []
for definition in definitions:
	definitionList.append(definition.text_content())

definitionDictionary[wordType] = definitionList

# populate a dictionary of quotes
quotes = []
sources = []
for usage in usages:
	if usage.attrib.get("class") == None:
		quotes.append(usage.text_content())
	elif usage.attrib.get("class") == "author":
		sources.append(usage.text_content())

quoteList = []
i = 0
for quote in quotes:
	q = {
		'quote': quote,
		'source': sources[i]
			}
	quoteList.append(q)
	i = i + 1

wordDate = datetime.date.today().isoformat()

app = Flask(__name__)

@app.route("/")
def main():
    return render_template("index.html", word = word,
										pronounciation = pronounciation,
										definitions = definitionDictionary,
										quotes = quoteList,
										origin = origin)

@app.route("/data")
def data():
		return jsonify(	word = word,
										wordDate = wordDate,
										pronounciation = pronounciation,
										definitions = definitionDictionary,
										quotes = quoteList,
										origin = origin)

if __name__ == "__main__":
	app.run()
