import socket, time
from header import *


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
hostname = "google.com"
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

#response question should be the exact same as the request. confirm this, then simply reuse request question for response question.
# assert response_question_hex == request_question.hex_representation
# response_question = request_question

response_question = Question(None, False, response_question_hex)

#response answer should contain the number of RRs listed in the response header
response_answer = Answer(response_hex, question_end, int(response_header.ancount, 2))
RRs = response_answer.RRs

print(response_header)
print(response_question)
for rr in RRs:
    print(rr)


