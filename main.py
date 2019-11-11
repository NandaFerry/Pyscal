from modulos.tag import Tag
from modulos.lexer import Lexer

if __name__ == "__main__":
    i = 0
    lexer = Lexer('programa.txt')

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


    print("\n=>Tabela de simbolos:")
    lexer.printTS()
    lexer.closeFile()

    print('\n=> Compilado com sucesso')
