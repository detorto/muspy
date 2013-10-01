#!/usr/bin/env python
# coding: utf-8

from Player import Player

class Controller():

	CB_SONG_CHANGED="songchanged"

	def __init__(self, session, player):
		self._player = player;
		self._player.register_callback(Player.CB_SONG_END, self.next_song);
		self._session = session;
		self._playlist = [];
		self._current_playing = 0;
		self._callbacks = {Controller.CB_SONG_CHANGED : self.empty_callback}

	def empty_callback(self):
		pass

	def register_callback(self, name, callback):
		if name not in self._callbacks.keys():
			raise BaseException("No such callback, %s" % name);
		self._callbacks[name] = callback;

	def next_song(self):
		self._player.stop();
		self._current_playing += 1;
		self.play()
		self._callbacks[Controller.CB_SONG_CHANGED]();

	def prev_song(self):
		self._player.stop();
		self._current_playing -= 1;
		self.play()
		self._callbacks[Controller.CB_SONG_CHANGED]();

	def song_by_nom(self, no):
		self._player.stop();
		self._current_playing = int(no);
		self._callbacks[Controller.CB_SONG_CHANGED]();

	def get_current_lirics(self):
		try:
			lir_id = self._playlist[self._current_playing]["lyrics_id"];
		except:
			return "No lirics for this song"


		return self._session.get_lirics(lir_id)
	def play(self):
		self._player.set_url(self._playlist[self._current_playing]["url"]);
		self._player.play();

	def pause(self):
		self._player.pause();

	def stop(self):
		self._player.stop();

	def load_playlist(self, atype, data):
		self._playlist = self._session.get_audios(atype,data);

	def get_current_uid(self):
		pass;

	def get_current_playlist(self):
		return self._playlist

	def get_current_song(self):
		return self._playlist[self._current_playing];

	def get_current_song_duration_ns(self):
		try:
			ns = self._player.get_duration_ns();
			return ns
		except:
			return 0;

	def get_current_song_pos_ns(self):
		try:
			ns = self._player.get_pos_ns()
			return ns

		except:
			return 0;

	def info():
		self.player.info();

	def get_session(self):
		return self._session;