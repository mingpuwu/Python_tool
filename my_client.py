import socket
import time
head = [0x0d,0x05]
enctry = [0x00]
ver = [0x19]
source_id = [0x12,0x4e,0x25,0xf3,0xa4,0x3c,0x44,0x82,0xbc,0x95,0x80,0x68,0xc7,0x59,0x3c,0x85]
tail = [0x0d,0x0a]
raw_data_len = [0x00,0x00]
head_len = [0x00,0x00]
AVN = [0x4e,0x33,0x33,0x31,0x30,0x31,0x30,0x31,0x30,0x33,0x30,0x30,0x30,0x32,0x31,0x34]
LEN_POS = 1

char_type = [0x01]
short_type = [0x02]
int_type = [0x03]
float_type = [0x04]
double_type = [0x05]

def checksum(data):
   
    checksum = 0
    for i in data:
        checksum += i
        checksum &= 0xFF # 强制截断  
    return checksum

def append_auth_mesg():
	request_num = [0x05,0x04]
	body = head_len+enctry+ver+source_id+request_num
	raw_data_len[1] = 17
	body = body+raw_data_len
	body = body+char_type
	body = body+AVN
	body[LEN_POS]=len(body)+1  
	SUM =  checksum(body)
	body= body+[SUM]
	return body

def append_head_tail(body):
	data = head
	data = data+body+tail
	return data

def host_to_network(data):
	host_len = len(data)-1
	net_dat =[]
	for i in range(host_len, -1, -1):
		net_dat = net_dat+[data[i]]
	return net_dat

def list_to_bytes(data):
	b_data = b''
	for tmp in data:
		b = tmp.to_bytes(1,'big')
		b_data = b+b_data
	return b_data
	
def my_connect():
	host_port = ('2.2.2.2',7788)
	client = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
	client.connect(host_port)
	return client
	
def send_auth(fd):
	body = append_auth_mesg()
	data = append_head_tail(body)
	net_data = host_to_network(data)
	fd.send(list_to_bytes(net_data))
	
def recv_authrand(fd):
	data = fd.recv(1024)	
	auth_data = [0,0,0,0]
	auth_data[3] = data[27]
	auth_data[2] = data[28]
	auth_data[1] = data[29]
	auth_data[0] = data[30]
	print("auth_rand is :",auth_data)
	return auth_data

def calc_authrand_to_authkey(data):
	authkey = [0,0,0,0]
	authkey[3] = data[2]^0x01
	authkey[2] = data[3]^0x02
	authkey[1] = data[0]^0x04
	authkey[0] = data[1]^0x08
	return authkey
	
def append_authkey_msg(authkey):
	request_num = [0x05,0x05]
	body = head_len+enctry+ver+source_id+request_num
	raw_data_len[1] = 5
	body = body+raw_data_len
	body = body+int_type
	body = body+authkey
	body[LEN_POS]=len(body)+1
	SUM =  checksum(body)
	body = body+[SUM]
	return body
	
def send_authkey(fd,au_data):	
	body = append_authkey_msg(au_data)
	data = append_head_tail(body)
	net_data = host_to_network(data)
	fd.send(list_to_bytes(net_data))

def get_authchallenge(fd):
	data = fd.recv(1024)
	return data

def append_heartbeat():
	request_num = [0x05,0x07]
	body = head_len+enctry+ver+source_id+request_num
	raw_data_len[1] = 0
	body = body+raw_data_len
	body[LEN_POS]=len(body)+1
	SUM =  checksum(body)
	body = body+[SUM]
	return body


def send_heartbeat(fd):
	body = append_heartbeat()
	data = append_head_tail(body)
	net_data = host_to_network(data)
	fd.send(list_to_bytes(net_data))

def send_authchallenge_syc(fd):
	request_num = [0x05,0x06]
	body = head_len+enctry+ver+source_id+request_num
	raw_data_len[1] = 2
	body = body+raw_data_len
	body = body+char_type
	syc_flag = [0x01]
	body = body+syc_flag
	body[LEN_POS]=len(body)+1
	SUM =  checksum(body)
	body = body+[SUM]
	data = append_head_tail(body)
	net_data = host_to_network(data)
	fd.send(list_to_bytes(net_data))

def send_wifi_onoff(fd,open):
	request_num = [0x02,0x03]
	body = head_len+enctry+ver+source_id+request_num
	raw_data_len[1] = 2
	body = body+raw_data_len
	body = body+char_type
	body = body+[open]
	body[LEN_POS]=len(body)+1
	SUM =  checksum(body)
	body = body+[SUM]
	data = append_head_tail(body)
	net_data = host_to_network(data)
	fd.send(list_to_bytes(net_data))

def run_loop(fd):
	i = 0
	open = 0
	while 1 :
		print("send heartbeat")
		send_heartbeat(fd)
		time.sleep(2)
		i= i+1
		if i>20 and open==0 :
			i=0
			print('send wifi open~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
			open = 1
			send_wifi_onoff(fd,open)
			#data = fd.recv(1024)
		elif i>20 and open==1 :
			i=0
			print('send wifi close~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
			open = 0
			send_wifi_onoff(fd,open)
			#data = fd.recv(1024)
		

if __name__ =='__main__':
	fd = my_connect()
	send_auth(fd)
	au_data = recv_authrand(fd)
	auth = calc_authrand_to_authkey(au_data)
	send_authkey(fd,auth)
	get_authchallenge(fd)
	time.sleep(1)
	send_authchallenge_syc(fd)
	time.sleep(1)
	send_wifi_onoff(fd,1)

	run_loop(fd)
