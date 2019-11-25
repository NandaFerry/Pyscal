import sys

from modulos.ts import TS
from modulos.tag import Tag
from modulos.token import Token
from modulos.lexer import Lexer

"""
 * *
 * [TODO]: tratar retorno 'None' do Lexer que esta sem Modo Panico
 *
 *
 * Modo Pânico do Parser: 
    * Para tomar a decisao de escolher uma das regras (quando mais de uma disponivel),
    * o parser usa incialmente o FIRST(), e para alguns casos, FOLLOW(). Essa informacao eh dada pela TP.
    * Caso nao existe a regra na TP que corresponda ao token da entrada,
    * informa-se uma mensagem de erro e inicia-se o Modo Panico:
    * [1] calcula-se o FOLLOW do NAO-TERMINAL (a esquerda) da regra atual: esse NAO-TERMINAL estara no topo da pilha;
    * [2] se o token da entrada estiver neste FOLLOW, desempilha-se o nao-terminal atual - metodo synch() - retorna da recursao;
    * [3] caso contrario, a entrada eh avancada para uma nova comparacao e mantem-se o nao-terminal no topo da pilha 
    * (se for a pilha recursiva, mantem o procedimento no topo da recursao) - metodo skip().
    * 
    * O Modo Panico encerra-se, 'automagicamente', quando um token esperado aparece.
    * Para NAO implementar o Modo Panico, basta sinalizar erro quando nao
    * for possivel utilizar alguma das regras. Em seguida, encerrar a execucao usando sys.exit(0).
"""


