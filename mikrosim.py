#coding: utf-8
import random as random
import re
from NBitInt import NBitInt
import operator
SIMULATOR_VERSION = "4"
SUPER_DEBUG = False # for debugging simulator as a student



class MikroSim:
    zeroInstruction = "0" * 22
    DATA_BITS = 16
    DATA_BIT_MASK = 0xFFFF
    MAR_WIDTH = 12
    MIR_WIDTH = 22
    MPC_WIDTH = 8
    DATA_ONE = NBitInt(DATA_BITS, 1)
    DATA_TWO = NBitInt(DATA_BITS, 2)

    def __init__(self, microProgram=None):

        self.resetRegisters()
        self.resetMPC()
        self.MPM = [self.zeroInstruction for x in range(0, 256)]
        self.MM = [NBitInt(self.DATA_BITS) for x in range(0, 4096)]

        if microProgram != None:
            self.MPM = [[str(x) for x in y] for y in microProgram.MPM]
            self.printClocks = microProgram.debug
            self.debug = microProgram.debug

        self.resetBus(True, True, True)

        if self.debug:
            self.printProgram()

    def resetBus(self, V1=False, V2=False, V3=False):
        if V1:
            self.V1 = NBitInt(self.DATA_BITS)
        if V2:
            self.V2 = NBitInt(self.DATA_BITS)
        if V3:
            self.V3 = NBitInt(self.DATA_BITS)

    def resetMIR(self):
        self.MIR_INS = self.MPM[0]

    def resetRegisters(self):
        self.A = NBitInt(self.DATA_BITS)
        self.B = NBitInt(self.DATA_BITS)
        self.C = NBitInt(self.DATA_BITS)
        self.D = NBitInt(self.DATA_BITS)
        self.MDR = NBitInt(self.DATA_BITS)
        self.MAR = NBitInt(self.MAR_WIDTH, unsigned=True)

    def resetMPC(self):
        self.MPC = NBitInt(self.MPC_WIDTH, unsigned=True)

    def clock1(self):
        MIR = self.MIR
        self.resetBus(True, True, True)
        for i in range(1, 5):
            if MIR(i):
                self.V2 = self.getABCD_complement()[i - 1]
        if MIR(5):
            self.V1 = self.DATA_ONE
        if MIR(6):
            self.V1 = self.MDR

        # Alu
        self.V3 = self.executeALU(self.V1, self.V2, MIR(7), MIR(8))

    def clock2(self):
        MIR = self.MIR
        if MIR(9):
            self.A = self.V3.copy()
        if MIR(10):
            self.B = self.V3.copy()
        if MIR(11):
            self.C = self.V3.copy()
        if MIR(12):
            self.D = self.V3.copy()
        if MIR(13):
            self.MDR = self.V3.copy()
        if MIR(14):
            discarded, marValue = self.V3.splitToArray(4,12)
            self.MAR = NBitInt(self.MAR_WIDTH, marValue, unsigned=True)

    def clock3(self):
        MIR = self.MIR
        if MIR(15):
            self.MDR = self.MM[int(self.MAR)]
        if MIR(16):
            self.MM[int(self.MAR)] = self.MDR

    def clock4(self):
        MIR = self.MIR
        self.resetBus(True, True, True)

        if MIR(17):
            self.V1 = self.DATA_ONE
        if MIR(18):
            self.V1 = NBitInt(self.DATA_BITS, int("".join(self.MIR_INS[:8]),2))
        if MIR(19):
            if self.A.isZero():
                self.V1 = self.DATA_ONE
            else:
                self.V1 = self.DATA_TWO
        if MIR(20):
            if self.A.isSigned():
                self.V1 = self.DATA_ONE
            else:
                self.V1 = self.DATA_TWO
        if MIR(21):
            highOrderBits = self.MDR.splitToArray(4, self.DATA_BITS-4)[0]
            self.V1 = NBitInt(self.DATA_BITS, highOrderBits)
        if MIR(22):
            self.V2 = self.MPC
        self.V3 = self.executeALU(self.V1, self.V2, 0, 0)

    def clock5(self):
        self.MPC = self.V3.copy()
        self.MIR_INS = self.MPM[int(self.MPC)]

    def executeALU(self, v1, v2, complement, x2):
        result = NBitInt(self.DATA_BITS, int(v1))
        if complement:
            result.complement()
        result += v2
        if x2:
            result <<= 1

        return result

    def clocks(self):
        return [self.clock1, self.clock2, self.clock3, self.clock4, self.clock5]

    def executeCycle(self):
        if self.printClocks:
            print ("Executing address[" + str(self.MPC)) + "] MIR=" + "".join(self.MIR_INS[:8]) + " "\
                ""+"".join(self.MIR_INS[8:14]) + " " + "".join(self.MIR_INS[14:16]) + " " + "".join(self.MIR_INS[16:])

        for i in range(0, 5):
            self.clocks()[i]()
            if self.printClocks:
                print "After clock", (i + 1), ":"
                self.printState()

    def printState(self):
        print self.printRegisters(*[True for x in range(7)])

    def MIR(self, cc):
        return int(self.MIR_INS[cc - 1])



    def aluTest(self):
        print self.executeALU(self.DATA_ONE,self.DATA_ONE,0,0).copy()

    def execute(self):
        self.resetBus()
        self.resetMPC()
        self.resetMIR()
        while (True):
            if ("".join(self.MIR_INS) == self.zeroInstruction):
                if self.printClocks:
                    print "Microprogram ended."
                break
            self.executeCycle()

    def setA(self, num):
        self.A = NBitInt(self.DATA_BITS, num)

    def setB(self, num):
        self.B = NBitInt(self.DATA_BITS, num)

    def setC(self, num):
        self.C = NBitInt(self.DATA_BITS, num)

    def setC(self, num):
        self.C = NBitInt(self.DATA_BITS, num)

    def setD(self, num):
        self.D = NBitInt(self.DATA_BITS, num)

    def getABCD_complement(self):
        return [self.A, self.B, self.C, self.D]

    def setABCD(self, a, b, c, d):
        self.setA(a)
        self.setB(b)
        self.setC(c)
        self.setD(d)

    def setMemory(self,address, data):
        self.MM[address] = NBitInt(self.DATA_BITS, data)
    def getMemory(self, address):
        return int(self.MM[address])

    def printRegisters(self, a=False, b=False, c=False, d=False, mdr=False, mar=False, mpc=False):
        s = ""
        if a:
            s += "[A:"+ str(self.A)+ "]"
        if b:
            s += "[B:"+ str(self.B)+ "]"
        if c:
            s += "[C:"+ str(self.C)+ "]"
        if d:
            s += "[D:"+ str(self.D)+ "]"
        if mdr:
            s += "[MDR:"+str( self.MDR)+ "]"
        if mar:
            s += "[MAR:"+ str(self.MAR)+ "]"
        if mpc:
            s += "<MPC:"+ str(self.MPC)+ ">"
        return s

    def printProgram(self):
        indexed = [(idx, "  ".join(self.MPM[idx])) for idx in range(0,256)]
        indexed = [("%s: %s" % ("{0: < 4}".format(pair[0]), pair[1])) for pair in indexed if pair[1].replace(" ", "") != self.zeroInstruction]
        print("      " + " ".join(["{0:<2}".format(x) for x in range(1,23)]))
        print("\n".join(indexed))


