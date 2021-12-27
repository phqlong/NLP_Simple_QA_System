from Models.tokenizer import Token


class Relation:
    def __init__(self, rule, head, tail):
        self.rule = rule
        self.head = head
        self.tail = tail

    def __str__(self) -> str:
        return f'{self.rule}({self.head}, {self.tail})'


class DependencyParser:
    def __init__(self, inputBuf=[]):
        self.inputBuf = inputBuf
        self.relation = []
        self.stack = []

    def shift(self):
        curToken = self.inputBuf.pop(0)
        self.stack.append(curToken)
        # print("Shift\n")
        return

    def reduce(self):
        self.stack.pop()
        # print("Reduce\n")
        return

    def rightarc(self, rule):
        stackW = self.stack[-1].word
        inputW = self.inputBuf[0].word

        rel = Relation(rule, stackW, inputW)
        self.relation.append(rel)

        temp = self.inputBuf.pop(0)
        self.stack.append(temp)

        # print('Rightarc')
        # print(rel)
        # print()
        return rel

    def leftarc(self, rule):
        stackW = self.stack[-1].word
        inputW = self.inputBuf[0].word

        rel = Relation(rule, inputW, stackW)
        self.relation.append(rel)

        self.stack.pop()

        # print('Leftarc')
        # print(rel)
        # print()
        return rel

    def parse(self):
        self.stack.append(Token('ROOT', 'ROOT'))

        while self.inputBuf:
            stackPos = self.stack[-1].pos
            inputPos = self.inputBuf[0].pos
            # print(stackPos, inputPos)

            if stackPos == 'ROOT':
                if inputPos in ['RUN-V', 'ARRIVE-V']:   # ROOT -> chạy | đến
                    self.rightarc('ROOT')
                else:                                   # ROOT <== Đầu câu
                    self.shift()

            elif stackPos == 'TRAIN-N':
                if inputPos in ['RUN-V', 'ARRIVE-V']:   # Tàu hỏa <- chạy | đến
                    self.leftarc('nsubj')
                elif inputPos == 'WH-DET':              # Tàu hỏa -> nào
                    self.rightarc('det-wh')
                elif inputPos == 'TRAIN-NAME':          # Tàu hỏa -> B3
                    self.rightarc('namemod')
                else:
                    self.shift()

            elif stackPos == 'RUN-V':
                if inputPos == 'YN-AUX':        # chạy ... -> ...không ?
                    self.rightarc('advmod')
                elif inputPos == 'QT':          # chạy ... -> ...?
                    self.rightarc('punct')
                elif inputPos == 'CITY-NAME':   # chạy từ/đến -> Huế
                    self.rightarc('obl')
                elif inputPos == 'TIME-MOD':    # chạy lúc -> 00:00HR
                    self.rightarc('obl')
                elif inputPos == 'WH-TIME-MOD': # chạy ... -> mấy giờ?
                    self.rightarc('obl')
                else:
                    self.shift()

            elif stackPos == 'ARRIVE-V':
                if inputPos == 'YN-AUX':        # đến ... -> ...không ?
                    self.rightarc('advmod')
                elif inputPos == 'QT':          # đến ... -> ...?
                    self.rightarc('punct')
                elif inputPos == 'CITY-NAME':   # đến -> Huế
                    self.rightarc('dobj-a')
                elif inputPos == 'TIME-MOD':    # đến lúc -> 00:00HR
                    self.rightarc('obl')
                elif inputPos == 'WH-TIME-MOD': # đến ... -> mấy giờ?
                    self.rightarc('obl')
                else:
                    self.shift()

            elif stackPos == 'TIME-N':
                if inputPos == 'TRAIN-N':       # Thời gian <- tàu hỏa
                    self.leftarc('nmod')
                else:
                    self.reduce()

            elif stackPos == 'AUX':
                if inputPos in ['RUN-V', 'ARRIVE-V']:   # có <- chạy/đến
                    self.leftarc('advmod')
                elif inputPos == 'WH-TIME-MOD':         # là mấy giờ ?
                    self.leftarc('is')
                else:
                    self.reduce()

            elif stackPos == 'FROM':
                if inputPos == 'CITY-NAME':     # từ <- Huế
                    self.leftarc('case-d')
                else:
                    self.shift()

            elif stackPos == 'TO':
                if inputPos == 'CITY-NAME':     # đến <- Huế
                    self.leftarc('case-a')
                else:
                    self.shift()

            elif stackPos == 'AT-TIME':
                if inputPos == 'TIME-MOD':      # lúc <- 19:00HR
                    self.leftarc('case-t')
                elif inputPos == 'WH-TIME-MOD': # lúc <- mấy giờ
                    self.leftarc('case-t-wh')
                else:
                    self.reduce()

            elif stackPos == 'CITY-N':
                if inputPos == 'CITY-NAME':     # thành phố <- Huế
                    self.leftarc('nmod')
                else:
                    self.reduce()

            else:
                self.reduce()
