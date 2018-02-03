# DDL Processor
## What it does?
- This program can run as server, and as client on cluster computer.
- This program will execute the ddlfile (e.g books.sql) on multiple machine on the cluster at the same time using threading.
- This program will also create a catalog of the tables that are stored in the database of each computer in the cluster.
## How it works?

### Files included:
- `runDDL.py`: run on client machines. When executed, this file will connect to the cluster machine that has configuration stored in `cluster.cfg` file, then it will send the query to those machines, and also update the catalog database.
- `parDBd.py`: run on server machines. When executed, this file will create a connection and waits for the input(config data, sql query) from the client side, then it will execute the query based on the configuration. In the end, it will send back data about the query whether it success or fails to execute.
- `cluster.cfg`: contains configuration data for the computers in the cluster.  
- `books.sql`: contains the query that will execute on the server machines.

### Tested Enviroment:
- Ubuntu

### Requirements:
- [python3](https://www.python.org/download/releases/3.0/)
- [sqlite3](https://www.sqlite.org)
- `iputils-ping`, `iproute`, `dnsutils`
```
apt-get -y install iputils-ping
apt-get -y install iproute
apt-get -y install dnsutils
```

### Installation:
- Clone or download this repository. Then put the `runDDL.py`, `parDBd.py`, `cluster.cfg`, and `books.sql` in the same folder.

### Configure `cluster.cfg`
- In order for this program to work. You need to configure the `cluster.cfg` to give the right configuration for the server cluster computers. The hostname/ip must match the ip address on your computer. The server computers can share the same IP, but their port number must be different.

**Example**
`cluster.cfg`
```
numnodes=2

catalog.driver=com.ibm.db2.jcc.DB2Driver
catalog.hostname=172.17.0.2:50001/mycatdb

node1.driver=com.ibm.db2.jcc.DB2Driver
node1.hostname=172.17.0.2:50002/mydb1

node2.driver=com.ibm.db2.jcc.DB2Driver
node2.hostname=172.17.0.2:50003/mydb2

```
### Configure `ddlfile`
- This program comes with a `books.sql` file. However, you can use your own `ddlfile` to test with the program, but make sure you need to create a table first.


**Example**
`books.sql`
```
CREATE TABLE BOOKS(isbn char(14), title char(80), price
decimal);
CREATE TABLE VIDEOS(isbn char(14), title char(80), price
decimal);
```
### Run
- Since this program using python, you would need to compile and run it with python. To run this program, you would need at least a server for your `ddlfile`, and a server for the catalog.
In my example, I use one computer as two servers for `ddlfile`, and one for catalog.
```
python3 ./parDBd.py 172.17.0.2 50001 &
python3 ./parDBd.py 172.17.0.2 50002 &
python3 ./parDBd.py 172.17.0.2 50003
```
- You should notice that there are two arguments that I used for the server machines are `172.17.0.2` as host, and `50001, 50002, 50003` as port.

- On the client machine, type:
```
python3 ./runDDL.py ./cluster.cfg ./books.sql
```
- On the client, there are two arguments `./cluster.cfg` as cfgfile, and `./books.sql` as ddlfile.
### Output
- **Success** if all the query executed correctly (no conflicts with database and tables), it will return success. and catalog will say it's updated.
```
[172.17.0.2:50002/mydb1]: ./books.sql success.
[172.17.0.2:50003/mydb2]: ./books.sql success.
[172.17.0.2:50001/mycatdb]: catalog updated.
```
- **Failed** if I run it again, using the exact arguments and configuration, the query won't be executed since the `books.sql` can't create the same if one is already existed. Therefore, it will say failed. However, the catalog would still say it's updated.
```
[172.17.0.2:50002/mydb1]: ./books.sql failed.
[172.17.0.2:50003/mydb2]: ./books.sql failed.
[172.17.0.2:50001/mycatdb]: catalog updated.
```
