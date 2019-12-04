from enum import Enum


class Tag(Enum):
    # Fim de arquivo
    EOF = -1

    # Identificador
    ID = 1

    # Palavras-chave
    KW_CLASS = 2
    KW_END = 3
    KW_DEF = 4
    KW_RETURN = 5
    KW_DEFSTATIC = 6
    KW_VOID = 7
    KW_MAIN = 8
    KW_STRING = 9
    KW_BOOL = 10
    KW_INTEGER = 11
    KW_DOUBLE = 12
    KW_IF = 13
    KW_ELSE = 14
    KW_WHILE = 15
    KW_WRITE = 16
    KW_TRUE = 17
    KW_FALSE = 18
    KW_OR = 19
    KW_AND = 20

    # Operadores
    OP_MENOR = 21
    OP_MENOR_IGUAL = 22
    OP_MAIOR_IGUAL = 23
    OP_MAIOR = 24
    OP_IGUAL_IGUAL = 25
    OP_DIFERENTE = 26
    OP_MULTIPLICACAO = 27
    OP_DIVISAO = 28
    OP_ADICAO = 29

    # Operador Unario
    OP_UNARIO_IGUAL = 30
    OP_UNARIO_DIFERENTE = 31
    OP_UNARIO_MENOR = 32

    # Numeros
    NUM_INTEIRO = 33
    NUM_DOUBLE = 34

    # Caracteres

    OP_APA = 35
    OP_FPA = 36
    OP_ACO = 37
    OP_FCO = 38
    OP_VIRGULA = 39
    OP_PONTO_VIRGULA = 42
    OP_DOIS_PONTOS = 43

    COMENTARIO = 44

    LIT = 45

    OP_SUBTRACAO = 46
    OP_NEGACAO = 47

    OP_PONTO = 48

    # Constantes para tipos
    TIPO_VAZIO = 1000
    TIPO_LOGICO = 1001
    TIPO_INT = 1002
    TIPO_DOUBLE = 1003
    TIPO_ERRO = 1004
