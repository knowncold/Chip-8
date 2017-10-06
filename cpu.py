import random
import struct
import font
import sys
import pygame


class CPU:

    def __init__(self):
        self.PC = 0x200
        self.memory = []
        self.vRegister = [0] * 16
        self.curr_inst = 0
        self.SP = 0xFA0
        self.regI = 0
        self.DELAY = 60
        self.SOUND = 60
        self.lastKEY = -1
        self.keyboard = [0] * 16
        self.keyChanged = False

        self.loadFont()

        pygame.init()
        size = 64, 32
        black = 0, 0, 0
        self.surface = pygame.display.set_mode(size)
        pygame.display.set_caption("Chip-8")
        self.surface.fill(black)
        self.pxArray = pygame.PixelArray(self.surface)

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

    def loadROM(self, path):
        f = open(path, 'rb')
        while True:
            t = f.read(1)
            if t == '':
                break
            a, = struct.unpack('c', t)
            self.memory.append(ord(a))
        self.memory += [0] * (0x1000 - len(self.memory))

    def INST_CALL(self):    # 2NNN
        self.SP -= 2
        self.memory[self.SP] = (self.PC & 0xFF00) >> 8
        self.memory[self.SP + 1] = self.PC & 0xFF
        self.PC = self.curr_inst & 0xFFF

    def INST_CLEAR(self):
        for i in range(0xF00, 0x1000):
            self.memory[i] = 0

    def INST_GOTO(self):    # 1NNN
        if self.PC == self.curr_inst - 0x1000:
            print "Loop HALT"
        self.PC = self.curr_inst - 0x1000 - 2

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
            self.setCARRY(1) if self.vRegister[x] + self.vRegister[y] > 0xFF else self.setCARRY(0)
            self.vRegister[x] = (self.vRegister[x] + self.vRegister[y]) & 0xFF
        elif inst_type == 5:
            self.setCARRY(0) if self.vRegister[x] - self.vRegister[y] < 0 else self.setCARRY(1)
            self.vRegister[x] -= self.vRegister[y]      # if & 0xFF
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
            print "INST_REG ERROR"
            exit(1)

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
            print "INST_COND ERROR"
            exit(1)

    def INST_DISP(self):
        x, y = self.getXY(self.curr_inst)
        y = self.vRegister[y]
        n = self.curr_inst & 0x0F
        self.setCARRY(0)
        for i in range(0, n):
            sprite_bit = 7
            sprite = self.memory[self.regI + i]
            j = self.vRegister[x]
            while j < (self.vRegister[x] + 8) and j < 64:
                des_address = 0xF00 + j / 8 + (y+i) * 8
                bit_before = (self.memory[des_address] >> (7 - j % 8)) & 0x01
                bit_after = (sprite >> sprite_bit) & 0x01
                if bit_before == 1 and bit_after == 0:
                    self.setCARRY(1)
                    self.memory[des_address] &= (0xFF - (0x01 << (7 - j % 8)))
                elif bit_before == 0 and bit_after == 1:
                    self.memory[des_address] |= (0x01 << (7 - j % 8))
                j += 1
                sprite_bit -= 1

    def INST_KEY(self):
        x = self.getX(self.curr_inst)
        if self.curr_inst & 0xFF == 0x9E:
            if self.keyboard[self.vRegister[x]] == 1:
                self.PC += 2
        elif self.curr_inst & 0xFF == 0xA1:
            if self.keyboard[self.vRegister[x]] == 0:
                self.PC += 2
        else:
            print "KEY ERROR"
            exit(1)

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
                self.PC -= 2    # trick to generate a loop
        elif right == 0x15:
            self.DELAY = self.vRegister[x]
        elif right == 0x18:
            self.SOUND = self.vRegister[x]
        elif right == 0x1E:
            temp = self.regI + self.vRegister[x]
            self.setCARRY(1) if temp > 0xFFFF else self.setCARRY(0)     # it seems not need carry
            self.regI = temp & 0xFFFF
        elif right == 0x29:
            self.regI = self.vRegister[x] * 5
        elif right == 0x33:
            self.memory[self.regI] = self.vRegister[x] / 100
            self.memory[self.regI + 1] = self.vRegister[x] % 100 / 10
            self.memory[self.regI + 2] = self.vRegister[x] % 10
        elif right == 0x55:
            for i in range(0, x):
                self.memory[self.regI + i] = self.vRegister[i]
            self.regI += (x + 1)
        elif right == 0x65:
            for i in range(0, x):
                self.vRegister[i] = self.memory[self.regI + i]
            self.regI += (x + 1)
        else:
            print "INST_F ERROR"
            exit(1)

    def INST_RETURN(self):
        self.PC = (self.memory[self.SP] << 8) + self.memory[self.SP]
        self.SP += 2

    def RUN(self):
        self.curr_inst = (self.memory[self.PC] << 8) + self.memory[self.PC + 1]
        print "PC %x" % self.PC,
        print "%x" % self.curr_inst
        self.execINST()
        self.PC += 2

    def execINST(self):
        inst_type = (self.curr_inst & 0xF000) >> 12
        if inst_type == 0:
            if self.curr_inst == 0x00E0:
                self.INST_CLEAR()
            elif self.curr_inst == 0x00EE:
                self.INST_RETURN()
            else:
                print "0xNNN ERROR", self.curr_inst
                exit(1)
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
            self.regI = self.curr_inst & 0xFFF
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


