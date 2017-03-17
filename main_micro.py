#encoding: utf-8
from mikrosim import *
# User program starts here
userInput = """

debug
1 9 10 11 12 13 21 17        Tassa on kommentti
1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22

4: 1 9


"""

mp = MicroProgram(userInput)

cc = mp.setCC
sim = MikroSim(mp)
# data = random.randint(-2**10,2**10)

sim.resetRegisters()
sim.setA(2**16-1)


# print "<ignore>Ennen suoritusta:", sim.printRegisters(a=True), "</ignore>"
sim.execute()
# sim.aluTest()
print "Jälkeen:          ", sim.printRegisters(mdr=True)
