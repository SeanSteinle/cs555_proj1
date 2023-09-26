import random

class Header:
    def __init__(self, requestMode):
        if requestMode:
            self.write_header()
        else:
            self.process_header()
        return
    
    def write_header(self):
        self.id = [str(random.randint(0,1)) for i in range(0,16)] #16 bits/first line
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

    def process_header(self):
        pass

h = Header(True)
print(h.id)
print(h.hex_representation)
print(len(h.hex_representation))