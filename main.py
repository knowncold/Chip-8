import cpu
import pygame
import sys
import view


processor = cpu.CPU()
video = view.View()
processor.loadROM('roms/MAZE')
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

    video.videoRefresh(processor)
    pygame.display.update()
    processor.RUN()
    fps_clk.tick(fps)
    processor.tick()
