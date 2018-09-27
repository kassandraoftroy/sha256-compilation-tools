from circuit_interpreter import Circuit
from dumb_compiler import compiler


def run_tests():
    vals = [
        test_maj(11, 22, 33),
        test_ch(491, 2222),
        test_bsig(2**30 + 1111),
        test_lsig(251, 999, 84),
        test_loop(221, 353, 99),
        test_add(2**32 - 20, 25)
    ]
    if vals == [True, True, True, True, True, True]:
        return "PASS"
    else:
        print vals
        return "FAIL"


def test_add(x, y):
    # Compilation
    text = compiler("add_script.txt")
    with open("add.txt", "w") as f:
        f.write(text)

    # Load compiled Maj circuit
    add_program = Circuit("add.txt")

    # Create inputs
    tape_tmp = [int(i) for i in int2bin32(x) + int2bin32(y)]
    tape = [tape_tmp[-(i + 1)] for i in range(len(tape_tmp))]
    print tape
    # Run compiled Cicuit
    result = add_program.run(tape)
    print result

    # Confirm Result
    a = int("".join([str(result[-(i + 1)]) for i in range(len(result))]), 2)
    print a
    print(x + y) % (2**32)
    return a == ((x + y) % (2**32))


def test_maj(x, y, z):
    # Compilation
    text = compiler("maj_script.txt")
    with open("maj.txt", "w") as f:
        f.write(text)

    # Load compiled Maj circuit
    maj_program = Circuit("maj.txt")

    # Create inputs
    tape = [int(i) for i in int2bin32(x) + int2bin32(y) + int2bin32(z)]

    # Run compiled Cicuit
    result = maj_program.run(tape)

    # Confirm Result
    return int("".join([str(i) for i in result]), 2) == Maj(x, y, z)


def test_ch(y, z):

    # Compilation
    text = compiler("ch_script.txt")
    with open("ch.txt", "w") as f:
        f.write(text)

    # Load compiled Loop Circuit
    ch_program = Circuit("ch.txt")

    # Create inputs
    tape = [int(i) for i in int2bin32(y) + int2bin32(z)]

    # Run Compiled Circuit
    result = ch_program.run(tape)

    # Confirm Result
    x = 2**31 + 3  # constant set in program
    return int("".join([str(i) for i in result]), 2) == Ch(x, y, z)


def test_loop(x, y, z):
    # Compilation
    text = compiler("loop_script.txt")
    with open("loop.txt", "w") as f:
        f.write(text)

    # Load compiled Loop Circuit
    loop_program = Circuit("loop.txt")

    # Create inputs
    tape = [int(i) for i in int2bin32(x) + int2bin32(y) + int2bin32(z)]

    # Run Compiled Circuit
    result = loop_program.run(tape)

    # Confirm Result
    return int("".join([str(i) for i in result]), 2) == check_loop_test(
        x, y, z)


# The loop program written in python as a control for test:
def check_loop_test(x, y, z):
    d = Maj(x, y, z)
    for _ in range(3):
        x = bsig0(x)
        e = bsig0(d)
        d = Maj(x, e, d)
    return d


def test_bsig(a):
    # Compilation
    text = compiler("bsig_script.txt")
    with open("bsig.txt", "w") as f:
        f.write(text)

    # Load compiled Loop Circuit
    bsig_program = Circuit("bsig.txt")

    # Create inputs
    tape = bin(a)[2:]
    while len(tape) < 256:
        tape = "0" + tape
    tape = [int(i) for i in tape]

    # Run Compiled Circuit
    result = bsig_program.run(tape)

    # Confirm Result
    check = check_bsig_test(tape)
    return int("".join([str(i) for i in result]), 2) == check


def check_bsig_test(l):
    a = int("".join([str(i) for i in l[0:32]]), 2)
    b = int("".join([str(i) for i in l[32:64]]), 2)
    c = int("".join([str(i) for i in l[68:100]]), 2)
    a = bsig0(a)
    b = bsig1(b)
    return Maj(a, b, c)


def test_lsig(x, y, z):
    text = compiler("lsig_script.txt")
    with open("lsig.txt", "w") as f:
        f.write(text)

    # Load compiled Loop Circuit
    lsig_program = Circuit("lsig.txt")

    # Create inputs
    tape = [int(i) for i in int2bin32(x) + int2bin32(y) + int2bin32(z)]

    # Run Compiled Circuit
    result = lsig_program.run(tape)

    # Confirm Result
    return int("".join([str(i) for i in result]), 2) == check_lsig_test(
        x, y, z)


def check_lsig_test(a, b, c):
    a = lsig0(a)
    b = lsig1(b)
    return Maj(a, b, c)


def test_loop2(a):
    # Compilation
    text = compiler("loop2_script.txt")
    with open("loop2.txt", "w") as f:
        f.write(text)

    # Load compiled Loop Circuit
    loop2_program = Circuit("loop2.txt")

    # Create inputs
    tape = bin(a)[2:]
    while len(tape) < 256:
        tape = "0" + tape
    tape = [int(i) for i in tape]

    # Run Compiled Circuit
    result = loop2_program.run(tape)

    # Confirm Result
    check = check_loop2_test(tape)
    return int("".join([str(i) for i in result]), 2) == check


def check_loop2_test(l):
    list1 = [
        int("".join([str(i) for i in l[224:256]]), 2),
        int("".join([str(i) for i in l[192:224]]), 2)
    ]
    a = int("".join([str(i) for i in l[100:132]]), 2)
    for j in range(2):
        b = list1[j]
        c = int("".join([str(i) for i in l[j * 32:(j + 1) * 32]]), 2)
        a = Ch(a, b, c)
    return a


# Helpers
def int2bin32(num):
    s = bin(num)[2:]
    if len(s) > 32:
        raise ValueError
    while len(s) < 32:
        s = "0" + s
    return s


def Maj(x, y, z):
    return (x & y) ^ (x & z) ^ (y & z)

ROR = lambda val, r_bits, max_bits: \
    ((val & (2**max_bits-1)) >> r_bits%max_bits) | \
    (val << (max_bits-(r_bits%max_bits)) & (2**max_bits-1))


def bsig0(x):
    return ROR(x, 2, 32) ^ ROR(x, 13, 32) ^ ROR(x, 22, 32)


def bsig1(x):
    return ROR(x, 6, 32) ^ ROR(x, 11, 32) ^ ROR(x, 25, 32)


def NOT(x):
    return ((2 << 32) - 1) ^ x


def Ch(x, y, z):
    return (x & y) ^ (NOT(x) & z)


def lsig0(x):
    return ROR(x, 7, 32) ^ ROR(x, 18, 32) ^ (x >> 3)


def lsig1(x):
    return ROR(x, 17, 32) ^ ROR(x, 19, 32) ^ (x >> 10)


print run_tests()
