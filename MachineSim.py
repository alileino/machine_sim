#encoding: utf-8
from NBitInt import NBitInt
import re

class MachineException(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

class MachineSim:
    debug = False
    DATA_BITS = 16
    OP_BITS = 4
    VALUE_BITS = 12
    MIN_ADDRESS = 0
    MAX_ADDRESS = 4095
    def __init__(self):
        self.resetRegisters()
        self.resetRam()

    def resetRegisters(self):
        self.ACC = NBitInt(self.DATA_BITS, 0)
        self.PC = 0
        self.IR = NBitInt(self.PC)

    def resetRam(self):
        self.MM = [NBitInt(self.DATA_BITS,0) for x in range(self.MIN_ADDRESS, self.MAX_ADDRESS+1)]

    def __updateIR(self):
        self.IR = self.MM[self.PC]

    def loadProgram(self, machineProgram):
        self.currentProgram = machineProgram
        self.PC = machineProgram.getStartAddress()
        self.__copyProgram()
        self.__updateIR()

    def setMemory(self, address, value):
        self.MM[address] = NBitInt(self.DATA_BITS, value)

    def __copyProgram(self):
        for line,ins in self.currentProgram.getProgramBinary().iteritems():
            self.MM[line] = ins.copy()

    def executeNext(self):
        rawOp, rawValue = self.IR.splitToArray(self.OP_BITS, self.VALUE_BITS)
        op = self.OPERATIONS_FUNC[rawOp]
        value = NBitInt(self.VALUE_BITS, rawValue)
        valueAtAddress=None
        if self.MIN_ADDRESS <= int(value) <= self.MAX_ADDRESS:
            valueAtAddress = self.MM[int(value)].copy()
        op(self, value, valueAtAddress)
        self.__updateIR()

    def incr_PC(self):
        self.PC = self.PC+1

    def opr_NOP(self, address, valueAtAddress):
        if self.debug:
            print self.oprDebugString("NOP", address)
        self.incr_PC()

    def opr_LOAD(self, address, valueAtAddress):
        if self.debug:
            print self.oprDebugString("LOAD", address, valueAtAddress)
        self.ACC = valueAtAddress
        self.incr_PC()

    def opr_STORE(self, address, valueAtAddress):
        if self.debug:
            print self.oprDebugString("STORE", address)
        self.MM[int(address)] = self.ACC.copy()
        self.incr_PC()

    def opr_ADD(self, address, valueAtAddress):
        if self.debug:
            print self.oprDebugString("ADD", address, valueAtAddress) + " to ACC=" + str(self.ACC)
        self.ACC += valueAtAddress
        self.incr_PC()

    def opr_SUBTRACT(self, address, valueAtAddress):
        if self.debug:
            print self.oprDebugString("SUBTRACT", address, valueAtAddress) + " from ACC=" + str(self.ACC)
        self.ACC -=valueAtAddress
        self.incr_PC()

    def opr_MULTIPLY(self, address, valueAtAddress):
        if self.debug:
            print self.oprDebugString("MULTIPLY", address, valueAtAddress) + " with ACC=" + str(self.ACC)
        self.ACC *= valueAtAddress
        self.incr_PC()

    def opr_DIVIDE(self, address, valueAtAddress):
        if self.debug:
            print self.oprDebugString("DIVIDE", address, valueAtAddress) + " with ACC=" + str(self.ACC)
        self.ACC //= valueAtAddress
        self.incr_PC()

    def opr_JUMP(self, address, valueAtAddress):
        if self.debug:
            print self.oprDebugString("JUMP", address)
        self.PC = int(address)

    def opr_JUMPZERO(self, address, valueAtAddress):
        if self.debug:
            print self.oprDebugString("JUMPZERO", address) + " with ACC=" + str(self.ACC)
        if self.ACC.isZero():
            self.PC = int(address)
        else:
            self.incr_PC()

    def opr_JUMPNEG(self, address, valueAtAddress):
        if self.debug:
            print self.oprDebugString("JUMPNEG", address) + " with ACC=" + str(self.ACC)
        if self.ACC.isSigned():
            self.PC = int(address)
        else:
            self.incr_PC()

    def opr_JUMPSUB(self, address, valueAtAddress):
        if self.debug:
            print self.oprDebugString("JUMPSUB", address)
        self.MM[int(address)] = NBitInt(self.DATA_BITS, self.PC + 1)
        self.PC = int(address)+1

    def opr_RETURN(self, address, valueAtAddress):
        if self.debug:
            print self.oprDebugString("RETURN", address, valueAtAddress)
        self.PC = int(valueAtAddress)

    def opr_LOADI(self, value, notUsed=None):
        if self.debug:
            print self.oprDebugString("LOADI", value)
        self.ACC = value
        self.incr_PC()

    def opr_LOADID(self, address, valueAtAddress):
        if self.debug:
            print self.oprDebugString("LOADID", address, valueAtAddress)
        self.ACC = self.MM[int(valueAtAddress)]
        self.incr_PC()

    def oprDebugString(self, operation, address, valueAtAddress=None):
        s = str(self.PC) + " " + operation + " "
        if valueAtAddress != None:
            s += "("
        s += str(address)

        if valueAtAddress != None:
            s += ")"
            s += "=" + str(valueAtAddress)
            s += "=" + valueAtAddress.bin()
        else:
            s += " ACC=" + str(self.ACC)
        return s

    def run(self, reload=False):
        if reload:
            self.resetRam()
            self.resetRegisters()
            self.loadProgram(self.currentProgram)
        lastIns = None
        while not self.IR.isZero():
            lastIns = self.PC
            self.executeNext()

    OPERATIONS_DEF =  {
              "NOP":        (0b0000, opr_NOP),
              "LOAD":       (0b0001, opr_LOAD),
              "STORE":      (0b0010, opr_STORE),
              "ADD":        (0b0011, opr_ADD),
              "SUBTRACT":   (0b0100, opr_SUBTRACT),
              "MULTIPLY":   (0b0101, opr_MULTIPLY),
              "DIVIDE":     (0b0110, opr_DIVIDE),
              "JUMP":       (0b0111, opr_JUMP),
              "JUMPZERO":   (0b1000, opr_JUMPZERO),
              "JUMPNEG":    (0b1001, opr_JUMPNEG),
              "JUMPSUB":    (0b1010, opr_JUMPSUB),
              "RETURN":     (0b1011, opr_RETURN),
    #extended instruction set
              "LOADI":      (0b1100, opr_LOADI),
              "LOADID":     (0b1101, opr_LOADID)
    }

    OPERATIONS_SIMPLE = {
        "NOP": (0b0000, opr_NOP),
        "LATAA": (0b0001, opr_LOAD),
        "TALLENNA": (0b0010, opr_STORE),
        "LISÄÄ": (0b0011, opr_ADD),
        "VÄHENNÄ": (0b0100, opr_SUBTRACT),
        "KERRO": (0b0101, opr_MULTIPLY),
        "JAA": (0b0110, opr_DIVIDE),
        "HYPPY": (0b0111, opr_JUMP),
        "NOLLAHYPPY": (0b1000, opr_JUMPZERO),
        "MIINUSHYPPY": (0b1001, opr_JUMPNEG),
        "OHJELMA": (0b1010, opr_JUMPSUB),
        "PALAA": (0b1011, opr_RETURN),
        # extended instruction set
        "LOADI": (0b1100, opr_LOADI),
        "LOADID": (0b1101, opr_LOADID)
    }

    # OPERATIONS_DEF = OPERATIONS_SIMPLE

    OPERATIONS = {keyword : value for keyword, (value,func) in OPERATIONS_DEF.items()}
    OPERATIONS_FUNC = {value : func for value, func in OPERATIONS_DEF.values()}

    def printState(self, memory=[],ACC=False, IR=False, PC=False):
        s = ""
        if ACC:
            s += "[ACC:"+ str(self.ACC)+ "]"
        if IR:
            s += "[IR:"+ str(self.IR.bin())+ "]"
        if PC:
            s += "<PC:"+ str(self.PC)+ ">"
        if len(memory) > 0:
            for address in memory:
                s += "[M" + str(address) + ":" + str(self.MM[address]) + "]"
        return s

class MachineProgram:
    MIN_ADDRESS = 0 # -1 used only internally, line never executed
    MAX_ADDRESS = 4095
    OPERATOR_ALIGN = 12

    def __init__(self, input):
        self.rawInput = input

        self.valueRegex = re.compile(r"\s*(?P<address>[0-9]+)\s+(?P<value>[0-9]+)(?P<comment>.*)")
        operatorStr = "|".join(MachineSim.OPERATIONS.keys())
        operatorSyntax = r"\s*(?P<address>[0-9]+)\s+(?P<operator>%s)\s+(?P<value>[0-9]+)?(?P<comment>.*)" % operatorStr
        self.operatorRegex = re.compile(operatorSyntax)
        self.nopRegex = re.compile(r"\s*(?P<address>[0-9]+)\s+(NOP)(?P<comment>.*)")
        self.commentRegex = re.compile(r"\s*#(?P<comment>.*)")
        self.program = self.parse(input)

        self.makeBinary()

        self.start = 0

    def makeBinary(self):
        self.programBinary = dict()
        for line in self.program:
            if len(line) == 2:
                self.programBinary[line[0]] = NBitInt(16, line[1])
            else:
                numValue = (line[1] << self.OPERATOR_ALIGN) | line[2]
                self.programBinary[line[0]] = NBitInt(16, numValue, unsigned=True)

    def getProgramArray(self):
        return self.program

    def getProgramBinary(self):
        return self.programBinary

    def getStartAddress(self):
        return self.start

    def setStartAddress(self, start):
        self.start = start

    def getLineStr(self, index):
        return "line " + str(index) + ": \"" + self.rawInput[index] + "\""

    def checkSpecialInstruction(self, instruction):
        instruction = instruction.strip().upper()
        if instruction == "DEBUG":
            MachineSim.debug = True
        elif instruction == "HELP":
            print repr(MachineSim.OPERATIONS.keys())
        else:
            return False
        return True

    def parseLine(self, input, lineNum):
        if len(input.strip())==0:
            return None
        valueMatch = self.valueRegex.match(input)
        if(valueMatch):
            return [int(valueMatch.group("address")), int(valueMatch.group("value"))]

        operatorMatch = self.operatorRegex.match(input)
        if(operatorMatch):
            operator = operatorMatch.group("operator")
            operator = MachineSim.OPERATIONS.get(operator)
            value = int(operatorMatch.group("value"))
            address = int(operatorMatch.group("address"))
            return [address, operator, value]
        nopMatch = self.nopRegex.match(input)
        if nopMatch:
            return [int(nopMatch.group("address")), MachineSim.OPERATIONS.get("NOP"), 1]
        if self.commentRegex.match(input):
            return None
        if(self.checkSpecialInstruction(input)):
            return None

        raise MachineException("Syntax error on line \"" + str(lineNum) + ":" + self.getLineStr(lineNum))

    def parse(self, input):
        input = [x for x in input.split("\n")]
        self.rawInput = input
        program = []
        for i in range(0, len(input)):

            line = input[i]
            parsedLine = self.parseLine(line, i)
            if(parsedLine):
                if parsedLine[0] < self.MIN_ADDRESS or parsedLine[0] > self.MAX_ADDRESS:
                    raise MachineException("Invalid address on line: " + line)
                program.append(parsedLine)
            continue

        return program

