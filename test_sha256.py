import hashlib
from circuit_interpreter import Circuit
from dumb_compiler import compiler

'''text=compiler("shortcutSHA256_script.txt")

with open("2blockSHA256_2.txt", "w") as f:
    f.write(text)'''

sha256_program = Circuit("2blockSHA256_better_2.txt")

def test_sha256(string):
	check = int(hashlib.sha256(string).hexdigest(), 16)
	tape = [int(i) for i in preprocess(string)]
	result = sha256_program.run(tape)
	return int("".join([str(i) for i in result]), 2) == check

def preprocess(to_hash):
	bits = "".join([char2bin8(char) for char in to_hash])
	n = len(bits)
	preprocessed = bits+"1"
	while len(preprocessed)%512 != 448:
		preprocessed += "0"

	b = bin(n)[2:]
	while len(b)<64:
		b = "0"+b
	preprocessed = preprocessed + b

	return preprocessed

def char2bin8(a):
	b = bin(ord(a))[2:]
	while len(b)<8:
		b = "0"+b
	return b

if test_sha256("a"*80):
	print "PASS"
else:
	print "FAIL"

