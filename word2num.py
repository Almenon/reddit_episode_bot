singleDigits = [
    "zero", "one", "two", "three", "four", "five", "six", "seven", "eight",
    "nine", "ten", "eleven", "twelve", "thirteen", "fourteen", "fifteen",
    "sixteen", "seventeen", "eighteen", "nineteen",
]

tens = ["", "", "twenty", "thirty", "forty", "fifty", "sixty", "seventy", "eighty", "ninety"]

numwords = {word: idx for idx, word in enumerate(singleDigits)}
numwords.update({word: idx * 10 for idx, word in enumerate(tens)})


def word2num(word):
    """
    converts a word along the lines of one / 1 / twentyone to the equivalent integer
    :return: 0-100 or null if not a number
    """
    # adapted from https://stackoverflow.com/questions/493174

    word = word.strip()
    if word is "": return None

    try:
        numbers = ''.join([c for c in word if c.isdigit()])
        return int(numbers)
    except ValueError:
        pass

    try:
        for ten in tens[2:]:
            if word.startswith(ten) and word is not ten:
                one = word[len(ten):]
                return numwords[ten] + numwords[one]

        return numwords[word]

    except KeyError as e:
        return None
