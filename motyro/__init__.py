# encoding=utf8

import logging

from flask import Flask, Blueprint, Request, Markup, render_template, url_for, send_from_directory
from jinja2 import PrefixLoader, PackageLoader, ChoiceLoader
from werkzeug.routing import BaseConverter
from werkzeug.utils import secure_filename
from socket import getfqdn
from os import path, listdir
from markdown import markdown
from re import findall
from imp import load_source
#debug purpose
from traceback import print_exc

class MotyroNode( object ):
	def __init__( self, *args, **kwargs ):
		super( MotyroNode, self ).__init__()

	def __getattribute__( self, key ):
		try:
			#print 'DEBUG: searching for "get_' + key + '"' 
			value = object.__getattribute__( self, 'get_' + key )()
		except AttributeError:
			#print 'DEBUG: searching for "' + key + '"' 
			value = object.__getattribute__( self, key )
		#print 'DEBUG: ...found ' + str(value) + '"' 
		return value

	def __setattr__( self, key, value ):
		setter = getattr( self, 'set_' + key, None )
		if callable( setter ):
			setter( value )
		else:
			object.__setattr__( self, key, value )

	def get_id( self ):
		return id_sep.join( [ self.host, self.type, self.name ] )

	def set_id( self, value ):
		raise MoyroError( '"id" is not writtable' )

	def get_name( self ):
		return getattr( self, '__name__' )

	def set_name( self, value ):
		setattr( self, '__name__', value )

	def get_host( self ):
		return getattr( self, '__host__', getfqdn() )

	def set_host( self, value ):
		setattr( self, '__host__', value )

	def get_type( self ):
		return self.__class__.__name__

	def set_class( self, value ):
		raise MotyroError( '"type" is not writtable' )

class Motyro( MotyroNode ):
	def __new__( cls, *args, **kwargs ):
		if not hasattr( cls, '__instance__' ):
			try:
				cls.name = args[0]
			except IndexError, error:
				cls.name = kwargs.get( 'name', 'Motyro' )
			cls.__app__ = Flask( __name__, static_folder = None )
			cls.__path__ = path.dirname( __file__ )
			cls.__instance__ = super( Motyro, cls ).__new__( cls )
			cls.__instance__.setup()
		return cls.__instance__

	def setup( self, setup_file = None ):
		if not setup_file:
			setup_file = '../setup.json'
		for file_name in set( [ 'setup.json', setup_file ] ):
			self.app.config.from_json( setup_file )

	def get_app( self ):
		if not self.__app__:
			return self.new()
		return self.__app__

	def get_path( self ):
		return self.__path__

	def get_module_folder( self ):
		try:
			return self.__module_folder__
		except AttributeError, error:
			self.__module_folder__ = self.get_config( 'module_folder', 'modules' )
			return self.__module_folder__

	def set_module_folder( self, value ):
		object.__setattr__( '__module_folder__', value )

	def set_path( self, value ):
		if path.exists( value ):
			return setattr( self, '__path__', value )
		raise MotyroError( '"' + value + '" path is not valid' )

	def get_url_map( self ):
		return getattr( self.app, 'url_map' )

	def get_run( self ):
		return getattr( self.app, 'run' )

	def get_modules( self, rebuild = False ):
		try:
			return self.__modules__
		except AttributeError, error:
			self.__modules__ = []
			for module in listdir( self.path + path.sep + self.module_folder ):
				try:
					self.__modules__.append( MotyroModule( module ) )
				except Exception, import_error:
					print_exc()
					logging.error( import_error )
			return self.__modules__

	def set_modules( self, value ):
		raise MotyroError( '"modules" is not writtable' )

	def get_config( self, *args ):
		config = self.app.config
		if len( args ):
			try:
				return config.get( args[0], args[1] )
			except IndexError, error:
				return config.get( args[0] )
		return config

	def set_config( self, *args ):
		received = 'a ' + ' and a '.join( map( lambda arg: arg.__class__.__name__ ), args )
		if len( args ) == 1:
			self.app.config.update( args[0] )
		elif len( args ) == 2:
			self.app.config.update( { args[0]: args[1] } )
		else:
			raise MotyroError( '< ' + self.__class__.__name__ + '.config > should receive a dict object or a pair of strings. Not ' + received + '.'   )

	def resource_filter( self, *resources ):
		resource_filter = lambda module: True # all modules are valid
		if len( resources ):
			resource_filter = lambda module: set( resources ).intersection( module.resources ) # modules are valid if one or more resources match
		return filter( resource_filter, self.modules )

	def add_route( self, url, target ):
		route_callback = target
		if not callable( target ):
			def route_callback( filename, static_folder = target **options ):
				#callback for static folders
				return send_from_directory( secure_filename( static_folder ), secure_filename( filename ), **options )
		self.app.route( url )( route_callback )


