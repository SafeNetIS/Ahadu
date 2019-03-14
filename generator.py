# Author: Temesgen Yibeltal <temesgen.yibeltal@safenet.et>.

"""
Command-line utility to generate permutation of possible words used in a password
"""
import argparse
import sys

SPECIAL_CHARACTERS_REPLACEMENTS = {
    "a": "@",
    "o": "0",
    "s": "$",
    "e": "3",
}

SPECIAL_CONNECTOR_CHARACTERS = [
    # "@"
]

SPECIAL_ADDITIONS = [
    "1", "12", "123", "1234"
]

SPECIAL_ADDITIONS_CHARACTERS = [
    "*"
]


class Generator:
    def __init__(self, words, output_file, level=5, strict_mode=False):
        self.results = []
        self.words = words
        self.level = level
        self.word_forms = {}
        for word in self.words:
            self.word_forms[word] = self.generate_word_forms(word)
        self.output_file = output_file

    def generate(self):
        self.generate_one_word_dictionary()
        self.generate_two_word_dictionary()
        self.generate_three_word_dictionary()

        for password_dict in self.one_word_dictionary:
            self.results.append(password_dict["pass"])
        for password_dict in self.two_word_dictionary:
            self.results.append(password_dict["pass"])
        for password_dict in self.three_word_dictionary:
            self.results.append(password_dict["pass"])


    def generate_one_word_dictionary(self):
        self.one_word_dictionary = []
        words_only = []
        words_with_special_additions = []
        words_with_special_addition_characters = []
        words_with_special_addition_and_special_characters = []
        for word in self.words:
            for word_form in self.word_forms[word]:
                words_only.append({"pass" : word_form, "forms":[word]})
                for special_addition in SPECIAL_ADDITIONS:
                    words_with_special_additions.append({"pass" : word_form + special_addition, "forms":[word]})
                for special_addition_character in SPECIAL_ADDITIONS_CHARACTERS:
                    words_with_special_addition_characters.append({"pass" : word_form + special_addition_character, "forms":[word]})
                for special_addition in SPECIAL_ADDITIONS:
                    for special_addition_character in SPECIAL_ADDITIONS_CHARACTERS:
                        words_with_special_addition_and_special_characters.append({"pass" : word_form + special_addition + special_addition_character, "forms":[word]})


        self.one_word_dictionary.extend(words_only)
        self.one_word_dictionary.extend(words_with_special_additions)
        self.one_word_dictionary.extend(words_with_special_addition_characters)
        self.one_word_dictionary.extend(words_with_special_addition_and_special_characters)

    def generate_two_word_dictionary(self):
        self.two_word_dictionary = []

        two_words = []
        two_words_with_connectors = []

        for word in self.words:
            for one_word in self.one_word_dictionary:
                if word in one_word["forms"]:
                    continue
                if len(one_word["forms"]) == 0:
                    continue

                for word_form in self.word_forms[word]:
                    two_words.append({"pass" : word_form + one_word["pass"], "forms":[word, one_word["forms"][0]]})
                    for connector in SPECIAL_CONNECTOR_CHARACTERS:
                        two_words_with_connectors.append({"pass" : word_form + connector + one_word["pass"], "forms":[word, one_word["forms"][0]]})

        self.two_word_dictionary.extend(two_words)
        self.two_word_dictionary.extend(two_words_with_connectors)

    def generate_three_word_dictionary(self):
        self.three_word_dictionary = []

        three_words = []
        three_words_with_connectors = []

        for word in self.words:
            for two_word in self.two_word_dictionary:
                if word in two_word["forms"]:
                    continue
                if len(two_word["forms"]) < 2:
                    continue

                for word_form in self.word_forms[word]:
                    three_words.append({"pass" : word_form + two_word["pass"], "forms":[word, two_word["forms"][0], two_word["forms"][1]]})
                    for connector in SPECIAL_CONNECTOR_CHARACTERS:
                        three_words_with_connectors.append({"pass" : word_form + connector + two_word["pass"], "forms":[word, two_word["forms"][0], two_word["forms"][1]]})

        self.three_word_dictionary.extend(three_words)
        self.three_word_dictionary.extend(three_words_with_connectors)

    def generate_word_forms(self, composite_word):
        composite_words = composite_word.split(":")
        aggregate_words = []
        for word in composite_words:
            words = [word.upper(), word.lower(), word.title(), word]
            for word_form in [word.upper(), word.lower(), word.title(), word]:
                for i in range(1, self.level + 1):
                    words.append(self.replace_word_with_special_characters(word_form, i))

            aggregate_words.extend(words)

        aggregate_words = self.remove_duplicates(aggregate_words)

        return aggregate_words

    def remove_duplicates(self, words):
        existing = []
        for word in words:
            if word not in existing:
                existing.append(word)

        return existing

    def replace_word_with_special_characters(self, word, level):
        if level == 5:
            level = 100
        output = word
        counter = 0
        for char in SPECIAL_CHARACTERS_REPLACEMENTS:
            output = output.replace(char, SPECIAL_CHARACTERS_REPLACEMENTS[char])
            output = output.replace(char.upper(), SPECIAL_CHARACTERS_REPLACEMENTS[char])
            counter += 1
            if counter >= level:
                break

        return output

    def write_output(self):
        for result in self.results:
            self.output_file.write(result + "\n")
        self.output_file.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='generate a password list from permutation of probable words')

    parser.add_argument('-w', required=True, metavar='word', nargs='+', type=str,
                        help='possible words used in the password')
    parser.add_argument('-s', action='store_true', default=False, help='ordered list of words')
    parser.add_argument('-l', metavar='level', default=5, type=int, help='possible words used in the password')
    parser.add_argument('-o', metavar='output.txt', default=sys.stdout, type=argparse.FileType('w'),
                        help='The output file where the password list should be written')

    args = parser.parse_args()

    generator = Generator(args.w, args.o, args.l, args.s)
    generator.generate()
    generator.write_output()
