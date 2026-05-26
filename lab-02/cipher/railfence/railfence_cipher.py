class RailFenceCipher:
    def __init__(self):
        pass

    def encrypt_text(self, text: str, key: int) -> str:
        # Create a matrix to cipher key x len(text)
        # fill the rail matrix to distinguish filled spaces from blank ones
        rail = [['\n' for i in range(len(text))]
                      for j in range(key)]
        
        # to find the direction
        dir_down = False
        row, col = 0, 0
        
        for i in range(len(text)):
            # check the direction of flow
            # reverse the direction if we've just filled the spaces or extremely top/bottom rails
            if (row == 0) or (row == key - 1):
                dir_down = not dir_down
            
            # fill the alphabet
            rail[row][col] = text[i]
            col += 1
            
            # find the next row using direction flag
            if dir_down:
                row += 1
            else:
                row -= 1
        
        # now we can construct the fill character by character
        result = []
        for i in range(key):
            for j in range(len(text)):
                if rail[i][j] != '\n':
                    result.append(rail[i][j])
        return "".join(result)

    def decrypt_text(self, text: str, key: int) -> str:
        # create the matrix to cipher key x len(text)
        # fill the rail matrix to distinguish filled spaces from blank ones
        rail = [['\n' for i in range(len(text))]
                      for j in range(key)]
        
        # to find the direction
        dir_down = None
        row, col = 0, 0
        
        # mark the places with '*'
        for i in range(len(text)):
            if row == 0:
                dir_down = True
            if row == key - 1:
                dir_down = False
            
            # place the marker
            rail[row][col] = '*'
            col += 1
            
            # find the next row using direction flag
            if dir_down:
                row += 1
            else:
                row -= 1
        
        # now we can construct the fill character by character
        index = 0
        for i in range(key):
            for j in range(len(text)):
                if (rail[i][j] == '*') and (index < len(text)):
                    rail[i][j] = text[index]
                    index += 1
        
        # now read the matrix in zig-zag manner to construct the original text
        result = []
        row, col = 0, 0
        for i in range(len(text)):
            # check the direction of flow
            if row == 0:
                dir_down = True
            if row == key - 1:
                dir_down = False
            
            # place the marker
            if rail[row][col] != '*':
                result.append(rail[row][col])
                col += 1
            
            # find the next row using direction flag
            if dir_down:
                row += 1
            else:
                row -= 1
        return "".join(result)
