#!/usr/bin/env python
# coding: utf-8
import getpass
import sys
import gtk

from VKSession import VKSession
from Player import Player
from Controller import Controller
from GUI import *

if __name__ == '__main__':

	print "Hello! Login please!";
	print "\n"
	login = raw_input("Login: ");
	password = getpass.getpass("Password:");

	session = VKSession();
	session.login(login,password);

	print ("Hello, %s" ) % (session.get_full_name(session.self_uid()));
	print ("You got %d audios.\n") % (len(session.get_audios("friend",session.self_uid())));

	player = Player();
	controller = Controller(session, player);


	ui = PlainUI(controller);

	try:
		ui.process_ui()
	except:
		ui.end_ui();
		raise


	print "Bye bye!";




