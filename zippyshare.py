import re
import requests
from bs4 import BeautifulSoup
from pprint import pprint
import urllib.parse

class ZippyLink():
	def __init__(self):
		self.REGEX_1 = r'(\(\'dlbutton\'\)\.href = )(.*)(\;)'
		self.zippy = []
		self._links = []
		self.REGEX_2 = r'(\")(.*)(\/\") (\+) (.*) (\+) (\")(.*)(\")'

	def domain(self):
		''' Main function which returns the list of download links '''

		self.get_links()
		print("Total Links = "+str(len(self.zippy)))
		for i in self.zippy:
			link, status = self.parse_link(i)
			if status:
				p = self.get_domain(i)[:-1]+link
				print(p)
				self._links.append(p)

		return self._links

	def get_domain(self, link):
		return '{uri.scheme}://{uri.netloc}/'.format(uri=urllib.parse.urlparse(link))

	def get_links(self, links=None):
		if links == None:
			''' Get zippyshare links from user or file '''
			opt = input("File(f) or List(l)? ")
			if opt == 'f' or opt=='F':
				try:
					file = open(input("File path: "), "r")
					links = tuple(file)
					links = [ i[:-1] for i in links ]
					print("File found. Beginning scraping.")
				except Exception as e:
					print(e)
					exit()

			else:
				links = []
				while True:
					n = input("Link (leave blank to terminate): ")
					if n != "":
						links.append(n)
					else:
						break

		self.zippy = links

	def get_text_block(self, link):
		''' Extracts the part that contains the expression '''
		r = requests.get(link)
		soup = BeautifulSoup(r.content, "lxml")
		text = ''
		for i in soup.find_all("script"):
			text += i.text

		return text

	def parse_link(self, link):
		''' Isolate the expression and extract and make the link '''
		block = self.get_text_block(link)

		matcher = re.search(self.REGEX_1, block)
		if matcher == None:
			# matching failed
			print("REGEX_1 Failed.")
			print(block)

			return None, False
		else:
			expression = matcher.group(2)
			parts = re.search(self.REGEX_2, expression)

			if parts == None:
				# matching failed
				print("REGEX_2 Failed.")

				return None, False
			else:
				part_1 = parts.group(2)
				part_2 = eval(parts.group(5))
				part_3 = parts.group(8)

				link = "{}/{}{}".format(part_1, part_2, part_3)
				link = re.sub('/pd/', '/d/', link)

				return link, True		



if __name__ == "__main__":
	parser = ZippyLink()
	links = parser.domain()
	file = open('links.txt', 'w')
	for i in links:
		file.write(i+"\n")

	file.close()
