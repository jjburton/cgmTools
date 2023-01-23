
from path import *
from misc import removeDupes


LOCALES = LOCAL, GLOBAL = 'local', 'global'
DEFAULT_XTN = 'preset'
DEFAULT_TOOL = 'zoo'

#define where the base directories are for presets
_LOCAL_BASE_DIR = Path( '~/zoo/presets/' )
_GLOBAL_BASE_DIR = Path( __file__ ).up( 2 )

class PresetError(Exception): pass


def getPresetDirs( locale=LOCAL, tool=DEFAULT_TOOL ):
	'''
	returns the base directory for a given tool's preset files
	'''
	if locale == LOCAL:
		localDir = _LOCAL_BASE_DIR / tool
		localDir.create()

		return [ localDir ]

	globalDir = _GLOBAL_BASE_DIR / tool
	globalDir.create()

	return [ globalDir ]


def listPresets( locale=LOCAL, tool=DEFAULT_TOOL, ext=DEFAULT_XTN ):
	'''
	lists the presets in a given locale for a given tool
	'''
	files = []
	alreadyAdded = set()
	for d in getPresetDirs( locale, tool ):
		if d.exists():
			for f in d.files():
				if f.name() in alreadyAdded:
					continue

				if f.hasExtension( ext ):
					files.append( f )
					alreadyAdded.add( f.name() )

	#remove duplicates
	files = removeDupes( files )
	files = [ Preset( *dataFromPresetPath( f ) ) for f in files ]

	return files


def listAllPresets( tool=DEFAULT_TOOL, ext=DEFAULT_XTN, localTakesPrecedence=False ):
	'''
	lists all presets for a given tool and returns a dict with local and global keys.  the dict
	values are lists of Path instances to the preset files, and are unique - so a preset in the
	global list will not appear in the local list by default.  if localTakesPrecedence is True,
	then this behaviour is reversed, and locals will trump global presets of the same name
	'''
	primaryLocale = GLOBAL
	secondaryLocale = LOCAL
	primary = listPresets(primaryLocale, tool, ext)
	secondary = listPresets(secondaryLocale, tool, ext)

	if localTakesPrecedence:
		primary, secondary = secondary, primary
		primaryLocale, secondaryLocale = secondaryLocale, primaryLocale

	#so teh localTakesPrecedence determines which locale "wins" when there are leaf name clashes
	#ie if there is a preset in both locales called "yesplease.preset", if localTakesPrecedence is
	#False, then the global one gets included, otherwise the local one is listed
	alreadyAdded = set()
	locales = {LOCAL:[], GLOBAL:[]}
	for p in primary:
		locales[ primaryLocale ].append( p )
		alreadyAdded.add( p.name() )

	for p in secondary:
		if p.name() in alreadyAdded: continue
		locales[ secondaryLocale ].append( p )

	return locales


def getPresetPath( presetName, tool=DEFAULT_TOOL, ext=DEFAULT_XTN, locale=GLOBAL ):
	'''
	given a preset name, this method will return a path to that preset if it exists.  it respects the project's
	mod hierarchy, so it may return a path to a file not under the current mod's actual preset directory...
	'''
	searchPreset = '%s.%s' % (presetName, ext)
	dirs = getPresetDirs(locale, tool)
	for dir in dirs:
		presetPath = dir / searchPreset
		if presetPath.exists():
			return presetPath


def findPreset( presetName, tool=DEFAULT_TOOL, ext=DEFAULT_XTN, startLocale=LOCAL ):
	'''
	looks through all locales and all search mods for a given preset name.  the startLocale simply dictates which
	locale is searched first - so if a preset exists under both locales, then then one found in the startLocale
	will get returned
	'''
	other = list( LOCALES ).remove( startLocale )
	for loc in [ startLocale, other ]:
		p = getPresetPath( presetName, tool, ext, loc )
		if p is not None: return p


