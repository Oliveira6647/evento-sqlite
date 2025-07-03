import sqlite3
import csv
from colorama import init, Fore, Style

init(autoreset=True)  # Inicializa o colorama

def conectar():
    return sqlite3.connect('evento.db')

# Mostrar lista de empresas ou salas com IDs
def mostrar_tabela(conn, tabela):
    cursor = conn.cursor()
    cursor.execute(f"SELECT id, name FROM {tabela}")
    print(Fore.YELLOW + f"\n📋 Lista de {tabela}s:")
    for row in cursor.fetchall():
        print(f"{row[0]} - {row[1]}")

# Inserção de dados com cores e validação
def inserir_dados(conn):
    print(Fore.CYAN + "\n=== Inserir novos dados ===")
    print("[1] Empresa")
    print("[2] Participante")
    print("[3] Sala")
    print("[4] Apresentação")
    print("[5] Inscrever participante em apresentação")
    subopcao = input(Fore.GREEN + "Escolha uma opção: ")
    cursor = conn.cursor()

    if subopcao == '1':
        nome = input("Nome da empresa: ")
        cursor.execute("INSERT INTO company (name) VALUES (?)", (nome,))
        print(Fore.GREEN + "✅ Empresa adicionada.")

    elif subopcao == '2':
        nome = input("Nome do participante: ")
        email = input("Email: ")
        mostrar_tabela(conn, 'company')
        company_id = input("ID da empresa (deixe vazio para NULL): ")
        company_id = int(company_id) if company_id else None
        cursor.execute("INSERT INTO attendee (name, email, company_id) VALUES (?, ?, ?)", (nome, email, company_id))
        print(Fore.GREEN + "✅ Participante adicionado.")

    elif subopcao == '3':
        nome = input("Nome da sala: ")
        capacidade = int(input("Capacidade: "))
        cursor.execute("INSERT INTO room (name, capacity) VALUES (?, ?)", (nome, capacidade))
        print(Fore.GREEN + "✅ Sala adicionada.")

    elif subopcao == '4':
        titulo = input("Título da apresentação: ")
        mostrar_tabela(conn, 'room')
        room_id = int(input("ID da sala: "))
        cursor.execute("SELECT id FROM room WHERE id = ?", (room_id,))
        if cursor.fetchone():
            inicio = input("Hora de início (ex: 10:00): ")
            fim = input("Hora de fim (ex: 11:00): ")
            cursor.execute("INSERT INTO presentation (title, room_id, start_time, end_time) VALUES (?, ?, ?, ?)", (titulo, room_id, inicio, fim))
            print(Fore.GREEN + "✅ Apresentação adicionada.")
        else:
            print(Fore.RED + "❌ Sala não encontrada.")

    elif subopcao == '5':
        cursor.execute("SELECT id, title FROM presentation")
        print(Fore.YELLOW + "\nApresentações disponíveis:")
        for row in cursor.fetchall():
            print(f"{row[0]} - {row[1]}")
        presentation_id = int(input("ID da apresentação: "))

        cursor.execute("SELECT id, name FROM attendee")
        print(Fore.YELLOW + "\nParticipantes disponíveis:")
        for row in cursor.fetchall():
            print(f"{row[0]} - {row[1]}")
        attendee_id = int(input("ID do participante: "))

        cursor.execute("INSERT INTO presentation_attendee (presentation_id, attendee_id) VALUES (?, ?)", (presentation_id, attendee_id))
        print(Fore.GREEN + "✅ Participante inscrito na apresentação.")

    else:
        print(Fore.RED + "❌ Opção inválida.")

    conn.commit()

# Consultas (iguais às anteriores)
def total_participantes_por_apresentacao(conn):
    cursor = conn.cursor()
    cursor.execute("""
    SELECT presentation.title, COUNT(presentation_attendee.attendee_id) AS total_participantes
    FROM presentation
    LEFT JOIN presentation_attendee ON presentation.id = presentation_attendee.presentation_id
    GROUP BY presentation.title
    """)
    print(Fore.CYAN + "\n▶ Total de participantes por apresentação:")
    for row in cursor.fetchall():
        print(f"{row[0]} → {row[1]} participante(s)")

