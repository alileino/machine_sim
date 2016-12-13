import re
exerciseFile = "main.py"
setVilleSeedStr = """
# This is a very ugly way to set rnd_seed in ViLLE-environment
# Otherwise, just use the default seed
try:
    random.seed(rnd_seed)
except NameError:
    pass
"""

nbitnum = open("NBitInt.py").read()
simulator = open("MachineSim.py").read()
exercise = open(exerciseFile).read()
importre = re.compile(r"(?P<line>^(import|from)\s+(MachineSim|NBitNum).*$)", re.MULTILINE)
randomre = re.compile(r"(^(import|from)\s+(random).*$)", re.MULTILINE)

exercise = randomre.sub(r"\1%s" % setVilleSeedStr, exercise)

# print exercise
simulator = importre.sub("", simulator)
exercise = importre.sub("", exercise)
newFile = nbitnum + simulator + exercise
with open("deployed.py", 'w') as f:
    f.write(newFile)


