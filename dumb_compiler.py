from my_lexer import getTokens

tape_len = 0
input_len = 0
id2var = {}
text = ""
prime_order = 2

types = {
    "BIT32": {
        "length": 32
    },
    "BIT256": {
        "length": 256
    },
    "BIT512": {
        "length": 512
    },
    "BIT2048": {
        "length":2048
    },
    "BIT": {
        "length": 1
    },
    "BIT4": {
        "length": 4
    }
}


def compiler(filename, prime=2):
    reset(prime)
    toks = getTokens(filename)
    lines = [[t for t in toks if t[2] == i] for i in range(1, toks[-1][2] + 1)]
    skip = False

    for line in lines:
        if len(line) > 0:
            if not skip:
                #constant
                if line[0][0] == "CONSTANT":
                    if not constant(line[1][0], line[2], line[3:]):
                        return "CONSTANT ERROR LINE %s" % line[0][2]
                #input
                if line[0][0] == "INPUT":
                    if not input(line[1][0], line[2]):
                        return "INPUT ERROR LINE %s" % line[0][2]

                #assignment
                if line[0][0] == "ASSIGN":
                    if not assign(line[1][0], line[2], line[4:]):
                        return "ASSIGNEMNT ERROR LINE %s %s" % (line[0][2], repr(line))

                #loops - no nestled looping for now
                if line[0][0] == "LOOP":
                    ok, error = loop(lines[lines.index(line):])
                    if not ok:
                        return error
                    else:
                        skip = True

                #output
                if line[0][0] == "OUTPUT":
                    if not output(line[1]):
                        return "OUTPUT ERROR"
            else:
                if line[0][0] == "RBRACE":
                    skip = False
    return text


def constant(type_, name, expr):
    global tape_len, input_len, id2var, text, prime_order

    if type_ not in types.keys():
        return False
    if name[0] != "ID" or expr[0][0] != "EQUALS":
        return False
    expr = expr[1:]
    vals = []
    for i in expr:
        if i[0] == "COMMA":
            pass
        elif i[0] == "NUMBER":
            vals.append(i[1] % prime_order)
        else:
            return False
    if len(vals) != types[type_]["length"]:
        return False
    id2var[name[1]] = {"type": type_, "address": tape_len}
    tape_len += types[type_]["length"]
    addr = id2var[name[1]]["address"]
    for i in range(len(vals)):
        text = "%s %s %s\n" % ("C", addr + i, vals[i]) + text
    return True


def input(type_, name):
    global tape_len, input_len, id2var, text, prime_order

    if type_ not in types.keys():
        return False
    if name[0] != "ID":
        return False
    id2var[name[1]] = {"type": type_, "address": tape_len}
    tape_len += types[type_]["length"]
    input_len += types[type_]["length"]
    return True


def assign(type_, name, expr):
    global tape_len, input_len, id2var, text, prime_order

    if type_ not in types.keys():
        return False
    if name[0] != "ID":
        return False

    # assign the output of a function
    if functions(expr[0][0], expr[1:]):
        id2var[name[1]] = {
            "address": tape_len - types[type_]["length"],
            "type": type_
        }
        return True

    # assign a slice of a previous variable
    elif expr[0][1] in id2var.keys() and expr[1][0] == "LBRACK":
        vals = expr[2][1], expr[4][1]
        if vals[1] - vals[0] != types[type_]["length"]:
            return False
        else:
            id2var[name[1]] = {
                "address": id2var[expr[0][1]]["address"] + vals[0],
                "type": type_
            }
            return True
    return False


