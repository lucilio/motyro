# encoding=utf8

from markdown import markdown
from flask import Markup
from motyro import site_info, get_resource

translate = get_resource('translate')

# --- SETUP VARS
## remember all 'all caps' variables are imported into app config (only in default modules) --- some prefixes are especial like 'site_info_'

SITE_NAME = 'Motyro' 
SITE_DESCRIPTION = 'A Sua Rede Social'
SITE_LOGO_URL = '/static/img/logo.png'

# --- TRIGGERS AND HOOKS

def record( setup_state ):
	pass

# --- AUX FUNCTIONS

def translate( term, namespace='' ):
	return term # Sim essas funções são inúteis, servem apenas como inspiração.

def markdown_to_html( text ):
	return Markup( markdown( text ) )

def site_name():
	return site_info('name')

def site_description():
	return site_info('description')

def get_title():
	return translate( u'Olá' )

def not_implemented_yet():
	return translate( 'Not implemented yet... :-/' )

# --- URL_MAP FUNCTIONS
def home():
	return {
		'head': {
			'title': ' :: '.join( [ site_name(), site_description(), get_title() ] ),
			'stylesheets': ['css/style.css'],
		},
		'sections': [
			{
				'title': translate( u'Conheça o Motyro' ),
				'content': markdown_to_html(
					translate(
u'''
Motyro é uma rede social baseada na livre apropriação e no código aberto.
Foi pensada para ser a _Rede Hacker_ por excelência é também uma estrutura aberta de desenvolvimento disponível para:

 - você publicar seu conteúdo;
 - mobilizar a sua própria rede;
 - criar e conectar redes em seu próprio servidor;
 - criar e distribuir seu próprio aplicativo, apriveitando o código que nós já escrevemos.

Motyro é uma ferramenta livre, no melhor estilo WTFPL.
'''
# multiline string lines from a string intended to be filtred in a markdown parser should start in a new line
						 )
					)
				,
			}
			,
		],
		'images': {
			'logo': '/static/img/logo.png',
		},
	}

# --- MODULE DESCRIPTOR (REQUIRED)

MOTYRO_MODULE = {
	'NAME': 'default', # Name of this module
	'PAGE': True, # Resource detector - this module generates front-end page(s)
	'THEME': 'default', # Resource detector: string or list with name(s) of templates (folder) included
	'STORAGE': False, # Resource detector - this module defines a database or other storage API (save, load, erase)
	'OBJECT': False, # Resource detector - this module defines a model API (__dict__, republish, rank )
	'WIDGET_MAP': {
		'login': not_implemented_yet #login.widget.render
	}, # Maps widgets to Widget objects (the 'render' interface must return HTML -- or whatever --  to render)
	'URL_MAP': {
		'/': home,
		'/css': 'templates/css',
	}, # Maps URLs to Dictionaries containing structure of variables needed to render pages
	'TEMPLATE_FOLDER': 'templates', #this is the default value if missing. Is the container folder to theme folders.
	'STATIC_FOLDER': 'static', #this is the default value if missing. files here will be served directly to browser trhough STATIC_URL url.
	'STATIC_URL': '/static', #this is the default value if missing. Is the url path to static files in STATIC_FOLDER.
}