class Parser():

    def __init__(self, lexer):
        self.lexer = lexer
        self.token = lexer.proxToken(None)  # Leitura inicial obrigatoria do primeiro simbolo

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

    # verifica token esperado t
    def eat(self, t):
        if self.token.getNome() == t:
            self.advance()
            return True
        else:
            return False

    def proximo(self, t):
        if self.token.getNome() == t:
            return True
        else:
            return False

    # TODO verificar todas as regras com vazio

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
            self.sinalizaErroSintatico("Esperado \"class\"; encontrado " + "\"" + self.token.getLexema() + "\"")

    # DeclaraID -> TipoPrimitivo ID ";"
    def DeclaraID(self):
        if self.eat(Tag.KW_BOOL) or self.eat(Tag.KW_INTEGER) or self.eat(Tag.KW_STRING) or self.eat(
                Tag.KW_DOUBLE) or self.eat(Tag.KW_VOID):
            self.TipoPrimitivo()
            if not self.eat(Tag.ID):
                self.sinalizaErroSintatico("Esperado \"ID\"; encontrado " + "\"" + self.token.getLexema() + "\"")
            if not self.eat(Tag.OP_PONTO_VIRGULA):
                self.sinalizaErroSintatico("Esperado \";\"; encontrado " + "\"" + self.token.getLexema() + "\"")
        else:
            self.skip(
                "Esperado \"void, String, bool, int, double, ID, ;\", encontrado " + "\"" + self.token.getLexema() + "\"")
            if self.token.getNome() != Tag.EOF: self.DeclaraID()

    # ListaFuncao -> ListaFuncao'
    def ListaFuncao(self):
        if self.eat(Tag.KW_DEF) or self.eat((Tag.KW_DEFSTATIC)):
            self.ListaFuncaoLinha()
        else:
            self.skip("Esperado \"def, defstatic\", encontrado " + "\"" + self.token.getLexema() + "\"")
            if self.token.getNome() != Tag.EOF: self.ListaFuncao()

    # ListaFuncao' -> Funcao ListaFuncao'| ε
    def ListaFuncaoLinha(self):
        if self.eat(Tag.KW_DEF):
            self.Funcao()
            self.ListaFuncaoLinha()

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
            self.sinalizaErroSintatico("Esperado \"def\"; encontrado " + "\"" + self.token.getLexema() + "\"")

    # DeclaraID RegexDeclaraId | ε
    def RegexDeclaraId(self):
        if self.eat(Tag.KW_VOID) or self.eat(Tag.KW_STRING) or self.eat(Tag.KW_BOOL) or self.eat(Tag.KW_INTEGER) or self.eat(Tag.KW_DOUBLE):

            self.DeclaraID()
            self.RegexDeclaraId()

            return
        if not self.eat(Tag.ID) or not self.eat(Tag.KW_END) or not self.eat(Tag.KW_RETURN) or not self.eat(Tag.KW_IF)\
                or not self.eat(Tag.KW_WRITE) or not self.eat(Tag.KW_WHILE):
            self.skip("Esperado \"id, end, return, if, write, while\", encontrado " + "\"" + self.token.getLexema() + "\"")
            if self.token.getNome() != Tag.EOF: self.RegexDeclaraId()

    # ListaArg -> Arf ListaArg'
    def ListaArg(self):
        if self.eat(Tag.KW_VOID) or self.eat(Tag.KW_STRING) or self.eat(Tag.KW_BOOL) or self.eat(Tag.KW_INTEGER) or self.eat(Tag.KW_DOUBLE):
            self.Arg()
            self.ListaArgLinha()
        else:
            self.skip(
                "Esperado \"void, String, bool, integer, double\", encontrado " + "\"" + self.token.getLexema() + "\"")
            if self.token.getNome() != Tag.EOF: self.ListaArg()

    # ListaArgLinha -> "," ListaArg | ε
    def ListaArgLinha(self):
        if self.eat(Tag.OP_VIRGULA):
            self.ListaArg()

            return

        if not self.eat(Tag.OP_APA):
            self.skip("Esperado \"',', )\", encontrado " + "\"" + self.token.getLexema() + "\"")
            if self.token.getNome() != Tag.EOF: self.ListaArgLinha()

    # Arg → TipoPrimitivo ID
    def Arg(self):
        if self.eat(Tag.KW_VOID) or self.eat(Tag.KW_STRING) or self.eat(Tag.KW_BOOL) or self.eat(
                Tag.KW_INTEGER) or self.eat(Tag.KW_DOUBLE):

            self.TipoPrimitivo()

            if not self.eat(Tag.ID):
                self.sinalizaErroSintatico("Esperado \"ID\"; encontrado " + "\"" + self.token.getLexema() + "\"")
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

            return
        if not self.eat(Tag.KW_END):
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
        else:
            self.skip("Esperado \"defstatic\", encontrado " + "\"" + self.token.getLexema() + "\"")
            if self.token.getNome() != Tag.EOF: self.Main()

    # TipoPrimitivo → "bool" | "integer" | "String" | "double" | "void"
    def TipoPrimitivo(self):
        if not self.eat(Tag.KW_BOOL) and not self.eat(Tag.KW_INTEGER) and not self.eat(Tag.KW_STRING) and not self.eat(
                Tag.KW_DOUBLE) and not self.eat(Tag.KW_VOID):
            self.sinalizaErroSintatico(
                "Esperado \"bool, integer, String, double, void\", encontrado " + "\"" + self.token.getLexema() + "\"");
            return

    # ListaCmd → ListaCmd’
    def ListaCmd(self):
        self.ListaCmdLinha()

    # TODO verificar este método
    # ListaCmd’ →  Cmd ListaCmd’ 23 | ε
    def ListaCmdLinha(self):
        self.Cmd()
        self.ListaCmdLinha()
        if self.token.getNome() == Tag.KW_RETURN or self.token.getNome() == Tag.KW_END or self.token.getNome() == Tag.KW_ELSE:
            return

    # Cmd → CmdIF | CmdWhile | ID CmdAtribFunc | CmdWrite
    def Cmd(self):
        if self.eat(Tag.KW_IF):
            self.CmdIF()
        elif self.eat(Tag.KW_WHILE):
            self.CmdWhile()
        elif self.eat(Tag.ID):
            self.CmdAtribFunc()
        elif self.eat(Tag.KW_WRITE):
            self.CmdWrite()
        else:
            self.sinalizaErroSintatico(
                "Esperado \"if, while, id ou whrite\", encontrado " + "\"" + self.token.getLexema() + "\"");
            return

    # TODO verificar este método
    # CmdAtribFunc→ CmdAtribui | CmdFuncao
    def CmdAtribFunc(self):
        if self.eat(Tag.OP_APA):
            self.CmdFuncao()
        else:
            self.CmdAtribFunc()

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
            self.sinalizaErroSintatico("Esperado \"if\"; encontrado " + "\"" + self.token.getLexema() + "\"")

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
            self.sinalizaErroSintatico("Esperado \"end, else\"; encontrado " + "\"" + self.token.getLexema() + "\"")

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
            self.sinalizaErroSintatico("Esperado \"while\"; encontrado " + "\"" + self.token.getLexema() + "\"")

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
            self.sinalizaErroSintatico("Esperado \"write\"; encontrado " + "\"" + self.token.getLexema() + "\"")

    # CmdAtribui → "=" Expressao ";"
    def CmdAtribui(self):
        if self.eat(Tag.OP_UNARIO_IGUAL):
            self.Expressao()
            if not self.eat(Tag.OP_PONTO_VIRGULA):
                self.sinalizaErroSintatico("Esperado \";\"; encontrado " + "\"" + self.token.getLexema() + "\"")
        else:
            self.sinalizaErroSintatico("Esperado \"=\"; encontrado " + "\"" + self.token.getLexema() + "\"")

    # CmdFuncao → "(" RegexExp ")" ";"
    def CmdFuncao(self):
        if self.eat(Tag.OP_APA):
            self.RegexExp()
            if not self.eat(Tag.OP_FPA):
                self.sinalizaErroSintatico("Esperado \")\"; encontrado " + "\"" + self.token.getLexema() + "\"")
            if not self.eat(Tag.OP_PONTO_VIRGULA):
                self.sinalizaErroSintatico("Esperado \";\"; encontrado " + "\"" + self.token.getLexema() + "\"")
        else:
            self.sinalizaErroSintatico("Esperado \"(\"; encontrado " + "\"" + self.token.getLexema() + "\"")

    # TODO verificar esta funcao
    # RegexExp → Expressao RegexExp’ | ε
    def RegexExp(self):
        self.Expressao()
        self.RegexExpLinha()
        if self.token.getNome() == Tag.OP_FPA:
            return

    # TODO verificar esta funcao
    # RegexExp’ → , Expressao RegexExp’ | ε
    def RegexExpLinha(self):
        if self.eat(Tag.OP_VIRGULA):
            self.Expressao()
            self.RegexExpLinha()
        elif self.token.getNome() == Tag.OP_FPA:
            return

    # Expressao → Exp1 Exp’
    def Expressao(self):
        self.Exp1()
        self.ExpLinha()

    # TODO verificar esta funcao
    # Exp’ → "or" Exp1 Exp’ | "and" Exp1 Exp’ | ε
    def ExpLinha(self):
        if self.eat(Tag.KW_OR) or self.eat(Tag.KW_AND):
            self.Exp1()
            self.ExpLinha()
        elif (
                self.token.getNome() == Tag.OP_FPA or self.token.getNome() == Tag.OP_PONTO_VIRGULA or self.token.getNome() == Tag.OP_VIRGULA):
            return

    # Exp1 → Exp2 Exp1’
    def Exp1(self):
        self.Exp2()
        self.Exp1Linha()

    # TODO verificar esta funcao

    #  Exp1’ → "<" Exp2 Exp1’  | "<=" Exp2 Exp1’  | ">" Exp2 Exp1’  | ">=" Exp2 Exp1’
    #  50 | "==" Exp2 Exp1’  | "!=" Exp2 Exp1’   | ε
    def Exp1Linha(self):
        if self.eat(Tag.OP_MENOR) or self.eat(Tag.OP_MENOR_IGUAL) or self.eat(Tag.OP_MAIOR) or self.eat(
                Tag.OP_MAIOR_IGUAL) or self.eat(Tag.OP_IGUAL_IGUAL) or self.eat(Tag.OP_DIFERENTE):
            return
        elif self.token.getNome() == Tag.KW_OR or self.token.getNome() == Tag.KW_AND or self.token.getNome() == \
                Tag.OP_FPA or self.token.getNome() == Tag.OP_PONTO_VIRGULA or self.token.getNome() == Tag.OP_VIRGULA:
            return

    # Exp2 → Exp3 Exp2’
    def Exp2(self):
        self.Exp3()
        self.Exp2Linha()

    # TODO verificar esta funcao
    # Exp2’ → "+" Exp3 Exp2’ | "-" Exp3 Exp2’ | ε
    def Exp2Linha(self):
        if self.eat(Tag.OP_ADICAO) or self.eat(Tag.OP_SUBTRACAO):
            self.Exp3()
            self.Exp2Linha()
        elif (
                self.token.getNome() == Tag.OP_MAIOR or self.token.getNome() == Tag.OP_MAIOR_IGUAL or self.token.getNome() == Tag.OP_MENOR or self.token.getNome() == Tag.OP_MENOR_IGUAL or self.token.getNome() == Tag.OP_IGUAL_IGUAL or self.token.getNome() == Tag.OP_DIFERENTE or self.token.getNome() == Tag.KW_OR or self.token.getNome() == Tag.KW_AND or self.token.getNome() == Tag.OP_FPA or self.token.getNome() == Tag.OP_PONTO_VIRGULA or self.token.getNome() == Tag.OP_VIRGULA):
            return

    # Exp3 → Exp4 Exp3’
    def Exp3(self):
        self.Exp4()
        self.Exp3Linha()

    # TODO verificar esta funcao
    # Exp3’ → "*" Exp4 Exp3’ | "/" Exp4 Exp3’ | ε
    def Exp3Linha(self):
        if self.eat(Tag.OP_MULTIPLICACAO) or self.eat(Tag.OP_DIVISAO):
            self.Exp4()
            self.Exp3Linha()
        elif (
                self.token.getNome() == Tag.OP_SUBTRACAO or self.token.getNome() == Tag.OP_ADICAO or self.token.getNome() == Tag.OP_MAIOR or self.token.getNome() == Tag.OP_MAIOR_IGUAL or self.token.getNome() == Tag.OP_MENOR or self.token.getNome() == Tag.OP_MENOR_IGUAL or self.token.getNome() == Tag.OP_IGUAL_IGUAL or self.token.getNome() == Tag.OP_DIFERENTE or self.token.getNome() == Tag.KW_OR or self.token.getNome() == Tag.KW_AND or self.token.getNome() == Tag.OP_FPA or self.token.getNome() == Tag.OP_PONTO_VIRGULA or self.token.getNome() == Tag.OP_VIRGULA):
            return

    # TODO verificar esta funcao
    # Exp4 → ID Exp4’ | ConstInteger | ConstDouble | ConstString | "true" | "false" | OpUnario Exp4 | "(" Expressao")"
    def Exp4(self):
        if self.eat(Tag.ID):
            self.Expr4Linha()
        elif self.eat(Tag.OP_NEGACAO) or self.eat(Tag.OP_DIFERENTE):
            self.Exp4()
        elif self.eat(Tag.OP_APA):
            self.Expressao()
            if not self.eat(Tag.OP_FPA):
                self.sinalizaErroSintatico("Esperado \")\"; encontrado " + "\"" + self.token.getLexema() + "\"")
        elif not self.eat(Tag.NUM_INTEIRO) and not self.eat(Tag.LIT) and self.eat(Tag.NUM_DOUBLE):
            self.sinalizaErroSintatico(
                "Esperado \"numero inteiro, numero double ou string\"; encontrado " + "\"" + self.token.getLexema() + "\"")

    # TODO verificar esta funcao
    # Exp4’ → "(" RegexExp ")" | ε
    def Exp4Linha(self):
        if self.eat(Tag.OP_APA):
            self.RegexExp()
            if not self.eat(Tag.OP_FPA):
                self.sinalizaErroSintatico("Esperado \")\"; encontrado " + "\"" + self.token.getLexema() + "\"")
        elif (
                self.token.getNome() == Tag.OP_MULTIPLICACAO or self.token.getNome() == Tag.OP_DIVISAO or self.token.getNome() == Tag.OP_SUBTRACAO or self.token.getNome() == Tag.OP_ADICAO or self.token.getNome() == Tag.OP_MAIOR or self.token.getNome() == Tag.OP_MAIOR_IGUAL or self.token.getNome() == Tag.OP_MENOR or self.token.getNome() == Tag.OP_MENOR_IGUAL or self.token.getNome() == Tag.OP_IGUAL_IGUAL or self.token.getNome() == Tag.OP_DIFERENTE or self.token.getNome() == Tag.KW_OR or self.token.getNome() == Tag.KW_AND or self.token.getNome() == Tag.OP_FPA or self.token.getNome() == Tag.OP_PONTO_VIRGULA or self.token.getNome() == Tag.OP_VIRGULA):
            return

    # OpUnario → "-" | "!"
    def OpUnario(self):
        if not self.eat(Tag.OP_NEGACAO) and not self.eat(Tag.OP_UNARIO_DIFERENTE):
            self.sinalizaErroSintatico("Esperado \"-, !\"; encontrado " + "\"" + self.token.getLexema() + "\"")
            return

    # ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
    def Cmd(self):
        # Cmd -> if E then { CMD } CMD'
        if (self.eat(Tag.KW_IF)):
            self.E()

            """
            ATENCAO: no caso 'terminal esperado' vs 'terminal na entrada', o 'terminal esperado' 
            não casou com o terminal da entrada, dai vamos simular o 'desempilha terminal',
            isto eh, continue a varredura, mantendo a entrada.
            */
            """
            if (not self.eat(Tag.KW_THEN)):
                self.sinalizaErroSintatico("Esperado \"then\", encontrado " + "\"" + self.token.getLexema() + "\"")
            if (not self.eat(Tag.SMB_AB_CHA)):
                self.sinalizaErroSintatico("Esperado \"{\", encontrado " + "\"" + self.token.getLexema() + "\"")
            self.Cmd()
            if not self.eat(Tag.SMB_FE_CHA):
                self.sinalizaErroSintatico("Esperado \"}\", encontrado " + "\"" + self.token.getLexema() + "\"")
            self.CmdLinha()
        # Cmd -> print T
        elif self.eat(Tag.KW_PRINT):
            self.T()
        else:
            """
            Percebemos na TP que os metodos skip() ou synch() podem ser executados. 
            A ideia do skip() eh avancar a entrada sem retirar Cmd() da pilha(recursiva). Porem chegamos ao fim 
            do metodo Cmd(). Como podemos mante-lo na pilha recursiva? Simples, chamamos o proprio metodo Cmd().
            A ideia do synch() eh tirar Cmd() da pilha(recursiva), pois apos esse procedimento, algum simbolo
            na pilha ira resolver a entrada. Como retirar esse procedimento da pilha? Um simples 'return'. 
            Lembres-se que o synch() tem preferencia em ser executado em relacao ao skip().
            */
            """

            # synch: FOLLOW(Cmd)
            if self.token.getNome() == Tag.SMB_FE_CHA or self.token.getNome() == Tag.EOF:
                self.sinalizaErroSintatico("Esperado \"if, print\", encontrado " + "\"" + self.token.getLexema() + "\"")
                return
            else:
                self.skip("Esperado \"if, print\", encontrado " + "\"" + self.token.getLexema() + "\"")
                if self.token.getNome() != Tag.EOF: self.Cmd();

    def CmdLinha(self):
        # CmdLinha -> else { CMD }
        if (self.eat(Tag.KW_ELSE)):
            if (not self.eat(Tag.SMB_AB_CHA)):
                self.sinalizaErroSintatico("Esperado \"{\", encontrado " + "\"" + self.token.getLexema() + "\"")
            self.Cmd()
            if (not self.eat(Tag.SMB_FE_CHA)):
                self.sinalizaErroSintatico("Esperado \"}\", encontrado " + "\"" + self.token.getLexema() + "\"")
        # CmdLinha -> epsilon
        elif (self.token.getNome() == Tag.SMB_FE_CHA or self.token.getNome() == Tag.EOF):
            return
        else:
            self.skip("Esperado \"else, }\", encontrado " + "\"" + self.token.getLexema() + "\"")
            if (self.token.getNome() != Tag.EOF): self.CmdLinha();

    # E -> F E'
    def E(self):
        if (self.token.getNome() == Tag.ID or self.token.getNome() == Tag.NUM):
            self.F()
            self.ELinha()
        else:
            # synch: FOLLOW(E)
            if (self.token.getNome() == Tag.KW_THEN):
                self.sinalizaErroSintatico("Esperado \"id, num\", encontrado " + "\"" + self.token.getLexema() + "\"")
                return
            else:
                self.skip("Esperado \"id, num\", encontrado " + "\"" + self.token.getLexema() + "\"")
                if (self.token.getNome() != Tag.EOF): self.E();

    '''
    E' --> ">" F E'  | "<" F E' | 
           ">=" F E' | "<=" F E'| 
           "==" F E' | "!=" F E'| epsilon
    '''

    def ELinha(self):
        if (self.eat(Tag.OP_MAIOR) or self.eat(Tag.OP_MENOR) or self.eat(Tag.OP_MAIOR_IGUAL) or
                self.eat(Tag.OP_MENOR_IGUAL) or self.eat(Tag.OP_IGUAL) or self.eat(Tag.OP_DIFERENTE)):
            self.F()
            self.ELinha()
        elif (self.token.getNome() == Tag.KW_THEN):
            return
        else:
            self.skip("Esperado \">, <, >=, <=, ==, !=, then\", encontrado " + "\"" + self.token.getLexema() + "\"")
            if (self.token.getNome() != Tag.EOF): self.ELinha();

    def F(self):
        if (self.token.getNome() == Tag.ID or self.token.getNome() == Tag.NUM):
            self.T()
            self.FLinha()
        else:
            # synch: FOLLOW(F)
            if (self.token.getNome() == Tag.KW_THEN or self.token.getNome() == Tag.OP_MENOR or
                    self.token.getNome() == Tag.OP_MAIOR or self.token.getNome() == Tag.OP_MENOR_IGUAL or
                    self.token.getNome() == Tag.OP_MAIOR_IGUAL or self.token.getNome() == Tag.OP_IGUAL or
                    self.token.getNome() == Tag.OP_DIFERENTE):
                self.sinalizaErroSintatico("Esperado \"id, num\", encontrado " + "\"" + self.token.getLexema() + "\"")
                return
            else:
                self.skip("Esperado \"id, num\", encontrado " + "\"" + self.token.getLexema() + "\"")
                if (self.token.getNome() != Tag.EOF): self.F();

    # F'  --> "+" T F' | "-" T F' | epsilon
    def FLinha(self):
        if (self.eat(Tag.OP_SOMA) or self.eat(Tag.OP_SUB)):
            self.T()
            self.FLinha()
        elif (self.token.getNome() == Tag.OP_MAIOR or self.token.getNome() == Tag.OP_MENOR or
              self.token.getNome() == Tag.OP_MAIOR_IGUAL or self.token.getNome() == Tag.OP_MENOR_IGUAL or
              self.token.getNome() == Tag.OP_DIFERENTE or self.token.getNome() == Tag.OP_IGUAL or
              self.token.getNome() == Tag.KW_THEN):
            return
        else:
            self.skip(
                "Esperado \"+, -, >, <, >=, <=, ==, !=, then\", encontrado " + "\"" + self.token.getLexema() + "\"")
            if (self.token.getNome() != Tag.EOF): self.FLinha();

    # T -> id | num
    def T(self):
        if (not self.eat(Tag.ID) and not self.eat(Tag.NUM)):
            # synch: FOLLOW(T)
            if (self.token.getNome() == Tag.OP_MAIOR or self.token.getNome() == Tag.OP_MENOR or
                    self.token.getNome() == Tag.OP_MAIOR_IGUAL or self.token.getNome() == Tag.OP_MENOR_IGUAL or
                    self.token.getNome() == Tag.OP_DIFERENTE or self.token.getNome() == Tag.OP_IGUAL or
                    self.token.getNome() == Tag.KW_THEN or self.token.getNome() == Tag.OP_SOMA or
                    self.token.getNome() == Tag.OP_SUB):
                self.sinalizaErroSintatico("Esperado \"num, id\", encontrado " + "\"" + self.token.getLexema() + "\"");
                return
            else:
                self.skip("Esperado \"num, id\", encontrado " + "\"" + self.token.getLexema() + "\"");
                if (self.token.getNome() != Tag.EOF): self.T();
