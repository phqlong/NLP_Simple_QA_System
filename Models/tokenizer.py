import re
from nltk import parse


class Token:
    def __init__(self, word, pos):
        self.word = word
        self.pos = pos

    def __str__(self) -> str:
        return f'(%s, %s)' % (self.word, self.pos)


class Tokenizer:
    def __init__(self, grammar):
        self.grammar = grammar
        self.tree = None
        self.posTokens = []

    def convert2utf8(self, text):
        # Unicode tổ hợp, ex: len('à') = 2
        char1252 = "à|á|ả|ã|ạ|ầ|ấ|ẩ|ẫ|ậ|ằ|ắ|ẳ|ẵ|ặ|è|é|ẻ|ẽ|ẹ|ề|ế|ể|ễ|ệ|ì|í|ỉ|ĩ|ị|ò|ó|ỏ|õ|ọ|ồ|ố|ổ|ỗ|ộ|ờ|ớ|ở|ỡ|ợ|ù|ú|ủ|ũ|ụ|ừ|ứ|ử|ữ|ự|ỳ|ý|ỷ|ỹ|ỵ|À|Á|Ả|Ã|Ạ|Ầ|Ấ|Ẩ|Ẫ|Ậ|Ằ|Ắ|Ẳ|Ẵ|Ặ|È|É|Ẻ|Ẽ|Ẹ|Ề|Ế|Ể|Ễ|Ệ|Ì|Í|Ỉ|Ĩ|Ị|Ò|Ó|Ỏ|Õ|Ọ|Ồ|Ố|Ổ|Ỗ|Ộ|Ờ|Ớ|Ở|Ỡ|Ợ|Ù|Ú|Ủ|Ũ|Ụ|Ừ|Ứ|Ử|Ữ|Ự|Ỳ|Ý|Ỷ|Ỹ|Ỵ"
        # Unicode dựng sẵn , ex: len('à') = 1
        charutf8 = "à|á|ả|ã|ạ|ầ|ấ|ẩ|ẫ|ậ|ằ|ắ|ẳ|ẵ|ặ|è|é|ẻ|ẽ|ẹ|ề|ế|ể|ễ|ệ|ì|í|ỉ|ĩ|ị|ò|ó|ỏ|õ|ọ|ồ|ố|ổ|ỗ|ộ|ờ|ớ|ở|ỡ|ợ|ù|ú|ủ|ũ|ụ|ừ|ứ|ử|ữ|ự|ỳ|ý|ỷ|ỹ|ỵ|À|Á|Ả|Ã|Ạ|Ầ|Ấ|Ẩ|Ẫ|Ậ|Ằ|Ắ|Ẳ|Ẵ|Ặ|È|É|Ẻ|Ẽ|Ẹ|Ề|Ế|Ể|Ễ|Ệ|Ì|Í|Ỉ|Ĩ|Ị|Ò|Ó|Ỏ|Õ|Ọ|Ồ|Ố|Ổ|Ỗ|Ộ|Ờ|Ớ|Ở|Ỡ|Ợ|Ù|Ú|Ủ|Ũ|Ụ|Ừ|Ứ|Ử|Ữ|Ự|Ỳ|Ý|Ỷ|Ỹ|Ỵ"

        map2utf8 = {c_1252: c_utf8 for c_1252, c_utf8 in zip(
            char1252.split('|'), charutf8.split('|'))}

        return re.sub(char1252, lambda c: map2utf8[c.group()], text)


    def split2token(self, text):
        # TP.Ho
        text = re.sub(r'\.', ' ', text)
        # , lúc
        text = re.sub(r',', ' ,', text)
        # không?
        text = re.sub(r'\?', ' ?', text)

        return text.split()


    def tokenize(self, text):
        # Convert to Utf8
        text = self.convert2utf8(text)
        # Tokenize text
        tokens = self.split2token(text)

        # Load parser from grammar.cfg
        nlp_grammar = parse.load_parser(self.grammar)
        self.tree = nlp_grammar.parse_one(tokens)

        # Get subtree in tree, which height==2, means get leave word and its label, ex: TRAIN-N and 'Tàu' 'hỏa'
        for s in self.tree.subtrees(lambda t: t.height() == 2):
            word = ' '.join(s.leaves())
            pos = str(s.label())
            self.posTokens.append(Token(word, pos))

        return self.posTokens
