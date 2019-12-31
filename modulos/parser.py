import copy
import sys
from modulos.no import No
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

    def sinalizaErroSemantico(self, message):
        print("[Erro Semantico] na linha " + str(self.token.getLinha()) + " e coluna " + str(
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

    # Programa -> Classe EOF
    def Programa(self):
        self.Classe()

        if self.token.getNome() != Tag.EOF:
            self.sinalizaErroSintatico("Esperado \"EOF\"; encontrado " + "\"" + self.token.getLexema() + "\"")

    # Classe -> "class" ID ":" ListaFuncao Main "end" "."
    def Classe(self):
        if self.eat(Tag.KW_CLASS):

            tempToken = copy.copy(self.token)

            if not self.eat(Tag.ID):
                self.sinalizaErroSintatico("Esperado \"ID\"; encontrado " + "\"" + self.token.getLexema() + "\"")

            self.lexer.ts.addToken(tempToken.getLexema(), Tag.TIPO_VAZIO)

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

            noTipoPrimitivo = self.TipoPrimitivo()

            tempToken = copy.copy(self.token)
            if not self.eat(Tag.ID):
                self.sinalizaErroSintatico("Esperado \"ID\"; encontrado " + "\"" + self.token.getLexema() + "\"")

            self.lexer.ts.addToken(tempToken.getLexema(), noTipoPrimitivo.tipo)

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

            noTipoPrimitivo = self.TipoPrimitivo()

            tempToken = copy.copy(self.token)

            if not self.eat(Tag.ID):
                self.sinalizaErroSintatico("Esperado \"ID\"; encontrado " + "\"" + self.token.getLexema() + "\"")

            self.lexer.ts.addToken(tempToken.getLexema(), noTipoPrimitivo.tipo)

            if not self.eat(Tag.OP_APA):
                self.sinalizaErroSintatico("Esperado \"(\"; encontrado " + "\"" + self.token.getLexema() + "\"")

            self.ListaArg()

            if not self.eat(Tag.OP_FPA):
                self.sinalizaErroSintatico("Esperado \")\"; encontrado " + "\"" + self.token.getLexema() + "\"")
            if not self.eat(Tag.OP_DOIS_PONTOS):
                self.sinalizaErroSintatico("Esperado \":\"; encontrado " + "\"" + self.token.getLexema() + "\"")

            self.RegexDeclaraId()
            self.ListaCmd()

            noRetorno = self.Retorno()

            if noRetorno.tipo != noTipoPrimitivo.tipo:
                self.sinalizaErroSemantico("Tipo de retorno incompativo")

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
            if self.token.getNome() in (Tag.ID, Tag.KW_END, Tag.KW_RETURN, Tag.KW_IF, Tag.KW_WRITE, Tag.KW_WHILE):
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

            noTipoPrimitivo = self.TipoPrimitivo()

            tempToken = copy.copy(self.token)

            if not self.eat(Tag.ID):
                self.sinalizaErroSintatico("Esperado \"ID\"; encontrado " + "\"" + self.token.getLexema() + "\"")

            self.lexer.ts.addToken(tempToken.getLexema(), noTipoPrimitivo.tipo)

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

        noRetorno = No()

        if self.eat(Tag.KW_RETURN):

            noExpressao = self.Expressao()

            if not self.eat(Tag.OP_PONTO_VIRGULA):
                self.sinalizaErroSintatico("Esperado \";\"; encontrado " + "\"" + self.token.getLexema() + "\"")

            noRetorno.tipo = noExpressao.tipo

            return noRetorno

        else:
            if self.token.getNome() == Tag.KW_END:
                return noRetorno
            else:
                self.skip(
                    "Esperado \"void, String, bool, integer, double\", encontrado " + "\"" + self.token.getLexema() + "\"")
                if self.token.getNome() != Tag.EOF: self.Retorno()

            return noRetorno

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

            tempToken = copy.copy(self.token)

            if not self.eat(Tag.ID):
                self.sinalizaErroSintatico("Esperado \"ID\"; encontrado " + "\"" + self.token.getLexema() + "\"")

            self.lexer.ts.addToken(tempToken.getLexema(), Tag.KW_STRING)

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
        noTipoPrimitivo = No()

        if self.eat(Tag.KW_BOOL):
            noTipoPrimitivo.tipo = Tag.TIPO_LOGICO
            return noTipoPrimitivo
        elif self.eat(Tag.KW_INTEGER):
            noTipoPrimitivo.tipo = Tag.TIPO_LOGICO
            return noTipoPrimitivo
        elif self.eat(Tag.KW_STRING):
            noTipoPrimitivo.tipo = Tag.TIPO_LOGICO
            return noTipoPrimitivo
        elif self.eat(Tag.KW_DOUBLE):
            noTipoPrimitivo.tipo = Tag.TIPO_LOGICO
            return noTipoPrimitivo
        elif self.eat(Tag.KW_VOID):
            noTipoPrimitivo.tipo = Tag.TIPO_LOGICO
            return noTipoPrimitivo

        if self.token.getNome() == Tag.ID:
            self.sync("Esperado \"bool, integer, String, double, void\", encontrado " + "\"" + self.token.getLexema() + "\"")
            return
        else:
             self.skip(
                "Esperado \"bool, integer, String, double, void\", encontrado " + "\"" + self.token.getLexema() + "\"")
             if self.token.getNome() != Tag.EOF: self.TipoPrimitivo()
             return noTipoPrimitivo

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
        tempToken = copy.copy(self.token)

        if self.token.getNome() == Tag.KW_IF:
            self.CmdIF()
        elif self.token.getNome() == Tag.KW_WHILE:
            self.CmdWhile()
        elif self.token.getNome() == Tag.KW_WRITE:
            self.CmdWrite()
        elif self.eat(Tag.ID):
            if self.lexer.ts.getToken(tempToken.getLexema() == None):
                self.sinalizaErroSemantico("ID não declarado")

            noCmdAtribFunc = self.CmdAtribFunc()

            if noCmdAtribFunc.tipo != Tag.TIPO_VAZIO and self.lexer.ts.getToken(tempToken.getLexema() != noCmdAtribFunc.tipo):
                self.sinalizaErroSemantico("Atribuição incompatível")

        else:
            if self.token.getNome() == Tag.KW_END or self.token.getNome() == Tag.KW_ELSE or self.token.getNome() == Tag.KW_RETURN:
                self.sync("Esperado \"if, while, id ou whrite\", encontrado " + "\"" + self.token.getLexema() + "\"")
                return
            else:
                self.skip("Esperado \"if, while, id ou whrite\", encontrado " + "\"" + self.token.getLexema() + "\"")
                if self.token.getNome() != Tag.EOF: self.Cmd()

    # CmdAtribFunc→ CmdAtribui | CmdFuncao
    def CmdAtribFunc(self):

        noCmdAtribFunc = No()

        if self.token.getNome() == Tag.OP_UNARIO_IGUAL:
            noCmdAtribui = self.CmdAtribui()
            noCmdAtribFunc.tipo = (noCmdAtribFunc.tipo)
            return noCmdAtribFunc

        elif self.token.getNome() == Tag.OP_APA:
            self.CmdFuncao()
            self.noCmdAtribFun.tipo = (Tag.TIPO_VAZIO)
            return noCmdAtribFunc

        else:
            if self.token.getNome() == Tag.KW_WHILE or self.token.getNome() == Tag.KW_IF or self.token.getNome() == Tag.ID \
                    or self.token.getNome() == Tag.KW_RETURN or self.token.getNome() == Tag.KW_WRITE or \
                    self.token.getNome() == Tag.KW_END or self.token.getNome() == Tag.KW_ELSE:
                self.sync("Esperado \"(, =)\", encontrado " + "\"" + self.token.getLexema() + "\"")
                return noCmdAtribFunc
            else:
                self.sync("Esperado \"(, =)\", encontrado " + "\"" + self.token.getLexema() + "\"")
                if self.token.getNome() != Tag.EOF: self.CmdAtribFunc()

    # CmdIF → "if" "(" Expressao ")" ":" ListaCmd CmdIF’
    def CmdIF(self):
        if self.eat(Tag.KW_IF):
            if not self.eat(Tag.OP_APA):
                self.sinalizaErroSintatico("Esperado \"(\"; encontrado " + "\"" + self.token.getLexema() + "\"")

            noExpressao = self.Expressao()

            if not self.eat(Tag.OP_FPA):
                self.sinalizaErroSintatico("Esperado \")\"; encontrado " + "\"" + self.token.getLexema() + "\"")

            if noExpressao.tipo != Tag.TIPO_LOGICO:
                self.sinalizaErroSemantico("Tipo esperado: lógico")

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

            noExpressao = self.Expressao()

            if not self.eat(Tag.OP_FPA):
                self.sinalizaErroSintatico("Esperado \")\"; encontrado " + "\"" + self.token.getLexema() + "\"")

            if noExpressao.tipo != Tag.TIPO_LOGICO:
                self.sinalizaErroSemantico("Tipo esperado: Logico")

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

            noExpressao = self.Expressao()

            if noExpressao.tipo != Tag.TIPO_LOGICO:
                self.sinalizaErroSemantico("Tipo lógico esperado.")

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
        noCmdAtribui = No()

        if self.eat(Tag.OP_UNARIO_IGUAL):

            noExpressao = self.Expressao()

            if not self.eat(Tag.OP_PONTO_VIRGULA):
                self.sinalizaErroSintatico("Esperado \";\"; encontrado " + "\"" + self.token.getLexema() + "\"")

            noCmdAtribui.tipo = (noExpressao.tipo)

            return noCmdAtribui
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
        noExpressao = No()

        if self.token.getNome() == Tag.ID or self.token.getNome() == Tag.NUM_INTEIRO or self.token.getNome() == Tag.NUM_DOUBLE \
                or self.token.getNome() == Tag.LIT or self.token.getNome() == Tag.KW_TRUE or self.token.getNome() == Tag.KW_FALSE or \
                self.token.getNome() == Tag.OP_APA or self.token.getNome() == Tag.OP_NEGACAO or self.token.getNome() == Tag.OP_UNARIO_DIFERENTE:

            noExp1 = self.Exp1()
            noExpLinha = self.ExpLinha()


            if noExpLinha.tipo == Tag.TIPO_VAZIO:
                noExpressao.tipo = noExp1.tipo
            elif noExpLinha.tipo == noExp1.tipo and noExpLinha.tipo == Tag.TIPO_LOGICO:
                noExpressao.tipo = Tag.TIPO_LOGICO
            else:
                noExpressao.tipo = Tag.TIPO_ERRO
            return noExpressao
        else:
            noExpressao.tipo = Tag.TIPO_VAZIO
            if self.token.getNome() == Tag.OP_FPA or self.token.getNome() == Tag.OP_PONTO_VIRGULA or self.token.getNome() == Tag.OP_VIRGULA:
                self.sync(
                    "Esperado \"ID, integer, double, String, true, false, !, -, (\", encontrado " + "\"" + self.token.getLexema() + "\"")
                return noExpressao
            else:
                self.skip(
                    "Esperado \"ID, integer, double, String, true, false, !, -, (\", encontrado " + "\"" + self.token.getLexema() + "\"")
                if self.token.getNome() != Tag.EOF: self.Expressao()
                return noExpressao

    # Exp’ → "or" Exp1 Exp’ | "and" Exp1 Exp’ | ε
    def ExpLinha(self):
        noExpLinha = No()

        if self.eat(Tag.KW_OR) or self.eat(Tag.KW_AND):
            noExp1 = self.Exp1()
            noExpLinha_ = self.ExpLinha()

            if noExpLinha.tipo == Tag.TIPO_VAZIO and noExp1.tipo == Tag.TIPO_LOGICO:
                noExpLinha.tipo = (Tag.TIPO_LOGICO)
            elif noExpLinha_.tipo == noExp1.tipo and noExp1.tipo == Tag.TIPO_LOGICO:
                noExpLinha.tipo = (Tag.TIPO_LOGICO)
            else:
                noExpLinha.tipo = (Tag.TIPO_ERRO)
            return noExpLinha
        else:
            if self.token.getNome() == Tag.OP_FPA or self.token.getNome() == Tag.OP_PONTO_VIRGULA or self.token.getNome() == Tag.OP_VIRGULA:
                return noExpLinha
            else:
                self.skip("Esperado \"or, and'\", encontrado " + "\"" + self.token.getLexema() + "\"")
                if self.token.getNome() != Tag.EOF: self.ExpLinha()

    # Exp1 → Exp2 Exp1’
    def Exp1(self):

        noExp1 = No()

        if self.token.getNome() == Tag.ID or self.token.getNome() == Tag.OP_APA or self.token.getNome() == Tag.NUM_INTEIRO \
                or self.token.getNome() == Tag.NUM_DOUBLE or self.token.getNome() == Tag.LIT or self.token.getNome() == Tag.KW_TRUE \
                or self.token.getNome() == Tag.KW_FALSE or self.token.getNome() == Tag.OP_UNARIO_DIFERENTE or self.token.getNome() == Tag.OP_NEGACAO:

            noExp2 = self.Exp2()
            noExp1Linha = self.Exp1Linha()

            if noExp1Linha == Tag.TIPO_VAZIO:
                noExp1.tipo = noExp2.tipo
            elif noExp1Linha.tipo == noExp2.tipo and noExp1Linha.tipo == Tag.TIPO_NUMERICO:
                noExp1.tipo = (Tag.TIPO_LOGICO)
            else:
                noExp1.tipo = (Tag.TIPO_ERRO)
            return noExp1
        else:
            if self.token.getNome() == Tag.KW_OR or self.token.getNome() == Tag.OP_FPA or self.token.getNome() == Tag.KW_AND or \
                    self.token.getNome() == Tag.OP_PONTO_VIRGULA or self.token.getNome() == Tag.OP_VIRGULA:
                self.sync(
                    "Esperado \"ID, constInt, constDouble, constStr, true, false, - , !, (\", encontrado " + "\"" + self.token.getLexema() + "\"")
                return noExp1
            else:
                self.skip(
                    "Esperado \"ID, constInt, constDouble, constStr, true, false, - , !, (\", encontrado " + "\"" + self.token.getLexema() + "\"")
                if self.token.getNome() != Tag.EOF: self.Exp1()

    #  Exp1’ → "<" Exp2 Exp1’  | "<=" Exp2 Exp1’  | ">" Exp2 Exp1’  | ">=" Exp2 Exp1’
    #  50 | "==" Exp2 Exp1’  | "!=" Exp2 Exp1’   | ε
    def Exp1Linha(self):
        noExp1Linha = No()
        if self.eat(Tag.OP_MENOR) or self.eat(Tag.OP_MENOR_IGUAL) or self.eat(Tag.OP_MAIOR) or self.eat(
                Tag.OP_MAIOR_IGUAL) or self.eat(Tag.OP_IGUAL_IGUAL) or self.eat(Tag.OP_DIFERENTE):

            noExp2 = self.Exp2()
            noExp1Linha_ = self.Exp1Linha()

            if noExp1Linha_.tipo == Tag.TIPO_VAZIO and noExp2.tipo == Tag.TIPO_NUMERICO:
                noExp1Linha.setType(Tag.TIPO_NUMERICO)
            elif noExp1Linha_.tipo == noExp2.tipo and noExp2.tipo == Tag.TIPO_NUMERICO:
                noExp1Linha.tipo = (Tag.TIPO_NUMERICO)
            else:
                noExp1Linha.tipo = (Tag.TIPO_ERRO)

            return noExp1Linha

        else:
            if self.token.getNome() == Tag.KW_OR or not self.token.getNome() == Tag.KW_AND or not self.token.getNome() == \
                 Tag.OP_FPA or not self.token.getNome() == Tag.OP_PONTO_VIRGULA or not self.token.getNome() == Tag.OP_VIRGULA:
                return noExp1Linha
            else:
                self.skip(
                    "Esperado \"<, <=, >, >=, ',', or, and, ==, !=\"; encontrado " + "\"" + self.token.getLexema() + "\"")
                if self.token.getNome() != Tag.EOF: self.Exp1Linha()

    # Exp2 → Exp3 Exp2’
    def Exp2(self):
        noExp2 = No()
        if self.token.getNome() == Tag.ID or self.token.getNome() == Tag.OP_APA or self.token.getNome() == Tag.NUM_INTEIRO \
                or self.token.getNome() == Tag.NUM_DOUBLE or self.token.getNome() == Tag.LIT or self.token.getNome() == Tag.KW_TRUE \
                or self.token.getNome() == Tag.KW_FALSE or self.token.getNome() == Tag.OP_UNARIO_DIFERENTE or self.token.getNome() == Tag.OP_NEGACAO:
            noExp3 = self.Exp3()
            noExp2Linha = self.Exp2Linha()

            if noExp2Linha.tipo == Tag.TIPO_VAZIO:
                noExp2.tipo = (noExp3.tipo)
            elif noExp2Linha.tipo == noExp3.tipo and noExp2Linha.tipo == Tag.TIPO_NUMERICO:
                noExp2.tipo = (Tag.TIPO_NUMERICO)
            else:
                noExp2.tipo = (Tag.TIPO_ERRO)
            return noExp2
        else:
            if self.token.getNome() == Tag.OP_MENOR or self.token.getNome() == Tag.OP_MENOR_IGUAL or self.token.getNome() == Tag.OP_MAIOR \
                    or self.token.getNome() == Tag.OP_MAIOR_IGUAL or self.token.getNome() == Tag.OP_IGUAL_IGUAL or \
                    self.token.getNome() == Tag.OP_DIFERENTE or self.token.getNome() == Tag.KW_OR or self.token.getNome() == Tag.KW_AND \
                    or self.token.getNome() == Tag.OP_FPA or self.token.getNome() == Tag.OP_DOIS_PONTOS or self.token.getNome() == Tag.OP_VIRGULA:
                self.sync(
                    "Esperado \"ID, constInt, constDouble, constStr, true, false, - , !\", encontrado " + "\"" + self.token.getLexema() + "\"")
                return noExp2

            else:
                self.skip(
                    "Esperado \"ID, constInt, constDouble, constStr, true, false, - , !\", encontrado " + "\"" + self.token.getLexema() + "\"")
                if self.token.getNome() != Tag.EOF: self.Exp2()

    # Exp2’ → "+" Exp3 Exp2’ | "-" Exp3 Exp2’ | ε
    def Exp2Linha(self):
        noExp2Linha = No()
        if self.eat(Tag.OP_ADICAO) or self.eat(Tag.OP_SUBTRACAO):
            noExp3 = self.Exp3()
            noExp2Linha_ = self.Exp2Linha()

            if noExp2Linha_.tipo == Tag.TIPO_VAZIO and noExp3.tipo == Tag.TIPO_NUMERICO:
                noExp2Linha.tipo = (Tag.TIPO_NUMERICO)
            elif noExp2Linha_.tipo == noExp3.tipo and noExp3.tipo == Tag.TIPO_NUMERICO:
                noExp2Linha_.tipo = (Tag.TIPO_NUMERICO)
            else:
                noExp3.tipo = (Tag.TIPO_ERRO)
            return noExp2Linha
        else:
            if self.token.getNome() == Tag.OP_MAIOR or self.token.getNome() == Tag.OP_MAIOR_IGUAL or \
                    self.token.getNome() == Tag.OP_MENOR or self.token.getNome() == Tag.OP_MENOR_IGUAL or \
                    self.token.getNome() == Tag.OP_IGUAL_IGUAL or self.token.getNome() == Tag.OP_DIFERENTE or \
                    self.token.getNome() == Tag.KW_OR or self.token.getNome() == Tag.KW_AND or self.token.getNome() == Tag.OP_FPA \
                    or self.token.getNome() == Tag.OP_PONTO_VIRGULA or self.token.getNome() == Tag.OP_VIRGULA:
                return noExp2Linha
            else:
                self.skip(
                    "Esperado \"+, -, ;, ), ',', or, and, <, <=, >, >=, ==, !=\", encontrado " + "\"" + self.token.getLexema() + "\"")
                if self.token.getNome() != Tag.EOF: self.Exp2Linha()

    # Exp3 → Exp4 Exp3’
    def Exp3(self):
        noExp3 = No()

        if self.token.getNome() == Tag.ID or self.token.getNome() == Tag.OP_APA or self.token.getNome() == Tag.NUM_INTEIRO \
                or self.token.getNome() == Tag.NUM_DOUBLE or self.token.getNome() == Tag.LIT or self.token.getNome() == Tag.KW_TRUE \
                or self.token.getNome() == Tag.KW_FALSE or self.token.getNome() == Tag.OP_UNARIO_DIFERENTE or self.token.getNome() == Tag.OP_NEGACAO:
            noExp4 = self.Exp4()
            noExp3Linha = self.Exp3Linha()

            if noExp3Linha.tipo == Tag.TIPO_VAZIO:
                noExp3.tipo = (noExp4.tipo)
            elif noExp3Linha.tipo == noExp4.tipo and noExp3Linha.tipo == Tag.TIPO_NUMERICO:
                noExp3.tipo = (Tag.TIPO_NUMERICO)
            else:
                noExp3.tipo = (Tag.TIPO_ERRO)
            return noExp3

        else:
            if self.token.getNome() == Tag.OP_ADICAO or self.token.getNome() == Tag.OP_SUBTRACAO or self.token.getNome() == Tag.OP_MENOR \
                    or self.token.getNome() == Tag.OP_MENOR_IGUAL or self.token.getNome() == Tag.OP_MAIOR or self.token.getNome() == Tag.OP_MAIOR_IGUAL \
                    or self.token.getNome() == Tag.OP_IGUAL_IGUAL or self.token.getNome() == Tag.OP_DIFERENTE or self.token.getNome() == Tag.KW_OR \
                    or self.token.getNome() == Tag.KW_AND or self.token.getNome() == Tag.OP_FPA or self.token.getNome() == Tag.OP_PONTO_VIRGULA \
                    or self.token.getNome() == Tag.OP_VIRGULA:

                self.sync(
                    "Esperado \"ID, (, constInt, constDouble, String, true, false, !, -n\", encontrado " + "\"" + self.token.getLexema() + "\"")
                return noExp3

            else:
                self.skip(
                    "Esperado \"ID, (, constInt, constDouble, String, true, false, !, -n\", encontrado " + "\"" + self.token.getLexema() + "\"")
                if self.token.getNome() != Tag.EOF: self.Exp3()

    # Exp3’ → "*" Exp4 Exp3’ | "/" Exp4 Exp3’ | ε
    def Exp3Linha(self):
        noExp3Linha = No()
        if self.eat(Tag.OP_MULTIPLICACAO) or self.eat(Tag.OP_DIVISAO):
            noExp4 = self.Exp4()
            noExp3Linha_ = self.Exp3Linha()

            if noExp3Linha_.tipo == Tag.TIPO_VAZIO and noExp4.tipo == Tag.TIPO_NUMERICO:
                noExp3Linha.tipo(Tag.TIPO_NUMERICO)
            elif noExp3Linha_.tipo == noExp4.tipo and noExp4.tipo == Tag.TIPO_NUMERICO:
                noExp3Linha.tipo = (Tag.TIPO_NUMERICO)
            else:
                noExp3Linha.tipo = (Tag.TIPO_ERRO)
            return noExp3Linha
        else:
            if self.token.getNome() in (Tag.OP_SUBTRACAO, Tag.OP_ADICAO, Tag.OP_MAIOR, Tag.OP_MAIOR_IGUAL, Tag.OP_MENOR, \
                                       Tag.OP_MENOR_IGUAL, Tag.OP_IGUAL_IGUAL, Tag.OP_DIFERENTE, Tag.KW_OR, Tag.KW_AND, \
                                       Tag.OP_FPA, Tag.OP_PONTO_VIRGULA, Tag.OP_VIRGULA):
                return  noExp3Linha
            else:
                self.skip(
                    "Esperado \"/,*\", encontrado " + "\"" + self.token.getLexema() + "\"")
                if self.token.getNome() != Tag.EOF: self.Exp3Linha()

    # Exp4 → ID Exp4’ | ConstInteger | ConstDouble | ConstString | "true" | "false" | OpUnario Exp4 | "(" Expressao")"
    def Exp4(self):
        noExp4 = No()
        tempToken = copy.copy(self.token)

        if self.eat(Tag.ID):
            self.Exp4Linha()

            if noExp4.tipo == None:
                noExp4.tipo = (Tag.TIPO_ERRO)
                self.sinalizaErroSemantico("Id não declarado")
            return noExp4

        elif self.eat(Tag.OP_NEGACAO) or self.eat(Tag.OP_DIFERENTE):
            noOpUnario = self.OpUnario()
            noExp4_ = self.Exp4()

            if noExp4_.tipo == noOpUnario.tipo and noOpUnario.tipo == Tag.TIPO_NUMERICO:
                noExp4.tipo = (Tag.TIPO_NUMERICO)
            elif noExp4_.tipo == noOpUnario.tipo and noOpUnario.tipo == Tag.TIPO_LOGICO:
                noExp4.tipo = (Tag.TIPO_LOGICO)
            else:
                noExp4.tipo = (Tag.TIPO_ERRO)

            return noExp4

        elif self.eat(Tag.OP_APA):
            noExp = self.Expressao()
            if not self.eat(Tag.OP_FPA):
                self.sinalizaErroSintatico("Esperado \")\"; encontrado " + "\"" + self.token.getLexema() + "\"")
            noExp4.tipo = (noExp.tipo)
            return noExp4

        elif self.eat(Tag.NUM_INTEIRO) or self.eat(Tag.NUM_DOUBLE):
            noExp4.tipo = (Tag.TIPO_NUMERICO)
            return noExp4
        elif self.eat(Tag.LIT):
            noExp4.tipo = (Tag.KW_STRING)
            return noExp4
        elif self.eat(Tag.KW_FALSE) or self.eat(Tag.KW_TRUE):
            noExp4.tipo = (Tag.TIPO_LOGICO)
            return noExp4
        elif not self.eat(Tag.NUM_INTEIRO) and not self.eat(Tag.LIT) and not self.eat(Tag.NUM_DOUBLE) and not self.eat(
                Tag.KW_TRUE) and not self.eat(Tag.KW_FALSE):
            if self.token.getNome() in (Tag.OP_MULTIPLICACAO, Tag.OP_DIVISAO, Tag.OP_ADICAO , Tag.OP_SUBTRACAO, Tag.OP_MENOR, \
                                        Tag.OP_MENOR_IGUAL, Tag.OP_MAIOR, Tag.OP_MAIOR_IGUAL, Tag.OP_IGUAL_IGUAL, Tag.OP_DIFERENTE,\
                                        Tag.KW_OR, Tag.KW_AND, Tag.OP_FPA, Tag.OP_PONTO_VIRGULA, Tag.OP_VIRGULA):
                self.sync("Esperado \"ID, constInt, constDouble, String, true, false, !, -n, (\"; encontrado " + "\"" + self.token.getLexema() + "\"")
                return noExp4
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
            if self.token.getNome() in (Tag.OP_MULTIPLICACAO, Tag.OP_DIVISAO, Tag.OP_SUBTRACAO, Tag.OP_ADICAO, Tag.OP_MAIOR, \
                                        Tag.OP_MAIOR_IGUAL, Tag.OP_MENOR, Tag.OP_MENOR_IGUAL, Tag.OP_IGUAL_IGUAL, Tag.OP_DIFERENTE, \
                                        Tag.KW_OR, Tag.KW_AND, Tag.OP_FPA, Tag.OP_PONTO_VIRGULA, Tag.OP_VIRGULA):
                return
            else:
                self.skip("Esperado \";, ), ',', or, and, <, <=, >, >=, ==, !=, + , -, *, /\", encontrado " + "\"" + self.token.getLexema() + "\"")
                if self.token.getNome() != Tag.EOF: self.Exp4Linha()

    # OpUnario → "-" | "!"
    def OpUnario(self):
        noOpUnario = No()

        if self.eat(Tag.OP_SUBTRACAO):
            noOpUnario.tipo = (Tag.TIPO_NUMERICO)
            return noOpUnario
        elif self.eat(Tag.OP_NEGACAO):
            noOpUnario.tipo = (Tag.TIPO_LOGICO)
            return noOpUnario

        if not self.eat(Tag.OP_NEGACAO) and not self.eat(Tag.OP_UNARIO_DIFERENTE):
            if self.token.getNome() in (Tag.ID, Tag.NUM_INTEIRO, Tag.NUM_DOUBLE, Tag.LIT,Tag.KW_TRUE, Tag.KW_FALSE, Tag.OP_NEGACAO, Tag.OP_UNARIO_DIFERENTE, Tag.OP_APA):
                self.sync("Esperado \"-n, !\", encontrado " + "\"" + self.token.getLexema() + "\"")

                return noOpUnario

            else:
                self.skip("Esperado \"-n, !\", encontrado " + "\"" + self.token.getLexema() + "\"")
                if self.token.getNome() != Tag.EOF: self.OpUnario()
