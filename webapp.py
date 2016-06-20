# encoding=utf8

from sys import argv
from motyro import Motyro

app = Motyro('lucilio.net')

args = map( lambda arg: arg.lower(), argv )
debug = 'debug' in args

if __name__=='__main__':
	print '\n\t\t\t\t\t*** \n' + str(app.modules)
	app.run( debug=debug )