def dataFromPresetPath( path ):
	'''
	returns a tuple containing the locale, tool, name, extension for a given Path instance.  a PresetError
	is raised if the path given isn't an actual preset path
	'''
	locale, tool, name, ext = None, None, None, None
	path = Path( path )
	if path.isUnder( _GLOBAL_BASE_DIR ):
		locale = GLOBAL
		path -= _GLOBAL_BASE_DIR
	elif path.isUnder( _LOCAL_BASE_DIR ):
		locale = LOCAL
		path -= _LOCAL_BASE_DIR
	else:
		raise PresetError("%s isn't under the local or the global preset dir" % file)

	tool = path[ -2 ]
	name = path.name()

	return locale, tool, name, path.getExtension()


class PresetManager(object):
	def __init__( self, tool, ext=DEFAULT_XTN ):
		self.tool = tool
		self.extension = ext
	def getPresetDirs( self, locale=GLOBAL ):
		'''
		returns the base directory for a given tool's preset files
		'''
		return getPresetDirs(locale, self.tool)
	def presetPath( self, name, locale=GLOBAL ):
		return Preset(locale, self.tool, name, self.extension)
	def findPreset( self, name, startLocale=LOCAL ):
		return Preset( *dataFromPresetPath( findPreset(name, self.tool, self.extension, startLocale) ) )
	def listPresets( self, locale=GLOBAL ):
		return listPresets(locale, self.tool, self.extension)
	def listAllPresets( self, localTakesPrecedence=False ):
		return listAllPresets(self.tool, self.extension, localTakesPrecedence)
	def savePreset( self, name, data, locale ):
		'''
		given a contents string, this convenience method will store it to a preset file
		'''
		preset = Preset( locale, tool, presetName, ext )
		preset.path().write( contentsStr )


class Preset(object):
	'''
	provides a convenient way to write/read and otherwise handle preset files
	'''
	def __init__( self, locale, tool, name, ext=DEFAULT_XTN ):
		'''
		locale should be one of either GLOBAL or LOCAL object references.  tool is the toolname
		used to refer to all presets of that kind, while ext is the file extension used to
		differentiate between multiple preset types a tool may have
		'''
		path = getPresetPath( name, tool, ext, locale )
		if path is None:
			path = getPresetDirs( locale, tool )[0] / ('%s.%s' % (name, ext))

		self._path = path
		self._locale = locale
		self._tool = tool
		self._name = name
		self._ext = ext
	def path( self ):
		return self._path
	getFilepath = path
	def locale( self ):
		return self._locale
	def tool( self ):
		return self._tool
	def up( self, levels=1 ):
		return self._path.up( levels )
	def otherLocale( self ):
		'''
		returns the "other" locale - ie if teh current instance points to a GLOBAL preset, otherLocale()
		returns LOCAL
		'''
		return LOCAL if self._locale == GLOBAL else GLOBAL
	def otherPreset( self ):
		return Preset( self.otherLocale(), self._tool, self._name, self._ext )
	def copy( self ):
		'''
		copies the current instance from its current locale to the "other" locale. handles all
		perforce operations when copying a file from one locale to the other.  NOTE: the current
		instance is not affected by a copy operation - a new Preset instance is returned
		'''
		otherPreset = self.otherPreset()
		Path.copy( self.path(), otherPreset.path() )

		return otherPreset
	def move( self ):
		'''
		moves the preset from the current locale to the "other" locale
		'''
		newPreset = self.copy()

		#delete the file from disk - and handle p4 reversion if appropriate
		self.delete()

		return newPreset
	def rename( self, newName ):
		'''
		newName needs only be the new name for the preset - extension is optional.  All perforce
		transactions are taken care of.  all instance attributes are modified in place

		ie: a = Preset(GLOBAL, 'someTool', 'presetName')
		a.rename('the_new_name)
		'''
		if not newName.endswith( self._ext ):
			newName = '%s.%s' % (newName, self._ext)

		return Path.rename( self.path(), newName, True )
	def name( self ):
		return self._name


#end
