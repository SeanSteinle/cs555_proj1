import socket, time, sys
from dns_lib import *


#sends request of hex to Google's DNS server
def send_request(request):
    print("Contacting DNS server..")
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.connect(('8.8.8.8', 53))
    for attempt_num in range(1,4):
        print("Sending DNS query..")
        sending_bytes = sock.sendto(request,('8.8.8.8', 53))

        (message,src_addr) = sock.recvfrom(2048) #4096 is the max bytes we'll receive
        if message != None:
            print(f"DNS response received (attempt {attempt_num} of 3)")
            break
        time.sleep(5)
    if message == None:
        raise TimeoutError("Timeout! No response from the DNS server.")
    sock.close()
    return message

#main
print("Preparing DNS query..")
assert len(sys.argv) == 2 #run like `python dns_client.py <hostname>`
hostname = sys.argv[1]
request_header = Header(True, "")
request_question = Question(hostname, True, None)

#send request, receive and split response
request_hex = request_header.hex_representation+request_question.hex_representation
response_hex = send_request(request_hex)
question_end = 12+len(request_question.hex_representation)
response_header_hex, response_question_hex, response_answer_hex = response_hex[:12], response_hex[12:question_end], response_hex[question_end:]

#process response
print("Processing DNS response..")

#response header is similar to the request header, but a few flags may be different.
response_header = Header(False, response_header_hex)

#parse question header
response_question = Question(None, False, response_question_hex)

#response answer should contain the number of RRs listed in the response header
numRRs = int(response_header.arcount, 2) + int(response_header.ancount, 2) + int(response_header.nscount, 2)
response_answer = Answer(response_hex, question_end, numRRs)
RRs = response_answer.RRs

print(response_header)
print(response_question)
for rr in RRs:
    print(rr)


