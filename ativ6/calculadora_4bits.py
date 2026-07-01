import time

CPU_FREQ_MHZ = 1200

def para_signed_4bits(valor):
    bits = valor & 0x0F
    if bits >= 8:
        return bits - 16
    return bits

def para_binario_4bits(valor):
    bits = valor & 0x0F
    return f"{bits:04b}"

def multiply(a, b):
    result = 0
    abs_b = abs(b)
    for _ in range(abs_b):
        result += a
    return -result if b < 0 else result

def factorial(n):
    """Fatorial por laço"""
    if n <= 1:
        return 1
    result = 1
    for i in range(2, n + 1):
        result *= i
    return result

def obter_inteiro_4bits(mensagem):
    while True:
        try:
            num = int(input(mensagem))
            if -8 <= num <= 7:
                return num
            print("Erro: O número deve estar entre -8 e 7 (limite de 4 bits com sinal).")
        except ValueError:
            print("Por favor, insira um número inteiro válido.")

def executar_benchmark(op_nome, func, *args):
    """Captura o tempo de execução e calcula os ciclos de CPU equivalentes"""
    start_time = time.perf_counter_ns()
    resultado_real = func(*args)
    end_time = time.perf_counter_ns()
    
    elapsed_ns = end_time - start_time
    # Ciclos = (Tempo em ns * Frequência em MHz) / 1000
    elapsed_cycles = int((elapsed_ns * CPU_FREQ_MHZ) / 1000)
    
    return resultado_real, elapsed_cycles, float(elapsed_ns)

def main():
    print(f"=== BENCHMARK CALCULADORA 4-BITS: COMPLEMENTO DE DOIS ===")
    print(f"Frequência da CPU: {CPU_FREQ_MHZ} MHz")
    
    while True:
        print("\nMenu de Operações:")
        print("1. Soma (+)")
        print("2. Subtração (-)")
        print("3. Multiplicação (*)")
        print("4. Fatorial (!)")
        print("5. Sair")
        
        opcao = input("Escolha uma opção (1-5): ")
        
        if opcao == '5':
            print("Encerrando benchmark.")
            break
            
        if opcao in ['1', '2', '3']:
            a = obter_inteiro_4bits("Operando A (-8 a 7): ")
            b = obter_inteiro_4bits("Operando B (-8 a 7): ")
            
            if opcao == '1':
                res_real, ciclos, tempo = executar_benchmark("soma", lambda x, y: x + y, a, b)
                op_str = "soma"
            elif opcao == '2':
                res_real, ciclos, tempo = executar_benchmark("subtracao", lambda x, y: x - y, a, b)
                op_str = "subtracao"
            elif opcao == '3':
                res_real, ciclos, tempo = executar_benchmark("multiplicacao", multiply, a, b)
                op_str = "multiplicacao"
                
        elif opcao == '4':
            a = obter_inteiro_4bits("Operando A (Fatorial: 0 a 7): ")
            if a < 0:
                print("Fatorial exige número maior ou igual a 0.")
                continue
            res_real, ciclos, tempo = executar_benchmark("fatorial", factorial, a)
            op_str = "fatorial"
        else:
            print("Opção inválida. Tente novamente.")
            continue

        # Aplica o comportamento de 4 bits no resultado final
        res_4bits = para_signed_4bits(res_real)
        bin_4bits = para_binario_4bits(res_real)

        # Exibição dos resultados
        print(f"\nResultado Matemático Real: {res_real}")
        print(f"Resultado ULA (4-bits Signed): {res_4bits}")
        print(f"Representação Binária: {bin_4bits}")
        
        if res_real < -8 or res_real > 7:
            print("Ocorreu Overflow Aritmético!")
            
        print(f"Operação: {op_str} | Ciclos da CPU: {ciclos} | Tempo de processamento: {tempo:.2f} ns")
        print("-" * 50)

if __name__ == "__main__":
    main()
