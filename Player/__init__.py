#!/usr/bin/env python
# coding: utf-8
import pygst
pygst.require("0.10")

import gst
import gtk
import threading

class Player(threading.Thread):

	CB_SONG_END = "songend"
	CB_SONG_PAUSE = "songpause"
	CB_SONG_STOP = "songstop"
	CB_SONG_PLAY = "songplay"
	CB_SONG_ERROR = "songerror"

	def __init__(self):
		threading.Thread.__init__(self)
		self._music_stream_url = None;
		self._player = gst.element_factory_make("playbin2", "player")

		self.bus = self._player.get_bus()
		self.bus.add_signal_watch()
		self.bus.connect("message", self._on_message)
		gtk.gdk.threads_init()

		self._callbacks = { Player.CB_SONG_END : self._empty_callback,
					 		Player.CB_SONG_PAUSE : self._empty_callback,
					 		Player.CB_SONG_STOP : self._empty_callback,
					 		Player.CB_SONG_PLAY : self._empty_callback,
					 		Player.CB_SONG_ERROR : self._empty_callback }

		self.start();

	def run(self):
		gtk.gdk.threads_init()
		gtk.main()
	def _empty_callback(self):
		pass

	def _on_message(self, bus, message):
		t = message.type

		if t == gst.MESSAGE_EOS:
			self._callbacks[Player.CB_SONG_END]()

		elif t == gst.MESSAGE_ERROR:
			self.player.set_state(gst.STATE_NULL)
			err, debug = message.parse_error()
			print "Error: %s" % err, debug

	def register_callback(self, name, callback):
		if name not in self._callbacks.keys():
			raise BaseException("No such callback, %s" % name)
		self._callbacks[name] = callback;

	def info():
		pass

	def play(self):
		self._player.set_property('uri', self._music_stream_url)
		self._player.set_state(gst.STATE_PLAYING)
		self._callbacks[Player.CB_SONG_PLAY]()

	def stop(self):
		self._player.set_state(gst.STATE_NULL)
		self._callbacks[Player.CB_SONG_STOP]()

	def pause(self):
		self._player.set_state(gst.STATE_PAUSED)
		self._callbacks[Player.CB_SONG_PAUSE]()

	def set_pos_ns(self, nsec):
		pass;

	def get_duration_ns(self):
		dur_int = self._player.query_duration(gst.FORMAT_TIME, None)[0]
		if dur_int == -1:
			return 0;
		else:
			return dur_int

	def get_pos_ns(self):
			pos_int = self._player.query_position(gst.FORMAT_TIME, None)[0]
			return pos_int

	def set_url(self, url):
		self._music_stream_url = url
	def exit(self):
		gtk.main_quit()