class MotyroModule( MotyroNode ):

	def __init__( self, module, **kwargs ):
		self.app = kwargs.get( 'parent', Motyro() )
		self.path = path.sep.join( [ self.app.path, self.app.module_folder, module ] )
		if path.isdir( self.path ):
			self.path = self.path + path.sep + '__init__.py'
		self.module = load_source( module, self.path )
		self.setup()

	def setup( self ):
		#search for themes, pages and other resources in modules (other resources may become new other classes)
		module_elements = filter( lambda module: isinstance( module, MotyroModuleElement ),  )
		for module_element in module_elements:
			module_element.module = self.module


class MotyroModuleElement( MotyroNode ):

	def __init__( self, name, module=None, *args, **kwargs ):
		self.motyro = kwargs.get( 'motyro', Motyro() )
		self.name = name
		self.module = module # would be nice a way to auto identify the module
		super( MotyroModuleElement, self ).__init__( self )


class MotyroPage( MotyroModuleElement ):

	def get_template( self ):
		return self.__template_name__

	def set_template( self, template ):
		if isinstance( template, MotyroTheme ):
			self.template = template.template
		elif isinstance( template, basestring ):
			self.template = template
		else:
			raise MotyroError( 'invalid template type (' + template.__class__.__name__ + ')' )

	def set_route( self, values ):
		if isinstance( values, basestring ):
			values = [ values ]
		if isinstance( values, list ):
			for value in values:
				try:
					self.__routes__.append( value )
				except AttributeError, error:
					self.__routes__ = [ value ]
		else:
			raise MotyroError('Route must be a string or list of strings')

	def get_route( self ):
		try:
			return self.__routes__
		except AttributeError, error:
			self.__routes__ = []
			return self.__routes__

	def get_content( self ):
		def def_get_template_vars( content, self=self ):
			if callable( content ):
				self.get_template_vars = content
			elif isinstance( content, dict ):
				self.get_template_vars = lambda:content
			print self.get_template_vars
		return def_get_template_vars

	def set_content( self, value ):
		raise MotyroError( 'content is a decorator and can not be overwritten' )

	def render( self ):
		return render_template( self.template, self.template_vars )


class MotyroTheme( MotyroModuleElement ):
	def set_template_folder( self, route ):
		if isinstance( route, dict ):
			for url, folder in route.items():
				self.template_folder( ( url, folder ) )
		url, folder = route
		@self.motyro.app.route( '/' + url.strip('/') + '/<path:filename>' )
		def static_folder( filename ):
			send_from_directory( folder, filename )


class MotyroWidget( MotyroNode ):
	pass


class DefaultConverter( BaseConverter ):
	# Default value to variables when not declared and no
    def __init__(self, map, *items):
        BaseConverter.__init__(self, map)
        self.items = items
    def to_python(self, value):
        return value

class MotyroError( Exception ):
	pass

# Aux Functions which will not live here forever

def translate( text ):
	return text

def markdown_to_html( content ):
	html = markdown( content )
	return html