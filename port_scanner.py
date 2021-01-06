from socket import *
import asyncio
from time import perf_counter
import sys

async def scan(tasks, open_ports):
    while tasks.qsize():
        ip, port = await tasks.get()
        # print(f'checking {port}')
        
        if port <= 0 or port > 65535:
            open_ports.append((port, 'not valid'))
            tasks.task_done()

        else:
            # low level method:
            loop = asyncio.get_event_loop()
            sock = socket(AF_INET, SOCK_STREAM)
            sock.settimeout(1)
            try:
                await loop.sock_connect(sock, (ip, port))
            except PermissionError:
                open_ports.append((port, 'permission needed'))
            except ConnectionRefusedError:
                # it means the port is not open or there is no connection from the server of this address and port
                pass
            else:
                open_ports.append((port, 'open'))
            finally:
                tasks.task_done()
                sock.close()
            
            # # high level method

            # conn = asyncio.open_connection(ip, port)
            # try:
            #     await asyncio.wait_for(conn, timeout=0.5)
            # except PermissionError:
            #     open_ports.append((port, 'needs permission!'))
            # except:
            #     pass
            # else:
            #     open_ports.append((port, 'open'))
            # finally:
            #     tasks.task_done()

async def create_tasks(ip, ports, tasks_q):
    for port in ports:
        await tasks_q.put((ip, port))

async def main(workers, ip, port_range):
    tasks_q = asyncio.Queue()
    open_ports = []

    producer = asyncio.create_task(create_tasks(ip, port_range, tasks_q))
    consumers = [asyncio.create_task(scan(tasks_q, open_ports)) for _ in range(workers)]
    
    await producer
    await tasks_q.join()

    return open_ports

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print('please enter IP PORT_RANGE(ex: 127.0.0.1 100_2000)')
    else:
        t1 = perf_counter()

        ip = sys.argv[1]
        port_range_lst = sys.argv[2].split('_')
        port_range = range(int(port_range_lst[0]), int(port_range_lst[1]))
        open_ports = asyncio.run(main(2000, ip, port_range))

        t2 = perf_counter()
        
        print('task completed in {:.3f}s'.format(t2-t1))
        print(open_ports)

    # couldn't get appropriate result from more than 3000 workers (in my machine, of course!)