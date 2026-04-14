import sqlite3
from datetime import datetime


SENHA_CORRETA = "adminnuzzi26" 

def verificar_senha():
    print("\n" + "="*50)
    print("          SISTEMA DE VENDAS")
    print("="*50)
    
    tentativas = 3
    while tentativas > 0:
        senha = input(f"\nDigite a senha para acessar ({tentativas} tentativas restantes): ")
        
        if senha == SENHA_CORRETA:
            print("✅ Acesso liberado! Bem-vindo ao sistema.\n")
            return True
        else:
            tentativas -= 1
            print("❌ Senha incorreta!")
    
    print("❌ Você excedeu o número de tentativas. Sistema encerrado.")
    return False


# ====================== CONEXÃO COM O BANCO ======================
def conectar():
    conn = sqlite3.connect('sistema_vendas.db')
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def criar_tabelas():
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS clientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            cpf TEXT UNIQUE,
            telefone TEXT,
            email TEXT,
            endereco TEXT
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS produtos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            codigo TEXT UNIQUE,
            nome TEXT NOT NULL,
            preco REAL NOT NULL,
            estoque INTEGER NOT NULL DEFAULT 0
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS vendas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cliente_id INTEGER,
            data_venda TEXT NOT NULL,
            total REAL NOT NULL,
            FOREIGN KEY (cliente_id) REFERENCES clientes(id)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS itens_venda (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            venda_id INTEGER NOT NULL,
            produto_id INTEGER NOT NULL,
            quantidade INTEGER NOT NULL,
            preco_unitario REAL NOT NULL,
            subtotal REAL NOT NULL,
            FOREIGN KEY (venda_id) REFERENCES vendas(id),
            FOREIGN KEY (produto_id) REFERENCES produtos(id)
        )
    ''')

    conn.commit()
    conn.close()
    print("✅ Banco de dados carregado com sucesso!\n")


# ====================== CLIENTES ======================
def cadastrar_cliente():
    print("\n--- Cadastro de Cliente ---")
    nome = input("Nome completo: ").strip()
    cpf = input("CPF (opcional): ").strip() or None
    telefone = input("Telefone: ").strip() or None
    email = input("Email: ").strip() or None
    endereco = input("Endereço: ").strip() or None

    conn = conectar()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO clientes (nome, cpf, telefone, email, endereco)
            VALUES (?, ?, ?, ?, ?)
        ''', (nome, cpf, telefone, email, endereco))
        conn.commit()
        print("✅ Cliente cadastrado com sucesso!")
    except sqlite3.IntegrityError:
        print("❌ Erro: CPF já cadastrado!")
    finally:
        conn.close()


def listar_clientes():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT id, nome, cpf, telefone FROM clientes ORDER BY nome")
    clientes = cursor.fetchall()
    conn.close()

    if not clientes:
        print("Nenhum cliente cadastrado.")
        return

    print("\n--- Lista de Clientes ---")
    print(f"{'ID':<5} {'Nome':<30} {'CPF':<15} {'Telefone':<15}")
    print("-" * 70)
    for c in clientes:
        print(f"{c[0]:<5} {c[1]:<30} {c[2] or '---':<15} {c[3] or '---':<15}")


