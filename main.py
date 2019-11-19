from modulos.tag import Tag
from modulos.token import Token
from modulos.lexer import Lexer
from modulos.parser import Parser

if __name__ == "__main__":
    i = 0
    lexer = Lexer('programa.txt')
    parser = Parser(lexer)

    parser.Programa()


    print("\n=>Lista de tokens:")
    token = lexer.proxToken(None)
    ultimo = token

    while token is not None and token.getNome() != Tag.EOF:
        if token.getNome() == Tag.COMENTARIO:
            pass
        else:
            print(token.toString(), "Linha: " + str(token.getLinha()) + " Coluna: " + str(token.getColuna()))
        token = lexer.proxToken(ultimo)
        ultimo = token


    parser.lexer.closeFile()
    print("\n=>Tabela de simbolos:")
    lexer.printTS()
    lexer.closeFile()

    print('\n=> Compilado com sucesso')
