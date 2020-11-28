#!/usr/bin/env python
import os
import sys
import socket
from functions import * 


def connect(port):
  serverName = '127.0.0.1'
  serverPort = port
  
  # create socket
  s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

  s.connect((serverName, serverPort))

  return s

def getData(mySocket):
  # get raw data from user
  x = input('ftp>')
  b = x.split(" ")
  cmd = b[0]

  # if user enters quit
  # it breaks the loop and ends the program
  while cmd != 'quit':
    if len(b) == 1:
      cmd = b[0]
    else:
      cmd = b[0]
      fileName = b[1]

    # based on user input, call appropriate function
    if cmd == 'put':

      # first send the cmd text ('put') to the server 
      transfer(cmd, mySocket)

      # send the file name over for logging
      transfer(fileName, mySocket)   

      # create the ephemeral port
      data_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
      # bind it to some available port
      data_sock.bind(('', 0)) 

      ipAddr = data_sock.getsockname()[0] 
      portNum = data_sock.getsockname()[1]
      clientInfo = ipAddr + " " + str(portNum)  

      # get the ip addr and port number for the data transfer to the server
      transfer(clientInfo, mySocket)

      data_sock.listen(1)

      while True:

        client_sock, addr = data_sock.accept()

        # for loop termination below
        servResponseFileSize = 0
        # send the file over to the server
        put(fileName, client_sock)

        # wait for the logging info from server after uploading
        servResponseFileName = client_sock.recv(40)
        servResponseFileSize = client_sock.recv(40)

        # servResponseFileSize will only be true when the full file size
        # is returned from the server, since anything other than 0 is false
        if(int(servResponseFileSize.decode('utf-8'))):
          break

      # log file name and file size 
      sys.stdout.write('File Name: ' + servResponseFileName.decode('utf-8') + '\n')
      sys.stdout.write('Bytes Transferred: ' + servResponseFileSize.decode('utf-8') + 'bytes' + '\n' + '\n')
      sys.stdout.flush()

    elif cmd == 'get':

      # send cmd text over to ftp server
      transfer(cmd, mySocket)

      # now the server is waiting for the filename
      transfer(fileName, mySocket)

      # create the ephemeral port
      data_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
      # bind it to some available port
      data_sock.bind(('', 0))

      ipAddr = data_sock.getsockname()[0] 
      portNum = data_sock.getsockname()[1]
      clientInfo = ipAddr + " " + str(portNum)

      # get the ip addr and port number for the data transfer to the server
      transfer(clientInfo, mySocket)

      # listen on this port for a server connection
      data_sock.listen(1)

      # sys.stdout.write(f'connection socket: {data_sock.getsockname()}' + '\n')
      # sys.stdout.flush()
      while True:

        client_sock, addr = data_sock.accept()

        # the buffer to all data received from the client
        fileData = ""

        # the temporary buffer to store the received receuved bytes
        #recvBuff = ""

        # size of the incoming file
        fileSize = 0

        # the buffer containing the file size
        fileSizeBuff = ""

        # receive the first 10 bytes indicating the filesize
        fileSizeBuff = recvAll(client_sock, 10)

        # get the file size
        fileSize = int(fileSizeBuff)

        # get the file data
        fileData = recvAll(client_sock, fileSize)

        # print('The file data is: ')
        #sys.stdout.write(fileData + '\n')
        #sys.stdout.flush()

        # break if all the data has been read
        if(len(fileData) == fileSize):

          # log file name and file size 
          sys.stdout.write('File Name: ' + fileName + '\n')
          sys.stdout.write('Bytes Transferred: ' + str(len(fileData)) + 'bytes' + '\n' + '\n')
          sys.stdout.flush()

          # overwrite the contents of the 'download' file
          dl = open('download.txt', 'w')
          dl.write(fileData)
          dl.close()

          break

      data_sock.close()

    elif cmd == 'ls':
      # list files on the server
      transfer(cmd, mySocket)
      lsoutput = mySocket.recv(1024)
      print(lsoutput.decode('utf-8'))

    else:
      # return error print menu options
      invalidInputResponse()
      
    x = input('ftp>')
    b = x.split(' ')
    cmd = b[0]

  # disconnect from server
  mySocket.close()

def main():
  # command line checks
  if len(sys.argv) < 3:
    print('Error: expecting port number - python ftp-server.py <SERVER_NAME> <PORT_NUM>')
    sys.exit(1) 

  #fileName = sys.argv[0]
  serverPort = int(sys.argv[2])

  # connect control socket to server
  s = connect(serverPort)
  # pass it to the function that handles user commands
  getData(s)

if __name__ == '__main__':
  main()
