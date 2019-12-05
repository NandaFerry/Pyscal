from modulos.tag import Tag
from modulos.lexer import Lexer
from modulos.parser import Parser

# Fernanda Teixeira Ferry e Vitória Maria

if __name__ == "__main__":
    lexer = Lexer('programa.txt')
    parser = Parser(lexer)

    parser.Programa()

    token = lexer.proxToken()

    print("\n=>Tabela de simbolos:")

    lexer.printTS()
    lexer.closeFile()
    parser.lexer.closeFile()

    print('\n=> Compilado com sucesso')
