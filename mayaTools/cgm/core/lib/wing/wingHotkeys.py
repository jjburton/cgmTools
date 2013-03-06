# wingHotkeys.py
# Author:  Eric Pavey - warpcat@sbcglobal.net

import wingapi
import socket
import os

def getWingText():
   """
   Based on the Wing API, get the selected text, and return it
   """
   editor = wingapi.gApplication.GetActiveEditor()
   if editor is None:
      return
   doc = editor.GetDocument()
   start, end = editor.GetSelection()
   txt = doc.GetCharRange(start, end)
   return txt

def send_to_maya(language):
   """
   Send the selected code to be executed in Maya

   language : string : either 'mel' or 'python'
   """
   # The port the sever is listening on in mayaWingServer.py :
   commandPort = 6000

   if language != "mel" and language != "python":
      raise ValueError("Expecting either 'mel' or 'python'")

   # Save the text to a temp file.  If we're dealing with mel, make sure it
   # ends with a semicolon, or Maya could become angered!
   txt = getWingText()
   if language == 'mel':
      if not txt.endswith(';'):
         txt += ';'
   # This saves a temp file on Window.  Mac\Linux will probably need to
   # change this to support their OS.
   tempFile = os.path.join(os.environ['TMP'], 'wingData.txt')
   f = open(tempFile, "w")
   f.write(txt)
   f.close()

   # Create the socket that will connect to Maya,  Opening a socket can vary from
   # machine to machine, so if one way doesn't work, try another... :-S
   mSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # works in 2013...
   #mSocket = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
   # More generic code for socket creation thanks to Derek Crosby:
   #res = socket.getaddrinfo("localhost", commandPort, socket.AF_UNSPEC, socket.SOCK_STREAM)
   #af, socktype, proto, canonname, sa = res[0]
   #mSocket = socket.socket(af, socktype, proto)

   # Now ping Maya over the command-port
   try:
      # Make our socket-> Maya connection:   There are different connection ways
      # which vary between machines, so sometimes you need to try different
      # solutions to get it to work... :-S
      mSocket.connect(("127.0.0.1", commandPort)) # works in 2013...
      #mSocket.connect(("::1",commandPort)) 
      #mSocket.connect(("localhost", commandPort))

      # Send our code to Maya:
      # It is intercepted via the function processDataInMaya(), created via mayaWingServer.py
      mSocket.send(language)
   except Exception, e:
      print "Send to Maya fail:", e

   mSocket.close()

def python_to_maya():
   """Send the selected Python code to Maya"""
   send_to_maya('python')

def mel_to_maya():
   """Send the selected code to Maya as mel"""
   send_to_maya('mel')