#name = input("How are you?")
#print("Hello,",name)

#table = "orders"
#rows = 15000
#print(f"Table {table} has {rows:,} rows")

server2 = {"name": "db01", "cpu": 85, "disk": 40}
server1 = {"name": "db02", "cpu": 30, "disk": 95}
servers=[server1,server2]
#if server["cpu"] > 80:
 #   print(f"{server['name']}: CPU is high")

def check_server_cpu(server):
    return server["cpu"] > 80 

def check_server_disk(server):
    return server["disk"] > 90

for s in servers:
    if check_server_cpu(s):
        print("Alert:", s["name"],"CPU is High")
    if check_server_disk(s):
            print("Alert:", s["name"],"DISK is Full")