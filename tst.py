successes, attempts = 0, 100
for i in range(0,attempts):
    hostname = "gmu.edu"
    request_header = Header(True, "")
    request_question = Question(hostname)
    request_hex = request_header.hex_representation+request_question.hex_representation
    response = send_request(request_hex)
    successes += response != None #should check that the response actually contains the answer..
    time.sleep(random.randint(0,5))
print(successes/attempts)
