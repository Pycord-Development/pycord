# import HTMLSession from requests_html
from requests_html import HTMLSession
 
# create an HTML Session object
session = HTMLSession()
 
# Use the object above to connect to needed webpage
resp = session.get("https://www.wolfgame.tools/address/0x6e34247a8ee476282E07E07a322b934c74641993")
 
# Run JavaScript code on webpage
resp.html.render()