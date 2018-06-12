import requests
import json

class RequestHandler:
 
	def __init__(self):
		self.url = "https://api.idex.market/"
		
	def getURL(self, method):
		return self.url + method
	
	def post(self, method, params):
		res = requests.post(self.getURL(method), data = json.dumps(params))
		return res
	
	def get(self, method, params):
		res = requests.get(self.getURL(method), data = json.dumps(params))
		return res