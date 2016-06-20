# encoding=utf8

from importlib import import_module
from os import path, listdir
from warnings import warn

class MotyroError( Exception ):
	pass

class MotyroWarning( Warning ):
	pass

__all__ = set( [ entry if path.isdir( entry ) else entry.rsplit('.',1)[0] for entry in listdir( path.dirname( __file__ ) ) ] )
__exclude_modules__ = [ 'motyro_modules', '__init__'  ]
__modules__ = {}
__default_module_name__ = 'default'

def init_module( module, module_name = None ):
	global __modules__
	if module_name is None:
		module_name = module.__name__
	if not hasattr( module, 'MOTYRO_MODULE' ):
		warn( module_name + ' is not a Motyro Module', MotyroWarning )
	else:
		__modules__.update( { module_name: module } )
	def getter( *args ):
		try:
			key = args[0].upper()
			#print 'GETTER GETTING ' + key + ' FROM ' + module.__name__
		except IndexError, error:
			raise TypeError('the getter function receives at least 1 argument ( ' + str( len(args) ) + ' received )')
		module_attrs = getattr( module, 'MOTYRO_MODULE', {} )
		default_value = None
		try:
			default_value = args[1]
		except IndexError, error:
			if not key in module_attrs.keys():
				raise MotyroError( module_name + ' has not value for ' + key )
		return module_attrs.get( key, default_value )
	setattr( module, 'get', getter )
	setattr( module, 'path', path.dirname( module.__file__ ) )

def motyro_modules( resource="ALL", **kwargs ):
	load_modules()
	motyro_modules = []
	if not kwargs.get( 'deny', False ):
		deny=['motyro_modules']
	for module_name, module in __modules__.iteritems():
		#print 'RESOURCE LOOKUP: ' + resource
		if resource is "ALL" or module.get( resource, False ):
			motyro_modules.append( module )
	default_module = kwargs.get( 'default', False )
	if default_module and default_module in motyro_modules: 
		motyro_modules.append( motyro_modules.pop( motyro_modules.index( default_module ) ) )
	return motyro_modules

def load_modules():
	for module_name in __all__:
		if not module_name in __exclude_modules__:
			try:
				module = import_module( 'motyro.' + module_name )
			except ImportError, error:
				warn( error.message, MotyroWarning )
			else:
				init_module( module, module_name )