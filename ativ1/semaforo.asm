# -----------------------------------------------------
# Função setup()
# -----------------------------------------------------
setup:
    # Prepara a pilha (stack) para guardar o endereço de retorno
    addi    sp, sp, -16      
    sw      ra, 12(sp)       # Guarda o registador de retorno (ra)

    # pinMode(LED_BUILTIN, OUTPUT);
    li      a0, 8            # Carrega o pino do LED (ex: 8) no registador a0
    li      a1, 2            # Carrega a constante OUTPUT (geralmente 2 ou 3) no registador a1
    call    pinMode          # Salta para a função pinMode da biblioteca do Arduino

    # Restaura a pilha e regressa
    lw      ra, 12(sp)       
    addi    sp, sp, 16       
    ret                      

# -----------------------------------------------------
# Função loop()
# -----------------------------------------------------
loop:
    # Prepara a pilha
    addi    sp, sp, -16      
    sw      ra, 12(sp)       

    # 1. rgbLedWrite(LED_BUILTIN, 0, 255, 0);
    li      a0, 8            # a0 = Pino do LED
    li      a1, 0            # a1 = Vermelho (0)
    li      a2, 255          # a2 = Verde (255)
    li      a3, 0            # a3 = Azul (0)
    call    rgbLedWrite

    # 2. delay(3000);
    li      a0, 3000         # a0 = 3000 ms
    call    delay

    # 3. rgbLedWrite(LED_BUILTIN, 255, 255, 0);
    li      a0, 8            # a0 = Pino do LED
    li      a1, 255          # a1 = Vermelho (255)
    li      a2, 255          # a2 = Verde (255)
    li      a3, 0            # a3 = Azul (0)
    call    rgbLedWrite

    # 4. delay(1000);
    li      a0, 1000         # a0 = 1000 ms
    call    delay

    # 5. rgbLedWrite(LED_BUILTIN, 255, 0, 0);
    li      a0, 8            # a0 = Pino do LED
    li      a1, 255          # a1 = Vermelho (255)
    li      a2, 0            # a2 = Verde (0)
    li      a3, 0            # a3 = Azul (0)
    call    rgbLedWrite

    # 6. delay(4000);
    li      a0, 4000         # a0 = 4000 ms
    call    delay

    # Restaura a pilha e regressa (para o Arduino chamar o loop de novo)
    lw      ra, 12(sp)       
    addi    sp, sp, 16       
    ret