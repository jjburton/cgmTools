
import typeFactories


class EventId(int): pass


class EventManager(object):
	__metaclass__ = typeFactories.SingletonType

	def __init__( self ):
		self._events = {}
	def createEventId( self ):
		'''
		returns a new, unique EventId object that can be used to register events using
		'''
		eventIds = self._events.keys()
		eventIds.sort()

		if eventIds:
			newEventId = EventId( eventIds[-1] + 1 )
		else:
			newEventId = EventId(0)

		self._events.setdefault( newEventId, [] )

		return newEventId
	def addEventCallback( self, eventId, eventCallback ):
		'''
		adds the given callable object to the list of callbacks for the given EventId.  The arguments expected by the
		callback is the responsibility of the code that triggers the event.
		'''
		if not isinstance( eventId, EventId ):
			raise TypeError( "You must provide an EventId instance when adding an event callback!" )

		try:
			eventCallbacks = self._events[ eventId ]
		except KeyError:
			raise KeyError( "The event given has not been registered yet!" )

		if eventCallback not in eventCallbacks:
			eventCallbacks.append( eventCallback )
	def triggerEvent( self, eventId, *a, **kw ):
		'''
		call this when you actually want to execute the events that have been registered for the given event.  Any args
		and kwargs passed to this method are handed to the callbacks being executed.
		'''
		if not isinstance( eventId, EventId ):
			raise TypeError( "You must provide an EventId instance when triggering an event!" )

		#bail if there are no callbacks for the event
		if eventId not in self._events:
			return

		eventCallbacks = self._events[ eventId ]
		for eventCallback in eventCallbacks:
			try:
				eventCallback( *a, **kw )
			except:
				import traceback
				traceback.print_exc()
				print "Callback %s failed"


#end
