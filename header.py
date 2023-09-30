import random

class Header:
    def __init__(self, requestMode, responseHeaderStr):
        if requestMode:
            self.write_header()
        else:
            self.process_header(responseHeaderStr)
        return
    
    def write_header(self):
        self.id = ['1','1','1','1','1','1','1','1','1','1','1','1','1','1','1','1'] #16 bits/first line
        self.id[0] = '1'
        self.qr = ['0'] #1 bit. set to '0' for query.
        self.opcode = ['0','0','0','0'] #4 bits. '0' signifies standard query.
        self.aa = ['0'] #1 bit
        self.tc = ['0'] #1 bit
        self.rd = [1] #1 bit. set to 1 for recursive pursuit of query.
        self.ra = ['0'] #1 bit
        self.z = ['0','0','0'] #3 bits
        self.rcode = ['0','0','0','0'] # 4 bits
        self.qdcount = ['0' for i in range(0,16)]
        self.qdcount[15] = 1 #set qdcount to 1 because we send 1 query at a time.
        self.ancount, self.nscount, self.arcount = ['0' for i in range(0,16)], ['0' for i in range(0,16)], ['0' for i in range(0,16)]
        line2 = [*self.qr, *self.opcode, *self.aa, *self.tc, *self.rd, *self.ra, *self.z, *self.rcode]
        header = [*self.id, *line2, *self.qdcount, *self.ancount, *self.nscount, *self.arcount]
        self.hex_representation = bytes.fromhex(hex(int(''.join(map(str, header)), 2))[2:])
        #self.header = [*id, *line2, *qdcount, *ancount, *nscount, *arcount]

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
        self.hex_representation = bytes.fromhex(hex(int(''.join(map(str, header)), 2))[2:])

class Question:
    def __init__(self, hostname):
        self.write_question(hostname)

    def write_question(self, hostname):
        self.qname = self.create_labels(hostname) #up to 16 bits but no padding. encodes the content of the query. TD: do this!
        self.qtype = [0 for i in range(0,16)] #16 bits. set to 1 because we want type A records.
        self.qtype[15] = 1 
        #IN is the code for internet... what else would it be?
        # qclass = text2bin("IN")
        #IN in the correct code. But the value of IN is 1 apparently
        self.qclass = [0 for i in range(0, 16)]
        self.qclass[15] = 1
        question = [*self.qname, *self.qtype, *self.qclass]
        print(question)
        self.hex_representation = bytes.fromhex(hex(int(''.join(map(str, question)), 2))[2:])
    
    #does entire label creation routine, including ending with a 0. separators are 1 byte unsigned ints. returns as list of str where each elem is '0' or '1'
    def create_labels(self, hostname):
        labels = hostname.split(".")
        labels_bin = []
        for label in labels:
            labels_bin.extend(self.num2bin(8, len(label)))
            labels_bin.extend(self.text2bin(label))
        labels_bin.extend(self.num2bin(8, 0))
        return labels_bin
    
    #returns ASCII code in binary for provided text. returns as list of str where each elem is '0' or '1'
    def text2bin(self, text):
        chars = [format(ord(i), '08b') for i in text]
        return [int(bit) for char in chars for bit in char]

    #returns list of 0 or 1 for the provide integer of length bits.
    def num2bin(self, bits, num):
        bin = [0 for i in range(0, bits)]
        i = bits - 1
        while num != 0:
            bin[i] = num % 2
            num //= 2
            i -= 1
        return bin

#main
hostname = "gmu.edu"
request_header = Header(True, "")
request_question = Question(hostname)

print(f"header hex: {request_header.hex_representation}\tquestion hex: {request_question.hex_representation}")
#HERE
#request = request_header.hex_representation+request_question.hex_representation

#response = send_request(request)

#response_header_hex, response_question_hex, response_answer_hex = split_response(response)

#response_header = Header(False, response_header_hex)

#response question should be the exact same as the request. confirm this, then simply reuse request question for response question.
#assert response_question_hex == request_question.hex_representation
#response_question = request_question

#response_answer = Answer(response_answer_hex)

#iterate and print like: https://stackoverflow.com/questions/11637293/iterate-over-object-attributes-in-python

#print(f"header id: {h.id}\nheader hex representation: {h.hex_representation}\nheader hex length: {len(h.hex_representation)}")
#print("processing header: ")
#h = Header(False, response)