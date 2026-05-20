# -----------------------------------------------------
# Função setup()
# -----------------------------------------------------
setup:
    # Prepara a pilha (stack) para guardar o endereço de retorno
    addi    sp, sp, -16      
    sw      ra, 12(sp)       # Guarda o registador de retorno (ra)

    # pinMode(LED_BUILTIN, OUTPUT);
    li      a0, 8            # Carrega o número do pino do LED (ex: 8) no registador a0
    li      a1, 2            # Carrega a constante OUTPUT (que internamente é 2) no registador a1
    call    pinMode          # Salta para a função pinMode na biblioteca base do Arduino

    # Restaura a pilha e regressa
    lw      ra, 12(sp)       
    addi    sp, sp, 16       
    ret                      

# -----------------------------------------------------
# Função loop()
# -----------------------------------------------------
loop:
    # Prepara a pilha para a função loop
    addi    sp, sp, -16      
    sw      ra, 12(sp)       

    # 1. digitalWrite(LED_BUILTIN, HIGH);
    li      a0, 8            # a0 = Pino do LED (8)
    li      a1, 1            # a1 = Nível HIGH (1)
    call    digitalWrite     # Chama a função para aplicar tensão no pino

    # 2. delay(1000);
    li      a0, 1000         # a0 = 1000 milissegundos (1 segundo)
    call    delay            # Chama a função que faz o processador esperar

    # 3. digitalWrite(LED_BUILTIN, LOW);
    li      a0, 8            # a0 = Pino do LED (8)
    li      a1, 0            # a1 = Nível LOW (0)
    call    digitalWrite     # Chama a função para cortar a tensão no pino

    # 4. delay(1000);
    li      a0, 1000         # a0 = 1000 milissegundos (1 segundo)
    call    delay            # Chama a função que faz o processador esperar

    # Restaura a pilha e regressa (para o sistema operativo interno chamar o loop de novo)
    lw      ra, 12(sp)       
    addi    sp, sp, 16       
    ret