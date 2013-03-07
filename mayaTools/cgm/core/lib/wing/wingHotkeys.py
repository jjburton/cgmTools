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

def getWingTextPython():
   """
   Josh Burton mod
   Based on the Wing API, get the selected text, and return it
   Thanks to:http://wingware.com/pipermail/wingide-users/2009-December/007332.html for insignt for mod
   """
   editor = wingapi.gApplication.GetActiveEditor()
   if editor is None:
      return
   
   doc = editor.GetDocument()
   start, end = editor.GetSelection()
   start_lineno = doc.GetLineNumberFromPosition(start)
   end_lineno = doc.GetLineNumberFromPosition(end)
   fullText = doc.GetCharRange(start, end)
   returnText = []
   #returnText.append("#fullText: %s"%fullText)
   #returnText.append("#start: %s"%start)
   #returnText.append("#end: %s"%end)
   # We want to process lines so that we can add log.info to things we want info on
   for i in range(start_lineno,end_lineno+1):
      checkState = False      
      line_start = doc.GetLineStart(i)
      line_end = doc.GetLineEnd(i)
      line_text = doc.GetCharRange(line_start, line_end)
      returnText.append("#line_text: %s"%line_text)
      #returnText.append("#line_start: %s"%line_start)
      #returnText.append("#line_end: %s"%line_end)   
      #Only do something if the entire line is in our selection
      #mc.ls(i_obj.mNode,type = 'transform',long = True)
      if line_start in range(start,end+1) and line_end in range(start,end+1) and line_start!=end:
         if len(list(line_text))>1:#Finding check for empty lines
            checkState = True         
            for key in ['from','import','def','=','   ','class',':']:
               #returnText.append("#[:3]: %s"%line_text[:3])               
               if key in line_text and line_text[:3] != 'mc.':
                  checkState = False
         if checkState:
            line_text = 'log.info('+line_text+')'
            #line_text = 'print('+line_text+')'
         returnText.append(line_text)   
   return returnText

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
   if language == 'mel':
      txt = getWingText()      
      if not txt.endswith(';'):
         txt += ';'
   if language == 'python':
      txt = getWingTextPython()
         
   # This saves a temp file on Window.  Mac\Linux will probably need to
   # change this to support their OS.
   tempFile = os.path.join(os.environ['TMP'], 'wingData.txt')
   f = open(tempFile, "w")
   if language == 'mel':
      f.write(txt)
   # Edit -- (Josh Burton) added logger and mc initialization and use our python grabber    
   if language == 'python':
      f.write('import maya.cmds as mc\n')
      f.write('import logging\n')
      f.write('logging.basicConfig()\n')
      f.write('log = logging.getLogger(__name__)\n')
      f.write('log.setLevel(logging.INFO)\n')      
      #f.write('mc.undoInfo(openChunk=True)\n')
      for l in txt:
         f.write(l+'\n')           
      #f.write('mc.undoInfo(openChunk=False)\n')   
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