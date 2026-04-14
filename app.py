import sqlite3
from datetime import datetime

# ====================== CREDENCIAIS DE ACESSO ======================
USUARIO_CORRETO = "admin"
SENHA_CORRETA = "adminnuzzi26"

def verificar_login():
    print("\n" + "="*50)
    print("          SISTEMA DE VENDAS")
    print("="*50)
    
    tentativas = 3
    while tentativas > 0:
        print(f"\n--- Tentativa {4 - tentativas} de 3 ---")
        usuario = input("Usuário: ").strip()
        senha = input("Senha: ").strip()

        if usuario == USUARIO_CORRETO and senha == SENHA_CORRETA:
            print("\n✅ Acesso liberado! Bem-vindo ao sistema.\n")
            return True
        else:
            tentativas -= 1
            print("❌ Usuário ou senha incorretos!")
    
    print("\n❌ Você excedeu o número de tentativas. Sistema encerrado.")
    return False


# ====================== CONEXÃO COM O BANCO ======================
def conectar():
    # timeout maior + check_same_thread=False para maior estabilidade
    conn = sqlite3.connect('sistema_vendas.db', timeout=20)
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
    
    while True:
        preco_str = input("Preço (R$): ").strip()
        preco_str = preco_str.replace(',', '.')  
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


# ====================== REALIZAR COMPRA (Versão mais estável) ======================
def realizar_compra():
    print("\n--- Realizar Compra ---")
    
    conn = conectar()
    cursor = conn.cursor()

    try:
        data_atual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("INSERT INTO vendas (cliente_id, data_venda, total) VALUES (?, ?, 0)", 
                       (None, data_atual))
        venda_id = cursor.lastrowid
        total_venda = 0.0

        print("\n" + "="*70)
        print("          ADICIONANDO PRODUTOS À COMPRA")
        print("="*70)

        while True:
            # Lista os produtos
            cursor.execute("SELECT id, codigo, nome, preco, estoque FROM produtos ORDER BY nome")
            produtos = cursor.fetchall()

            if not produtos:
                print("Nenhum produto cadastrado ainda.")
                break

            print("\n--- Lista de Produtos ---")
            print(f"{'ID':<5} {'Código':<12} {'Nome':<35} {'Preço':<10} {'Estoque':<8}")
            print("-" * 80)
            for p in produtos:
                print(f"{p[0]:<5} {p[1] or '---':<12} {p[2]:<35} R${p[3]:<8.2f} {p[4]:<8}")

            print("\n--- Digite o NOME do produto (ou parte dele) - 0 para finalizar ---")
            busca = input("Nome do produto: ").strip()

            if busca == "0":
                break

            cursor.execute("""
                SELECT id, nome, preco, estoque 
                FROM produtos 
                WHERE nome LIKE ? 
                ORDER BY nome
            """, (f"%{busca}%",))
            
            encontrados = cursor.fetchall()

            if not encontrados:
                print("❌ Nenhum produto encontrado!")
                continue

            if len(encontrados) == 1:
                prod_id, nome_prod, preco, estoque = encontrados[0]
            else:
                print("\nProdutos encontrados:")
                for idx, (_, nome, preco, est) in enumerate(encontrados, 1):
                    print(f"{idx}. {nome} (Estoque: {est}) - R${preco:.2f}")
                
                try:
                    escolha = int(input("\nEscolha o número: "))
                    if 1 <= escolha <= len(encontrados):
                        prod_id, nome_prod, preco, estoque = encontrados[escolha-1]
                    else:
                        print("❌ Escolha inválida!")
                        continue
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

            # Insere item
            cursor.execute('''
                INSERT INTO itens_venda (venda_id, produto_id, quantidade, preco_unitario, subtotal)
                VALUES (?, ?, ?, ?, ?)
            ''', (venda_id, prod_id, qtd, preco, subtotal))

            # **Diminui o estoque**
            cursor.execute("UPDATE produtos SET estoque = estoque - ? WHERE id = ?", (qtd, prod_id))

            print(f"✅ {qtd}x {nome_prod} adicionado (Subtotal: R${subtotal:.2f})")

        # Finaliza a venda
        cursor.execute("UPDATE vendas SET total = ? WHERE id = ?", (total_venda, venda_id))
        conn.commit()

        print(f"\n🎉 Compra finalizada com sucesso!")
        print(f"   Total: R${total_venda:.2f}")

    except sqlite3.OperationalError as e:
        print(f"❌ Erro de banco (locked): {e}")
        print("   Tente novamente. Se persistir, feche o programa completamente e rode de novo.")
        conn.rollback()
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        conn.rollback()
    finally:
        conn.close()


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
        print("5. Realizar Compra")
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
            realizar_compra()
        elif opcao == "0":
            print("👋 Sistema encerrado. Até logo!")
            break
        else:
            print("❌ Opção inválida!")


# ====================== INÍCIO ======================
if __name__ == "__main__":
    if verificar_login():
        menu_principal()
