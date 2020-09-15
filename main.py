import cpu
import pygame
import sys
import time

processor = cpu.CPU()
processor.loadROM('roms/PONG2')

scale = 10
pygame.init()
size = 64 * scale, 32 * scale
black = 0, 0, 0
surface = pygame.display.set_mode(size)
pygame.display.set_caption("Chip-8")
surface.fill(black)
pxArray = pygame.PixelArray(surface)


# class Aa(threading.Timer):
#     def run(self):
#         while not self.finished.is_set():
#             self.finished.wait(self.interval)
#             self.function(*self.args, **self.kwargs)
#
#         self.finished.set()

def videoRefresh(pxArray, cpu, scale):
    array = pxArray
    for i in range(32):
        for j in range(8):
            v_ram = cpu.memory[0xF00 + i * 8 + j]
            for k in range(0, 8):
                x = j * 8 + 7 - k
                y = i
                if (v_ram & 0x01) == 1:
                    array[(scale * x):(scale * (x + 1)), (scale * y):(scale * (y + 1))] = (255, 255, 255)
                else:
                    array[scale * x:scale * (x + 1), scale * y: scale * (y + 1)] = (0, 0, 0)
                v_ram >>= 1


tick = time.time()

# test()
#
# processor.RUN(200)
# print(processor.PC)
# exit(0)
# processor.RUN(186, False)
count = 0

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

    processor.RUN()
    videoRefresh(pxArray, processor, scale)
    pygame.display.update()
    # count += 1
    # if count % 2 == 0:
    # processor.addTimer(1)
    past = time.time() - tick
    add_timer = past // (1.0 / 60)
    if add_timer > 0:
        processor.addTimer(int(add_timer))
        tick = time.time()
