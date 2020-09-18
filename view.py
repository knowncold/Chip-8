import pygame


class View:

    def __init__(self, scale):
        pygame.init()
        self.scale = scale
        size = 64*scale, 32*scale
        black = 0, 0, 0
        self.surface = pygame.display.set_mode(size)
        pygame.display.set_caption("Chip-8")
        self.surface.fill(black)
        self.pxArray = pygame.PixelArray(self.surface)

    def videoRefresh(self, cpu):  # TODO reshape
        array = self.pxArray
        for i in range(32):
            for j in range(0, 8):
                v_ram = cpu.memory[0xF00 + i * 8 + j]
                for k in range(0, 8):
                    if (v_ram & 0x01) == 1:
                        array[j * 8 + 7 - k][i] = (255, 255, 255)
                    else:
                        array[j * 8 + 7 - k][i] = (0, 0, 0)
                    v_ram >>= 1
        pygame.display.update()
