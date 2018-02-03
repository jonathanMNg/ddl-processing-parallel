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
---
apt-get -y install iputils-ping
apt-get -y install iproute
apt-get -y install dnsutils
---

### Installing:
- Clone or download this repository. Then put the `runDDL.py`, `parDBd.py`, `cluster.cfg`, and `books.sql` in the same folder.
