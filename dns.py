#imports
import sys, random, socket, struct, io

#helper functions

#returns ASCII code in binary for provided text. returns as list of str where each elem is '0' or '1'
def text2bin(text):
    chars = [format(ord(i), '08b') for i in text]
    return [int(bit) for char in chars for bit in char]

#returns list of 0 or 1 for the provide integer of length bits.
def num2bin(bits, num):
    bin = [0 for i in range(0, bits)]
    i = bits - 1
    while num != 0:
        bin[i] = num % 2
        num //= 2
        i -= 1
    return bin

#does entire label creation routine, including ending with a 0. separators are 1 byte unsigned ints. returns as list of str where each elem is '0' or '1'
def create_labels_without_asciinums(hostname):
    labels = hostname.split(".")
    labels_bin = []
    for label in labels:
        labels_bin.extend(num2bin(8, len(label)))
        labels_bin.extend(text2bin(label))
    labels_bin.extend(num2bin(8, 0))
    return labels_bin

#does entire label creation routine, including ending with a "0". returns as list of str where each elem is '0' or '1'
def create_labels(hostname):
    labels = hostname.split(".")
    labels_bin = []
    for label in labels:
        labels_bin.append(text2bin(str(len(label))))
        for char in list(label):
            labels_bin.append(text2bin(char))
    labels_bin.append(text2bin("0")) #add len 0 byte (TD: should this be 00000000 or "0" ?)
    return [bit for char in labels_bin for bit in char] #flatten and return

#core functions
def write_header():
    id = [random.randint(0,1) for i in range(0,16)] #16 bits/first line
    qr = [0] #1 bit. set to 0 for query.
    opcode = [0,0,0,0] #4 bits. 0 signifies standard query.
    aa = [0] #1 bit
    tc = [0] #1 bit
    rd = [1] #1 bit. set to 1 for recursive pursuit of query.
    ra = [0] #1 bit
    z = [0,0,0] #3 bits
    rcode = [0,0,0,0] # 4 bits
    line2 = [*qr, *opcode, *aa, *tc, *rd, *ra, *z, *rcode]
    qdcount = [0 for i in range(0,16)]
    qdcount[15] = 1 #set qdcount to 1 because we send 1 query at a time.
    ancount, nscount, arcount = [0 for i in range(0,16)], [0 for i in range(0,16)], [0 for i in range(0,16)]
    header = [*id, *line2, *qdcount, *ancount, *nscount, *arcount]
    return header

def write_question(hostname):
    qname = create_labels_without_asciinums(hostname) #up to 16 bits but no padding. encodes the content of the query. TD: do this!
    qtype = [0 for i in range(0,16)] #16 bits. set to 1 because we want type A records.
    qtype[15] = 1 
    #IN is the code for internet... what else would it be?
    # qclass = text2bin("IN")
    #IN in the correct code. But the value of IN is 1 apparently
    qclass = [0 for i in range(0, 16)]
    qclass[15] = 1
    question = [*qname, *qtype, *qclass]
    return question

#main logic
#Section #0: Prompt User
assert len(sys.argv) == 2 #run like `python dns.py <hostname>`
hostname = sys.argv[1]

#Section #1: Construct DNS Query
print(f"Preparing DNS query...")

header = write_header()
question = write_question(hostname)
query = [*header, *question]

request = bytes.fromhex(hex(int(''.join(map(str, query)), 2))[2:]) #get hex string, chop off "0x", convert to bytes object
request_header, request_question = request[:12],request[12:]

print(f"DNS query: {request}")

print(f"Sending DNS query...")

#Section #2: Send DNS Query
print(f"Contacting DNS server...\n")
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.connect(('8.8.8.8', 53))
for attempt_num in range(1,4):
    sending_bytes = sock.sendto(request,('8.8.8.8', 53))

    (message,src_addr) = sock.recvfrom(2048) #4096 is the max bytes we'll receive
    if message != None:
        break
if message == None:
    raise TimeoutError("Timeout! No response from the DNS server.")
sock.close()

print(f"request header:: {request_header}\nresponse header: {message[:12]}\nentire response: {message}")

#Section #3: Interpret DNS Response
print(f"DNS response received (attempt {attempt_num} of 3).")

print(f"Processing DNS response...")

#TD:
#1. start by parsing header!!

response_header = message[0:len(request_header)]
assert len(response_header) == len(request_header)
response_question = message[len(request_header):len(request_header)+len(request_question)]
assert len(response_question) == len(request_question)
response_answer = message[len(request_header)+len(request_question):]

#parse response header
resp_id = f'{response_header[0]:08b}'+f'{response_header[1]:08b}' #bin parsing idea from https://stackoverflow.com/questions/10411085/converting-integer-to-binary-in-python
resp_line2 = f'{response_header[2]:08b}'+f'{response_header[3]:08b}' #should not get printed
resp_qr = resp_line2[0]
resp_opcode = resp_line2[1:5]
resp_aa = resp_line2[5]
resp_tc = resp_line2[6]
resp_rd = resp_line2[7]
resp_ra = resp_line2[8]
resp_z = resp_line2[9:12]
resp_rcode = resp_line2[12:]
resp_qdcount = f'{response_header[4]:08b}'+f'{response_header[5]:08b}'
resp_ancount = f'{response_header[6]:08b}'+f'{response_header[7]:08b}'
resp_nscount = f'{response_header[8]:08b}'+f'{response_header[9]:08b}'
resp_arcount = f'{response_header[10]:08b}'+f'{response_header[11]:08b}'

#parse response question

#parse response answer

#things to assert: rcode is 0, req and resp questions identical?

response = ""
print(f"DNS response: {response}")


class question:
    pass

class answer:
    pass

#pseudocode
""" 
create header object
write header hex
create question
write question hex
request = hhex + qhex

send request

extract header
extract question
extract answer """