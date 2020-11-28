import sys
import socket

def put(fileName, mySocket):
  # open the file
  fileObj = open(fileName, "r")
  # number of bytes sent
  numBytesSent = 0
  # file date
  fileData = None
  # keep sending data until it's all sent
  while True:
    fileData = fileObj.read(65536)

    # make sure EOF is not read
    if fileData:
      # get the size od the data read and convert it a string
      dataSize = str(len(fileData))

      # prepends 0's to the size string
      # until the size is 10 bytes
      while len(dataSize) < 10:
        dataSize = "0" + dataSize
      
      # prepend the size of the data to the file data
      fileData = dataSize + fileData

      # the number of bytes sent
      numBytesSent = 0

      # send the data
      while len(fileData) > numBytesSent:
        numBytesSent += mySocket.send(bytes(fileData[numBytesSent:], 'utf-8'))

    # the file has been read
    else:
      break

  # close the file
  fileObj.close()

# sends commands between client and server
def transfer(x, mySocket):
  data = x
  numBytesSent = 0

  # keep sending bytes until all the bytes are sent
  while numBytesSent != len(data):
    # send that string
    numBytesSent += mySocket.send(bytes(data[numBytesSent:], 'utf-8'))

def invalidInputResponse():
  print('ERROR::[Invalid Input]: The following commands are avaiable...')
  print('put <filename>')
  print('get <filename>')
  print('ls')
  print('quit', '\n')

def recvAll(socket, numBytes):
  # the buffer
  recvBuff = ""
  # the temporary buffer
  tempBuff = ""

  # keep receiving till all data is received
  while len(recvBuff) < numBytes:
    # attempt to receive bytes
    tempBuff = socket.recv(numBytes)

    # the other side has closed the socket
    if not tempBuff:
      break

    # add the received the bytes to the buffer
    recvBuff += tempBuff.decode('utf-8')

  return recvBuff