from modulos.tag import Tag
from modulos.lexer import Lexer
from modulos.parser import Parser

if __name__ == "__main__":
    lexer = Lexer('programa.txt')
    #parser = Parser(lexer)

   # parser.Programa()

    print("\n=>Lista de tokens:")
    token = lexer.proxToken()

    while token is not None and token.getNome() != Tag.EOF:

        print(token.toString(), "Linha: " + str(token.getLinha()) + " Coluna: " + str(token.getColuna()))
        token = lexer.proxToken()

    print("\n=>Tabela de simbolos:")
    lexer.printTS()
    lexer.closeFile()
    #parser.lexer.closeFile()
    print('\n=> Compilado com sucesso')