import random, socket, time

#helper function that converts string of bits (easy to construct and manipulate) to bytes() (required by socket) object! check out: https://stackoverflow.com/questions/32675679/convert-binary-string-to-bytearray-in-python-3
def bitstring2bytes(s):
    return int(s, 2).to_bytes((len(s) + 7) // 8, byteorder='big')

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
def create_labels(hostname):
    labels = hostname.split(".")
    labels_bin = []
    for label in labels:
        labels_bin.extend(num2bin(8, len(label)))
        labels_bin.extend(text2bin(label))
    labels_bin.extend(num2bin(8, 0))
    return labels_bin

#helper function to parse length separated web address from bytes
def separatedBytes(bytes):
    web_address = ''
    offset = 0
    while bytes[offset] != 0:
        if web_address != '':
            web_address += '.'
        nextSegment = bytes[offset] + offset + 1
        for byte in bytes[offset+1:nextSegment]:
            web_address += chr(byte)
        offset = nextSegment
    offset+=1
    return (web_address, offset)

#sends request of hex to Google's DNS server
def send_request(request):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.connect(('8.8.8.8', 53))
    for attempt_num in range(1,4):
        sending_bytes = sock.sendto(request,('8.8.8.8', 53))

        (message,src_addr) = sock.recvfrom(2048) #4096 is the max bytes we'll receive
        if message != None:
            break
        time.sleep(5)
    if message == None:
        raise TimeoutError("Timeout! No response from the DNS server.")
    sock.close()
    return message

class Header:
    def __init__(self, requestMode, responseHeader):
        if requestMode:
            self.write_header()
        else:
            self.process_header(responseHeader)
        return
    
    def write_header(self):
        self.id = [str(random.randint(0,1)) for i in range(0,16)] #16 bits/first line
        self.id[0] = '1'
        self.qr = ['0'] #1 bit. set to '0' for query.
        self.opcode = ['0','0','0','0'] #4 bits. '0' signifies standard query.
        self.aa = ['0'] #1 bit
        self.tc = ['0'] #1 bit
        self.rd = ['1'] #1 bit. set to 1 for recursive pursuit of query.
        self.ra = ['0'] #1 bit
        self.z = ['0','0','0'] #3 bits
        self.rcode = ['0','0','0','0'] # 4 bits
        self.qdcount = ['0' for i in range(0,16)]
        self.qdcount[15] = '1' #set qdcount to 1 because we send 1 query at a time.
        self.ancount, self.nscount, self.arcount = ['0' for i in range(0,16)], ['0' for i in range(0,16)], ['0' for i in range(0,16)]
        line2 = [*self.qr, *self.opcode, *self.aa, *self.tc, *self.rd, *self.ra, *self.z, *self.rcode]
        header = [*self.id, *line2, *self.qdcount, *self.ancount, *self.nscount, *self.arcount]
        header_str = ''.join(header)
        self.hex_representation = bitstring2bytes(header_str)

    def process_header(self, response_header_str):
        self.id = f'{response_header_str[0]:08b}'+f'{response_header_str[1]:08b}' #bin parsing idea from https://stackoverflow.com/questions/10411085/converting-integer-to-binary-in-python
        line2 = f'{response_header_str[2]:08b}'+f'{response_header_str[3]:08b}' #should not get printed
        self.qr = line2[0]
        self.opcode = line2[1:5]
        self.aa = line2[5]
        self.tc = line2[6]
        self.rd = line2[7]
        self.ra = line2[8]
        self.z = line2[9:12]
        self.rcode = line2[12:]
        self.qdcount = f'{response_header_str[4]:08b}'+f'{response_header_str[5]:08b}'
        self.ancount = f'{response_header_str[6]:08b}'+f'{response_header_str[7]:08b}'
        self.nscount = f'{response_header_str[8]:08b}'+f'{response_header_str[9]:08b}'
        self.arcount = f'{response_header_str[10]:08b}'+f'{response_header_str[11]:08b}'
        header = [*self.id, *line2, *self.qdcount, *self.ancount, *self.nscount, *self.arcount]
        header_str = ''.join(header)
        self.hex_representation = bitstring2bytes(header_str)

    def __str__(self):
        return f"""header.ID = {self.id}
header.QR = {self.qr}
header.OPCODE = {self.opcode}
header.AA = {self.aa}
header.TC = {self.tc}
header.RD = {self.rd}
header.RA = {self.ra}
header.Z = {self.z}
header.RCODE = {self.rcode}
header.QDCOUNT = {self.qdcount}
header.ANCOUNT = {self.ancount}
header.NSCOUNT = {self.nscount}
header.ARCOUNT = {self.arcount}
"""
              
    def fields(self):
        return [a for a in dir(self) if not a.startswith('__') and not callable(getattr(self, a))]

class Question:
    def __init__(self, hostname, requestMode, responseAnswer):
        if requestMode:
            self.write_question(hostname)
        else:
            self.process_question(responseAnswer)

    def write_question(self, hostname):
        self.qname = create_labels(hostname) #up to 16 bits but no padding. encodes the content of the query. TD: do this!
        self.qtype = ['0' for i in range(0,16)] #16 bits. set to 1 because we want type A records.
        self.qtype[15] = '1'
        #IN in the correct code. But the value of IN is 1 apparently
        self.qclass = ['0' for i in range(0, 16)]
        self.qclass[15] = '1'
        question = [*self.qname, *self.qtype, *self.qclass]
        question = [str(bit) for bit in question]
        question_str = ''.join(question)
        self.hex_representation = bitstring2bytes(question_str)
    
    def process_question(self, responseQuestionBytes):
        self.qname, offset = separatedBytes(responseQuestionBytes)
        responseQuestionBytes = responseQuestionBytes[offset:]
        self.qtype = f'{responseQuestionBytes[0]:08b}'+f'{responseQuestionBytes[1]:08b}'
        self.qclass = f'{responseQuestionBytes[2]:08b}'+f'{responseQuestionBytes[3]:08b}'
    
    def __str__(self):
        return f"""question.QNAME = {self.qname}
question.QTYPE = {self.qtype}
question.QCLASS = {self.qclass}
"""

    def fields(self):
        return [a for a in dir(self) if not a.startswith('__') and not callable(getattr(self, a))]

class Answer:
    def __init__(self, answerBytes, endQuestion, numRecords):
        self.RRs = self.process_response(answerBytes, endQuestion, numRecords)

    def process_response(self, answerBytes, endQuestion, numRecords):
        RRs = []
        offset = endQuestion

        for i in range(numRecords):
            rr = ResourceRecord(answerBytes[offset:])
            if rr.name == None:
                rr.name = separatedBytes(answerBytes[rr.pointer:])[0]
            offset += rr.end
            RRs.append(rr)
            
        return RRs #return list of RRs
    
class ResourceRecord:

    def __init__(self, rrBytes):
        offset = 0 #beginning of the RR after the name field
        if rrBytes[0] >= 192: #192 is 1100 0000 which indicates that the entry uses compression
            offset = 2
            self.name = None
            self.pointer = rrBytes[1]
        else:
            web_address, offset = separatedBytes(rrBytes)
            self.name = web_address
        
        rrBytes = rrBytes[offset:]

        self.atype = f'{rrBytes[0]:08b}'+f'{rrBytes[1]:08b}'
        self.aclass = f'{rrBytes[2]:08b}'+f'{rrBytes[3]:08b}'
        self.ttl = int.from_bytes(rrBytes[4:8], byteorder='big')
        self.rdlength = int.from_bytes(rrBytes[8:10], byteorder='big')
        self.rdata = self.parseIP(rrBytes[10:14])
        self.end = offset + 14
    
    def parseIP(self, rdata):
        return ''.join(
            [f'{rdata[0]}', '.',
            f'{rdata[1]}', '.',
            f'{rdata[2]}', '.',
            f'{rdata[3]}'])
    
    def __str__(self):
        return f"""answer.NAME = {self.name}
answer.TYPE = {self.atype}
answer.CLASS = {self.aclass}
answer.TTL = {self.ttl}
answer.RDLENGTH = {self.rdlength}
answer.RDATA = {self.rdata}
"""
    
    def fields(self):
        return [a for a in dir(self) if not a.startswith('__') and not callable(getattr(self, a))]
