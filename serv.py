import os
import sys
import socket
import subprocess
from functions import * 

def main():

  if len(sys.argv) < 2:
    print('Error: expecting port number - python ftp-server.py <PORT_NUM>')
    sys.exit(1) 

  #fileName = sys.argv[0]
  serverPort = int(sys.argv[1])
  # create the socket
  control_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  # bind it to a port
  control_sock.bind(('', serverPort))

  # start listening for incoming connections
  control_sock.listen(5)
  print('server socket listening on port ', serverPort)

  while True:
    sys.stdout.write('ready to receive...')
    sys.stdout.write('\n')
    sys.stdout.flush()

    cs, addr = control_sock.accept()

    tempBuff = ""
    data = ""

    # accept commands from the client
    while not len(data) == 40:
      tempBuff = ""
      data = ""

      # receive cmd from client
      tempBuff = cs.recv(40)

      # listen for unexpected closed socket
      if not tempBuff:
        break

      # decode bytes in string
      cmd = tempBuff.decode("utf-8")

      # do commands
      if cmd == 'ls':
        lsoutput = subprocess.Popen(['ls','-1'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, stdin=subprocess.PIPE)
        output = lsoutput.stdout.read()
        cs.send(output)

        sys.stdout.write(cmd + ' - Status: SUCCESS' + '\n')
        sys.stdout.flush()
        
      elif cmd == 'get':

        # get the file name
        fileName = ""
        fileName = cs.recv(40)

        # get the client socket info
        clientSockDataBytes = cs.recv(40)        
        clientSockData = clientSockDataBytes.decode('utf-8').split()
        
        #clientIpAddr = clientSockData[0]
        clientPortNum = clientSockData[1]

        # open the file 
        # if you enter a file that it cant find or doesn't exist
        # the program will throw an exception, tried to solve this but i'm too tired
        fileObj = open(fileName.decode('utf-8'), 'r')

        # create server socket
        server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # connect our new socket to the client port
        server_sock.connect(('127.0.0.1', int(clientPortNum)))

        while True:
          fileData = fileObj.read(65536)

          # make sure EOF is not read
          if fileData:
            # get the size of the data as string
            dataSize = str(len(fileData))

            # prepend 0's to dataSize until its 10 bytes long
            while len(dataSize) < 10:
              dataSize = '0' + dataSize

            # prepend dataSize to the fileData
            fileData = dataSize + fileData

            # number of bytes sent
            numBytesSent = 0

            # send the data over
            while len(fileData) > numBytesSent:
              numBytesSent += server_sock.send(bytes(fileData[numBytesSent:], 'utf-8'))

          # the file has been read
          else:
            break

        # close the file  
        fileObj.close()
        # close the socket
        server_sock.close()

        # log command status
        sys.stdout.write(cmd + ' ' + fileName.decode('utf-8') + ' - Status: SUCCESS' + '\n')
        sys.stdout.flush()

      elif cmd == 'put':

        # get the file name for logging at the end
        fileName = cs.recv(40)

        # get the client socket info
        clientSockDataBytes = cs.recv(40)        
        clientSockData = clientSockDataBytes.decode('utf-8').split()
        
        #clientIpAddr = clientSockData[0]
        clientPortNum = clientSockData[1]

        # create server socket
        server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # connect our new socket to the client port
        server_sock.connect(('127.0.0.1', int(clientPortNum)))

        # the buffer to all data received from the client
        fileData = ""

        # the temporary buffer to store the received receuved bytes
        #recvBuff = ""

        # size of the incoming file
        fileSize = 0

        # the buffer containing the file size
        fileSizeBuff = ""

        # receive the first 10 bytes indicating the filesize
        fileSizeBuff = recvAll(server_sock, 10)

        # get the file size
        fileSize = int(fileSizeBuff)

        # get the file data
        fileData = recvAll(server_sock, fileSize)

        # overwrite the contents of the 'upload.txt' file
        ul = open('upload.txt', 'w')
        ul.write(fileData)
        ul.close()

        # return file name and file size to client
        transfer(fileName.decode('utf-8'), server_sock)
        transfer(str(len(fileData)), server_sock)

        # close connection
        server_sock.close()

        # log command status
        sys.stdout.write(cmd + ' ' + fileName.decode('utf-8') + ' - Status: SUCCESS' + '\n')
        sys.stdout.flush()

    cs.close()
      
if __name__ == '__main__':
  main()