def videoRefresh(cpu):      # TODO reshape
    array = cpu.pxArray
    for i in range(32):
        for j in range(0, 8):
            v_ram = cpu.memory[0xF00 + i*8 + j]
            for k in range(0, 8):
                if (v_ram & 0x01) == 1:
                    array[j*8 + 7 - k][i] = (255, 255, 255)
                else:
                    array[j*8 + 7 - k][i] = (0, 0, 0)
                v_ram >>= 1


def main():
    processor = CPU()
    processor.loadROM('roms/Fishie.ch8')
    fps_clk = pygame.time.Clock()
    fps = 60

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            if event.type == pygame.KEYDOWN:
                processor.keyChanged = True

                if event.key == pygame.K_0:
                    processor.lastKEY = 0
                    processor.keyboard[0] = 1
                if event.key == pygame.K_1:
                    processor.lastKEY = 1
                    processor.keyboard[1] = 1
                if event.key == pygame.K_2:
                    processor.lastKEY = 2
                    processor.keyboard[2] = 1
                if event.key == pygame.K_3:
                    processor.lastKEY = 3
                    processor.keyboard[3] = 1
                if event.key == pygame.K_4:
                    processor.lastKEY = 4
                    processor.keyboard[4] = 1
                if event.key == pygame.K_5:
                    processor.lastKEY = 5
                    processor.keyboard[5] = 1
                if event.key == pygame.K_6:
                    processor.lastKEY = 6
                    processor.keyboard[6] = 1
                if event.key == pygame.K_7:
                    processor.lastKEY = 7
                    processor.keyboard[7] = 1
                if event.key == pygame.K_8:
                    processor.lastKEY = 8
                    processor.keyboard[8] = 1
                if event.key == pygame.K_9:
                    processor.lastKEY = 9
                    processor.keyboard[9] = 1
                if event.key == pygame.K_a:
                    processor.lastKEY = 0xA
                    processor.keyboard[0xA] = 1
                if event.key == pygame.K_b:
                    processor.lastKEY = 0xB
                    processor.keyboard[0xB] = 1
                if event.key == pygame.K_c:
                    processor.lastKEY = 0xC
                    processor.keyboard[0xC] = 1
                if event.key == pygame.K_d:
                    processor.lastKEY = 0xD
                    processor.keyboard[0xD] = 1
                if event.key == pygame.K_e:
                    processor.lastKEY = 0xE
                    processor.keyboard[0xE] = 1
                if event.key == pygame.K_f:
                    processor.lastKEY = 0xF
                    processor.keyboard[0xF] = 1

            if event.type == pygame.KEYUP:
                if event.key == pygame.K_0:
                    processor.lastKEY = 0
                    processor.keyboard[0] = 0
                if event.key == pygame.K_1:
                    processor.lastKEY = 1
                    processor.keyboard[1] = 0
                if event.key == pygame.K_2:
                    processor.lastKEY = 2
                    processor.keyboard[2] = 0
                if event.key == pygame.K_3:
                    processor.lastKEY = 3
                    processor.keyboard[3] = 0
                if event.key == pygame.K_4:
                    processor.lastKEY = 4
                    processor.keyboard[4] = 0
                if event.key == pygame.K_5:
                    processor.lastKEY = 5
                    processor.keyboard[5] = 0
                if event.key == pygame.K_6:
                    processor.lastKEY = 6
                    processor.keyboard[6] = 0
                if event.key == pygame.K_7:
                    processor.lastKEY = 7
                    processor.keyboard[7] = 0
                if event.key == pygame.K_8:
                    processor.lastKEY = 8
                    processor.keyboard[8] = 0
                if event.key == pygame.K_9:
                    processor.lastKEY = 9
                    processor.keyboard[9] = 0
                if event.key == pygame.K_a:
                    processor.lastKEY = 0xA
                    processor.keyboard[0xA] = 0
                if event.key == pygame.K_b:
                    processor.lastKEY = 0xB
                    processor.keyboard[0xB] = 0
                if event.key == pygame.K_c:
                    processor.lastKEY = 0xC
                    processor.keyboard[0xC] = 0
                if event.key == pygame.K_d:
                    processor.lastKEY = 0xD
                    processor.keyboard[0xD] = 0
                if event.key == pygame.K_e:
                    processor.lastKEY = 0xE
                    processor.keyboard[0xE] = 0
                if event.key == pygame.K_f:
                    processor.lastKEY = 0xF
                    processor.keyboard[0xF] = 0

        videoRefresh(processor)
        pygame.display.update()
        processor.RUN()
        fps_clk.tick(fps)
        processor.tick()


if __name__ == "__main__":
    main()