# ====================== PRODUTOS ======================
def cadastrar_produto():
    print("\n--- Cadastro de Produto ---")
    nome = input("Nome do produto: ").strip()
    codigo = input("Código do produto (opcional): ").strip() or None
    
    try:
        preco = float(input("Preço (R$): "))
        estoque = int(input("Quantidade em estoque: "))
    except ValueError:
        print("❌ Valores inválidos!")
        return

    conn = conectar()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO produtos (codigo, nome, preco, estoque)
            VALUES (?, ?, ?, ?)
        ''', (codigo, nome, preco, estoque))
        conn.commit()
        print("✅ Produto cadastrado com sucesso!")
    except sqlite3.IntegrityError:
        print("❌ Erro: Código já existe!")
    finally:
        conn.close()


def listar_produtos():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT id, codigo, nome, preco, estoque FROM produtos ORDER BY nome")
    produtos = cursor.fetchall()
    conn.close()

    if not produtos:
        print("Nenhum produto cadastrado.")
        return

    print("\n--- Lista de Produtos ---")
    print(f"{'ID':<5} {'Código':<12} {'Nome':<35} {'Preço':<10} {'Estoque':<8}")
    print("-" * 80)
    for p in produtos:
        print(f"{p[0]:<5} {p[1] or '---':<12} {p[2]:<35} R${p[3]:<8.2f} {p[4]:<8}")


# ====================== VENDAS ======================
def realizar_venda():
    listar_clientes()
    try:
        cliente_id = int(input("\nDigite o ID do cliente (0 = Venda sem cliente): "))
        if cliente_id == 0:
            cliente_id = None
    except:
        cliente_id = None

    conn = conectar()
    cursor = conn.cursor()

    data_atual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("INSERT INTO vendas (cliente_id, data_venda, total) VALUES (?, ?, 0)", 
                   (cliente_id, data_atual))
    venda_id = cursor.lastrowid
    total_venda = 0

    print("\n--- Realizar Venda (digite 0 para finalizar) ---")
    while True:
        listar_produtos()
        try:
            prod_id = int(input("\nID do produto (0 = Finalizar venda): "))
            if prod_id == 0:
                break
        except:
            print("ID inválido!")
            continue

        cursor.execute("SELECT nome, preco, estoque FROM produtos WHERE id = ?", (prod_id,))
        produto = cursor.fetchone()
        if not produto:
            print("Produto não encontrado!")
            continue

        nome_prod, preco, estoque = produto
        try:
            qtd = int(input(f"Quantidade (estoque disponível: {estoque}): "))
            if qtd <= 0 or qtd > estoque:
                print("❌ Quantidade inválida!")
                continue
        except:
            print("❌ Quantidade inválida!")
            continue

        subtotal = preco * qtd
        total_venda += subtotal

        cursor.execute('''
            INSERT INTO itens_venda (venda_id, produto_id, quantidade, preco_unitario, subtotal)
            VALUES (?, ?, ?, ?, ?)
        ''', (venda_id, prod_id, qtd, preco, subtotal))

        cursor.execute("UPDATE produtos SET estoque = estoque - ? WHERE id = ?", (qtd, prod_id))

        print(f"✅ {qtd}x {nome_prod} adicionado (Subtotal: R${subtotal:.2f})")

    cursor.execute("UPDATE vendas SET total = ? WHERE id = ?", (total_venda, venda_id))
    conn.commit()
    conn.close()

    print(f"\n🎉 Venda finalizada com sucesso! Total: R${total_venda:.2f}")


def listar_vendas():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT v.id, v.data_venda, c.nome, v.total
        FROM vendas v
        LEFT JOIN clientes c ON v.cliente_id = c.id
        ORDER BY v.id DESC
    ''')
    vendas = cursor.fetchall()
    conn.close()

    if not vendas:
        print("Nenhuma venda registrada.")
        return

    print("\n--- Histórico de Vendas ---")
    print(f"{'ID':<5} {'Data':<20} {'Cliente':<30} {'Total':<12}")
    print("-" * 75)
    for v in vendas:
        cliente = v[2] if v[2] else "Cliente não informado"
        print(f"{v[0]:<5} {v[1]:<20} {cliente:<30} R${v[3]:.2f}")


# ====================== MENU PRINCIPAL ======================
def menu_principal():
    criar_tabelas()

    while True:
        print("\n" + "="*60)
        print("          SISTEMA DE VENDAS - MENU PRINCIPAL")
        print("="*60)
        print("1. Cadastrar Cliente")
        print("2. Listar Clientes")
        print("3. Cadastrar Produto")
        print("4. Listar Produtos")
        print("5. Realizar Venda")
        print("6. Listar Vendas")
        print("0. Sair")
        print("="*60)

        opcao = input("\nEscolha uma opção: ").strip()

        if opcao == "1":
            cadastrar_cliente()
        elif opcao == "2":
            listar_clientes()
        elif opcao == "3":
            cadastrar_produto()
        elif opcao == "4":
            listar_produtos()
        elif opcao == "5":
            realizar_venda()
        elif opcao == "6":
            listar_vendas()
        elif opcao == "0":
            print("👋 Sistema encerrado. Até logo!")
            break
        else:
            print("❌ Opção inválida! Tente novamente.")


# ====================== INÍCIO DO PROGRAMA ======================
if __name__ == "__main__":
    if verificar_senha():           
        menu_principal()