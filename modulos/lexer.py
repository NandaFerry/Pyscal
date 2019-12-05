import sys
from modulos.ts import TS
from modulos.tag import Tag
from modulos.token import Token


class Lexer:

    def __init__(self, input_file):
        try:
            self.input_file = open(input_file, 'rb')
            self.lookahead = 0
            self.n_line = 1
            self.n_column = 0
            self.ts = TS()
            self.erro = []
        except IOError:
            print('Erro ao abrir arquivo.')
            sys.exit(0)

    def closeFile(self):
        try:
            self.input_file.close()
        except IOError:
            print('Erro ao fechar arquivo.')
            sys.exit(0)

    def sinalizaErroLexico(self, message):
        print("[Erro Lexico]: ", message, "\n")

    def retornaPonteiro(self):
        if self.lookahead.decode('ascii') != '':
            self.input_file.seek(self.input_file.tell() - 1)
            self.n_column -= 1

    def printTS(self):
        self.ts.printTS()

    def erros(self):
        print('!!! ' + self.erro + ' !!!')

    def proxToken(self):
        estado = 0
        lexema = ""
        c = '\u0000'

        while True:
            self.lookahead = self.input_file.read(1)
            c = self.lookahead.decode('ascii')

            if c == '\t':
                self.n_column += 4
            else:
                self.n_column += 1

            if estado == 0:
                if c == '\n':
                    self.n_column = 1
                    self.n_line += 1
                    estado = 0
                if c == '':
                    return Token(Tag.EOF, "EOF", self.n_line, self.n_column)
                elif c == '\t' or c == '\n' or  c == '\r':
                    estado = 0
                elif c == ' ':
                    estado == 0
                elif c == '*':
                    estado = 1
                elif c == '/':
                    estado = 2
                elif c == '+':
                    estado = 3
                elif c == '=':
                    estado = 4
                elif c == '!':
                    estado = 7
                elif c == '>':
                    estado = 10
                elif c == '<':
                    estado = 13
                elif c == '(':
                    estado = 20
                elif c == ')':
                    estado = 21
                elif c == '[':
                    estado = 22
                elif c == ']':
                    estado = 23
                elif c == ',':
                    estado = 24
                elif c == ';':
                    estado = 25
                elif c == ':':
                    estado = 26
                elif c == '#':
                    estado = 27
                elif c == '"':
                    estado = 29
                elif c == '-':
                    x = self.retornaPonteiro()
                    print(x)
                    if  x == Tag.ID or x == Tag.NUM_INTEIRO:
                        estado = 36
                    else:
                        estado = 34
                elif c == '.':
                    estado = 35
                elif c.isdigit():
                    lexema += c
                    estado = 16
                elif c.isalpha():
                    lexema += c
                    estado = 32
                else:
                    self.sinalizaErroLexico("Caractere invalido [" + c + "] na linha " +
                                            str(self.n_line) + " e coluna " + str(self.n_column))

            # -- begin estado 1
            elif estado == 1:
                self.retornaPonteiro()
                return Token(Tag.OP_MULTIPLICACAO, "*", self.n_line, self.n_column)
            # -- end estado 1

            # -- begin estado 2
            elif estado == 2:
                self.retornaPonteiro()
                return Token(Tag.OP_DIVISAO, "/", self.n_line, self.n_column)
            # -- end estado 2

            # -- begin estado 3
            elif estado == 3:
                self.retornaPonteiro()
                return Token(Tag.OP_ADICAO, "+", self.n_line, self.n_column)
            # -- end estado 3

            # -- begin estado 4
            elif estado == 4:
                if c == '=':
                    return Token(Tag.OP_IGUAL_IGUAL, "==", self.n_line, self.n_column)
                else:
                    self.retornaPonteiro()
                    return Token(Tag.OP_UNARIO_IGUAL, "=", self.n_line, self.n_column)
            # -- end estado 4

            # -- begin estado 7
            elif estado == 7:
                if c == '=':
                    return Token(Tag.OP_DIFERENTE, "!=", self.n_line, self.n_column)
                else:
                    self.retornaPonteiro()
                    return Token(Tag.OP_UNARIO_DIFERENTE, "!", self.n_line, self.n_column)
            # -- end estado 7

            # -- begin estado 10
            elif estado == 10:
                if c == '=':
                    return Token(Tag.OP_MAIOR_IGUAL, ">=", self.n_line, self.n_column)
                else:
                    self.retornaPonteiro()
                    return Token(Tag.OP_MAIOR, ">", self.n_line, self.n_column)
            # -- end estado 10

            # -- begin estado 13
            elif estado == 13:
                if c == '=':
                    return Token(Tag.OP_MENOR_IGUAL, "<=", self.n_line, self.n_column)
                else:
                    self.retornaPonteiro()
                    return Token(Tag.OP_MENOR, "<", self.n_line, self.n_column)
            # -- end estado 13

            # -- begin estado 16
            elif estado == 16:
                if c.isalnum():
                    lexema += c
                elif c == '.':
                    lexema += c
                    estado = 18
                else:
                    self.retornaPonteiro()
                    token = self.ts.getToken(lexema)
                    if token is None:
                        token = Token(Tag.NUM_INTEIRO, lexema, self.n_line, self.n_column)
                    return token
            # -- end estado 16

            # -- begin estado 18
            elif estado == 18:
                if c.isalnum():
                    lexema += c
                else:
                    self.retornaPonteiro()
                    token = self.ts.getToken(lexema)
                    if token is None:
                        token = Token(Tag.NUM_DOUBLE, lexema, self.n_line, self.n_column)
                    return token
            # -- end estado 18

            # -- begin estado 20
            elif estado == 20:
                self.retornaPonteiro()
                return Token(Tag.OP_APA, "(", self.n_line, self.n_column)
            # -- end estado 20

            # -- begin estado 21
            elif estado == 21:
                self.retornaPonteiro()
                return Token(Tag.OP_FPA, ")", self.n_line, self.n_column)
            # -- end estado 21

            # -- begin estado 22
            elif estado == 22:
                self.retornaPonteiro()
                return Token(Tag.OP_ACO, "[", self.n_line, self.n_column)
            # -- end estado 22

            # -- begin estado 23
            elif estado == 23:
                self.retornaPonteiro()
                return Token(Tag.OP_FCO, "]", self.n_line, self.n_column)
            # -- end estado 23

            # -- begin estado 24
            elif estado == 24:
                self.retornaPonteiro()
                return Token(Tag.OP_VIRGULA, ",", self.n_line, self.n_column)
            # -- end estado 24

            # -- begin estado 25
            elif estado == 25:
                self.retornaPonteiro()
                return Token(Tag.OP_PONTO_VIRGULA, ";", self.n_line, self.n_column)
            # -- end estado 25

            # -- begin estado 26
            elif estado == 26:
                self.retornaPonteiro()
                return Token(Tag.OP_DOIS_PONTOS, ":", self.n_line, self.n_column)
            # -- end estado 26

            # -- begin estado 27
            elif estado == 27:
                if c == '\n':
                    estado = 0
                    self.n_line += 1
                    self.n_column = 0
            # -- end estado 27

            # -- begin estado 29
            elif estado == 29:
                if c == '':
                    self.sinalizaErroLexico("String aberta [" + '"' + lexema + '"' + "] na linha " +
                                            str(self.n_line) + " e coluna " + str(self.n_column))
                    token = None
                    estado = 0
                elif c.isalnum():
                    lexema += c
                elif c.isalpha():
                    lexema += c
                elif c != '"':
                    lexema += c
                elif lexema == '':
                    self.sinalizaErroLexico("String vazia [" + '"' + lexema + '"' + "] na linha " +
                                            str(self.n_line) + " e coluna " + str(self.n_column))
                    token = None
                    estado = 0
                else:
                    if lexema.__contains__('\n'):
                        self.sinalizaErroLexico("String em mais de uma linha [" + '"' + lexema + '"' + "] na linha " +
                                                str(self.n_line) + " e coluna " + str(self.n_column))
                        token = None
                        estado = 0
                    else:
                        return Token(Tag.LIT, "%s" % lexema, self.n_line, self.n_column)
            # -- end estado 29

            # -- begin estado 32
            elif estado == 32:
                if c.isalnum() or c.isalpha() or c == '_':
                    lexema += c
                else:
                    self.retornaPonteiro()
                    token = self.ts.getToken(lexema)
                    if token is None:
                        token = Token(Tag.ID, " %s" % lexema, self.n_line, self.n_column)
                        self.ts.addToken(lexema, token)
                    else:
                        token = Token(self.ts.getToken(lexema).nome, lexema, self.n_line, self.n_column)
                    return token
            # -- end estado 32

            # -- begin estado 34
            elif estado == 34:
                if (c == '-'):
                    return Token(Tag.OP_NEGACAO, "-", self.n_line, self.n_column)
                else:
                    self.retornaPonteiro()
                    return Token(Tag.OP_NEGACAO, "-", self.n_line, self.n_column)

            # -- end estado 34

            # -- begin estado 35
            elif estado == 35:
                self.retornaPonteiro()
                return Token(Tag.OP_PONTO, ".", self.n_line, self.n_column)
            # -- end estado 35

                # -- begin estado 35
            elif estado == 36:
                self.retornaPonteiro()
                return Token(Tag.OP_SUBTRACAO, "-", self.n_line, self.n_column)
            # -- end estado 35