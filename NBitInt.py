#encoding: utf-8
import operator

class NBitInt:
    def __init__(self, bits, num=0, unsigned=False):
        self.value = num
        self.bits = bits
        self.bitmask = 2**bits-1
        self.unsigned = unsigned

        if num < 0:
            self.value = abs(num)
            self.value = NBitInt.__complement_impl(self.bits, self.value)

    def __signBit(self):
        if not self.unsigned:
            return (self.value >> (self.bits-1)) & 1
        return 0 # treat first bit as data bit

    def isSigned(self):
        return self.__signBit() != 0

    def isZero(self):
        return self.value == 0

    def splitToArray(self, *args):
        if sum(args) != self.bits:
            raise ValueError("Invalid params: " + repr(args))
        result = []
        mask = self.bitmask

        cumulBits = 0
        for bits in args:
            num = (self.value << cumulBits) & self.bitmask #discard high order bits
            num = num >> (self.bits - bits)
            cumulBits += bits
            result.append(num)

        return result

    def copy(self):
        return NBitInt(self.bits,int(self),self.unsigned)

#OPERATORS
#ARITHMETIC
    @staticmethod
    def __add_impl(x, y, bitmask):
        return (x+y) & bitmask

    def __add__(self, other):
        other = int(other)
        return NBitInt(self.bits,
                       NBitInt.add_impl(self.value, other.value, self.bitmask),
                       unsigned=self.unsigned)

    def __iadd__(self, other):
        other = int(other)
        self.value = NBitInt.__add_impl(self.value, other, self.bitmask)
        return self

    @staticmethod
    def __subtract_impl(lhs, rhs):
        rhs = -rhs
        result = lhs + rhs
        return result

    def __sub__(self, other):
        return NBitInt.subtract_impl(self, other)

    def __isub__(self, other):
        other = -other
        self += other
        return self

    @staticmethod
    def __multiply_impl(bitmask, x, y):
        return (x*y) & bitmask

    def __mul__(self, other):
        other = int(other)
        return NBitInt(self.bits,
                       NBitInt.multiply_impl(self.bitmask, self.value, other),
                       unsigned=self.unsigned)

    def __imul__(self, other):
        other = int(other)
        self.value = NBitInt.__multiply_impl(self.bitmask, self.value, other)
        return self

    @staticmethod
    def __complement_impl(bits, y):
        return 2**bits - y


    def __neg__(self):
        value = NBitInt.__complement_impl(self.bits, self.value)
        return NBitInt(self.bits, value, unsigned=self.unsigned)

    @staticmethod
    def __divide_impl(x, y):
        x,y = map(int, (x,y))
        result = x//y
        return result

    def __floordiv__(self, other):
        value = NBitInt.divide_impl(self.value, other)
        return NBitInt(self.bits, value, unsigned=self.unsigned)

    def __ifloordiv__(self, other):
        value = NBitInt.__divide_impl(self.value, other)
        if value < 0:
            value = self.complement_impl(value)
        self.value = value
        return self

#END ARITHMETIC OPERATORS

#SHIFT OPERATORS

    def __lshift_impl(self, num):
        return (self.value << num) & self.bitmask

    def __lshift__(self, num):
        return NBitInt(self.bits, self.lshift_impl(num), unsigned=self.unsigned)

    def __ilshift__(self, num):
        self.value = self.lshift_impl(num)
        return self

    def __rshift__(self, num):
        return NBitInt(self.bits, self.value >> num, unsigned=self.unsigned)

    def __irshift__(self, num):
        self.value >>= num
        return self

    #If one of the operands is unsigned, the result will also be. The result has as many bits as the largest operand
    @staticmethod
    def binop_impl(num1, num2, oper):
        isNbit = [isinstance(x, NBitInt) for x in [num1, num2]]
        bits = 16
        unsigned = True
        val1 = val2 = 0
        if all(isNbit):
            bits = max(num1.bits, num2.bits)
            unsigned = num1.unsigned | num2.unsigned
            val1, val2 = num1.value, num2.value
        elif any(isNbit):
            if isNbit[1]:
                num1,num2 = num2,num1 #swap
            val1, val2 = num1.value, num2
            bits = num1.bits
            unsigned = num1.unsigned
        val = oper(val1, val2)
        return NBitInt(bits, num=val, unsigned=unsigned)

    def __and__(self, other):
        return NBitInt.binop_impl(self, other, operator.__and__)

    def __iand__(self, other):
        self.value = NBitInt.binop_impl(self, other, operator.__and__).value
        return self

    def __or__(self, other):
        return NBitInt.binop_impl(self, other, operator.__or__)

    def __ior__(self, other):
        self.value = NBitInt.binop_impl(self, other, operator.__or__).value
        return self

    def __xor__(self, other):
        return NBitInt.binop_impl(self, other, operator.__xor__)

    def __ixor__(self, other):
        self.value = NBitInt.binop_impl(self, other, operator.__ixor__).value
        return self

#Unary operators
    def __invert__(self):
        return NBitInt(self.bits, num=(self.bitmask - self.value), unsigned=self.unsigned)

    def __pos__(self):
        return self.copy()
#End unary operators

#Built-in functions
    def __abs__(self):
        return NBitInt(self.bits, num=abs(self.value))

    def __int__(self):
        if self.isSigned():
            return -NBitInt.__complement_impl(self.bits, self.value)
        return self.value

    def __oct__(self):
        return oct(self.value)

    def __hex__(self):
        return hex(self.value)

    #Not actually built-in, but it fits here
    def bin(self):
        return bin(self.value)

    def __str__(self):
        return str(int(self))