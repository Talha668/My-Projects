questions = ("What Is The Name Of The Brightest Star In The Night sky?:",
             "What Is The Name of The Longest River in the World?:",
             "What Is The Power House OF A Cell?:",
             "How Many Planets In Our Solar System?:",
             "Who Invented Plane")


options = (("A. Sirius", "B. Vega", "C. Rigel", "D. Pollux"),
           ("A. Indus", "B. Amazon", "C. Nile", "D. Brahmaputra"),
           ("A. Cell wall", "B. Mitochondria", "C. Nucleus", "D. Cytoplasm"),
           ("A. 6", "B. 5", "C. 9", "D. 8"),
           ("A. Graham Bell", "B. Wright Brothers", "C. Nicola Tesla", "D. Thomas Edison"))


answers = ("A", "C", "B", "D", "B")
guesses = []
score = 0
question_num = 0

for question in questions:
    print("---------------")
    print(question)
    for option in options[question_num]:
        print(option)

    guess = input("Enter (A, B, C, D,):").upper()
    guesses.append(guess)
    if guess == answers[question_num]:
        score += 1
        print("CORRECT")
    else:
        print("INCORRECT")
        print(f"{answers[question_num]} is the correct answer")
    question_num += 1


print("-------------")
print('   RESULTS   ')
print("-------------")

print("answers: ", end="")
for answer in answers:
    print(answer, end="")
print()


print("guesses: ", end="")
for guess in guesses:
    print(guess, end="")
print()

score = int(score / len(questions) * 100)
print(f"Your Score Is: {score}%")
