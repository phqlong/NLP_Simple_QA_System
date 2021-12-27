from Models import *
import optparse
import sys


def parse_args(args):
    parser = optparse.OptionParser(description='Run QA Train System')

    parser.add_option('--grammar',
                      dest='grammar',
                      default='Models/grammar.cfg',
                      help='File name which contains the model')
    parser.add_option('--database',
                      dest='database',
                      default='Models/database.txt',
                      help='Text file which contains data of database')

    parser.add_option('--input-dir',
                      dest='inputDir',
                      default='Input',
                      help='Root of input directory which contains inputs')
    parser.add_option('--output-dir',
                      dest='outputDir',
                      default='Output',
                      help='Root of output directory which contains outputs')

    parser.add_option('--input-file',
                      dest='inputFile',
                      default="input_01.txt",
                      help='File name which contains the input')
    parser.add_option('--input-string',
                      dest='inputStr',
                      default=None,
                      help='Insert input query string')

    parser.add_option('--verbose',
                      dest='verbose',
                      default=1,
                      help="""Verbose Option: 
                        1 - Print result with parse tree by steps and Write output
                        2 - Only print result with parse tree
                        3 - Print result by steps and Write output
                        4 - Only print result""")

    options, _ = parser.parse_args(args)
    return options


def read_input(path):
    with open(path, 'r', encoding='utf8') as f:
        text = f.read()
    return text


def write_output(path, result):
    with open(path, 'w', encoding='utf8') as f:
        f.write(result)


if __name__ == '__main__':
    args = parse_args(sys.argv)
    args.verbose = int(args.verbose)

    if args.inputStr:
        inputText = args.inputStr
    else:
        inputText = read_input(args.inputDir + '/' + args.inputFile)
    print("Input text: " + inputText)

    ##################################################################################
    # a) Xây dựng bộ phân tích cú pháp của văn phạm phụ thuộc.
    # Tokenization
    print("\n========================== Tokenization ==========================")
    tk = Tokenizer(args.grammar)
    token = tk.tokenize(inputText)
    tokenStr = ' '.join(str(t) for t in token)
    print(tokenStr)

    if args.verbose == 1:
        print("\n========================== Parse tree ==========================")
        tk.tree.pretty_print(unicodelines=True, nodedist=3)
        write_output(args.outputDir + '/output_a.txt', tokenStr)
    elif args.verbose == 2:
        print("\n========================== Parse tree ==========================")
        tk.tree.pretty_print(unicodelines=True, nodedist=3)
    elif args.verbose == 3:
        write_output(args.outputDir + '/output_a.txt', tokenStr)

    ##################################################################################
    # b) Phân tích cú pháp và xuất ra các quan hệ ngữ nghĩa của các câu truy vấn.
    # Dependency Parsing
    print("\n========================== Dependency Parsing ==========================")
    parser = DependencyParser(token)
    parser.parse()
    depParseStr = '\n'.join(str(t) for t in parser.relation)
    print(depParseStr)

    if args.verbose in [1, 3]:
        write_output(args.outputDir + '/output_b.txt', depParseStr)

    ##################################################################################
    # c) Từ kết quả ở b) tạo các quan hệ văn phạm với cơ sở dữ liệu đã cho ở trên.
    # Grammatical Relations
    print("\n========================== Grammatical Relations ==========================")
    gr = GrammaticalRelations(parser.relation)
    gramRel = gr.getGramRel()
    gramRelStr = '\n'.join(str(t) for t in gramRel)
    print(gramRelStr)

    if args.verbose in [1, 3]:
        write_output(args.outputDir + '/output_c.txt', gramRelStr)

    ##################################################################################
    # d) Tạo dạng luận lý từ các quan hệ văn phạm ở c)
    # Logical Forms
    print("\n========================== Logical Forms ==========================")
    logicalFormStr = gr.getLogicalForms()
    print(logicalFormStr)

    if args.verbose in [1, 3]:
        write_output(args.outputDir + '/output_d.txt', logicalFormStr)

    ##################################################################################
    # e) Tạo ngữ nghĩa thủ tục từ dạng luận lý ở d).
    # Procedural Semantics
    print("\n========================== Procedural Semantics ==========================")
    re = ProceduralSemantic(gr.queryPatterns, gr.var)
    procLst = re.getProcedure()
    procStr = '\n'.join(proc for proc in procLst)
    print(procStr)

    if args.verbose in [1, 3]:
        write_output(args.outputDir + '/output_e.txt', procStr)

    ##################################################################################
    # f) Truy xuất dữ liệu để tìm thông tin trả lời cho các câu truy vấn trên.
    # Retrieve Information
    print("\n========================== Retrieve Information ==========================")
    result = re.retrieveResult("Models/database.txt")
    resultStr = '\n'.join(res for res in result)
    print(resultStr)

    if args.verbose in [1, 3]:
        write_output(args.outputDir + '/output_f.txt', resultStr)
