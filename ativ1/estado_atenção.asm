# -----------------------------------------------------
# Função setup()
# -----------------------------------------------------
setup:
    # Prepara a pilha (stack) para guardar o endereço de retorno
    addi    sp, sp, -16      
    sw      ra, 12(sp)       # Guarda o registador de retorno (ra)

    # pinMode(LED_BUILTIN, OUTPUT);
    li      a0, 8            # Carrega o pino do LED (assumindo que o LED_BUILTIN é 8) no registador a0
    li      a1, 2            # Carrega a constante OUTPUT (geralmente 2 ou 3) no registador a1
    call    pinMode          # Salta para a função pinMode na biblioteca

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

    # 1. rgbLedWrite(LED_BUILTIN, 255, 255, 0);
    li      a0, 8            # a0 = Pino do LED
    li      a1, 255          # a1 = Vermelho (255)
    li      a2, 255          # a2 = Verde (255)
    li      a3, 0            # a3 = Azul (0)
    call    rgbLedWrite

    # 2. digitalWrite(LED_BUILTIN, HIGH);
    li      a0, 8            # a0 = Pino do LED
    li      a1, 1            # a1 = HIGH (1)
    call    digitalWrite

    # 3. delay(1000);
    li      a0, 1000         # a0 = 1000 milissegundos
    call    delay

    # 4. digitalWrite(LED_BUILTIN, LOW);
    li      a0, 8            # a0 = Pino do LED
    li      a1, 0            # a1 = LOW (0)
    call    digitalWrite

    # 5. delay(1000);
    li      a0, 1000         # a0 = 1000 milissegundos
    call    delay

    # Restaura a pilha e regressa (para o Arduino chamar o loop novamente)
    lw      ra, 12(sp)       
    addi    sp, sp, 16       
    ret