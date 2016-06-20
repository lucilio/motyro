# encoding=utf8

from motyro import Motyro, MotyroTheme, MotyroPage, translate

# --- MODULE DESCRIPTOR (REQUIRED)

NAME = 'admin' # Name of this module
DESCRIPTION = "Global Settings",

# --- MODULE RESOURCES (GOOD TO HAVE :-))

admin = MotyroTheme( 'Admin' )
admin.template_folder = ( '/templates', 'templates' )

home = MotyroPage( 'Admin' )
@home.content( '/admin/<panel=home>' )
def admin_panel( panel ):
	if panel == 'home':
		admin_panel = {
		'articles': [
		{
		'...'
		}
		]
		}
	return admin_panel

widget = MotyroWidget('Admin')
@widget.content
def admin_widget( *args, **kwargs ):
	return 'Not implemented yet'

