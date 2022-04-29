import numpy as np
from numpy.polynomial import polynomial as poly

n = 1024
q = 2 ** 32 - 1
base_n = [1] + [0] * (n - 1) + [1]

class bcolors:
    HEADER = '\033[95m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'

def generate_poly(n, q):
    global base_n
    coeffs = np.floor(np.random.normal(0, size=n))
    return coeffs


def round_public(public):
    zeros = np.asarray([0] * n)
    for i in range(len(zeros)):
        if len(public) <= i:
            break
        if int(public[i] / (q / 4)) == 0:
            zeros[i] = 0
        elif int(public[i] / (q / 2)) == 0:
            zeros[i] = 1
        elif int(public[i] / (3 * q / 4)) == 0:
            zeros[i] = 0
        elif int(public[i] / q) == 0:
            zeros[i] = 1
        else:
            print(bcolors.FAIL + "Rounding error for zeros" + bcolors.ENDC)
        i += 1
    return zeros

def round_shared(zeros, key):
    for i in range(len(zeros)):
        # Region 0 (0 --- q/4 and q/2 --- 3q/4)
        if zeros[i] == 0:
            if q * 0.125 <= key[i] < q * 0.625:
                key[i] = 1
            else:
                key[i] = 0

        # Region 1 (q/4 --- q/2 and 3q/4 --- q)
        elif zeros[i] == 1:
            if q * 0.875 <= key[i] < q * 0.375:
                key[i] = 0
            else:
                key[i] = 1

        else:
            print(bcolors.FAIL + "Rounding error for shared key" + bcolors.ENDC)
    return key


def main():
    print(bcolors.HEADER + "====================================="  + bcolors.ENDC)
    print(bcolors.HEADER + "=\t\t RLWE-KEX Math Demo\t\t    =" + bcolors.ENDC)
    print(bcolors.HEADER + "=====================================" + bcolors.ENDC)

    print(bcolors.OKCYAN + "RLWE Values: n = " + str(n) + " q = " + str(q) + bcolors.ENDC)
    print()

    print(bcolors.OKCYAN + "Generating A - random polynomial coefficient values:" + bcolors.ENDC)
    A = np.floor(np.random.random(size=n) * q) % q
    A = np.floor(poly.polydiv(A, base_n)[1])
    print("A:", A)
    print()

    print(bcolors.OKCYAN + "Generating client secret and error:" + bcolors.ENDC)
    sC = generate_poly(n, q)
    eC = generate_poly(n, q)
    print("Client Secret:", sC)
    print("Client Error:", eC)
    print()

    print(bcolors.OKCYAN + "Generating client public value - A * secret + error" + bcolors.ENDC)
    bC = poly.polymul(A, sC) % q
    bC = np.floor(poly.polydiv(sC, base_n)[1])
    bC = poly.polyadd(bC, eC) % q
    print("Client Public:", bC)
    print()

    print(bcolors.OKCYAN + "Generating server secret and error:" + bcolors.ENDC)
    sS = generate_poly(n, q)
    eS = generate_poly(n, q)
    print("Server Secret:", sS)
    print("Server Error:", eS)
    print()

    print(bcolors.OKCYAN + "Generating server public value - A * secret + error" + bcolors.ENDC)
    bS = poly.polymul(A, sS) % q
    bS = np.floor(poly.polydiv(sS, base_n)[1])
    bS = poly.polyadd(bS, eS) % q
    print("Server Public:", bS)
    print()

    print(bcolors.OKCYAN + "Generating shared key - public * secret / (x^n+ 1)" + bcolors.ENDC)
    sharedClient = np.floor(poly.polymul(sC, bS) % q)
    sharedClient = np.floor(poly.polydiv(sharedClient, base_n)[1]) % q
    sharedServer = np.floor(poly.polymul(sS, bC) % q)
    sharedServer = np.floor(poly.polydiv(sharedServer, base_n)[1]) % q
    print("Shared Key:", sharedClient)
    print()

    print(bcolors.OKCYAN + "Completing reconciliation using modular approaches:" + bcolors.ENDC)
    zeros = round_public(bS)
    print("Correction map:", zeros)
    print("Original Server Shared Key:", sharedServer)
    sharedServer = round_shared(zeros, sharedServer)
    print("Rounded Server Shared Key:", sharedClient)
    print("----------------------------------------------")
    print("Original Client Shared Key:", sharedClient)
    sharedClient = round_shared(zeros, sharedClient)
    print("Rounded Client Shared Key:", sharedClient)
    print()

    print(bcolors.OKCYAN + "Verifying shared keys are the same:" + bcolors.ENDC)
    valid = True
    for i in range(len(sharedClient)):
        if sharedClient[i] != sharedServer[i]:
            valid = False
    if valid:
        print(bcolors.OKGREEN + "Keys verified." + bcolors.ENDC)
    else:
        print(bcolors.FAIL + "Keys could not be verified." + bcolors.ENDC)


if __name__ == "__main__":
    main()
