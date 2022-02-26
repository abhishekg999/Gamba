from __main__ import app

from flask import request, jsonify, flash
from flask import abort, redirect, url_for


from markupsafe import escape
import json

import random
import sqlite3
from sqlite3 import Error


def check_login(username, password):
	return True



@app.route('/login', methods=['POST'])
def login():
	username = escape(request.form['username'])
	password = escape(request.form['password'])
	if(check_login(username, password)):
		ret = {
			"login" : "true",
			"message" : "Login Successful"
		}
	else:
		ret = {
			"login" : "false",
			"message" : "Invalid username/password"
		}
	return jsonify(ret)


@app.route('/signup', methods=['POST'])
def signup():
	ret = {}
	return jsonify(ret)
