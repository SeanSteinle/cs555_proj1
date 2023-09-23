#imports
import sys, random, socket, struct, io

#helper functions

#returns ASCII code in binary for provided text. returns as list of str where each elem is '0' or '1'
def text2bin(text):
    chars = [format(ord(i), '08b') for i in text]
    return [int(bit) for char in chars for bit in char]

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
    qname = create_labels(hostname) #up to 16 bits but no padding. encodes the content of the query. TD: do this!
    qtype = [0 for i in range(0,16)] #16 bits. set to 1 because we want type A records.
    qtype[15] = 1
    qclass = text2bin("IN") #IN is the code for internet... what else would it be?
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
header_request, question_request = request[:12],request[12:]

print(f"DNS query: {request}")

print(f"Sending DNS query...")

#Section #2: Send DNS Query
print(f"Contacting DNS server...\n")
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.connect(('8.8.8.8', 53))
for attempt_num in range(1,4):
    sending_bytes = sock.sendto(request,('8.8.8.8', 53))
    (message,src_addr) = sock.recvfrom(1024) #4096 is the max bytes we'll receive
    if message != None:
        break
if message == None:
    raise TimeoutError("Timeout! No response from the DNS server.")
sock.close()

print(f"request header:: {header_request}\nresponse header: {message[:12]}\nentire response: {message}")

#Section #3: Interpret DNS Response
print(f"DNS response received (attempt {attempt_num} of 3).")

print(f"Processing DNS response...")
#reader = io.BytesIO(message)
#print(type(message))
#header = struct.unpack("!HHHHHH", reader.read(12))
#print(header)

response = ""
print(f"DNS response: {response}")