def replace_boolean_consts(filename):
	with open(filename, "r") as f:
	    text = f.read()

	lines = text.split("\n")
	known_dict = {}
	for line in lines:
	    words = line.split()
	    if words[0] == "C":
	        known_dict[words[1]] = words[2]

	ops = lines[len(known_dict)+1:]

	out = []
	for op in ops:
		v = op.split()
		if v[0] in known_dict.keys():
			v[0] = known_dict[v[0]]
		if v[1] in known_dict.keys():
			v[1] = known_dict[v[1]]
		out.append(" ".join(v))

	final = lines[:3]+out

	t = "\n".join(final)
	check_text = t.replace("\n", " Z ")
	words = check_text.split()
	vals = [str(i) for i in range(int(lines[0].split()[1])+2, int(lines[-1].split()[-2])+1)]
	final_words = [str(int(word) - len(known_dict) + 2) if word in vals else word for word in words]
	recombined = " ".join(final_words)
	t = recombined.replace(" Z ", "\n")
	with open("reduced_"+filename, "w") as f:
		f.write(t)
