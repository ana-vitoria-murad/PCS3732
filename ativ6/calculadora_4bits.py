import math

def truncar_4bits(valor):
    return valor & 0x0F

def obter_entrada_4bits(ordem):
    while True:
        try:
            num = int(input(f"Digite o número {ordem} (0 a 15): "))
            if 0 <= num <= 15:
                return num
            print("Erro: O número deve estar entre 0 e 15 (4 bits).")
        except ValueError:
            print("Por favor, digite um número inteiro válido.")

def mostrar_resultado(operacao, res_completo):
    res_4bits = truncar_4bits(res_completo)
    print("\n" + "="*30)
    print(f"Resultado da {operacao}:")
    print(f"  Decimal (Real): {res_completo}")
    print(f"  Decimal (4-bits): {res_4bits}")
    print(f"  Binário (4-bits): {res_4bits:04b}")
    if res_completo > 15:
        print("Ocorreu Overflow!")
    print("="*30 + "\n")

def main():
    print("=== CALCULADORA BINÁRIA 4-BITS (Raspberry Pi 3) ===")
    
    while True:
        print("Menu de Operações:")
        print("1. Soma (+)")
        print("2. Subtração (-)")
        print("3. Multiplicação (*)")
        print("4. Fatorial (!)")
        print("5. Sair")
        
        opcao = input("Escolha uma opção (1-5): ")
        
        if opcao == '5':
            print("Saindo")
            break
            
        if opcao in ['1', '2', '3']:
            a = obter_entrada_4bits("A")
            b = obter_entrada_4bits("B")
            
            if opcao == '1':
                mostrar_resultado("Soma", a + b)
            elif opcao == '2':
                mostrar_resultado("Subtração", a - b)
            elif opcao == '3':
                mostrar_resultado("Multiplicação", a * b)
                
        elif opcao == '4':
            a = obter_entrada_4bits("A")
            res_fat = math.factorial(a)
            mostrar_resultado(f"Fatorial de {a}", res_fat)
        else:
            print("Opção inválida! \n")

if __name__ == "__main__":
    main()