def participantes_da_apresentacao(conn):
    titulo = input("Digite o título da apresentação: ")
    cursor = conn.cursor()
    cursor.execute("""
    SELECT attendee.name
    FROM attendee
    JOIN presentation_attendee ON attendee.id = presentation_attendee.attendee_id
    JOIN presentation ON presentation.id = presentation_attendee.presentation_id
    WHERE presentation.title = ?
    """, (titulo,))
    resultados = cursor.fetchall()
    if resultados:
        print(Fore.CYAN + f"\n▶ Participantes da apresentação '{titulo}':")
        for row in resultados:
            print("-", row[0])
    else:
        print(Fore.RED + "❌ Nenhum participante encontrado.")

def apresentacoes_do_participante(conn):
    nome = input("Digite o nome do participante: ")
    cursor = conn.cursor()
    cursor.execute("""
    SELECT presentation.title
    FROM presentation
    JOIN presentation_attendee ON presentation.id = presentation_attendee.presentation_id
    JOIN attendee ON attendee.id = presentation_attendee.attendee_id
    WHERE attendee.name = ?
    """, (nome,))
    resultados = cursor.fetchall()
    if resultados:
        print(Fore.CYAN + f"\n▶ Apresentações que {nome} vai assistir:")
        for row in resultados:
            print("-", row[0])
    else:
        print(Fore.RED + "❌ Nenhuma apresentação encontrada.")

def empresas_e_participantes(conn):
    cursor = conn.cursor()
    cursor.execute("""
    SELECT company.name, COUNT(attendee.id) AS total_participantes
    FROM company
    LEFT JOIN attendee ON company.id = attendee.company_id
    GROUP BY company.name
    """)
    print(Fore.CYAN + "\n▶ Empresas e número de participantes:")
    for row in cursor.fetchall():
        print(f"{row[0]} → {row[1]} participante(s)")

def salas_e_apresentacoes(conn):
    cursor = conn.cursor()
    cursor.execute("""
    SELECT room.name, room.capacity, COUNT(presentation.id) AS total_apresentacoes
    FROM room
    LEFT JOIN presentation ON room.id = presentation.room_id
    GROUP BY room.name
    """)
    print(Fore.CYAN + "\n▶ Salas e número de apresentações:")
    for row in cursor.fetchall():
        print(f"{row[0]} | Capacidade: {row[1]} | Apresentações: {row[2]}")

def exportar_relatorio_csv(conn):
    cursor = conn.cursor()
    cursor.execute("""
    SELECT presentation.title, COUNT(presentation_attendee.attendee_id) AS total_participantes
    FROM presentation
    LEFT JOIN presentation_attendee ON presentation.id = presentation_attendee.presentation_id
    GROUP BY presentation.title
    """)
    resultados = cursor.fetchall()
    with open('relatorio_apresentacoes.csv', 'w', newline='', encoding='utf-8') as arquivo:
        writer = csv.writer(arquivo)
        writer.writerow(['Apresentação', 'Total de Participantes'])
        writer.writerows(resultados)
    print(Fore.GREEN + "✅ Relatório 'relatorio_apresentacoes.csv' exportado com sucesso.")

# Menu principal
def menu():
    conn = conectar()
    while True:
        print(Fore.MAGENTA + "\n===== MENU DE CONSULTAS E AÇÕES =====")
        print("[1] Total de participantes por apresentação")
        print("[2] Ver participantes de uma apresentação")
        print("[3] Ver apresentações de um participante")
        print("[4] Ver empresas e número de participantes")
        print("[5] Ver salas e número de apresentações")
        print("[6] Inserir novos dados")
        print("[7] Exportar relatório para CSV")
        print("[8] Ver participantes por empresa")
        print("[9] Ver inscritos por sala")
        print("[0] Sair")

        escolha = input(Fore.GREEN + "Escolha uma opção: ")

        if escolha == '1':
            total_participantes_por_apresentacao(conn)
        elif escolha == '2':
            participantes_da_apresentacao(conn)
        elif escolha == '3':
            apresentacoes_do_participante(conn)
        elif escolha == '4':
            empresas_e_participantes(conn)
        elif escolha == '5':
            salas_e_apresentacoes(conn)
        elif escolha == '6':
            inserir_dados(conn)
        elif escolha == '7':
            exportar_relatorio_csv(conn)
        elif escolha == '8':
            participantes_por_empresa(conn)
        elif escolha == '9':
            inscritos_por_sala(conn)
        elif escolha == '0':
            print(Fore.CYAN + "Encerrando...")
            break
        else:
            print(Fore.RED + "❗ Opção inválida. Tente novamente.")

    conn.close()

if __name__ == '__main__':
    menu()
