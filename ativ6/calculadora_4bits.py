import time

CPU_FREQ_MHZ = 1200

def multiply(a, b):
    result = 0
    abs_b = abs(b)
    for _ in range(abs_b):
        result += a
    return -result if b < 0 else result

def factorial(n):
    if n <= 1:
        return 1
    result = 1
    for i in range(2, n + 1):
        result *= i
    return result

def obter_inteiro(mensagem):
    while True:
        try:
            return int(input(mensagem))
        except ValueError:
            print("Por favor, insira um número inteiro válido.")

def executar_benchmark(op_nome, func, *args):
    start_time = time.perf_counter_ns()
    resultado = func(*args)
    end_time = time.perf_counter_ns()
    
    elapsed_ns = end_time - start_time
    # Ciclos = (Tempo em ns * Frequência em MHz) / 1000
    elapsed_cycles = int((elapsed_ns * CPU_FREQ_MHZ) / 1000)
    
    return resultado, elapsed_cycles, float(elapsed_ns)

def main():
    print(f"=== BENCHMARK CALCULADORA RASPBERRY PI 3 ({CPU_FREQ_MHZ} MHz) ===")
    
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
            a = obter_inteiro("Operando A: ")
            b = obter_inteiro("Operando B: ")
            
            if opcao == '1':
                res, ciclos, tempo = executar_benchmark("soma", lambda x, y: x + y, a, b)
                op_str = "soma"
            elif opcao == '2':
                res, ciclos, tempo = executar_benchmark("subtracao", lambda x, y: x - y, a, b)
                op_str = "subtracao"
            elif opcao == '3':
                res, ciclos, tempo = executar_benchmark("multiplicacao", multiply, a, b)
                op_str = "multiplicacao"
                
        elif opcao == '4':
            a = obter_inteiro("Operando A (Fatorial): ")
            if a < 0:
                print("Fatorial exige número maior ou igual a 0.")
                continue
            res, ciclos, tempo = executar_benchmark("fatorial", factorial, a)
            op_str = "fatorial"
        else:
            print("Opção inválida. Tente novamente.")
            continue

        # Exibição dos resultados no mesmo padrão do monitor Serial do seu ESP32
        print(f"\nResultado ULA: {res}")
        print(f"Operação: {op_str} | Ciclos da CPU: {ciclos} | Tempo de processamento: {tempo:.2f} ns")
        print("-" * 50)

if __name__ == "__main__":
    main()
