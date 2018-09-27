class Circuit:

	def __init__(self, path_to_file):
		with open(path_to_file, "r") as f:
			text = f.read()
		text = text.split("\n")

		first_line = text[0].split()
		# first line of text file has 4 values to fill these 4 variables:
		self.prime = int(first_line[0])
		self.n_inputs = int(first_line[1])
		self.n_outputs = int(first_line[2])
		self.tape_length = int(first_line[3])

		text = text[1:]

		count = 0
		for t in text:
			if t.split()[0] == "C":
				count += 1
			else:
				break
		consts, circuit = text[:count], text[count:]

		self.constant_tape = [None for _ in range(len(consts))]
		for t in consts:
			line = t.split()
			self.constant_tape[int(line[1])] = int(line[2])

		self.circuit = [i.split() for i in circuit]

	def run(self, tape):
		if len(tape) == self.n_inputs:
			tape = self.constant_tape + tape
			while len(tape)< self.tape_length:
				tape.append(0)
		if len(tape) != self.tape_length:
			return "TAPE NOT PROPERLY FORMATTED"
		for gate in self.circuit:
			if gate[-1] == 'ADD':
				tape[int(gate[-2])] = self.ADD(tape[int(gate[-3])], tape[int(gate[-4])])
			if gate[-1] == 'MUL':
				tape[int(gate[-2])] = self.MUL(tape[int(gate[-3])], tape[int(gate[-4])])
		return tape[self.tape_length-self.n_outputs:]

	def ADD(self, a, b):
		return (a+b)%self.prime

	def MUL(self, a, b):
		return (a*b)%self.prime



