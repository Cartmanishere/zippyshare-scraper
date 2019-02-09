import re
import json
import requests
import urllib.parse
from bs4 import BeautifulSoup

class ZippyLink():
	def __init__(self):
		self.REGEX_1 = r'(\(\'dlbutton\'\)\.href = )(.*)(\;)'
		self.zippy = []
		self._links = []
		# self.REGEX_2 = r'(\")(.*)(\/\")(.*)(\")(.*)(\")'
		self.REGEX_2 = r'(\".*\")(\+)(.*)(\+)(\".*\")'
		self.REGEX_3 = r'(var a = )([0-9]+);'
		self._session = requests.Session()

	def do_main(self):
		''' Main function which returns the list of download links '''

		self.get_links()
		print("Total Links = "+str(len(self.zippy)))
		for i in self.zippy:
			extract, status = self.parse_link(i)
			if status:
				p = self.get_domain(i)[:-1]+extract
				p, count = self.remove_redirects(p)
				print("Redirects Removed = {}\tLink = {}".format(count, p))
				self._links.append(p)

		return self._links

	def get_domain(self, link):
		return '{uri.scheme}://{uri.netloc}/'.format(uri=urllib.parse.urlparse(link))

	def get_links(self, links=None):
		if links == None:
			''' Get zippyshare links from user or file '''
			opt = input("File(f) | List(l) | dlcfile (d)? ")
			if opt.lower() == 'f':
				try:
					file = open(input("File path: "), "r")
					links = tuple(file)
					file.close()
					links = [ i[:-1] for i in links if (i != '' and i != '\n') ]
					print("File found. Beginning scraping.")
				except Exception as e:
					print(e)
					exit()

			elif opt.lower() == 'l':
				links = []
				while True:
					n = input("Link (leave blank to terminate): ")
					if n != "":
						if n!='' and re.search(r'http(s)?:\/\/', n) is not None:
							links.append(n)
					else:
						break

			elif opt.lower()=='d':
				dlcfile = input('Enter path of dlc file: ')
				if dlcfile[-3:] != 'dlc':
					print("This is not a dlc file.")
					exit()
				try:
					post_data = {'content': open(dlcfile, 'r').read()}
					r = requests.post('http://dcrypt.it/decrypt/paste', data=post_data)
					if r.status_code == 200:
						jobj = json.loads(r.content.decode())
						if jobj.get('success', None) != None:
							links = jobj.get('success').get('links', [])
						else:
							print("DLC file decryption failed.")
							exit()
					else:
						print("DLC file decryption failed.")
						exit()
				except Exception as e:
					print(e)
					exit()

			else:
				print('\nPlease enter correct option.\n\n')
				exit()


		self.zippy = links

	def get_text_block(self, link):
		''' Extracts the part that contains the expression '''
		r = self._session.get(link)
		soup = BeautifulSoup(r.content, "lxml")
		text = ''
		for i in soup.find_all("script"):
			text += i.text

		return text


	def remove_redirects(self, link):
		''' Removes zippyshare redirects for ad and return direct downloadable link '''
		count = -1
		headers = {"Range": "bytes=0-200"}
		new_link = link
		while True:
			count += 1
			p = self._session.get(new_link, headers=headers)
			if p.headers.get('Content-Type', None) == None:
				print("No content-type header sent. Manually analyse the following link.")
				print(new_link)
				exit()
			else:
				if p.headers.get('Content-Type') == 'text/html;charset=UTF-8':
					extract, status = self.parse_link(new_link)
					if status:
						new_link = self.get_domain(new_link)[:-1]+extract

				else:
					if p.content != None:
						''' The link is probably clear at this point but can't be sure if there are some hidden redirects'''
						return new_link, count



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
				print(expression)
			#  	return None, False
			# a = self.get_value_of_a(block)
			# if a == None:
			# 	print("REGEX 3 failed.")
				return None, False
			else:

				part_1 = parts.group(1).replace("\"", '')
				a = self.get_value_of_a(block)
				b = 3 # Currently hardcoded in their sourcecode

				part_2 = (a ** 3) + b

				part_3 = parts.group(5).replace('"', '')

				# part_3 = parts.group(8)

				extract = "{}{}{}".format(part_1, part_2, part_3)
				extract = re.sub('/pd/', '/d/', extract)

				return extract, True		

	def get_value_of_a(self, script_block):
		matcher = re.search(self.REGEX_3, script_block)
		if matcher == None:
			return None

		a = int(matcher.group(2))
		return a


if __name__ == "__main__":
	parser = ZippyLink()
	links = parser.do_main()
	file = open('links.txt', 'w')
	for i in links:
		file.write(i+"\n")

	file.close()
