import web

class RequestHandler:

	def GET(self):
		print "Received GET request"
		return "Echo from server"

	def POST(self):
		print "Received POST request"
		payload = web.data()
		return "Echoed: " + payload

def createListener():
	urlRegex = '/.*'        # Captures requests at this URL
	classHandler = 'RequestHandler'
	urls = (urlRegex, classHandler)
	return web.application(urls, globals())

if __name__ == "__main__":
	app = createListener()
	app.run()
