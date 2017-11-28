from flask import Flask
app=Flask(__name__, static_url_path = "/")
@app.route("/")
def main():
	#serve main page
	return app.send_static_file('demo/index.html')
if __name__ == "__main__":
    app.run()
