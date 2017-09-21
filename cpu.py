import random
import struct

import pygame
import threading


class CPU:

    def __init__(self):
        self.PC = 0x200
        self.memory = [0] * 0x200
        self.vRegister = [0] * 16
        self.curr_inst = 0
        self.SP = 0x0EFF
        self.I = 0
        self.DELAY = 60
        self.SOUND = 60
        self.keyWaiting = True
        self.lastKEY = -1

        pygame.init()
        size = height, width = 64, 32
        black = 0, 0, 0
        self.surface = pygame.display.set_mode(size)
        pygame.display.set_caption("Chip-8")
        self.surface.fill(black)
        self.pxArray = pygame.PixelArray(self.surface)

    def tick(self):
        if self.DELAY > 0:
            self.DELAY -= 1
        else:
            self.DELAY = 60

        if self.SOUND > 0:
            self.SOUND -= 1
        else:
            self.SOUND = 60

        timer = threading.Timer(1.0/60, self.tick)
        timer.start()

    def loadROM(self, path):
        f = open(path, 'rb')
        while True:
            left = f.read(1)
            if left == '':
                break
            right = f.read(1)
            a, = struct.unpack('c', left)
            b, = struct.unpack('c', right)
            self.memory.append((ord(a) << 8) + ord(b))
        self.memory += [0] * (0x1000 - len(self.memory))
        # print len(self.memory)
        # a = map(lambda x: "%x" % x, self.memory)
        # print a

    def INST_CALL(self):    # 2NNN
        self.memory[self.SP] = self.PC
        self.PC = self.curr_inst & 0xFFF
        self.SP -= 1

    def INST_CLEAR(self):
        for i in range(0xF00, 0x1000):  # TODO specify the boundary
            self.memory[i] = 0  # TODO 0 or 1

    def INST_GOTO(self):    # 1NNN
        self.PC = self.curr_inst - 0x100

    def INST_REG(self):     # 8XYZ
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
            self.setCARRY(1) if self.vRegister[x] + self.vRegister[y] > 0xFF else self.setCARRY(0)  # TODO
            self.vRegister[x] = (self.vRegister[x] + self.vRegister[y]) & 0xFF
        elif inst_type == 5:
            self.setCARRY(0) if self.vRegister[x] - self.vRegister[y] < 0 else self.setCARRY(1)     # TODO
            self.vRegister[x] = (self.vRegister[x] - self.vRegister[y]) & 0xFF
        elif inst_type == 6:
            self.setCARRY(self.vRegister[x] & 1)
            self.vRegister[x] >>= 1
        elif inst_type == 7:
            self.setCARRY(0) if self.vRegister[y] - self.vRegister[x] < 0 else self.setCARRY(1)
            self.vRegister[x] = self.vRegister[y] - self.vRegister[x]
        elif inst_type == 0xE:
            self.setCARRY(self.vRegister[x] & 0x80)
            self.vRegister[x] <<= 1
        else:
            print "INST_REG ERROR"
            exit(1)

    def INST_COND(self):
        inst_type = self.curr_inst >> 12
        x, y = self.getXY(self.curr_inst)
        if inst_type == 3:
            if self.vRegister[x] == self.curr_inst & 0xFF:
                self.PC += 1
        elif inst_type == 4:
            if self.vRegister[x] != self.curr_inst & 0xFF:
                self.PC += 1
        elif inst_type == 5:
            if self.vRegister[x] == self.vRegister[y]:
                self.PC += 1
        elif inst_type == 9:
            if self.vRegister[x] != self.vRegister[y]:
                self.PC += 1
        else:
            print "INST_COND ERROR"
            exit(1)

    def INST_DISP(self):    # TODO
        white = 255, 255, 255
        black = 0, 0, 0
        print "DISP"
        x, y = self.getXY(self.curr_inst)
        n = self.curr_inst & 0x01
        for i in range(0, n):
            row = self.memory[self.I + i]
            for j in range(0, 8):
                self.pxArray[self.vRegister[x], self.vRegister[y]] = white if (row & (1 << i)) >> i > 0 else black
        pygame.display.update()

    def INST_KEY(self):
        x = self.getX(self.curr_inst)
        if self.curr_inst & 0xFF == 0x9E:
            if self.lastKEY == self.vRegister[x]:
                self.PC += 1
        elif self.curr_inst & 0xFF == 0xA1:
            if self.lastKEY != self.vRegister[x]:
                self.PC += 1
        print "KEY ERROR"
        exit(1)

    def INST_F(self):
        x = self.getX(self.curr_inst)
        right = self.curr_inst & 0xFF
        if right == 0x07:
            self.vRegister[x] = self.DELAY
        elif right == 0x0A:
            if self.keyWaiting:
                self.PC -= 1
            else:
                self.vRegister[x] = self.lastKEY
        elif right == 0x15:
            self.DELAY = self.vRegister[x]
        elif right == 0x18:
            self.SOUND = self.vRegister[x]
        elif right == 0x1E:
            temp = self.I + self.vRegister[x]
            self.setCARRY(1) if temp > 0xFFFF else self.setCARRY(0)
            self.I = temp & 0xFFFF
        elif right == 0x29:   # TODO
            print "0x29"
            exit(1)
        elif right == 0x33:
            self.memory[self.I] = self.vRegister[x] / 100
            self.memory[self.I+1] = self.vRegister[x] % 100 / 10
            self.memory[self.I+2] = self.vRegister[x] % 10
        elif right == 0x55:
            for i in range(0, 0x0F):
                self.memory[self.I + i] = self.vRegister[i]
        elif right == 0x65:
            for i in range(0, 0x0F):
                self.vRegister[i] = self.memory[self.I + i]
        else:
            print "INST_F ERROR"
            exit(1)

    def INST_RETURN(self):
        self.SP += 1
        self.PC = self.memory[self.SP]

    def RUN(self):
        print "%x" % self.curr_inst
        print "PC %x" % self.PC
        self.curr_inst = self.memory[self.PC]
        self.PC += 1
        self.execINST()

    def execINST(self):
        inst_type = (self.curr_inst & 0xF000) >> 12
        if inst_type == 0:
            if self.curr_inst == 0x00E0:
                self.INST_CLEAR()
            elif self.curr_inst == 0x00EE:
                self.INST_RETURN()
            else:
                print "0xNNN ERROR", self.curr_inst
                # exit(1)
        elif inst_type == 1:
            self.INST_GOTO()
        elif inst_type == 2:
            self.INST_CALL()
        elif inst_type in [3, 4, 5, 9]:
            self.INST_COND()
        elif inst_type == 6:
            self.vRegister[(self.curr_inst & 0xF00) >> 8] = self.curr_inst & 0xFF
        elif inst_type == 7:
            self.vRegister[(self.curr_inst & 0xF00) >> 8] += self.curr_inst & 0xFF
        elif inst_type == 8:
            self.INST_REG()
        elif inst_type == 0xA:
            self.I = self.curr_inst & 0xFFF
        elif inst_type == 0xB:
            self.PC = self.vRegister[0] + self.curr_inst & 0xFFF
        elif inst_type == 0xC:
            x = self.getX(self.curr_inst)
            self.vRegister[x] = random.randint(0, 255) & (self.curr_inst & 0xFF)
        elif inst_type == 0xD:
            self.INST_DISP()
        elif inst_type == 0xE:
            self.INST_KEY()
        elif inst_type == 0xF:
            self.INST_F()

    def setCARRY(self, value):
        self.vRegister[0xF] = value

    @staticmethod
    def getXY(value):
        return (value & 0x0F00) >> 8, (value & 0x00F0) >> 4

    @staticmethod
    def getX(value):
        return (value & 0x0F00) >> 8

def main():
    processor = CPU()
    # processor.loadROM('roms/PONG')
    processor.loadROM('roms/Pong.ch8')
    fps_clk = pygame.time.Clock()
    fps = 60

    timer = threading.Timer(0, processor.tick)
    timer.start()
    # i = 0x200
    # while i < 0x2ea:
    #     print "%x" % processor.memory[i]
    #     i += 0x1

    while True:
        processor.RUN()
        fps_clk.tick(fps)


if __name__ == "__main__":
    main()
