import header

testaddr = "www.google.com"

testbin = header.create_labels(testaddr)
# print(testbin)

s = ''.join(str(v) for v in testbin)
# print(s)

testbytes = header.bitstring2bytes(s)
print(testbytes)

print(header.separatedBytes(testbytes))