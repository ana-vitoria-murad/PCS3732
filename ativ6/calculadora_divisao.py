import time

CPU_FREQ_MHZ = 1200

def calcular_limites(bits):
    min_val = -(1 << (bits - 1))
    max_val = (1 << (bits - 1)) - 1
    return min_val, max_val

def para_signed_nbits(valor, bits):
    mask = (1 << bits) - 1
    bits_isolados = valor & mask
    threshold = 1 << (bits - 1)
    if bits_isolados >= threshold:
        return bits_isolados - (1 << bits)
    return bits_isolados

def para_binario_nbits(valor, bits):
    mask = (1 << bits) - 1
    bits_isolados = valor & mask
    return f"{bits_isolados:0{bits}b}"

def multiply(a, b):
    result = 0
    abs_b = abs(b)
    for _ in range(abs_b):
        result += a
    return -result if b < 0 else result

def divide_op(a, b):
    return int(a / b)

def factorial(n):
    if n <= 1:
        return 1
    result = 1
    for i in range(2, n + 1):
        result *= i
    return result

def obter_inteiro_nbits(mensagem, min_val, max_val):
    while True:
        try:
            num = int(input(mensagem))
            if min_val <= num <= max_val:
                return num
            print(f"O número deve estar entre {min_val} e {max_val}.")
        except ValueError:
            print("Por favor, insira um número inteiro válido.")

def executar_benchmark(func, *args):
    start_time = time.perf_counter_ns()
    resultado_real = func(*args)
    end_time = time.perf_counter_ns()
    
    elapsed_ns = end_time - start_time
    elapsed_cycles = int((elapsed_ns * CPU_FREQ_MHZ) / 1000)
    
    return resultado_real, elapsed_cycles, float(elapsed_ns)

def main():
    print("=== BENCHMARK FORÇANDO ERRO DE DIVISÃO (Raspberry Pi 3) ===")
    
    while True:
        try:
            largura_bits = int(input("Escolha a largura de bits (ex: 4, 8, 16, 32): "))
            if largura_bits >= 2:
                break
        except ValueError:
            pass
            
    min_val, max_val = calcular_limites(largura_bits)
    
    while True:
        print("\nMenu de Operações:")
        print("1. Soma (+)")
        print("2. Subtração (-)")
        print("3. Multiplicação (*)")
        print("4. Divisão (/)")
        print("5. Fatorial (!)")
        print("6. Sair")
        
        opcao = input("Escolha uma opção (1-6): ")
        
        if opcao == '6':
            break
            
        if opcao in ['1', '2', '3', '4']:
            a = obter_inteiro_nbits(f"Operando A ({min_val} a {max_val}): ", min_val, max_val)
            b = obter_inteiro_nbits(f"Operando B ({min_val} a {max_val}): ", min_val, max_val)
            
            if opcao == '1':
                res_real, ciclos, tempo = executar_benchmark(lambda x, y: x + y, a, b)
            elif opcao == '2':
                res_real, ciclos, tempo = executar_benchmark(lambda x, y: x - y, a, b)
            elif opcao == '3':
                res_real, ciclos, tempo = executar_benchmark(multiply, a, b)
            elif opcao == '4':
                # Aqui o erro vai acontecer e vai quebrar a execução do programa
                res_real, ciclos, tempo = executar_benchmark(divide_op, a, b)
                
        elif opcao == '5':
            a = obter_inteiro_nbits(f"Operando A (0 a {max_val}): ", 0, max_val)
            res_real, ciclos, tempo = executar_benchmark(factorial, a)
        else:
            continue

        res_nbits = para_signed_nbits(res_real, largura_bits)
        bin_nbits = para_binario_nbits(res_real, largura_bits)

        print(f"\nResultado ULA: {res_nbits} | Tempo: {tempo:.2f} ns")

if __name__ == "__main__":
    main()
