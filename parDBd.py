import socket
import sqlite3
import sys
from runDDL import parseUrl
from runDDL import parse_config
from sqlite3 import Error
"""
function: init()
parameter: None
return: none
This function will get the value for clustercfg and ddlfile
then declare them as global values
"""
def init():
    global host
    global port
    host = sys.argv[1]
    port = int(sys.argv[2])

"""
function: create_connection()
parameter: (string) database_file
return: Connection object or None
This function creates a database connection to the SQLite database
specified by database_file
"""
def create_connection(db_file):
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Error as e:
        print(e)

    return None
"""
function: execute_sql()
parameter: (connection object) conn, (string) sqlStatement, (hash) pc_config,
            (string) ddlfile
return: None
This function execute the sql statement
"""
def execute_sql(conn, sqlFile, cp, ddlfile):
    try:
        c = conn.cursor()
        c.executescript(sqlFile)
        conn.commit()
        if(ddlfile == "catalog"):
            msg = '[' + cp['host'] + ':' + cp['port'] + '/' + cp['db'] + ']:' + ' '
            msg += ddlfile + ' updated.'
        else:
            msg = '[' + cp['host'] + ':' + cp['port'] + '/' + cp['db'] + ']:' + ' '
            msg += ddlfile + ' success.'
        return msg
    except Error as e:
        msg = '[' + cp['host'] + ':' + cp['port'] + '/' + cp['db'] + ']:' + ' '
        msg += ddlfile + ' failed.'
        return msg
"""
function: create table()
parameter: (connection object) conn, (string) sqlStatement
return: None
This function execute the sql statement to create the table
"""
def create_table(conn, create_table_sql):
    try:
        c = conn.cursor()
        c.execute(create_table_sql)
    except Error as e:
        print(e)
"""
function: create update_catalog()
parameter: (string) cfg_filename, (array) tableNames, (int) nodeID
return: (string) msg
This function execute the sql statement to update the catalog table
and return a message says if the catalog is updated
"""
def update_catalog(cfg_cat, tNames, node):
    nodeid = int(node)
    cfg = parse_config(cfg_cat)
    cat_hostname = cfg['catalog.hostname']
    cat_driver = cfg['catalog.driver']
    cat_cfg = parseUrl(cat_hostname)
    nodedriver = cfg['node%d.driver'%nodeid]
    nodeurl = cfg['node%d.hostname'%nodeid]
    #query to create table if not exists
    sql_table_query = """CREATE TABLE IF NOT EXISTS
                    dtables(tname char(32),
                    nodedriver char(64),
                    nodeurl char(128),
                    nodeuser char(16),
                    nodepasswd char(16),
                    partmtd int,
                    nodeid int,
                    partcol char(32),
                    partparam1 char(32),
                    partparam2 char(32));"""
    cat_db_conn = create_connection(cat_cfg['db'])
    if cat_db_conn is not None:
        create_table(cat_db_conn, sql_table_query)
        #create table if it not yet exists
        for tName in tNames:
            sql_update_query = """INSERT INTO dtables(
                                tname, nodedriver, nodeurl, nodeuser,
                                nodepasswd, partmtd, nodeid, partcol,
                                partparam1, partparam2)
                                SELECT '%s', '%s', '%s', NULL, NULL, NULL, %d,
                                NULL, NULL, NULL
                                WHERE NOT EXISTS (
                                SELECT 1 FROM dtables
                                WHERE tname = '%s'
                                AND nodeid = %d);
                                """ %(tName, nodeurl, nodedriver, nodeid, tName, nodeid)
            execute_sql(cat_db_conn, sql_update_query, cat_cfg, 'catalog')

        msg = '[' + cat_cfg['host'] + ':' + cat_cfg['port'] + '/' + cat_cfg['db'] + ']:' + ' '
        msg += 'catalog' + ' updated.'
        return msg

    else:
        print("Error! cannot create the database connection.")

"""
function: main()
parameter: none
return: none
Main function of the program
"""
def Main():
    if len(sys.argv) < 3:
        print("Error: You didn't enter enough arguments!")
        print("Usage: python3 parDBd.py 'host/ip' 'port'")
        sys.exit()
    else:
        init()
        mySocket = socket.socket()
        mySocket.bind((host,port))

        mySocket.listen(1)
        socket_conn, addr = mySocket.accept()
        #receive type of pc
        data_pc_type = socket_conn.recv(1024).decode()
        if (data_pc_type == "catalog"):
            #do something with catalog database
            socket_conn.send(str("received data_pc_type").encode())
            #receive config data (e.g. 172.17.0.2:50001/mycatdb)
            data_config = socket_conn.recv(1024).decode()
            socket_conn.send(str("received data_config").encode())
            #receive cfgFile (e.g clustercfg)
            cfgFile = socket_conn.recv(1024).decode()
            #parse data from cfgFile
            cfg = parse_config(cfgFile)

            numnodes = int(cfg['numnodes'])
            """
            For each node
                parse the config from that node
                connect to that node's database
                execute SQL file to show tables
                store all the table name into tNames[] array
                run update_catalog() and store the output in data_cat variable
                send the ouput to client
            """
            for node in range(1, numnodes + 1):
                cp = parseUrl(cfg['node%d.hostname' % node])
                db_conn = create_connection(cp['db'])
                c = db_conn.cursor()
                c.execute("SELECT name FROM sqlite_master WHERE type='table';")
                tNames = []
                for row in c.fetchall():
                    tNames.append(row[0])

                data_cat = update_catalog(cfgFile, tNames, node)
                socket_conn.send(data_cat.encode())

        elif (data_pc_type == "node"):
            #do something with node database
            socket_conn.send(str("received data_pc_type").encode())
            #receive data_config from client
            data_config = socket_conn.recv(1024).decode()
            cp = parseUrl(data_config)
            db_conn = create_connection(cp['db'])
            if db_conn is not None:
                data = "received config"
                socket_conn.send(data.encode())
                #receive ddlfile name from client
                data_ddlFile = socket_conn.recv(1024).decode()
                #execute statements from sqlFile
                fd = open(data_ddlFile, 'r')
                sqlFile = fd.read()
                fd.close()
                data = execute_sql(db_conn, sqlFile, cp, data_ddlFile)
                socket_conn.send(data.encode())
        else:
            return
        socket_conn.close()

if __name__ == '__main__':
    Main()