def loop(lines):
    loop = lines[0]
    if loop[2][0] != 'NUMBER':
        return False, "LOOP ERROR LINE %s: MUST LOOP OVER A NUMBER" % loop[0][2]
    lines = lines[1:]
    found = False
    for i in range(len(lines)):
        if len(lines[i]) > 0:
            if lines[i][0][0] == "RBRACE":
                lines = lines[:i]
                found = True
                break
    if not found:
        return False, "LOOP ERROR LINE %s: NO CLOSING BRACE" % loop[0][2]
    for i in range(loop[2][1]):
        new_lines = []
        for line in lines:
            if "STAR" in [j[0] for j in line]:
                star_index = [j[0] for j in line].index("STAR")
                if line[star_index-1][0] == "LBRACK":
                    num = line[star_index+1][1]
                    new_toks = getTokens(None, "%s:%s]"%(i*num, (i+1)*num))
                    new_lines.append(line[:star_index]+new_toks)
                elif line[star_index-1][0] == "ID" and line[star_index-2][0]=="EQUALS":
                	length = types[id2var["%s%s"%(line[star_index-1][1], i)]["type"]]["length"]
                	new_toks = getTokens(None, "%s%s[0:%s]"%(line[star_index-1][1], i, length))
                	new_lines.append(line[:star_index-1]+new_toks)

            else:
                new_lines.append(line)
        for line in new_lines:
            if len(line) > 0:
                if line[0][0] == "LBRACE" or line[0][0] == "RBRACE":
                    pass
                elif line[0][0] == "ASSIGN":
                    if not assign(line[1][0], line[2], line[4:]):
                        return False, "ASSIGNEMNT ERROR LINE %s" % line[0][2]
                else:
                    return False, "LOOP ERROR LINE %s" % line[0][2]
    return True, None


def output(id_):
    global tape_len, input_len, id2var, text, prime_order

    if id_[0] != "ID":
        if id_[0] == "NUMBER":
            output_len = id_[1]
            first_line = "%s %s %s %s\n" % (prime_order, input_len,
                                            output_len, tape_len)
            text = first_line + text[:-1]
            return True        
        return False
    else:
        if id_[1] not in id2var.keys():
            return False
        else:
            if id2var[id_[1]]["address"] + types[id2var[
                    id_[1]]["type"]]["length"] != tape_len:
                return False
            else:
                # if everything is as expected, then simply write the header line and the compilation is done
                output_len = types[id2var[id_[1]]["type"]]["length"]
                first_line = "%s %s %s %s\n" % (prime_order, input_len,
                                                output_len, tape_len)
                text = first_line + text[:-1]
                return True


