#!/usr/bin/env python
# coding: utf-8
import urllib2
import json

from vkappauth import VKAppAuth

VKAPPLICATION_ID = "3812530"
VKAPI_URLSTRING = "https://api.vk.com/method/%s?%s&access_token=%s";

class VKSession():

	def __init__(self):
		self._vk_auth = VKAppAuth()
		self._vk_data = None

	def login(self, login, pwd):
		scope = ['audio', 'offline', 'friends']
		self._vk_data = self._vk_auth.auth(login, pwd, "3812530", scope)
		return self;

	def access_token(self):
		return self._vk_data["access_token"];

	def self_uid(self):
		return self._vk_data["user_id"];

	def api_query(self, method,data):
		data = "&".join(["%s=%s" % (k, v) for k, v in data.items()])

		urlstring = (VKAPI_URLSTRING)%(method,data,self.access_token())

		url = urllib2.urlopen(urlstring)

		try:
			data = json.loads(url.read())["response"];
		except:
			return [];

		if len(data) > 1:
			return data;
		else:
			return data[0];

	def get_lirics(self,lir_id):
		data = self.api_query("audio.getLyrics",{"lyrics_id":lir_id})
		return data["text"]

	def get_full_name(self, uid):
		data = self.api_query("users.get", {"uids":uid});
		return data["first_name"] + " " + data["last_name"];

	def get_friends(self):
		data = self.api_query("friends.get", {"uid":self.self_uid(), "fields":"uid,first_name,last_name"});
		return data;

	def get_audios(self,atype,data):
		if atype == "friend":
			return self.api_query("audio.get", {"uid":data});

		if atype == "search":
				return self.api_query("audio.search",{"q":data,"auto_complite":"1","count":100})[1:]
		if atype == "recommendations":
				return self.api_query("audio.getRecommendations",{"user_id":self.self_uid(),"shuffle":"1"});