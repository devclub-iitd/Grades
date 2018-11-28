from flask import Flask, render_template, request, Markup
from bs4 import BeautifulSoup
import requests
import threading

ACADEMICS_URL = 'https://academics1.iitd.ac.in/Academics/'


def remove_attrs(soup):
    for tag in soup.findAll(True):
        tag.attrs = None
    return soup


class getData(threading.Thread):
    def __init__(self, url, type_):
        self.url = url
        self.data = ""
        self.type = type_
        threading.Thread.__init__(self)

    def run(self):
        if(self.url is not None):
            r_loc = requests.post(
                ACADEMICS_URL + self.url, verify=False)

            soup = BeautifulSoup(r_loc.text, features="html.parser")
            soup_without_attributes = remove_attrs(soup)
            final_soup = soup_without_attributes.findAll(
                'table')[0].findAll('table')[1].findAll('table')
            if(self.type == "new"):
                final_soup = final_soup[2]
                for x in final_soup.find_all():
                    if len(x.text) == 0:
                        x.extract()
                self.data = str(final_soup)
            else:
                for div in final_soup:
                    for x in div.find_all():
                        if len(x.text) == 0:
                            x.extract()
                limit = len(final_soup)
                for i in range(2, limit):
                    self.data += str(final_soup[i])

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

    if (new_grades_url is None) and (all_grades_url is None):
        return (True, "Invalid Login Credentials")

    all_grades_thread = getData(all_grades_url, "all")
    all_grades_thread.start()
    new_grades_thread = getData(new_grades_url, "new")
    new_grades_thread.start()

    all_grades_thread.join()
    new_grades_thread.join()

    grades_str = new_grades_thread.get_fetched_data()
    grades_str += all_grades_thread.get_fetched_data()

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
        grades = Markup(res)
        return render_template('table.html', grades=grades)


@app.route('/<path:path>')
def static_file(path):
    return app.send_static_file(path)


if __name__ == "__main__":
    app.run(port=5051)
