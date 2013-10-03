# coding: utf-8
import threading
import time
import os
import sys
import termios
import fcntl

from Controller import Controller


def getch():

	fd = sys.stdin.fileno()

	oldterm = termios.tcgetattr(fd)
	newattr = termios.tcgetattr(fd)
	newattr[3] = newattr[3] & ~termios.ICANON & ~termios.ECHO
	termios.tcsetattr(fd, termios.TCSANOW, newattr)

	oldflags = fcntl.fcntl(fd, fcntl.F_GETFL)
	fcntl.fcntl(fd, fcntl.F_SETFL, oldflags | os.O_NONBLOCK)
	try:
	  	c = sys.stdin.read(1)
	except IOError: c=None;
	finally:
		termios.tcsetattr(fd, termios.TCSAFLUSH, oldterm)
		fcntl.fcntl(fd, fcntl.F_SETFL, oldflags)
	return c

def format_time_ns(t):
	s,ns = divmod(t, 1000000000)
	m,s = divmod(s, 60)

	if m < 60:
		return "%02i:%02i" %(m,s)
	else:
		h,m = divmod(m, 60)
		return "%i:%02i:%02i" %(h,m,s)

def printable_music_info(musicrecord):
	return ("%s - %s") % (musicrecord["title"], musicrecord["artist"])

class TerminalProcessor(threading.Thread):

	def __init__(self,controller):
		threading.Thread.__init__(self)
		self.controller = controller
		self.command_buffer = [];
		self.command_ready = False;
		self.command = "";
		self.cursorpos = 0;
		self.filler_count  = 0;
		self.working = True;
		self.err_msg = "";
		self.prevtime = 0
		self.curtime = 0

	def stop(self):
		self.working = False;

	def run(self):
		self.command_ready = False;
		while self.working:
			self.update();

	def error_message(self,message):
		self.err_msg = "Error: "+message;

	def update_command_buffer(self,ch):
		if not ch:
			return;

		if ch == "\x1b[D":
				self.cursorpos -=1;

		if ch == "\x1b[C":
				self.cursorpos +=1;

		if ch == "\x1b[A":
				pass #up

		if ch == "\x1b[B":
				pass #down

		if self.cursorpos < -len(self.command_buffer):
			self.cursorpos = -len(self.command_buffer);

		if self.cursorpos > 0:
			self.cursorpos = 0;

		if len(ch) > 1:
			return;

		ch = ch[0]
		if ch == '\n':
			self.command_ready = True;
			self.command = self.command_buffer_str();
			self.filler_count = len(self.command_buffer)
			self.command_buffer = [];
			self.cursorpos = 0
			return


		if self.err_msg != "":
			self.filler_count = len(self.err_msg)
			self.err_msg = "";

		if ord(ch) == 127:
			try:
				self.command_buffer.pop();
				self.filler_count = len(self.command_buffer)
			except:
				pass
			finally:
				if self.err_msg != "":
					self.filler_count = len(self.err_msg)
					self.err_msg = "";
				return

		self.command_buffer.insert(len(self.command_buffer)+self.cursorpos,ch[0])


	def command_buffer_str(self):
		string = "";
		for c in self.command_buffer:
			string+=c;
		return string

	def left_esk_seq(self,count):
		count = - count;
		seq = "";
		for i in xrange(count):
			seq=seq+"\033[1D"
		return seq
	def reset(self):
		self.prevtime = self.curtime = 0;
		self.curtime = 0;

	def update(self):
		import readline
		import termios

		sys.stdout.write(("\r\033[1ANow playing: [%s | %s] %s\n") % (
						(format_time_ns(self.controller.get_current_song_pos_ns()),
						format_time_ns(self.controller.get_current_song_duration_ns()),
						printable_music_info(self.controller.get_current_song()))))

		message = self.command_buffer_str();
		postmessage = self.left_esk_seq(self.cursorpos);

		if (self.err_msg and len(self.command_buffer) == 0):
			message = self.err_msg

		sys.stdout.write(("%s\r> %s%s")%
						(" "*(self.filler_count+4),
						message,
						postmessage) );

		sys.stdout.flush()

		ch = getch()

		seq = "";
		while ch:
			seq = seq+ch;
			ch = getch();

		self.update_command_buffer(seq);

	def get_command(self):
		while not self.command_ready:
			time.sleep(0.1);
		self.command_ready = False;
		return self.command