class MicroProgram(object):
    zeroInstruction = [0]*22

    def __init__(self, userInput):
        self.MPM = [list(self.zeroInstruction) for x in range(0, 256)]
        self.MPC = 0
        self.debug = False
        self.parse(userInput)

    def setCurrent(self, address):
        self.MPC = address

    def next(self):
        self.MPC += 1

    def setCC(self, *ccs):
        for cc in ccs:
            self.MPM[self.MPC][cc - 1] = 1
        self.next()

    def clearCC(self, cc):
        self.MPM[self.MPC][cc - 1] = 0

    def parse(self, input):
        input = [s.strip() for s in input.split("\n") if len(s.strip()) > 0]

        ccre = None
        splitre = re.compile(r"(\d*)[-a-zA-Z,\s]+")

        lineNum = 0
        for line in input:
            if "debug" in line:
                self.debug = True
                continue
            if ":" in line:
                lineNum, line = line.split(":", 1)
                lineNum = int(lineNum)
                line = line.strip()

            if "cc" in line: #Assume old notation
                if ccre is None:
                    ccre = re.compile(r".*cc\((.*)\)")
                line = ccre.split(line)[1]

            nums = [int(x) for x in splitre.split(line) if len(x)>0]
            self.setCurrent(lineNum)
            self.setCC(*nums)
            lineNum += 1



def debug():
    global mp
    mp.debug = True
    print "VAROITUS: palautuksesta ei saa pisteitä, jos debug()-kutsu on vastauksessa!"

