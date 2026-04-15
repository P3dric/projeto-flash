import sqlite3
from datetime import datetime

# ====================== CREDENCIAIS ======================
ADMIN_USUARIO = "admin"
ADMIN_SENHA = "adminnuzzi26"

# ====================== CONEXÃO COM O BANCO ======================
def conectar():
    conn = sqlite3.connect('sistema_vendas.db', timeout=30, isolation_level=None)
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
            total REAL NOT NULL
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS itens_venda (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            venda_id INTEGER NOT NULL,
            produto_id INTEGER NOT NULL,
            quantidade INTEGER NOT NULL,
            preco_unitario REAL NOT NULL,
            subtotal REAL NOT NULL
        )
    ''')

    conn.commit()
    conn.close()
    print("✅ Banco de dados carregado com sucesso!\n")


# ====================== LOGIN ======================
def fazer_login():
    print("\n" + "="*50)
    print("          SISTEMA DE VENDAS - LOGIN")
    print("="*50)
    
    print("\n1. Login como Administrador")
    print("2. Login como Cliente")
    print("0. Sair")
    
    opcao = input("\nEscolha uma opção: ").strip()

    if opcao == "1":
        # Login Admin
        tentativas = 3
        while tentativas > 0:
            print(f"\n--- Tentativa {4 - tentativas} de 3 ---")
            usuario = input("Usuário Admin: ").strip()
            senha = input("Senha Admin: ").strip()

            if usuario == ADMIN_USUARIO and senha == ADMIN_SENHA:
                print("\n✅ Login de Administrador realizado com sucesso!\n")
                return "admin", None
            else:
                tentativas -= 1
                print("❌ Usuário ou senha incorretos!")
        
        print("\n❌ Excedeu o número de tentativas.")
        return None, None

    elif opcao == "2":
        # Login Cliente
        listar_clientes_simples()
        try:
            cliente_id = int(input("\nDigite seu ID de Cliente: ").strip())
            conn = conectar()
            cursor = conn.cursor()
            cursor.execute("SELECT id, nome FROM clientes WHERE id = ?", (cliente_id,))
            cliente = cursor.fetchone()
            conn.close()

            if cliente:
                print(f"\n✅ Bem-vindo, {cliente[1]}!\n")
                return "cliente", cliente[0]
            else:
                print("❌ Cliente não encontrado!")
                return None, None
        except:
            print("❌ ID inválido!")
            return None, None

    elif opcao == "0":
        print("👋 Até logo!")
        return None, None
    else:
        print("❌ Opção inválida!")
        return None, None


def listar_clientes_simples():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT id, nome FROM clientes ORDER BY nome")
    clientes = cursor.fetchall()
    conn.close()

    if not clientes:
        print("Nenhum cliente cadastrado ainda.")
        return

    print("\n--- Clientes Cadastrados ---")
    for c in clientes:
        print(f"ID: {c[0]:<5} | Nome: {c[1]}")


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


# ====================== VER MEUS DADOS (Novo!) ======================
def ver_meus_dados(cliente_id):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT nome, cpf, telefone, email, endereco 
        FROM clientes 
        WHERE id = ?
    """, (cliente_id,))
    cliente = cursor.fetchone()
    conn.close()

    if not cliente:
        print("❌ Dados não encontrados.")
        return

    print("\n" + "="*60)
    print("          MEUS DADOS")
    print("="*60)
    print(f"Nome completo     : {cliente[0]}")
    print(f"CPF               : {cliente[1] or 'Não informado'}")
    print(f"Telefone          : {cliente[2] or 'Não informado'}")
    print(f"Email             : {cliente[3] or 'Não informado'}")
    print(f"Endereço          : {cliente[4] or 'Não informado'}")
    print("="*60)


# ====================== PRODUTOS ======================
def cadastrar_produto():
    print("\n--- Cadastro de Produto ---")
    nome = input("Nome do produto: ").strip()
    codigo = input("Código do produto (opcional): ").strip() or None
    
    while True:
        preco_str = input("Preço (R$): ").strip().replace(',', '.')
        try:
            preco = float(preco_str)
            if preco <= 0:
                print("❌ O preço deve ser maior que zero!")
                continue
            break
        except ValueError:
            print("❌ Preço inválido!")

    while True:
        estoque_str = input("Quantidade em estoque inicial: ").strip()
        try:
            estoque = int(estoque_str)
            if estoque < 0:
                print("❌ O estoque não pode ser negativo!")
                continue
            break
        except ValueError:
            print("❌ Quantidade inválida!")

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


# ====================== REALIZAR COMPRA ======================
def realizar_compra(cliente_id=None):
    print("\n--- Realizar Compra ---")
    
    conn = conectar()
    cursor = conn.cursor()

    try:
        data_atual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("INSERT INTO vendas (cliente_id, data_venda, total) VALUES (?, ?, 0)", 
                       (cliente_id, data_atual))
        venda_id = cursor.lastrowid
        total_venda = 0.0

        print("\n" + "="*70)
        print("          ADICIONANDO PRODUTOS À COMPRA")
        print("="*70)
        print("Dica: Deixe o nome em branco e aperte ENTER para finalizar\n")

        while True:
            cursor.execute("SELECT id, codigo, nome, preco, estoque FROM produtos ORDER BY nome")
            produtos = cursor.fetchall()

            if not produtos:
                print("Nenhum produto cadastrado.")
                break

            print("\n--- Lista de Produtos ---")
            print(f"{'ID':<5} {'Código':<12} {'Nome':<35} {'Preço':<10} {'Estoque':<8}")
            print("-" * 80)
            for p in produtos:
                print(f"{p[0]:<5} {p[1] or '---':<12} {p[2]:<35} R${p[3]:<8.2f} {p[4]:<8}")

            busca = input("\nNome do produto: ").strip()

            if busca == "":
                break

            cursor.execute("SELECT id, nome, preco, estoque FROM produtos WHERE nome LIKE ?", (f"%{busca}%",))
            encontrados = cursor.fetchall()

            if not encontrados:
                print("❌ Nenhum produto encontrado!")
                continue

            if len(encontrados) == 1:
                prod_id, nome_prod, preco, estoque = encontrados[0]
            else:
                print("\nProdutos encontrados:")
                for idx, (_, nome, preco, est) in enumerate(encontrados, 1):
                    print(f"{idx}. {nome} (Estoque: {est})")
                try:
                    escolha = int(input("\nEscolha o número: "))
                    prod_id, nome_prod, preco, estoque = encontrados[escolha-1]
                except:
                    print("❌ Escolha inválida!")
                    continue

            if estoque <= 0:
                print(f"❌ {nome_prod} sem estoque!")
                continue

            try:
                qtd = int(input(f"Quantidade (máximo {estoque}): "))
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

            print(f"✅ {qtd}x {nome_prod} adicionado → R${subtotal:.2f}")

        if total_venda > 0:
            cursor.execute("UPDATE vendas SET total = ? WHERE id = ?", (total_venda, venda_id))
            conn.commit()
            print("\n" + "="*60)
            print("🎉 COMPRA REALIZADA COM SUCESSO!")
            print("="*60)
            print(f"   Total: R${total_venda:.2f}")
            print("="*60)
        else:
            print("\nNenhum produto adicionado.")

    except Exception as e:
        print(f"❌ Erro: {e}")
        conn.rollback()
    finally:
        conn.close()


# ====================== MENU PRINCIPAL ======================
def menu_admin():
    while True:
        print("\n" + "="*60)
        print("          MENU ADMINISTRADOR")
        print("="*60)
        print("1. Cadastrar Cliente")
        print("2. Listar Clientes")
        print("3. Cadastrar Produto")
        print("4. Listar Produtos")
        print("5. Realizar Compra")
        print("0. Sair")
        print("="*60)

        opcao = input("\nEscolha uma opção: ").strip()

        if opcao == "1": cadastrar_cliente()
        elif opcao == "2": listar_clientes()
        elif opcao == "3": cadastrar_produto()
        elif opcao == "4": listar_produtos()
        elif opcao == "5": realizar_compra()
        elif opcao == "0":
            print("👋 Saindo do sistema...")
            break
        else:
            print("❌ Opção inválida!")


def menu_cliente(cliente_id):
    while True:
        print("\n" + "="*60)
        print("          MENU CLIENTE")
        print("="*60)
        print("1. Realizar Compra")
        print("2. Ver Meus Dados")
        print("0. Sair")
        print("="*60)

        opcao = input("\nEscolha uma opção: ").strip()

        if opcao == "1":
            realizar_compra(cliente_id)
        elif opcao == "2":
            ver_meus_dados(cliente_id)
        elif opcao == "0":
            print("👋 Até logo!")
            break
        else:
            print("❌ Opção inválida!")


# ====================== INÍCIO DO PROGRAMA ======================
if __name__ == "__main__":
    criar_tabelas()
    
    tipo_usuario, cliente_id = fazer_login()
    
    if tipo_usuario == "admin":
        menu_admin()
    elif tipo_usuario == "cliente":
        menu_cliente(cliente_id)