class PlainUI():
	def __init__(self, controller):
		self._controller = controller;
		self._session = controller.get_session();

		self._commands = {	"h" : self._show_help,
						 	"p" : self._play,
						 	"pp" : self._pause,
						 	"s" : self._stop,
						 	">" : self._next,
						 	"<" : self._prev,
						 	"pl" : self._list_current_playlist,
						 	"fl" : self._list_friends,
						 	"fpl" : self._list_friend_playlist,
						 	"set" : self._set_playlist,
						 	"srch" : self._search,
						 	"i" : self._info,
						 	"lir": self._print_lirics,
						 }

		#allways need a default friend, who is id is yours
		self._friends = { "0":
							{
								"uid":self._session.self_uid(),
								"name":self._session.get_full_name(self._session.self_uid())
							}
						}
		#loading playlist for you
		self._set_playlist(["fpl","0"])

		#self._controller.register_callback(Controller.CB_SONG_CHANGED,self._print_commandline);
		self.cc = 0;
		self.term_processor = TerminalProcessor(self._controller);


	def _info():
		self.controller.info();
		#self._print_commandline();

	def _show_help(self, params):
		print "===============Controls======================="
		print "h - \tthis message"
		print "==============player controls================="
		print "p - \tstart playing "
		print "p XXX - \tstart playing XXX song from list"
		print "pp - \tplay/pause "
		print "s - \tstop plaing "
		print "> - \tnext song"
		print "< - \tprev song"
		print "==============playlist controls=================";
		print "pl (playlist) - \tlist current playlist"
		print "fl (friendslist)- \tlist all friends"
		print "fpl (friendplaylist)- \tlist all songs from XXXX friend playlist"
		print "srch (search)- \t search for keyword"
		print "rcm - \t recomendations"
		print "set fpl  - \tswitch to XXXX friend playlist"
		print "set srch - \tswitch to keyword playlist"
		print "set rcm - \tswitch to keyword playlist"
		print "lir - \t get current playing lirics"
		print ""
		print "0 - is You number!\n\n"

	def _print_list(self, data, params):
		count = len(data)

		frm = 0;
		to = 0;

		try:
			frm = int(params[0]);
			to = int(params[1]);
		except:
			pass

		if to == frm:
			to = len(data);
			frm = 0;


		for i in range( min(frm,to), max(frm,to) ):
			print ("%d:\t %s")%(i, data[i]) ;

	def _play (self, params):
		self._controller.play();

	def _pause (self, params):
		self._controller.pause();

	def _stop (self, params):
		self._controller.stop();

	def _next (self, params):
		n = 1
		try:
			n = int(params[0])
		except:
			pass

		for i in xrange(n):
			self._controller.next_song();
		self.term_processor.reset()

	def _prev (self, params):
		n = 1
		try:
			n = int(params[0])
		except:
			pass

		for i in xrange(n):
			self._controller.prev_song();
		self.term_processor.reset()


	def _list_friends (self, params = []):
		print "listing friends"
		data = self._session.get_friends();

		print ("0:\t%s") % (self._friends["0"]["name"])

		printabledata = [];
		printabledata.append(("%s")%(self._friends["0"]["name"]))
		i = 1;
		for d in data:
			fstr = ("%s %s")%(d["first_name"], d["last_name"]);
			printabledata.append(fstr)
			da = {"uid":str(d["uid"]),"name":fstr};
			self._friends[str(i)] = da;
			i+=1;

		self._print_list(printabledata, params)

	def _list_friend_playlist (self, params):
		try:
			no = int(params[0])
		except:
			return
		uid = self._friends[str(no)]["uid"];
		music = self._session.get_audios("friend",uid);

		printabledata = [printable_music_info(m) for m in music];
		self._print_list(printabledata,params[1:]);

	def _search(self,params):
		keyword = params[0];
		if len(params)>1:

			for p in params[1:]:
				try:
					keyword = keyword +"+" + p;
				except:
					continue

		music = self._session.get_audios("search",keyword);
		printabledata = [printable_music_info(m) for m in music];
		self._print_list(printabledata,len(printabledata));

	def _recomendations(self,params):
		music = self._session.get_audios("recomendations");
		printabledata = [printable_music_info(m) for m in music];
		self._print_list(printabledata,params[1:]);

	def _list_current_playlist(self,params):
		try:
			no = int(params[0])
		except:
			pass
		music = self._controller.get_current_playlist();

		printabledata = [printable_music_info(m) for m in music];
		self._print_list(printabledata,params[1:]);

	def _print_lirics(self,params):
		print self._controller.get_current_lirics();

	def _set_playlist(self, params):

		if params[0] == "fpl":
			self._controller.load_playlist("friend",self._friends[params[1]]["uid"]);
		if params[0] == "srch":
			keyword = params[1];
			if len(params[1:])>1:

				for p in params[2:]:
					try:
						keyword = keyword +"+" + p;
					except:
						continue

			self._controller.load_playlist("search",keyword);
		if  params[0] == "rcm":
			self._controller.load_playlist("recomendations","");


	def process_ui(self):
		self.term_processor.start()
		while True:
			#cmd = raw_input()
			cmd = self.term_processor.get_command();
			#self.term_processor.update()

			#cmd = None;

			#if self.term_processor.command_ready:
			#	cmd = self.term_processor.get_command()

			if cmd == "exit":
				return;

			if cmd:
				try:
					cmd = cmd.split();
					self._commands[cmd[0]](cmd[1:])
				except BaseException as exc:
					self.term_processor.error_message(str(exc))

	def end_ui(self):
		self.term_processor.stop();
		del self._controller;