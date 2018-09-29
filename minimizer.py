
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
	with open("reduced_"+filename, "w") as f:
		f.write(t)

'''with open("better2block.txt", "r") as f:
	text = f.read()

text = text.replace("\n", "Z")
lines = text.split("Z")
ops = lines[3:]
K = 0
for i in range(len(ops)-256):
	print K
	v = ops[i].split()
	if v[0] == "0" or v[1] == "0":
		if v[3] == "ADD":
			val = v[1] if v[0] == "0" else v[0]
			new_text = " ".join([val if word==v[2] else word for word in text.split()])
			new_lines = new_text.split("Z")
			new_ops = new_lines[3:]
			new_ops[i] = "SKIP"
			text = "Z".join(lines[:3]+new_ops)
			ops = new_ops
		if v[3] == "MUL":
			new_text = " ".join(["0" if word==v[2] else word for word in text.split()])
			new_lines = new_text.split("Z")
			new_ops = new_lines[3:]
			new_ops[i] = "SKIP"
			text = "Z".join(lines[:3]+new_ops)
			ops = new_ops
	if v[0] == "1" or v[1] == "1":
		if v[3] == "MUL":
			val = v[1] if v[0] == "1" else v[0]		
			new_text = " ".join([val if word==v[2] else word for word in text.split()])
			new_lines = new_text.split("Z")
			new_ops = new_lines[3:]
			new_ops[i] = "SKIP"
			text = "Z".join(lines[:3]+new_ops)
			ops = new_ops
	K += 1

final = lines[:3]+ops
final = [f for f in final if f!="SKIP"]
t = "\n".join(final)
with open("check2block.txt", "w") as f:
	f.write(t)'''
