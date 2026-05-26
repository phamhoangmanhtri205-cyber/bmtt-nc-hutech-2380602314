class PlayfairCipher:
    def __init__(self):
        pass

    def create_matrix(self, key: str) -> list:
        # Preprocess key: uppercase, replace J with I, keep only alphabetic characters
        key = key.upper().replace('J', 'I')
        seen = []
        for char in key:
            if char.isalpha() and char not in seen:
                seen.append(char)
        
        # Fill the rest of the alphabet (excluding J)
        alphabet = "ABCDEFGHIKLMNOPQRSTUVWXYZ"
        for char in alphabet:
            if char not in seen:
                seen.append(char)
        
        # Reshape to 5x5 matrix
        matrix = [seen[i:i+5] for i in range(0, 25, 5)]
        return matrix

    def _find_position(self, matrix: list, char: str) -> tuple:
        for r in range(5):
            for c in range(5):
                if matrix[r][c] == char:
                    return r, c
        return None

    def _prepare_text(self, text: str) -> str:
        text = text.upper().replace('J', 'I')
        cleaned = "".join([c for c in text if c.isalpha()])
        prepared = []
        i = 0
        while i < len(cleaned):
            char1 = cleaned[i]
            if i + 1 < len(cleaned):
                char2 = cleaned[i+1]
                if char1 == char2:
                    prepared.append(char1)
                    prepared.append('X')
                    i += 1
                else:
                    prepared.append(char1)
                    prepared.append(char2)
                    i += 2
            else:
                prepared.append(char1)
                prepared.append('X')
                i += 1
        return "".join(prepared)

    def encrypt_text(self, text: str, key: str) -> str:
        matrix = self.create_matrix(key)
        prepared = self._prepare_text(text)
        ciphertext = []
        
        for i in range(0, len(prepared), 2):
            char1, char2 = prepared[i], prepared[i+1]
            pos1 = self._find_position(matrix, char1)
            pos2 = self._find_position(matrix, char2)
            
            if not pos1 or not pos2:
                # Fallback if character not in matrix (should not happen for cleaned A-Z)
                ciphertext.append(char1)
                ciphertext.append(char2)
                continue
                
            r1, c1 = pos1
            r2, c2 = pos2
            
            if r1 == r2:
                # Same row: shift right
                ciphertext.append(matrix[r1][(c1 + 1) % 5])
                ciphertext.append(matrix[r2][(c2 + 1) % 5])
            elif c1 == c2:
                # Same column: shift down
                ciphertext.append(matrix[(r1 + 1) % 5][c1])
                ciphertext.append(matrix[(r2 + 1) % 5][c2])
            else:
                # Rectangle: swap columns
                ciphertext.append(matrix[r1][c2])
                ciphertext.append(matrix[r2][c1])
                
        return "".join(ciphertext)

    def decrypt_text(self, text: str, key: str) -> str:
        matrix = self.create_matrix(key)
        text = text.upper().replace('J', 'I')
        cleaned = "".join([c for c in text if c.isalpha()])
        decrypted = []
        
        for i in range(0, len(cleaned), 2):
            if i + 1 >= len(cleaned):
                # Fallback if odd length (should be even for valid playfair ciphertext)
                decrypted.append(cleaned[i])
                break
                
            char1, char2 = cleaned[i], cleaned[i+1]
            pos1 = self._find_position(matrix, char1)
            pos2 = self._find_position(matrix, char2)
            
            if not pos1 or not pos2:
                decrypted.append(char1)
                decrypted.append(char2)
                continue
                
            r1, c1 = pos1
            r2, c2 = pos2
            
            if r1 == r2:
                # Same row: shift left
                decrypted.append(matrix[r1][(c1 - 1) % 5])
                decrypted.append(matrix[r2][(c2 - 1) % 5])
            elif c1 == c2:
                # Same column: shift up
                decrypted.append(matrix[(r1 - 1) % 5][c1])
                decrypted.append(matrix[(r2 - 1) % 5][c2])
            else:
                # Rectangle: swap columns
                decrypted.append(matrix[r1][c2])
                decrypted.append(matrix[r2][c1])
                
        return "".join(decrypted)
