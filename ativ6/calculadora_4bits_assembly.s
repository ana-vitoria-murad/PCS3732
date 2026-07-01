.global _start
_start:
    // -------------------------------------------------------------------------
    // 1. Definição de Valores de Teste (Entradas de 4 bits: gama de 0 a 15)
    // -------------------------------------------------------------------------
    MOV R0, #3              // Primeiro número de entrada (exemplo: 3)
    MOV R1, #4              // Segundo número de entrada (exemplo: 4)

    // -------------------------------------------------------------------------
    // 2. Rotina de Multiplicação com Tratamento (Pedido no Slide 8)
    // -------------------------------------------------------------------------
    MUL R2, R0, R1          // Executa a operação: R2 = R0 * R1
    CMP R2, #15             // Compara o resultado com o limite máximo de 4 bits (15)
    BGT overflow_handler    // Se R2 > 15, desvia para a rotina de erro

sucesso:
    // O resultado é válido (está entre 0 e 15) e pode seguir para a ULA.
    // O fluxo continua para a conversão de Binário -> ASCII para exibição.
    B fim

overflow_handler:
    // Tratamento de interrupção/erro quando o valor excede 4 bits.
    MOV R2, #0xFF           // Aloca um padrão de erro (ex: 255 ou indicador visual) em R2
    B fim

fim:
    B fim                   // Loop infinito para parar a execução no simulador