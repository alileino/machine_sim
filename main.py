#encoding: utf-8
from MachineSim import *
user_input = """
100 LOAD 98
101 ADD 99
102 STORE 97
"""
p = MachineProgram(user_input)
sim = MachineSim()
p.setStartAddress(100)
for rValue in [5,4,1,0]:
    sim.setMemory(98, rValue)
    sim.setMemory(99, rValue*2)
    print "Ennen suoritusta:", sim.printState(memory=[98, 99])
    sim.loadProgram(p)
    sim.run()
    print "Jälkeen: ", sim.printState(memory=[97])
# Muistipaikaassa 98 on luku >= 0, jota merkitään n:llä. Laske muistipaikkaan 99 luvun n kertoma, eli
# toteuta konekielellä pseudokoodi:
# kertoma := 1
# WHILE n > 0:
#   kertoma := kertoma * n
#   n := n - 1
