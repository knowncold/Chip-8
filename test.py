import cpu

p = cpu.CPU()

p.loadROM('roms/Pong.ch8')

p.regI = 0
p.curr_inst = 0xD12e
p.vRegister[1] = 62
p.vRegister[2] = 2
for i in range(0, 0xe):
    p.memory[i] = 192
p.execINST()

for i in range(0,32):
    for j in range(0, 8):
        print bin(p.memory[0xF00 + 8*i + j])[2:],
    print