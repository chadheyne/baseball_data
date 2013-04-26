import sys, os
from cx_Freeze import setup, Executable

includes = ["datetime", "email", "smtplib", "os", "email.mime.base", "email.mime.multipart", "email.mime.text",   \
			"PyQt4.QtGui", "PyQt4.QtCore", "PyQt4.QtWebKit", "collections", \
			"urllib", "sys", "time", "csv", "os", "datetime", \
			"os", "re", "sys", "bs4", "collections", "urllib", "time", "csv", "json", "requests", "download", "promo_interface", "email_data"]

includefiles = ['Data/MLB 2013 Req Daily Info - Websites.csv', 'Data/MLB 2013 - Allergy codes.csv']

packages = ["datetime", "email", "smtplib", "os", "email.mime.base", "email.mime.multipart", "email.mime.text",   \
			"PyQt4.QtGui", "PyQt4.QtCore", "PyQt4.QtWebKit", "collections", \
			"urllib", "sys", "time", "csv", "os", "datetime", \
			"os", "re", "sys", "bs4", "collections", "urllib", "time", "csv", "json", "requests", "download", "promo_interface", "email_data"]
eggsacutibull = Executable(
	script = "baseball_interface.py",
	initScript = None,
	base = 'Win32GUI',
	targetName = "baseball_interface.exe",
	compress = True,
	copyDependentFiles = True,
	appendScriptToExe = True,
	appendScriptToLibrary = False,
	icon = None
	)




setup(
		name = "Baseball Data",
		version = "0.1",
		author = 'Chad',
		description = "Crawl Websites for Data.",
		options = {"build_exe": {"includes":includes, 'include_files':includefiles, 'packages':packages}},
		executables = [eggsacutibull]
		)