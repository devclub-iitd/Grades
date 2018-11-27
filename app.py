from flask import Flask, render_template, request
import requests
import threading
from flask import Markup
from bs4 import BeautifulSoup

ACADEMICS_URL = 'https://academics1.iitd.ac.in/Academics/'
class getData(threading.Thread):
	def __init__(self, url, type_):
		self.url = url
		self.data = None
		self.type = type_
		threading.Thread.__init__(self)

	def run(self):
		r_loc = requests.post(
			ACADEMICS_URL + self.url, verify=False)
		if(self.type == "new" and self.url is not None):
			self.data = r_loc.text
		elif(self.url is not None):
			self.data = r_loc.text

	def get_fetched_data(self):
		return self.data


def find_grades(username, password):

	r = requests.post(ACADEMICS_URL + "index.php?page=tryLogin",
					  data={'username': username, 'password': password}, verify=False)

	soup = BeautifulSoup(r.text, features="html.parser")

	new_grades_url = None
	all_grades_url = None

	for link in soup.findAll('a'):
		link_url = link.get('href')
		if (link_url.find('vgrd') != -1):
			new_grades_url = link_url
		if (link_url.find('grade') != -1):
			all_grades_url = link_url

	all_grades_thread = getData(all_grades_url, "all")
	all_grades_thread.start()
	new_grades_thread = getData(new_grades_url, "new")
	new_grades_thread.start()

	all_grades_thread.join()
	new_grades_thread.join()

	all_grades_data = all_grades_thread.get_fetched_data()
	new_grades_data = new_grades_thread.get_fetched_data()

	if (new_grades_url is None) and (all_grades_url is None):
		return (True, "Invalid Login Credentials")

	def remove_attrs(soup):
		for tag in soup.findAll(True):
			tag.attrs = None
		return soup

	grades_str = ''

	if not(new_grades_url is None or new_grades_data is None):

		soup = BeautifulSoup(new_grades_data, features="html.parser")
		soup_without_attributes = remove_attrs(soup)
		final_soup = soup_without_attributes.findAll('table')[0].findAll('table')[
			1].findAll('table')[2]
		for x in final_soup.find_all():
			if len(x.text) == 0:
				x.extract()

		grades_str += str(final_soup)


	if not(all_grades_url is None or all_grades_data is None):

		soup = BeautifulSoup(all_grades_data, features="html.parser")
		soup_without_attributes = remove_attrs(soup)
		final_soup = soup_without_attributes.findAll(
			'table')[0].findAll('table')[1].findAll('table')
		for div in final_soup:
			for x in div.find_all():
				if len(x.text) == 0:
					x.extract()

		limit = len(final_soup)
		for i in range(2, limit):
			grades_str += str(final_soup[i])


	return (False, grades_str)


app = Flask(__name__,
			static_url_path='',
			static_folder='static',
			template_folder='templates')


@app.route("/")
def main():
	return render_template('index.html')


@app.route("/", methods=['POST'])
def main_form():
	username = request.form['username']
	password = request.form['password']
	(err, res) = find_grades(username, password)
	if(err):
		return render_template('index.html', error=res)
	else:
		grades = Markup(res.encode('ascii', 'ignore').decode())
		return render_template('table.html', grades=grades)


@app.route('/<path:path>')
def static_file(path):
	return app.send_static_file(path)


if __name__ == "__main__":
	app.run(port=5051)
