import random
from io import StringIO
import argparse


class ExistedTerm(Exception):
    def __init__(self, term):
        self.message = 'The card "{}" already exists. Try again: '.format(term)
        super().__init__(self.message)


class DuplicateDefinition(Exception):
    def __init__(self, definition):
        self.message = 'The definition "{}" already exists. Try again: '.format(definition)
        super().__init__(self.message)


class WrongDefinition(Exception):
    def __init__(self, correct, another):
        self.message = 'Wrong. The right answer is "{}", but your definition is correct for "{}".'.format(correct,
                                                                                                          another)
        super().__init__(self.message)


class RemoveFinder(Exception):
    def __init__(self, term):
        self.message = "Can't remove " + term + ": there is no such card. "
        super().__init__(self.message)


class NoMistakes(Exception):
    def __init__(self):
        self.message = "There are no cards with errors.\n"
        super().__init__(self.message)


class Cards:
    flashcards = dict()
    card_term = str()
    card_num = 1

    def __init__(self, action):
        self.action = action
        if action == 'add':
            self.card_appender()
        elif action == 'remove':
            self.remove()
        elif action == 'import':
            self.file_importer()
        elif action == 'export':
            self.file_exporter()
        elif action == 'ask':
            self.checker()
        elif action == 'reset stats':
            self.reset_stat()
        elif action == 'hardest card':
            self.hardest_card()
        elif action == 'log':
            logger.export_log()

    def card_appender(self):
        for i in range(self.card_num):
            logger.printer('The card: ')
            while True:
                try:
                    term = input()
                    logger.output.write(term + '\n')
                    if term in self.flashcards.keys():
                        raise ExistedTerm(term)
                    else:
                        break
                except ExistedTerm:
                    logger.printer(ExistedTerm(term).message)

            logger.printer('The definition of the card: ')
            while True:
                try:
                    definition = input()
                    logger.output.write(definition + '\n')
                    for definitions in self.flashcards.values():
                        if definition in definitions['definition']:
                            raise DuplicateDefinition(definition)
                        else:
                            break
                except DuplicateDefinition:
                    logger.printer(DuplicateDefinition(definition).message)
                else:
                    break
            self.flashcards[term] = {'definition': definition, 'mistakes': 0}
            logger.printer(f'The pair ("{term}":"{definition}") has been added.')

    def remove(self):
        try:
            logger.printer('Which card?')
            card = input()
            logger.output.write(card + '\n')
            if card in self.flashcards.keys():
                del self.flashcards[card]
                logger.printer(f'The card has been removed. {card}')
            else:
                raise RemoveFinder(card)
        except RemoveFinder:
            logger.printer(RemoveFinder(card).message)

    def file_importer(self, arg=False):
        if arg:
            path = arg
        else:
            logger.printer('File name:')
            path = input()
            logger.output.write(path + '\n')
        try:
            file = open(path, 'r')
            n = 0
            for i in file:
                try:
                    imported_list = i.split(' ')
                    imported_list[1] = imported_list[1].replace(',', '')
                    imported_list[2] = int(imported_list[2].replace('\n', ''))
                    self.flashcards[imported_list[0]] = {'definition': imported_list[1], 'mistakes': imported_list[2]}
                    n += 1
                except IndexError:
                    pass
            logger.printer(f"{n} cards have been loaded.")
            file.close()
        except FileNotFoundError:
            logger.printer('File not found.')

    def file_exporter(self, arg=False):
        if arg:
            path = arg
        else:
            logger.printer('File name: ')
            path = input()
            logger.output.write(path + '\n')
        file = open(path, 'w')
        n = 0
        for i in self.flashcards.keys():
            file.write(f'{i} {self.flashcards.get(i)["definition"]}, {self.flashcards.get(i)["mistakes"]}\n')
            n += 1
        logger.printer('{} cards have been saved.'.format(n))
        file.close()

    def checker(self):
        logger.printer('How many times to ask?')
        ask_num = int(input())
        logger.output.write(str(ask_num) + '\n')
        for i in range(ask_num):
            try:
                random_key = random.choice(list(self.flashcards.keys()))
                logger.printer(f'Print the definition of "{random_key}":')
                answer = input()
                logger.output.write(answer + '\n')
                if answer == self.flashcards.get(random_key)['definition']:
                    logger.printer('Correct!')
                elif answer != self.flashcards.get(random_key)['definition'] and \
                        [x['definition'] for x in self.flashcards.values() if x['definition'] == answer]:
                    for key, defi in zip(self.flashcards.keys(), self.flashcards.values()):
                        if answer == defi['definition']:
                            correct_key = key
                            defi['mistakes'] += 1
                            raise WrongDefinition(self.flashcards.get(random_key)['definition'], correct_key)
                else:
                    logger.printer(f'Wrong. The right answer is "{self.flashcards.get(random_key)["definition"]}".')
                    self.flashcards.get(random_key)["mistakes"] += 1
            except WrongDefinition:
                logger.printer(WrongDefinition(self.flashcards.get(random_key)['definition'], correct_key))

    def hardest_card(self):
        max_f_loop = 0
        keys = []
        try:
            for key_card, value_card in zip(self.flashcards.keys(), self.flashcards.values()):
                if int(value_card['mistakes']) > max_f_loop:
                    max_f_loop = int(value_card['mistakes'])
                    hardest_card_res = key_card
            if len(self.flashcards) > 1:
                for keys_loop, values in zip(self.flashcards.keys(), self.flashcards.values()):
                    if int(values['mistakes']) == max_f_loop:
                        keys.append(keys_loop)
            if max_f_loop > 0 and len(keys) <= 1:
                logger.printer(f'The hardest card is "{hardest_card_res}". You have {max_f_loop} errors answering it.')
            elif max_f_loop > 0 and len(keys) > 1:
                print(f'The hardest cards are {str(keys)}. You have {max_f_loop} errors answering them.\n')
            else:
                raise NoMistakes()
        except NoMistakes:
            logger.printer(NoMistakes())

    def reset_stat(self):
        for i in self.flashcards.values():
            i['mistakes'] = 0
        logger.printer('Card statistics have been reset.')


class ProjectLogger:
    def __init__(self):
        self.output = StringIO()

    def export_log(self):
        self.printer('File name: ')
        path = input()
        self.output.write(path + '\n')
        content = self.output.getvalue()
        with open(path, 'w') as file:
            file.write(content)
        self.printer('The log has been saved.')

    def ender(self):
        self.output.close()

    def printer(self, message):
        print(message)
        print(message, file=self.output, end='\n')


class ProjectParser(Cards):
    def __init__(self):
        self.parser = argparse.ArgumentParser()
        self.parser.add_argument('--import_from')
        self.parser.add_argument('--export_to')
        self.args = self.parser.parse_args()

        self.importer = self.args.import_from
        self.exporter = self.args.export_to

        if self.importer:
            self.import_cards()

    def import_cards(self):
        super().file_importer(self.importer)

    def export_cards(self):
        super().file_exporter(self.exporter)


if __name__ == '__main__':
    logger = ProjectLogger()
    parser = ProjectParser()
    while True:
        logger.printer('Input the action (add, remove, import, export, ask, exit, log, hardest card, reset stats): ')
        option = input()
        logger.output.write(option + '\n')
        if option == 'exit':
            logger.printer('Bye bye!')
            if parser.exporter:
                parser.export_cards()
            break
        Cards(option)
    logger.ender()
