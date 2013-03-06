"""
mayaWingServer.py
Author : Eric Pavey - 2012-10-23
"""
import sys
import socket
import threading

import maya.utils as mu
import maya.OpenMaya as om

import executeWingCode

#-----------------
PORT = 6000  # Needs to be the same value as authored in wingHotkeys.py below.
SIZE = 1024
BACKLOG = 5

def processDataInMaya(data):
    """
    This function is designed to be passed as the 'processFunc' arg of
    the mayaServer function.  It is mainly a try\except wrapper around the
    executeWingCode.main() function.

    data : string : The data passed from wing.  Currently this is 'python' or 'mel'.
    """
    try:
        # If we don't evaluate in maya.util.executeInMainThreadWithResult(),
        # Maya can crash, and that's no good.
        mu.executeInMainThreadWithResult(executeWingCode.main, data)
    except Exception, e:
        om.MGlobal.displayError("Encountered exception: %s"%e)

def server(processFunc=processDataInMaya, port=PORT, backlog=BACKLOG, size=SIZE):
    """
    Create a server that will listen for incoming data from Wing, and process it.

    Modified example taken from:
    http://ilab.cs.byu.edu/python/socket/echoserver.html

    The server will wait to recieve data from a single client.  When it receives
    data, it will 'process' it via the processFunc function.

    Parameters :
    processFunc : function : A function object that will
        process the data recieved by the client.  It should accept a single
        string argument.
    port : int : Default to global PORT.  The port to connect to.
    backlog : int : Default to global BACKLOG.  The number of connections the
        server can have waiting.
    size : int : Default to global SIZE.  The size in bytes to recieve back from
        the client.
    """
    host = ''
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.bind((host,port))
    except:
        print "Tried to open port %s, but failed:  It's probably already open\n"%port
        return

    s.listen(backlog)
    print "Starting Python server, listening on port %s...\n"%port
    while True:
        client, address = s.accept() # client is a socket object
        data = client.recv(size)
        if data:
            processFunc(data)
        client.close()

def startServer():
    """
    When Maya starts up, execute this to start the Wing listener server:
    """
    threading.Thread(target=server).start()