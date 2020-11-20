import entity, random, math


class Point(entity.Entity):
    def __init__(self, cp_of_maze, cp_of_pacman, index):
        self.MAZE = cp_of_maze
        self.PACMAN = cp_of_pacman

        xt, yt = self.MAZE.indexToTile(index) # returnerer xTile og yTile
        position = self.MAZE.tileToPosition(xt, yt)

        tileType = self.MAZE.grid[index]

        self.doNotShow = False
        print(2 >= tileType)
        if (2 >= tileType <= 3): self.doNotShow = True # Hvis der er en væg, så oprettes der ikke et point
        
        point = entity.Sprite('./assets/points.png', grid={'rows': 1, 'columns': 3}, beginFrame=0, endFrame=0, animationSpeed=5, animationBounce=True )
        cheese = entity.Sprite('./assets/points.png', correspondingState='cheese', grid={'rows': 1, 'columns': 3}, beginFrame=1, endFrame=1, animationSpeed=5, animationBounce=True )
        none = entity.Sprite('./assets/points.png', correspondingState='none', grid={'rows': 1, 'columns': 3}, beginFrame=2, endFrame=2, animationSpeed=5, animationBounce=True )
        spritesArr = [ point, cheese, none ]

        super().__init__(position['x']-3, position['y']-4, sprites = spritesArr, state='main')

    def update(self, dt):
        # Kollision
        xTile, yTile = self.MAZE.getXYTileFromPos(self.x+16, self.y+24)
        px, py = self.PACMAN.getTilePosition()
        if px >= xTile >= px:
            if py >= yTile >= py:
                self.setSprite('none')

        # super.update(dt)