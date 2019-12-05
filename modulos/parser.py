import sys

from modulos.ts import TS
from modulos.tag import Tag
from modulos.token import Token
from modulos.lexer import Lexer

class Parser():

    def __init__(self, lexer):
        self.lexer = lexer
        self.token = lexer.proxToken()  # Leitura inicial obrigatoria do primeiro simbolo

    def sinalizaErroSintatico(self, message):
        print("[Erro Sintatico] na linha " + str(self.token.getLinha()) + " e coluna " + str(
            self.token.getColuna()) + ": ")
        print(message, "\n")

    def advance(self):
        print("[DEBUG] token: ", self.token.toString())
        self.token = self.lexer.proxToken()

    def skip(self, message):
        self.sinalizaErroSintatico(message)
        self.advance()

    def sync(self, message):
        self.sinalizaErroSintatico(message)

    # verifica token esperado t
    def eat(self, t):
        if self.token.getNome() == t:
            self.advance()
            return True
        else:
            return False
###
    # Programa -> Classe EOF
    def Programa(self):
        self.Classe()

        if self.token.getNome() != Tag.EOF:
            self.sinalizaErroSintatico("Esperado \"EOF\"; encontrado " + "\"" + self.token.getLexema() + "\"")

    # Classe -> "class" ID ":" ListaFuncao Main "end" "."
    def Classe(self):
        if self.eat(Tag.KW_CLASS):
            if not self.eat(Tag.ID):
                self.sinalizaErroSintatico("Esperado \"ID\"; encontrado " + "\"" + self.token.getLexema() + "\"")
            if not self.eat(Tag.OP_DOIS_PONTOS):
                self.sinalizaErroSintatico("Esperado \":\"; encontrado " + "\"" + self.token.getLexema() + "\"")

            self.ListaFuncao()
            self.Main()

            if not self.eat(Tag.KW_END):
                self.sinalizaErroSintatico("Esperado \"end\"; encontrado " + "\"" + self.token.getLexema() + "\"")
            if not self.eat(Tag.OP_PONTO):
                self.sinalizaErroSintatico("Esperado \".\"; encontrado " + "\"" + self.token.getLexema() + "\"")
        else:
            if self.token.getNome() == Tag.EOF:
                self.sync("Esperado \"class\"; encontrado " + "\"" + self.token.getLexema() + "\"")
                return
            else:
                self.skip("Esperado \"class\"; encontrado " + "\"" + self.token.getLexema() + "\"")
                if self.token.getNome() != Tag.EOF: self.Classe()

    # DeclaraID -> TipoPrimitivo ID ";"
    def DeclaraID(self):
        if self.token.getNome() == Tag.KW_BOOL or self.token.getNome() == Tag.KW_INTEGER or \
                self.token.getNome() == Tag.KW_STRING or self.token.getNome() == Tag.KW_DOUBLE \
                or self.token.getNome() == Tag.KW_VOID:

            self.TipoPrimitivo()

            if not self.eat(Tag.ID):
                self.sinalizaErroSintatico("Esperado \"ID\"; encontrado " + "\"" + self.token.getLexema() + "\"")
            if not self.eat(Tag.OP_PONTO_VIRGULA):
                self.sinalizaErroSintatico("Esperado \";\"; encontrado " + "\"" + self.token.getLexema() + "\"")
        else:
            if self.token.getNome() == Tag.ID or self.token.getNome() == Tag.KW_END or \
                    self.token.getNome() == Tag.KW_RETURN or self.token.getNome() == Tag.KW_IF or \
                    self.token.getNome() == Tag.KW_WHILE or self.token.getNome() == Tag.KW_WRITE:

                self.sync(
                    "Esperado \"void, String, bool, int, double, ID, ;\"; encontrado " + "\"" + self.token.getLexema() + "\"")
                return
            else:
                self.skip(
                    "Esperado \"void, String, bool, int, double, ID, ;\"; encontrado " + "\"" + self.token.getLexema() + "\"")
                if self.token.getNome() != Tag.EOF: self.DeclaraID()

    # ListaFuncao -> ListaFuncao'
    def ListaFuncao(self):
        if self.token.getNome() == Tag.KW_DEF:

            self.ListaFuncaoLinha()

        else:
            if self.token.getNome() == Tag.KW_DEFSTATIC:
                self.sync("Esperado \"def, defstatic\", encontrado " + "\"" + self.token.getLexema() + "\"")
                return
            else:
                self.skip("Esperado \"def, defstatic\", encontrado " + "\"" + self.token.getLexema() + "\"")
                if self.token.getNome() != Tag.EOF: self.ListaFuncao()

    # ListaFuncao' -> Funcao ListaFuncao'| ε
    def ListaFuncaoLinha(self):
        if self.token.getNome() == Tag.KW_DEF:

            self.Funcao()
            self.ListaFuncaoLinha()

        else:
            if self.token.getNome() == Tag.KW_DEFSTATIC:
                return
            else:
                self.skip("Esperado \"def\", encontrado " + "\"" + self.token.getLexema() + "\"")
                if self.token.getNome() != Tag.EOF: self.ListaFuncaoLinha()

    # Funcao -> "def" TipoPrimitivo ID "(" ListaArg ")" ":" RegexDeclaraId ListaCmd Retorno "end" ";"
    def Funcao(self):
        if self.eat(Tag.KW_DEF):

            self.TipoPrimitivo()

            if not self.eat(Tag.ID):
                self.sinalizaErroSintatico("Esperado \"ID\"; encontrado " + "\"" + self.token.getLexema() + "\"")
            if not self.eat(Tag.OP_APA):
                self.sinalizaErroSintatico("Esperado \"(\"; encontrado " + "\"" + self.token.getLexema() + "\"")

            self.ListaArg()

            if not self.eat(Tag.OP_FPA):
                self.sinalizaErroSintatico("Esperado \")\"; encontrado " + "\"" + self.token.getLexema() + "\"")
            if not self.eat(Tag.OP_DOIS_PONTOS):
                self.sinalizaErroSintatico("Esperado \":\"; encontrado " + "\"" + self.token.getLexema() + "\"")

            self.RegexDeclaraId()
            self.ListaCmd()
            self.Retorno()

            if not self.eat(Tag.KW_END):
                self.sinalizaErroSintatico("Esperado \"end\"; encontrado " + "\"" + self.token.getLexema() + "\"")
            if not self.eat(Tag.OP_PONTO_VIRGULA):
                self.sinalizaErroSintatico("Esperado \";\"; encontrado " + "\"" + self.token.getLexema() + "\"")
        else:
            if self.token.getNome() == Tag.KW_DEFSTATIC:
                self.sync("Esperado \"defstatic\"; encontrado " + "\"" + self.token.getLexema() + "\"")
                return
            else:
                self.skip("Esperado \"def, defstatic\"; encontrado " + "\"" + self.token.getLexema() + "\"")
                if self.token.getNome() != Tag.EOF: self.Funcao()

    # DeclaraID RegexDeclaraId | ε
    def RegexDeclaraId(self):
        if self.token.getNome() == Tag.KW_VOID or self.token.getNome() == Tag.KW_STRING or \
                self.token.getNome() == Tag.KW_BOOL or self.token.getNome() == Tag.KW_INTEGER or \
                self.token.getNome() == Tag.KW_DOUBLE:

            self.DeclaraID()
            self.RegexDeclaraId()

        else:
            if self.token.getNome() == Tag.ID or self.token.getNome() == Tag.KW_END or self.token.getNome() == Tag.KW_RETURN \
                or self.token.getNome() == Tag.KW_IF or self.token.getNome() == Tag.KW_WRITE or self.token.getNome() == Tag.KW_WHILE:
                return
            else:
                self.skip("Esperado \"String, double, void, bool, integer" + "\"" + self.token.getLexema() + "\"")
                if self.token.getNome() != Tag.EOF: self.RegexDeclaraId()

    # ListaArg -> Arf ListaArg'
    def ListaArg(self):
        if self.token.getNome() == Tag.KW_VOID or self.token.getNome() == Tag.KW_STRING or \
                self.token.getNome() == Tag.KW_BOOL or self.token.getNome() == Tag.KW_INTEGER or \
                self.token.getNome() == Tag.KW_DOUBLE:

            self.Arg()
            self.ListaArgLinha()

        else:
            if self.token.getNome() == Tag.OP_FPA:
                self.sync(
                    "Esperado \"void, String, bool, integer, double\", encontrado " + "\"" + self.token.getLexema() + "\"")
                return
            else:
                self.skip(
                    "Esperado \"void, String, bool, integer, double\", encontrado " + "\"" + self.token.getLexema() + "\"")
                if self.token.getNome() != Tag.EOF: self.ListaArg()

    # ListaArgLinha -> "," ListaArg | ε
    def ListaArgLinha(self):
        if self.eat(Tag.OP_VIRGULA):
            self.ListaArg()

        if self.token.getNome() == Tag.OP_FPA:
            return
        else:
            self.skip("Esperado \"',', )\", encontrado " + "\"" + self.token.getLexema() + "\"")
            if self.token.getNome() != Tag.EOF: self.ListaArgLinha()

    # Arg → TipoPrimitivo ID
    def Arg(self):
        if self.token.getNome() == Tag.KW_VOID or self.token.getNome() == Tag.KW_STRING or \
                self.token.getNome() == Tag.KW_BOOL or self.token.getNome() == Tag.KW_INTEGER or \
                self.token.getNome() == Tag.KW_DOUBLE:

            self.TipoPrimitivo()

            if not self.eat(Tag.ID):
                self.sinalizaErroSintatico("Esperado \"ID\"; encontrado " + "\"" + self.token.getLexema() + "\"")
        else:
            if self.token.getNome() == Tag.OP_FPA or self.token.getNome() == Tag.OP_VIRGULA:
                self.sync(
                    "Esperado \"void, String, bool, integer, double\", encontrado " + "\"" + self.token.getLexema() + "\"")
                return
            else:
                self.skip(
                    "Esperado \"void, String, bool, integer, double\", encontrado " + "\"" + self.token.getLexema() + "\"")
                if self.token.getNome() != Tag.EOF: self.Arg()


    # Retorno → "return" Expressao ";" | ε
    def Retorno(self):
        if self.eat(Tag.KW_RETURN):

            self.Expressao()

            if not self.eat(Tag.OP_PONTO_VIRGULA):
                self.sinalizaErroSintatico("Esperado \";\"; encontrado " + "\"" + self.token.getLexema() + "\"")
        else:
            if self.token.getNome() == Tag.KW_END:
                return
            else:
                self.skip(
                    "Esperado \"void, String, bool, integer, double\", encontrado " + "\"" + self.token.getLexema() + "\"")
                if self.token.getNome() != Tag.EOF: self.Retorno()

    # Main → "defstatic" "void" "main" "(" "String" "[" "]" ID ")" ":" RegexDeclaraId ListaCmd "end" ";"
    def Main(self):
        if self.eat(Tag.KW_DEFSTATIC):
            if not self.eat(Tag.KW_VOID):
                self.sinalizaErroSintatico("Esperado \"void\"; encontrado " + "\"" + self.token.getLexema() + "\"")
            if not self.eat(Tag.KW_MAIN):
                self.sinalizaErroSintatico("Esperado \"main\"; encontrado " + "\"" + self.token.getLexema() + "\"")
            if not self.eat(Tag.OP_APA):
                self.sinalizaErroSintatico("Esperado \"(\"; encontrado " + "\"" + self.token.getLexema() + "\"")
            if not self.eat(Tag.KW_STRING):
                self.sinalizaErroSintatico(
                    "Esperado \"String\"; encontrado " + "\"" + self.token.getLexema() + "\"")
            if not self.eat(Tag.OP_ACO):
                self.sinalizaErroSintatico("Esperado \"[\"; encontrado " + "\"" + self.token.getLexema() + "\"")
            if not self.eat(Tag.OP_FCO):
                self.sinalizaErroSintatico("Esperado \"]\"; encontrado " + "\"" + self.token.getLexema() + "\"")
            if not self.eat(Tag.ID):
                self.sinalizaErroSintatico("Esperado \"ID\"; encontrado " + "\"" + self.token.getLexema() + "\"")
            if not self.eat(Tag.OP_FPA):
                self.sinalizaErroSintatico("Esperado \")\"; encontrado " + "\"" + self.token.getLexema() + "\"")
            if not self.eat(Tag.OP_DOIS_PONTOS):
                self.sinalizaErroSintatico("Esperado \":\"; encontrado " + "\"" + self.token.getLexema() + "\"")

            self.RegexDeclaraId()
            self.ListaCmd()

            if not self.eat(Tag.KW_END):
                self.sinalizaErroSintatico("Esperado \"end\"; encontrado " + "\"" + self.token.getLexema() + "\"")
            if not self.eat(Tag.OP_PONTO_VIRGULA):
                self.sinalizaErroSintatico("Esperado \";\"; encontrado " + "\"" + self.token.getLexema() + "\"")
        elif self.token.getNome() == Tag.KW_END:
            self.sync("Esperado \"defstatic\", encontrado " + "\"" + self.token.getLexema() + "\"")
            return
        else:
            self.skip("Esperado \"defstatic\", encontrado " + "\"" + self.token.getLexema() + "\"")
            if self.token.getNome() != Tag.EOF: self.Main()

    # TipoPrimitivo → "bool" | "integer" | "String" | "double" | "void"
    def TipoPrimitivo(self):
        if not self.eat(Tag.KW_BOOL) and not self.eat(Tag.KW_INTEGER) and not self.eat(Tag.KW_STRING) and not self.eat(
                Tag.KW_DOUBLE) and not self.eat(Tag.KW_VOID):
            if self.token.getNome() == Tag.ID:
                self.sync("Esperado \"bool, integer, String, double, void\", encontrado " + "\"" + self.token.getLexema() + "\"")
                return
            else:
                self.skip(
                    "Esperado \"bool, integer, String, double, void\", encontrado " + "\"" + self.token.getLexema() + "\"")
                if self.token.getNome() != Tag.EOF: self.TipoPrimitivo()

    # ListaCmd → ListaCmd’
    def ListaCmd(self):
        if self.token.getNome() == Tag.ID or self.token.getNome() == Tag.KW_IF or self.token.getNome() == Tag.KW_WHILE \
                or self.token.getNome() == Tag.KW_WRITE or self.token.getNome() == Tag.KW_RETURN or self.token.getNome() == Tag.KW_END\
                or self.token.getNome() == Tag.KW_ELSE:

            self.ListaCmdLinha()
        else:
            self.skip("Esperado \"ID, if, while, write, return\", encontrado " + "\"" + self.token.getLexema() + "\"")
            if self.token.getNome() != Tag.EOF: self.ListaCmd()

    # ListaCmd’ →  Cmd ListaCmd’ 23 | ε
    def ListaCmdLinha(self):
        if self.token.getNome() == Tag.ID or self.token.getNome() == Tag.KW_IF or self.token.getNome() == Tag.KW_WHILE \
                or self.token.getNome() == Tag.KW_WRITE:
            self.Cmd()
            self.ListaCmdLinha()

        else:
            if self.token.getNome() == Tag.KW_RETURN or self.token.getNome() == Tag.KW_END or self.token.getNome() == Tag.KW_ELSE:
                return
            else:
                self.skip("Esperado \"ID, if, while, write, return, end, else\", encontrado " + "\"" + self.token.getLexema() + "\"")
                if self.token.getNome() != Tag.EOF: self.ListaCmdLinha()

    # Cmd → CmdIF | CmdWhile | ID CmdAtribFunc | CmdWrite
    def Cmd(self):
        if self.token.getNome() == Tag.KW_IF:
            self.CmdIF()
        elif self.token.getNome() == Tag.KW_WHILE:
            self.CmdWhile()
        elif self.token.getNome() == Tag.KW_WRITE:
            self.CmdWrite()
        elif self.eat(Tag.ID):
            self.CmdAtribFunc()
        else:
            if self.token.getNome() == Tag.KW_END or self.token.getNome() == Tag.KW_ELSE or self.token.getNome() == Tag.KW_RETURN:
                self.sync("Esperado \"if, while, id ou whrite\", encontrado " + "\"" + self.token.getLexema() + "\"")
                return
            else:
                self.skip("Esperado \"if, while, id ou whrite\", encontrado " + "\"" + self.token.getLexema() + "\"")
                if self.token.getNome() != Tag.EOF: self.Cmd()

    # CmdAtribFunc→ CmdAtribui | CmdFuncao
    def CmdAtribFunc(self):
        if self.token.getNome() == Tag.OP_UNARIO_IGUAL:
            self.CmdAtribui()
        elif self.token.getNome() == Tag.OP_APA:
            self.CmdFuncao()
        else:
            if self.token.getNome() == Tag.KW_WHILE or self.token.getNome() == Tag.KW_IF or self.token.getNome() == Tag.ID \
                    or self.token.getNome() == Tag.KW_RETURN or self.token.getNome() == Tag.KW_WRITE or \
                    self.token.getNome() == Tag.KW_END or self.token.getNome() == Tag.KW_ELSE:
                self.sync("Esperado \"(, =)\", encontrado " + "\"" + self.token.getLexema() + "\"")
                return
            else:
                self.sync("Esperado \"(, =)\", encontrado " + "\"" + self.token.getLexema() + "\"")
                if self.token.getNome() != Tag.EOF: self.CmdAtribFunc()

    # CmdIF → "if" "(" Expressao ")" ":" ListaCmd CmdIF’
    def CmdIF(self):
        if self.eat(Tag.KW_IF):
            if not self.eat(Tag.OP_APA):
                self.sinalizaErroSintatico("Esperado \"(\"; encontrado " + "\"" + self.token.getLexema() + "\"")

            self.Expressao()

            if not self.eat(Tag.OP_FPA):
                self.sinalizaErroSintatico("Esperado \")\"; encontrado " + "\"" + self.token.getLexema() + "\"")
            if not self.eat(Tag.OP_DOIS_PONTOS):
                self.sinalizaErroSintatico("Esperado \":\"; encontrado " + "\"" + self.token.getLexema() + "\"")

            self.ListaCmd()
            self.CmdIFLinha()

        else:
            if self.token.getNome() == Tag.KW_WHILE or self.token.getNome() == Tag.ID or self.token.getNome() == Tag.KW_WRITE \
                    or self.token.getNome() == Tag.KW_RETURN or self.token.getNome() == Tag.KW_ELSE \
                    or self.token.getNome() == Tag.KW_END:
                self.sync("Esperado \"if\"; encontrado " + "\"" + self.token.getLexema() + "\"")

                return
            else:
                self.skip("Esperado \"if\"; encontrado " + "\"" + self.token.getLexema() + "\"")
                if self.token.getNome() != Tag.EOF: self.CmdIF()


    # CmdIF’ → "end" ";"| "else" ":" ListaCmd "end" ";"
    def CmdIFLinha(self):
        if self.eat(Tag.KW_END):
            if not self.eat(Tag.OP_PONTO_VIRGULA):
                self.sinalizaErroSintatico("Esperado \";\"; encontrado " + "\"" + self.token.getLexema() + "\"")
        elif self.eat(Tag.KW_ELSE):
            if not self.eat(Tag.OP_DOIS_PONTOS):
                self.sinalizaErroSintatico("Esperado \":\"; encontrado " + "\"" + self.token.getLexema() + "\"")

            self.ListaCmd()

            if not self.eat(Tag.KW_END):
                self.sinalizaErroSintatico("Esperado \"end\"; encontrado " + "\"" + self.token.getLexema() + "\"")
            if not self.eat(Tag.OP_PONTO_VIRGULA):
                self.sinalizaErroSintatico("Esperado \";\"; encontrado " + "\"" + self.token.getLexema() + "\"")
        else:
            if self.token.getNome() == Tag.ID or self.token.getNome() == Tag.KW_RETURN or self.token.getNome() == Tag.KW_IF \
                    or self.token.getNome() == Tag.KW_WRITE or self.token.getNome() == Tag.KW_WHILE:
                self.sync("Esperado \"end, else\"; encontrado " + "\"" + self.token.getLexema() + "\"")

                return
            else:
                self.skip("Esperado \"end, else\"; encontrado " + "\"" + self.token.getLexema() + "\"")
                if self.token.getNome() != Tag.EOF: self.CmdIFLinha()

    # CmdWhile → "while" "(" Expressao ")" ":" ListaCmd "end" ";" 34
    def CmdWhile(self):
        if self.eat(Tag.KW_WHILE):
            if not self.eat(Tag.OP_APA):
                self.sinalizaErroSintatico("Esperado \"(\"; encontrado " + "\"" + self.token.getLexema() + "\"")

            self.Expressao()

            if not self.eat(Tag.OP_FPA):
                self.sinalizaErroSintatico("Esperado \")\"; encontrado " + "\"" + self.token.getLexema() + "\"")
            if not self.eat(Tag.OP_DOIS_PONTOS):
                self.sinalizaErroSintatico("Esperado \":\"; encontrado " + "\"" + self.token.getLexema() + "\"")

            self.ListaCmd()

            if not self.eat(Tag.KW_END):
                self.sinalizaErroSintatico("Esperado \"end\"; encontrado " + "\"" + self.token.getLexema() + "\"")
            if not self.eat(Tag.OP_PONTO_VIRGULA):
                self.sinalizaErroSintatico("Esperado \";\"; encontrado " + "\"" + self.token.getLexema() + "\"")
        else:
            if self.token.getNome() == Tag.KW_IF or self.token.getNome() == Tag.ID or self.token.getNome() == Tag.KW_WRITE \
                    or self.token.getNome() == Tag.KW_RETURN or self.token.getNome() == Tag.KW_ELSE or \
                    self.token.getNome() == Tag.KW_END:
                self.sync("Esperado \"while\"; encontrado " + "\"" + self.token.getLexema() + "\"")

                return
            else:
                self.skip("Esperado \"while\"; encontrado " + "\"" + self.token.getLexema() + "\"")
                if self.token.getNome() != Tag.EOF: self.CmdWhile()


    # CmdWrite → "write" "(" Expressao ")" ";"
    def CmdWrite(self):
        if self.eat(Tag.KW_WRITE):
            if not self.eat(Tag.OP_APA):
                self.sinalizaErroSintatico("Esperado \"(\"; encontrado " + "\"" + self.token.getLexema() + "\"")

            self.Expressao()

            if not self.eat(Tag.OP_FPA):
                self.sinalizaErroSintatico("Esperado \")\"; encontrado " + "\"" + self.token.getLexema() + "\"")
            if not self.eat(Tag.OP_PONTO_VIRGULA):
                self.sinalizaErroSintatico("Esperado \";\"; encontrado " + "\"" + self.token.getLexema() + "\"")
        else:
            if self.token.getNome() == Tag.KW_WHILE or self.token.getNome() == Tag.ID or self.token.getNome() == Tag.KW_RETURN or \
                    self.token.getNome() == Tag.KW_IF or self.token.getNome() == Tag.KW_END or self.token.getNome() == Tag.KW_ELSE:
                self.sync("Esperado \"write\"; encontrado " + "\"" + self.token.getLexema() + "\"")

                return
            else:
                self.skip("Esperado \"write\"; encontrado " + "\"" + self.token.getLexema() + "\"")
                if self.token.getNome() != Tag.EOF: self.CmdWrite()

    # CmdAtribui → "=" Expressao ";"
    def CmdAtribui(self):
        if self.eat(Tag.OP_UNARIO_IGUAL):

            self.Expressao()

            if not self.eat(Tag.OP_PONTO_VIRGULA):
                self.sinalizaErroSintatico("Esperado \";\"; encontrado " + "\"" + self.token.getLexema() + "\"")
        else:
            if self.token.getNome() == Tag.KW_WHILE or self.token.getNome() == Tag.ID or self.token.getNome() == Tag.KW_RETURN or \
                    self.token.getNome() == Tag.KW_IF or self.token.getNome() == Tag.KW_END or self.token.getNome() == Tag.KW_WRITE:
                self.sync("Esperado \"=\"; encontrado " + "\"" + self.token.getLexema() + "\"")

                return
            else:
                self.skip("Esperado \"=\"; encontrado " + "\"" + self.token.getLexema() + "\"")
                if self.token.getNome() != Tag.EOF: self.CmdWrite()


    # CmdFuncao → "(" RegexExp ")" ";"
    def CmdFuncao(self):
        if self.eat(Tag.OP_APA):

            self.RegexExp()

            if not self.eat(Tag.OP_FPA):
                self.sinalizaErroSintatico("Esperado \")\"; encontrado " + "\"" + self.token.getLexema() + "\"")
            if not self.eat(Tag.OP_PONTO_VIRGULA):
                self.sinalizaErroSintatico("Esperado \";\"; encontrado " + "\"" + self.token.getLexema() + "\"")
        else:
            if self.token.getNome() == Tag.KW_WHILE or self.token.getNome() == Tag.ID or self.token.getNome() == Tag.KW_RETURN or \
                    self.token.getNome() == Tag.KW_IF or self.token.getNome() == Tag.KW_END or self.token.getNome() == Tag.KW_WRITE \
                    or self.token.getNome() == Tag.KW_ELSE:
                self.sync("Esperado \"(\"; encontrado " + "\"" + self.token.getLexema() + "\"")

                return
            else:
                self.skip("Esperado \"(\"; encontrado " + "\"" + self.token.getLexema() + "\"")
                if self.token.getNome() != Tag.EOF: self.CmdFuncao()


    # RegexExp → Expressao RegexExp’ | ε
    def RegexExp(self):
        if self.token.getNome() == Tag.ID or self.token.getNome() == Tag.OP_APA or self.token.getNome() == Tag.NUM_INTEIRO \
                or self.token.getNome() == Tag.NUM_DOUBLE or self.token.getNome() == Tag.LIT or self.token.getNome() == Tag.KW_TRUE \
                or self.token.getNome() == Tag.KW_FALSE or self.token.getNome() == Tag.OP_NEGACAO or self.token.getNome() == Tag.OP_UNARIO_DIFERENTE:
            self.Expressao()
            self.RegexExpLinha()
        else:
            if self.token.getNome() == Tag.OP_FPA:
                return
            else:
                self.skip(
                    "Esperado \"(, ID, ConstInteger, ConstDouble, String, true, false, !, -n\", encontrado " + "\"" + self.token.getLexema() + "\"")
                if self.token.getNome() != Tag.EOF: self.RegexExp()


    # RegexExp’ → , Expressao RegexExp’ | ε
    def RegexExpLinha(self):
        if self.eat(Tag.OP_VIRGULA):
            self.Expressao()
            self.RegexExpLinha()
        else:
            if self.token.getNome() == Tag.OP_FPA:
                return
            else:
                self.skip("Esperado \"), ','\"; encontrado " + "\"" + self.token.getLexema() + "\"")
                if self.token.getNome() != Tag.EOF: self.RegexExpLinha()

    # Expressao → Exp1 Exp’
    def Expressao(self):
        if self.token.getNome() == Tag.ID or self.token.getNome() == Tag.NUM_INTEIRO or self.token.getNome() == Tag.NUM_DOUBLE \
                or self.token.getNome() == Tag.LIT or self.token.getNome() == Tag.KW_TRUE or self.token.getNome() == Tag.KW_FALSE or \
                self.token.getNome() == Tag.OP_APA or self.token.getNome() == Tag.OP_NEGACAO or self.token.getNome() == Tag.OP_UNARIO_DIFERENTE:
            self.Exp1()
            self.ExpLinha()
        else:
            if self.token.getNome() == Tag.OP_FPA or self.token.getNome() == Tag.OP_PONTO_VIRGULA or self.token.getNome() == Tag.OP_VIRGULA:
                self.sync(
                    "Esperado \"ID, integer, double, String, true, false, !, -, (\", encontrado " + "\"" + self.token.getLexema() + "\"")
                return
            else:
                self.skip(
                    "Esperado \"ID, integer, double, String, true, false, !, -, (\", encontrado " + "\"" + self.token.getLexema() + "\"")
                if self.token.getNome() != Tag.EOF: self.Expressao()

    # Exp’ → "or" Exp1 Exp’ | "and" Exp1 Exp’ | ε
    def ExpLinha(self):
        if self.eat(Tag.KW_OR) or self.eat(Tag.KW_AND):
            self.Exp1()
            self.ExpLinha()
            return
        else:
            if self.token.getNome() == Tag.OP_FPA or self.token.getNome() == Tag.OP_PONTO_VIRGULA or self.token.getNome() == Tag.OP_VIRGULA:
                return
            else:
                self.skip("Esperado \"or, and'\", encontrado " + "\"" + self.token.getLexema() + "\"")
                if self.token.getNome() != Tag.EOF: self.ExpLinha()

    # Exp1 → Exp2 Exp1’
    def Exp1(self):
        if self.token.getNome() == Tag.ID or self.token.getNome() == Tag.OP_APA or self.token.getNome() == Tag.NUM_INTEIRO \
                or self.token.getNome() == Tag.NUM_DOUBLE or self.token.getNome() == Tag.LIT or self.token.getNome() == Tag.KW_TRUE \
                or self.token.getNome() == Tag.KW_FALSE or self.token.getNome() == Tag.OP_UNARIO_DIFERENTE or self.token.getNome() == Tag.OP_NEGACAO:
            self.Exp2()
            self.Exp1Linha()
        else:
            if self.token.getNome() == Tag.KW_OR or self.token.getNome() == Tag.OP_FPA or self.token.getNome() == Tag.KW_AND or \
                    self.token.getNome() == Tag.OP_PONTO_VIRGULA or self.token.getNome() == Tag.OP_VIRGULA:
                self.sync(
                    "Esperado \"ID, constInt, constDouble, constStr, true, false, - , !, (\", encontrado " + "\"" + self.token.getLexema() + "\"")
                return
            else:
                self.skip(
                    "Esperado \"ID, constInt, constDouble, constStr, true, false, - , !, (\", encontrado " + "\"" + self.token.getLexema() + "\"")
                if self.token.getNome() != Tag.EOF: self.Exp1()

    #  Exp1’ → "<" Exp2 Exp1’  | "<=" Exp2 Exp1’  | ">" Exp2 Exp1’  | ">=" Exp2 Exp1’
    #  50 | "==" Exp2 Exp1’  | "!=" Exp2 Exp1’   | ε
    def Exp1Linha(self):
        if self.eat(Tag.OP_MENOR) or self.eat(Tag.OP_MENOR_IGUAL) or self.eat(Tag.OP_MAIOR) or self.eat(
                Tag.OP_MAIOR_IGUAL) or self.eat(Tag.OP_IGUAL_IGUAL) or self.eat(Tag.OP_DIFERENTE):
            self.Exp2()
            self.Exp1Linha()
        else:
            if self.token.getNome() == Tag.KW_OR or not self.token.getNome() == Tag.KW_AND or not self.token.getNome() == \
                 Tag.OP_FPA or not self.token.getNome() == Tag.OP_PONTO_VIRGULA or not self.token.getNome() == Tag.OP_VIRGULA:
                return
            else:
                self.skip(
                    "Esperado \"<, <=, >, >=, ',', or, and, ==, !=\"; encontrado " + "\"" + self.token.getLexema() + "\"")
                if self.token.getNome() != Tag.EOF: self.Exp1Linha()

    # Exp2 → Exp3 Exp2’
    def Exp2(self):
        if self.token.getNome() == Tag.ID or self.token.getNome() == Tag.OP_APA or self.token.getNome() == Tag.NUM_INTEIRO \
                or self.token.getNome() == Tag.NUM_DOUBLE or self.token.getNome() == Tag.LIT or self.token.getNome() == Tag.KW_TRUE \
                or self.token.getNome() == Tag.KW_FALSE or self.token.getNome() == Tag.OP_UNARIO_DIFERENTE or self.token.getNome() == Tag.OP_NEGACAO:
            self.Exp3()
            self.Exp2Linha()
        else:
            if self.token.getNome() == Tag.OP_MENOR or self.token.getNome() == Tag.OP_MENOR_IGUAL or self.token.getNome() == Tag.OP_MAIOR \
                    or self.token.getNome() == Tag.OP_MAIOR_IGUAL or self.token.getNome() == Tag.OP_IGUAL_IGUAL or \
                    self.token.getNome() == Tag.OP_DIFERENTE or self.token.getNome() == Tag.KW_OR or self.token.getNome() == Tag.KW_AND \
                    or self.token.getNome() == Tag.OP_FPA or self.token.getNome() == Tag.OP_DOIS_PONTOS or self.token.getNome() == Tag.OP_VIRGULA:
                self.sync(
                    "Esperado \"ID, constInt, constDouble, constStr, true, false, - , !\", encontrado " + "\"" + self.token.getLexema() + "\"")
                return

            else:
                self.skip(
                    "Esperado \"ID, constInt, constDouble, constStr, true, false, - , !\", encontrado " + "\"" + self.token.getLexema() + "\"")
                if self.token.getNome() != Tag.EOF: self.Exp2()

    # Exp2’ → "+" Exp3 Exp2’ | "-" Exp3 Exp2’ | ε
    def Exp2Linha(self):
        if self.eat(Tag.OP_ADICAO) or self.eat(Tag.OP_SUBTRACAO):
            self.Exp3()
            self.Exp2Linha()
        else:
            if self.token.getNome() == Tag.OP_MAIOR or self.token.getNome() == Tag.OP_MAIOR_IGUAL or \
                    self.token.getNome() == Tag.OP_MENOR or self.token.getNome() == Tag.OP_MENOR_IGUAL or \
                    self.token.getNome() == Tag.OP_IGUAL_IGUAL or self.token.getNome() == Tag.OP_DIFERENTE or \
                    self.token.getNome() == Tag.KW_OR or self.token.getNome() == Tag.KW_AND or self.token.getNome() == Tag.OP_FPA \
                    or self.token.getNome() == Tag.OP_PONTO_VIRGULA or self.token.getNome() == Tag.OP_VIRGULA:
                return
            else:
                self.skip(
                    "Esperado \"+, -, ;, ), ',', or, and, <, <=, >, >=, ==, !=\", encontrado " + "\"" + self.token.getLexema() + "\"")
                if self.token.getNome() != Tag.EOF: self.Exp2Linha()

    # Exp3 → Exp4 Exp3’
    def Exp3(self):
        if self.token.getNome() == Tag.ID or self.token.getNome() == Tag.OP_APA or self.token.getNome() == Tag.NUM_INTEIRO \
                or self.token.getNome() == Tag.NUM_DOUBLE or self.token.getNome() == Tag.LIT or self.token.getNome() == Tag.KW_TRUE \
                or self.token.getNome() == Tag.KW_FALSE or self.token.getNome() == Tag.OP_UNARIO_DIFERENTE or self.token.getNome() == Tag.OP_NEGACAO:
            self.Exp4()
            self.Exp3Linha()
        else:
            if self.token.getNome() == Tag.OP_ADICAO or self.token.getNome() == Tag.OP_SUBTRACAO or self.token.getNome() == Tag.OP_MENOR \
                    or self.token.getNome() == Tag.OP_MENOR_IGUAL or self.token.getNome() == Tag.OP_MAIOR or self.token.getNome() == Tag.OP_MAIOR_IGUAL \
                    or self.token.getNome() == Tag.OP_IGUAL_IGUAL or self.token.getNome() == Tag.OP_DIFERENTE or self.token.getNome() == Tag.KW_OR \
                    or self.token.getNome() == Tag.KW_AND or self.token.getNome() == Tag.OP_FPA or self.token.getNome() == Tag.OP_PONTO_VIRGULA \
                    or self.token.getNome() == Tag.OP_VIRGULA:

                self.sync(
                    "Esperado \"ID, (, constInt, constDouble, String, true, false, !, -n\", encontrado " + "\"" + self.token.getLexema() + "\"")
                return

            else:
                self.skip(
                    "Esperado \"ID, (, constInt, constDouble, String, true, false, !, -n\", encontrado " + "\"" + self.token.getLexema() + "\"")
                if self.token.getNome() != Tag.EOF: self.Exp3()

    # Exp3’ → "*" Exp4 Exp3’ | "/" Exp4 Exp3’ | ε
    def Exp3Linha(self):
        if self.eat(Tag.OP_MULTIPLICACAO) or self.eat(Tag.OP_DIVISAO):
            self.Exp4()
            self.Exp3Linha()
            return
        else:
            if self.token.getNome() == Tag.OP_SUBTRACAO or self.token.getNome() == Tag.OP_ADICAO or \
                    self.token.getNome() == Tag.OP_MAIOR or self.token.getNome() == Tag.OP_MAIOR_IGUAL or \
                    self.token.getNome() == Tag.OP_MENOR or self.token.getNome() == Tag.OP_MENOR_IGUAL or \
                    self.token.getNome() == Tag.OP_IGUAL_IGUAL or self.token.getNome() == Tag.OP_DIFERENTE \
                    or self.token.getNome() == Tag.KW_OR or self.token.getNome() == Tag.KW_AND or \
                    self.token.getNome() == Tag.OP_FPA or self.token.getNome() == Tag.OP_PONTO_VIRGULA or \
                    self.token.getNome() == Tag.OP_VIRGULA:
                return
            else:
                self.skip(
                    "Esperado \"/,*\", encontrado " + "\"" + self.token.getLexema() + "\"")
                if self.token.getNome() != Tag.EOF: self.Exp3Linha()

    # Exp4 → ID Exp4’ | ConstInteger | ConstDouble | ConstString | "true" | "false" | OpUnario Exp4 | "(" Expressao")"
    def Exp4(self):
        if self.eat(Tag.ID):
            self.Exp4Linha()
        elif self.eat(Tag.OP_NEGACAO) or self.eat(Tag.OP_DIFERENTE):
            self.OpUnario()
            self.Exp4()
        elif self.eat(Tag.OP_APA):
            self.Expressao()
            if not self.eat(Tag.OP_FPA):
                self.sinalizaErroSintatico("Esperado \")\"; encontrado " + "\"" + self.token.getLexema() + "\"")
        elif not self.eat(Tag.NUM_INTEIRO) and not self.eat(Tag.LIT) and not self.eat(Tag.NUM_DOUBLE) and not self.eat(
                Tag.KW_TRUE) and not self.eat(Tag.KW_FALSE):
            if self.token.getNome() == Tag.OP_MULTIPLICACAO or self.token.getNome() == Tag.OP_DIVISAO or \
                    self.token.getNome() == Tag.OP_ADICAO or self.token.getNome() == Tag.OP_SUBTRACAO or \
                    self.token.getNome() == Tag.OP_MENOR or self.token.getNome() == Tag.OP_MENOR_IGUAL or \
                    self.token.getNome() == Tag.OP_MAIOR or self.token.getNome() == Tag.OP_MAIOR_IGUAL or \
                    self.token.getNome() == Tag.OP_IGUAL_IGUAL or self.token.getNome() == Tag.OP_DIFERENTE or \
                    self.token.getNome() == Tag.KW_OR or self.token.getNome() == Tag.KW_AND or\
                    self.token.getNome() == Tag.OP_FPA or self.token.getNome() == Tag.OP_PONTO_VIRGULA or \
                    self.token.getNome() == Tag.OP_VIRGULA:
                self.sync("Esperado \"ID, constInt, constDouble, String, true, false, !, -n, (\"; encontrado " + "\"" + self.token.getLexema() + "\"")
                return
            else:
                self.skip("Esperado \"ID, constInt, constDouble, String, true, false, !, -n, (\"; encontrado " + "\"" + self.token.getLexema() + "\"")
                if self.token.getNome() != Tag.EOF: self.Exp4()

    # Exp4’ → "(" RegexExp ")" | ε
    def Exp4Linha(self):
        if self.eat(Tag.OP_APA):
            self.RegexExp()
            if not self.eat(Tag.OP_FPA):
                self.sinalizaErroSintatico("Esperado \")\"; encontrado " + "\"" + self.token.getLexema() + "\"")
        else:
            if self.token.getNome() == Tag.OP_MULTIPLICACAO or self.token.getNome() == Tag.OP_DIVISAO or \
                    self.token.getNome() == Tag.OP_SUBTRACAO or self.token.getNome() == Tag.OP_ADICAO or \
                    self.token.getNome() == Tag.OP_MAIOR or self.token.getNome() == Tag.OP_MAIOR_IGUAL or \
                    self.token.getNome() == Tag.OP_MENOR or self.token.getNome() == Tag.OP_MENOR_IGUAL or \
                    self.token.getNome() == Tag.OP_IGUAL_IGUAL or self.token.getNome() == Tag.OP_DIFERENTE or\
                    self.token.getNome() == Tag.KW_OR or self.token.getNome() == Tag.KW_AND or \
                    self.token.getNome() == Tag.OP_FPA or self.token.getNome() == Tag.OP_PONTO_VIRGULA \
                    or self.token.getNome() == Tag.OP_VIRGULA:
                return
            else:
                self.skip("Esperado \";, ), ',', or, and, <, <=, >, >=, ==, !=, + , -, *, /\", encontrado " + "\"" + self.token.getLexema() + "\"")
                if self.token.getNome() != Tag.EOF: self.Exp4Linha()

    # OpUnario → "-" | "!"
    def OpUnario(self):
        if not self.eat(Tag.OP_NEGACAO) and not self.eat(Tag.OP_UNARIO_DIFERENTE):
            if self.token.getNome() == Tag.ID or self.token.getNome() == Tag.NUM_INTEIRO or self.token.getNome() == Tag.NUM_DOUBLE or self.token.getNome() == Tag.LIT or \
            self.token.getNome() == Tag.KW_TRUE or self.token.getNome() == Tag.KW_FALSE or self.token.getNome() == Tag.OP_NEGACAO or self.token.getNome() == Tag.OP_UNARIO_DIFERENTE or\
            self.token.getNome() == Tag.OP_APA:
                self.sync("Esperado \"-n, !\", encontrado " + "\"" + self.token.getLexema() + "\"")
                return
            else:
                self.skip("Esperado \"-n, !\", encontrado " + "\"" + self.token.getLexema() + "\"")
                if self.token.getNome() != Tag.EOF: self.OpUnario()