def functions(name, expr):
    global tape_len, input_len, id2var, text, prime_order

    ## write functions here (this is where the circuit actually gets written)

    if name == "MAJ":
        if expr[0][0] == "LPAREN" and expr[6][0] == "RPAREN":
            ids = [expr[1][1], expr[3][1], expr[5][1]]
            addrs = []
            for id_ in ids:
                if id2var[id_]["type"] == "BIT32":
                    addrs.append(id2var[id_]["address"])
                else:
                    return False

            addrs.append(tape_len)
            for i in range(32):
                text += "%s %s %s ADD\n" % (addrs[1] + i, addrs[2] + i,
                                            tape_len)
                tape_len += 1
            addrs.append(tape_len)
            for i in range(32):
                text += "%s %s %s MUL\n" % (addrs[0] + i, addrs[3] + i,
                                            tape_len)
                tape_len += 1
            addrs.append(tape_len)
            for i in range(32):
                text += "%s %s %s MUL\n" % (addrs[1] + i, addrs[2] + i,
                                            tape_len)
                tape_len += 1
            for i in range(32):
                text += "%s %s %s ADD\n" % (addrs[4] + i, addrs[5] + i,
                                            tape_len)
                tape_len += 1
            return True

    if name == "CH":
        if expr[0][0] == "LPAREN" and expr[8][0] == "RPAREN":
            ids = [expr[1][1], expr[3][1], expr[5][1], expr[7][1]]
            addrs = []
            for i in range(len(ids)):
                if id2var[ids[i]]["type"] == "BIT32":
                    addrs.append(id2var[ids[i]]["address"])
                elif id2var[ids[i]]["type"] == "BIT" and i == 3:
                    addrs.append(id2var[ids[i]]["address"])
                else:
                    return False

            addrs.append(tape_len)
            for i in range(32):
                text += "%s %s %s ADD\n" % (addrs[0] + i, addrs[3], tape_len)
                tape_len += 1
            addrs.append(tape_len)
            for i in range(32):
                text += "%s %s %s MUL\n" % (addrs[0] + i, addrs[1] + i,
                                            tape_len)
                tape_len += 1
            addrs.append(tape_len)
            for i in range(32):
                text += "%s %s %s MUL\n" % (addrs[4] + i, addrs[2] + i,
                                            tape_len)
                tape_len += 1
            for i in range(32):
                text += "%s %s %s ADD\n" % (addrs[5] + i, addrs[6] + i,
                                            tape_len)
                tape_len += 1
            return True

    if name == "BSIG0":
        if expr[0][0] == "LPAREN" and expr[2][0] == "RPAREN":
            ids = [expr[1][1]]
            addrs = []
            for id_ in ids:
                if id2var[id_]["type"] == "BIT32":
                    addrs.append(id2var[id_]["address"])
                else:
                    return False

            registers = [i for i in range(addrs[0], addrs[0] + 32)]
            v1 = registers[-2:] + registers[:-2]
            v2 = registers[-13:] + registers[:-13]
            v3 = registers[-22:] + registers[:-22]
            addrs.append(tape_len)
            for i in range(32):
                text += "%s %s %s ADD\n" % (v1[i], v2[i], tape_len)
                tape_len += 1
            for i in range(32):
                text += "%s %s %s ADD\n" % (v3[i], addrs[1] + i, tape_len)
                tape_len += 1
            return True

    if name == "BSIG1":
        if expr[0][0] == "LPAREN" and expr[2][0] == "RPAREN":
            ids = [expr[1][1]]
            addrs = []
            for id_ in ids:
                if id2var[id_]["type"] == "BIT32":
                    addrs.append(id2var[id_]["address"])
                else:
                    return False

            registers = [i for i in range(addrs[0], addrs[0] + 32)]
            v1 = registers[-6:] + registers[:-6]
            v2 = registers[-11:] + registers[:-11]
            v3 = registers[-25:] + registers[:-25]
            addrs.append(tape_len)
            for i in range(32):
                text += "%s %s %s ADD\n" % (v1[i], v2[i], tape_len)
                tape_len += 1
            for i in range(32):
                text += "%s %s %s ADD\n" % (v3[i], addrs[1] + i, tape_len)
                tape_len += 1
            return True

    if name == "LSIG0":
        if expr[0][0] == "LPAREN" and expr[4][0] == "RPAREN":
            ids = [expr[1][1], expr[3][1]]
            addrs = []
            for i in range(len(ids)):
                if id2var[ids[i]]["type"] == "BIT32" and i == 0:
                    addrs.append(id2var[ids[i]]["address"])
                elif id2var[ids[i]]["type"] == "BIT" and i == 1:
                    addrs.append(id2var[ids[i]]["address"])
                else:
                    return False

            registers = [i for i in range(addrs[0], addrs[0] + 32)]
            v1 = registers[-7:] + registers[:-7]
            v2 = registers[-18:] + registers[:-18]
            v3 = [addrs[1] for _ in range(3)] + registers[0:len(registers) - 3]
            addrs.append(tape_len)
            for i in range(32):
                text += "%s %s %s ADD\n" % (v1[i], v2[i], tape_len)
                tape_len += 1
            for i in range(32):
                text += "%s %s %s ADD\n" % (v3[i], addrs[2] + i, tape_len)
                tape_len += 1
            return True
    if name == "LSIG1":
        if expr[0][0] == "LPAREN" and expr[4][0] == "RPAREN":
            ids = [expr[1][1], expr[3][1]]
            addrs = []
            for i in range(len(ids)):
                if id2var[ids[i]]["type"] == "BIT32" and i == 0:
                    addrs.append(id2var[ids[i]]["address"])
                elif id2var[ids[i]]["type"] == "BIT" and i == 1:
                    addrs.append(id2var[ids[i]]["address"])
                else:
                    return False

            registers = [i for i in range(addrs[0], addrs[0] + 32)]
            v1 = registers[-17:] + registers[:-17]
            v2 = registers[-19:] + registers[:-19]
            v3 = [addrs[1]
                  for _ in range(10)] + registers[0:len(registers) - 10]
            addrs.append(tape_len)
            for i in range(32):
                text += "%s %s %s ADD\n" % (v1[i], v2[i], tape_len)
                tape_len += 1
            for i in range(32):
                text += "%s %s %s ADD\n" % (v3[i], addrs[2] + i, tape_len)
                tape_len += 1
            return True

    if name == "ADD":
        if expr[0][0] == "LPAREN" and expr[4][0] == "RPAREN":
            ids = [expr[1][1], expr[3][1]]
            addrs = []
            for i in range(len(ids)):
                if id2var[ids[i]]["type"] == "BIT32":
                    addrs.append(id2var[ids[i]]["address"])
                else:
                    return False

            # First layer
            addrs.append(tape_len)
            p_ = tape_len
            for i in range(32):
                text += "%s %s %s ADD\n" % (addrs[0] + i, addrs[1] + i,
                                            tape_len)
                tape_len += 1

            addrs.append(tape_len)
            g_ = tape_len
            for i in range(32):
                text += "%s %s %s MUL\n" % (addrs[0] + i, addrs[1] + i,
                                            tape_len)
                tape_len += 1

            def PG(in1, in2):
                """
                Takes as input two pointers to two pairs of bits
                """
                global tape_len, text

                result0 = tape_len
                text += "%s %s %s MUL\n" % (in1[0], in2[0], result0)
                tape_len += 1

                result1 = tape_len
                text += "%s %s %s MUL\n" % (in1[1], in2[0], result1)
                tape_len += 1

                result2 = tape_len
                text += "%s %s %s ADD\n" % (result1, in2[1], result2)
                tape_len += 1

                return result0, result2

            # PGPre (notation from SecureSCM)
            addrs.append(tape_len)
            a = [[p_ + i, g_ + i] for i in range(32)]

            for i in range(1, 6):
                for j in range(1, (32 / pow(2, i)) + 1):
                    y = pow(2, i - 1) + (j - 1) * pow(2, i)
                    for z in range(1, 2**(i - 1)):
                        a[y + z - 2] = PG(a[y - 1], a[y + z - 2])

            # Now xor the carry bits with the original xor'ed result
            for i in range(32):
            	if i != 0:
                    text += "%s %s %s ADD\n" % (p_ + i, a[i-1][1], tape_len)
                else:
                	text += "%s %s %s ADD\n" % (p_ + i, 0, tape_len)
                tape_len += 1

            return True

    if name=="ADD4":
        if expr[0][0] == "LPAREN" and expr[4][0] == "RPAREN":
            ids = [expr[1][1], expr[3][1]]
            addrs = []
            for i in range(len(ids)):
                if id2var[ids[i]]["type"] == "BIT4":
                    addrs.append(id2var[ids[i]]["address"])
                else:
                    return False
                    
            addrs.append(tape_len)
            p_ = tape_len
            for i in range(4):
                text += "%s %s %s ADD\n" % (addrs[0] + i, addrs[1] + i,
                                            tape_len)
                tape_len += 1

            addrs.append(tape_len)
            g_ = tape_len
            for i in range(4):
                text += "%s %s %s MUL\n" % (addrs[0] + i, addrs[1] + i,
                                            tape_len)
                tape_len += 1

            def PG(in1, in2):
                """
                Takes as input two pointers to two pairs of bits
                """
                global tape_len, text

                result0 = tape_len
                text += "%s %s %s MUL\n" % (in1[0], in2[0], result0)
                tape_len += 1

                result1 = tape_len
                text += "%s %s %s MUL\n" % (in1[1], in2[0], result1)
                tape_len += 1

                result2 = tape_len
                text += "%s %s %s ADD\n" % (result1, in2[1], result2)
                tape_len += 1

                return result0, result2

            # PGPre (notation from SecureSCM)
            addrs.append(tape_len)
            a = [[p_ + i, g_ + i] for i in range(4)]

            for i in range(1, 3):
                for j in range(1, (4 / pow(2, i)) + 1):
                    y = pow(2, i - 1) + (j - 1) * pow(2, i)
                    for z in range(1, 2**(i - 1)):
                        a[y + z - 1] = PG(a[y - 1], a[y + z - 1])

            # Now xor the carry bits with the original xor'ed result
            for i in range(4):
                if i != 0:
                    text += "%s %s %s ADD\n" % (p_ + i, a[i-1][1], tape_len)
                else:
                    text += "%s %s %s ADD\n" % (p_ + i, 0, tape_len)
                tape_len += 1
        return True
    return False


def reset(prime):
    global tape_len, input_len, id2var, text, prime_order
    tape_len = 0
    input_len = 0
    id2var = {}
    text = ""
    prime_order = prime

