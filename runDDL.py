import sys
import sqlite3
from sqlite3 import Error
import time
import threading
from urllib.parse import urlparse
import socket
from socket import error as socket_error
"""
function: init()
parameter: None
return: none
This function will get the value for clustercfg and ddlfile
then declare them as global values
"""
def init():
    global clustercfg
    global ddlfile
    clustercfg = sys.argv[1]
    ddlfile = sys.argv[2]
"""
function: do_connect()
parameter: (hash) cp, (string) ddlfile
return: none
This function receive the information about the cluster pc, and ddlfile name
Then it will connect to the server PC(s) and send the config + query
for the server to process. It will print out success, if the query is
successful executed, otherwise it will print out failed.
"""
def do_connect(cp, ddlfile):

    mySocket = socket.socket()
    try:
        mySocket.connect((cp['host'], int(cp['port']) ))
        #pc type
        data_pc_type = "node"
        mySocket.send(data_pc_type.encode())
        #listen from server
        data = mySocket.recv(1024).decode()
        #send pc_config data
        data = cp['host'] + ':' + cp['port'] + '/' + cp['db']
        mySocket.send(data.encode())
        #receive signal from server
        data = mySocket.recv(1024).decode()
        #send ddlfile name to server
        mySocket.send(ddlfile.encode())
        #receive output from server
        data = mySocket.recv(1024).decode()
        print (data)
        mySocket.close()

    except socket_error as e:
        print (e)
"""
function: update_catalog_client()
parameter: (hash) cfg, (string) ddlfile
return: none
This function receive the information about the cluster pc, and ddlfile name
Then it will connect to the catalog server PC(s) and send the config + query
for the server to process. It will print out success, if the query is
successful executed, otherwise it will print out failed.
"""
def update_catalog_client(cfg, cfg_data):
    #get catalog hostname from cfg string using
    #parseUrl (e.g catalog.hostname=172.17.0.2:50001/mycatdb)
    cat_cp = parseUrl(cfg['catalog.hostname'])
    mySocket = socket.socket()
    try:
        mySocket.connect((cat_cp['host'], int(cat_cp['port'])))
        #pc type
        data_pc_type = "catalog"
        
        mySocket.send(data_pc_type.encode())
        #listen from server
        data_temp = mySocket.recv(1024).decode()
        #send pc_config data
        data_cp = cat_cp['host'] + ':' + cat_cp['port'] + '/' + cat_cp['db']
        mySocket.send(data_cp.encode())

        data_temp = mySocket.recv(1024).decode()
        #send cfgFile to server
        mySocket.send(cfg_data.encode())
        data_temp = mySocket.recv(1024).decode()
        print (data_temp)
        mySocket.close()

    except socket_error as e:
        print (e)
"""
function: parseUrl()
parameter: (string) hostname
return: (hash) node
This function receives hostname from clustercfg file as a string. Then it will
parse the string into host, port, and databse name that will contains in a node
that will be returned.
"""
def parseUrl(hostname):
    node = {}
    o = urlparse(hostname)
    data = o.path.split('/')
    node['host'] =  o.scheme
    node['port'] = (data[0])
    node['db'] = (data[1])
    return node
"""
function: parse_config()
parameter: (string) filename
return: hash (options)
This function receive the filename of the clustercfg file.
Then it will parse and store the information into a hash.
Users can retrieve the information by calling the variable
from the cfgfile
"""
def parse_config(filename):
    COMMENT_CHAR = '#'
    OPTION_CHAR = '='
    options = {}
    f = open(filename)
    for line in f:
        # First, remove comments:
        if COMMENT_CHAR in line:
            # split on comment char, keep only the part before
            line, comment = line.split(COMMENT_CHAR, 1)
        # Second, find lines with an option=value:
        if OPTION_CHAR in line:
            # split on option char:
            option, value = line.split(OPTION_CHAR, 1)
            # strip spaces:
            option = option.strip()
            value = value.strip()
            # store in dictionary:
            options[option] = value
    f.close()
    return options
"""
function: main()
parameter: none
return: none
Main function of the program
"""
def main():
    if len(sys.argv) < 3:
        print("Error: You didn't enter enough arguments!")
        print("Usage: python3 runDDL.py ./cfgfile ./ddlfile")
        sys.exit()
    else:
        init()
        cfg = parse_config(clustercfg)
        #get numnodes
        numnodes = int(cfg['numnodes'])
        #loop through all the nodes
        for node in range(1, numnodes + 1):
            cp = parseUrl(cfg['node%d.hostname' % node])
            t = threading.Thread(target=do_connect(cp,ddlfile))
            t.start()
            t.join()
        # updata catalog table
        update_catalog_client(cfg, clustercfg)

if __name__ == '__main__':
    main()
