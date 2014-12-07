from lxml import html
from lxml.cssselect import CSSSelector
import requests
import datetime
from flask import Flask
from flask import render_template
from flask import jsonify

page = requests.get('http://dictionary.reference.com/wordoftheday')
tree = html.fromstring(page.text)

# extract content from the page
word = (tree.cssselect('h2.me'))[0].text
pronounciation = "\\" + (tree.xpath("//*[@id='wotdcont']/div[1]/div[1]/span[@class='show_spellpr']/span[@class='pron']"))[0].text_content()
wordType = tree.xpath("//*[@id='wotdcont']/div[1]/div[1]/span[@class='show_spellpr']/span[@class='pron pos']")[0].text_content().replace(";", "")
definitions = tree.xpath("//*[@id='wotdcont']/div[1]/div[@class='defns rr_wid']")
quotes = tree.cssselect('div.quote')
sources = tree.cssselect('div.au_src')
origin = (tree.xpath('//*[@id="wotdcont"]/div/div/div[@class="origin"]'))[0].text_content()

# populate a dictionary with the word definitions, keyed on word type (noun, verb, etc)
definitionDictionary = {}
definitionList = []

for definitionLine in definitions[0]:
	# check for noun/verb indicator
	if definitionLine.get('class') == "pron pos" and definitionLine.text_content():
		# add list of definitions to dictionary and reset to build another list
		definitionDictionary[wordType] = definitionList
		wordType = definitionLine.text_content().replace(":", "")
		definitionList = []

	# get the definitions and add them to the list
	for definitionElement in definitionLine:
		if definitionElement.get('class') == "defn":
			definitionList.append(definitionElement.text_content())

# add remaining list of definitions to dictionary
definitionDictionary[wordType] = definitionList

# populate a dictionary of quotes
quoteList = []
i = 0
for quote in quotes:
	q = {
		'quote': quote.text_content(),
		'source': sources[i].text_content().replace("--", "")
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
