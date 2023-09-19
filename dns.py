import sys

#Section #0: Prompt User
assert len(sys.argv) == 2 #run like `python dns.py <hostname>`
hostname = sys.argv[1]

#Section #1: Construct DNS Query
print(f"Preparing DNS query...")

print(f"Sending DNS query...")

#Section #2: Send DNS Query
print(f"Contacting DNS server...\n")

#Section #3: Interpret DNS Response
attempt_num = -1
print(f"DNS response received (attempt {attempt_num} of 3).")

print(f"Processing DNS response...")

response = ""
print(f"DNS response: {response}")