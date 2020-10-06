import random
import struct
import font


class CPU:

    def __init__(self):
        self.PC = 0x200
        self.memory = []
        self.vRegister = [0] * 16
        self.curr_inst = 0
        self.SP = 0xEFF
        self.regI = 0
        self.DELAY = 60
        self.SOUND = 60
        self.lastKEY = -1
        self.keyboard = [0] * 16
        self.keyChanged = False
        self.loadFont()

    def loadFont(self):
        for i in font.Font:
            self.memory.append(int(i, 2))
        self.memory += [0] * (0x200 - len(self.memory))

    def tick(self):
        if self.DELAY > 0:
            self.DELAY -= 1
        else:
            self.DELAY = 60

        if self.SOUND > 0:
            self.SOUND -= 1
        else:
            self.SOUND = 60

    def addTimer(self, value):
        self.DELAY -= value
        if self.DELAY < 0:
            self.DELAY = 0
        self.SOUND -= value
        if self.SOUND < 0:
            self.SOUND = 0

    def loadROM(self, path):
        f = open(path, 'rb')
        while True:
            t = f.read(1)
            if t == b'':
                break
            a, = struct.unpack('c', t)
            self.memory.append(ord(a))
        self.memory += [0] * (0x1000 - len(self.memory))

    def INST_CLEAR(self):  # 00E0
        for i in range(0xF00, 0x1000):
            self.memory[i] = 0
        self.PC += 2

    def INST_RETURN(self):  # 00EE
        self.SP += 2
        if self.SP > 0xFA0:
            print("Wrong SP address")
            exit(1)
        self.PC = (self.memory[self.SP - 1] << 8) + self.memory[self.SP]
        # print("Return to: ", self.PC)

    def INST_GOTO(self):  # 1NNN
        if self.PC == self.curr_inst - 0x1000:
            print("Loop HALT")
            exit(1)
        self.PC = self.curr_inst - 0x1000

    def INST_CALL(self):  # 2NNN
        # print("Call from: ", self.PC)
        self.PC += 2
        self.memory[self.SP - 1] = (self.PC & 0xFF00) >> 8
        self.memory[self.SP] = self.PC & 0xFF
        self.SP -= 2
        self.PC = self.curr_inst & 0xFFF

    def INST_REG(self):  # 8XYZ
        inst_type = self.curr_inst & 0xF
        x, y = self.getXY(self.curr_inst)
        if inst_type == 0:
            self.vRegister[x] = self.vRegister[y]
        elif inst_type == 1:
            self.vRegister[x] = self.vRegister[x] | self.vRegister[y]
        elif inst_type == 2:
            self.vRegister[x] = self.vRegister[x] & self.vRegister[y]
        elif inst_type == 3:
            self.vRegister[x] = self.vRegister[x] ^ self.vRegister[y]
        elif inst_type == 4:
            self.setCARRY(1) if self.vRegister[x] + self.vRegister[y] > 0xFF else self.setCARRY(0)
            self.vRegister[x] = (self.vRegister[x] + self.vRegister[y]) & 0xFF
        elif inst_type == 5:
            self.setCARRY(0) if self.vRegister[x] - self.vRegister[y] < 0 else self.setCARRY(1)
            self.vRegister[x] -= self.vRegister[y]  # if & 0xFF
        elif inst_type == 6:
            self.setCARRY(self.vRegister[x] & 1)
            self.vRegister[x] >>= 1
        elif inst_type == 7:
            self.setCARRY(0) if self.vRegister[y] - self.vRegister[x] < 0 else self.setCARRY(1)
            self.vRegister[x] = self.vRegister[y] - self.vRegister[x]
        elif inst_type == 0xE:
            self.setCARRY((self.vRegister[x] & 0x80) >> 7)
            self.vRegister[x] <<= 1
        else:
            print("INST_REG ERROR")
            exit(1)
        self.PC += 2

    def INST_COND(self):
        inst_type = self.curr_inst >> 12
        x, y = self.getXY(self.curr_inst)
        if inst_type == 3:
            if self.vRegister[x] == self.curr_inst & 0xFF:
                self.PC += 2
        elif inst_type == 4:
            if self.vRegister[x] != self.curr_inst & 0xFF:
                self.PC += 2
        elif inst_type == 5:
            if self.vRegister[x] == self.vRegister[y]:
                self.PC += 2
        elif inst_type == 9:
            if self.vRegister[x] != self.vRegister[y]:
                self.PC += 2
        else:
            print("INST_COND ERROR")
            exit(1)
        self.PC += 2

    def INST_DISP(self):  # DXYN
        x, y = self.getXY(self.curr_inst)
        y = self.vRegister[y]
        height = self.curr_inst & 0x0F
        self.setCARRY(0)
        for i in range(0, height):
            sprite_bit = 7
            sprite = self.memory[self.regI + i]
            j = self.vRegister[x]
            while j < (self.vRegister[x] + 8) and j < 64:
                des_address = int(0xF00 + j // 8 + (y + i) * 8)  # vram address
                if des_address > 0xFFF:
                    break
                bit_before = (self.memory[des_address] >> (7 - j % 8)) & 0x01
                bit_after = (sprite >> sprite_bit) & 0x01
                if (bit_before == 1 and bit_after == 1) or (bit_after == 0 and bit_before == 0):
                    self.setCARRY(1)
                    self.memory[des_address] &= (0xFF - (0x01 << (7 - j % 8)))
                elif bit_before == 0 and bit_after == 1:
                    self.memory[des_address] |= (0x01 << (7 - j % 8))
                j += 1
                sprite_bit -= 1
        self.PC += 2

    def INST_KEY(self):
        x = self.getX(self.curr_inst)
        if self.curr_inst & 0xFF == 0x9E:
            if self.keyboard[self.vRegister[x]] == 1:
                self.PC += 2
        elif self.curr_inst & 0xFF == 0xA1:
            if self.keyboard[self.vRegister[x]] == 0:
                self.PC += 2
        else:
            print("KEY ERROR")
            exit(1)
        self.PC += 2

    def INST_F(self):
        x = self.getX(self.curr_inst)
        right = self.curr_inst & 0xFF
        if right == 0x07:
            self.vRegister[x] = self.DELAY
        elif right == 0x0A:
            if self.keyChanged:
                self.vRegister[x] = self.lastKEY
            else:
                self.keyChanged = False
                self.PC -= 2  # trick to generate a loop
        elif right == 0x15:
            self.DELAY = self.vRegister[x]
        elif right == 0x18:
            self.SOUND = self.vRegister[x]
        elif right == 0x1E:
            temp = self.regI + self.vRegister[x]
            # self.setCARRY(1) if temp > 0xFFFF else self.setCARRY(0)  # it seems not need carry
            self.regI = temp & 0xFFFF
        elif right == 0x29:
            self.regI = self.vRegister[x] * 5
        elif right == 0x33:
            self.memory[self.regI] = self.vRegister[x] // 100
            self.memory[self.regI + 1] = self.vRegister[x] % 100 // 10
            self.memory[self.regI + 2] = self.vRegister[x] % 10
        elif right == 0x55:
            for i in range(0, x + 1):
                self.memory[self.regI + i] = self.vRegister[i]
            self.regI += (x + 1)
        elif right == 0x65:
            for i in range(0, x + 1):
                self.vRegister[i] = self.memory[self.regI + i]
            self.regI += (x + 1)
        else:
            print("INST_F ERROR")
            print(right)
            exit(1)
        self.PC += 2

    def RUN(self, cycles=1, flag=True):
        for i in range(0, cycles):
            self.curr_inst = (self.memory[self.PC] << 8) + self.memory[self.PC + 1]
            # if flag:
            # print("PC %x %x %x" % (self.PC, self.curr_inst, self.vRegister[0]))
            # print("%x" % self.curr_inst)
            self.execINST()
            if self.PC < 0x200:
                print("wrong pc address")
                exit(1)

    def execINST(self):
        inst_type = (self.curr_inst & 0xF000) >> 12
        if inst_type == 0:
            if self.curr_inst == 0x00E0:
                self.INST_CLEAR()
            elif self.curr_inst == 0x00EE:
                self.INST_RETURN()
            else:
                print("0xNNN ERROR", self.curr_inst)
                exit(1)
        elif inst_type == 1:
            self.INST_GOTO()
        elif inst_type == 2:
            self.INST_CALL()
        elif inst_type in [3, 4, 5, 9]:
            self.INST_COND()
        elif inst_type == 6:
            self.vRegister[(self.curr_inst & 0xF00) >> 8] = self.curr_inst & 0xFF
            self.PC += 2
        elif inst_type == 7:
            tmp = self.vRegister[(self.curr_inst & 0xF00) >> 8] + self.curr_inst & 0xFF
            if tmp > 255:
                tmp -= 256
            self.vRegister[(self.curr_inst & 0xF00) >> 8] = tmp
            self.PC += 2
        elif inst_type == 8:
            self.INST_REG()
        elif inst_type == 0xA:
            self.regI = self.curr_inst & 0xFFF
            self.PC += 2
        elif inst_type == 0xB:
            self.PC = self.vRegister[0] + self.curr_inst & 0xFFF
        elif inst_type == 0xC:
            x = self.getX(self.curr_inst)
            self.vRegister[x] = random.randint(0, 0xFF) & (self.curr_inst & 0xFF)
            self.PC += 2
        elif inst_type == 0xD:
            self.INST_DISP()
        elif inst_type == 0xE:
            self.INST_KEY()
        elif inst_type == 0xF:
            self.INST_F()
        else:
            print("INST ERROR", self.curr_inst)
            exit(1)

    def setCARRY(self, value):
        self.vRegister[0xF] = value

    @staticmethod
    def getXY(value):
        return (value & 0x0F00) >> 8, (value & 0x00F0) >> 4

    @staticmethod
    def getX(value):
        return (value & 0x0F00) >> 8
