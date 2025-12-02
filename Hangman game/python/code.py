#                        Python Hangman game
import random

# List of predefined words
words = ["python", "hangman", "program", "developer", "keyboard"]

# Randomly select a word from the list
secret_word = random.choice(words)

# Create a list of underscores representing unguessed letters
guessed_word = ["_"] * len(secret_word)

# Keep track of incorrect guesses and letters guessed
incorrect_guesses = 0
max_incorrect = 6
guessed_letters = []

print("Welcome to Hangman!")
print("Try to guess the word, one letter at a time.")
print("You have 6 incorrect guesses allowed.\n")

# Main game loop
while incorrect_guesses < max_incorrect and "_" in guessed_word:
    print("Word:", " ".join(guessed_word))
    print("Guessed letters:", " ".join(guessed_letters))
    print(f"Incorrect guesses left: {max_incorrect - incorrect_guesses}")
    
    guess = input("Guess a letter: ").lower()
    
    # Validate input
    if len(guess) != 1 or not guess.isalpha():
        print("Please enter a single letter.\n")
        continue
    if guess in guessed_letters:
        print("You already guessed that letter!\n")
        continue
    
    guessed_letters.append(guess)
    
    # Check if guess is in the word
    if guess in secret_word:
        print(f"Good job! '{guess}' is in the word.\n")
        # Reveal all occurrences of the guessed letter
        for i in range(len(secret_word)):
            if secret_word[i] == guess:
                guessed_word[i] = guess
    else:
        print(f"Sorry, '{guess}' is not in the word.\n")
        incorrect_guesses += 1

# Game over — check win or lose
if "_" not in guessed_word:
    print("🎉 Congratulations! You guessed the word:", secret_word)
else:
    print("😢 Out of guesses! The word was:", secret_word)
    