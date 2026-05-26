import math

class TranspositionCipher:
    def __init__(self):
        pass

    def encrypt_text(self, text: str, key: int) -> str:
        # Create a list of strings for each column
        ciphertext = [''] * key
        
        # Loop through each column in the grid
        for col in range(key):
            pointer = col
            while pointer < len(text):
                ciphertext[col] += text[pointer]
                pointer += key
                
        return ''.join(ciphertext)

    def decrypt_text(self, text: str, key: int) -> str:
        # Calculate grid dimensions
        num_cols = key
        num_rows = math.ceil(len(text) / num_cols)
        num_shaded_boxes = (num_cols * num_rows) - len(text)
        
        # Prepare the grid structure
        plaintext = [''] * num_rows
        col = 0
        row = 0
        
        for symbol in text:
            plaintext[row] += symbol
            row += 1
            
            # Check if we need to move to the next column
            if (row == num_rows) or (row == num_rows - 1 and col >= num_cols - num_shaded_boxes):
                row = 0
                col += 1
                
        return ''.join(plaintext)
