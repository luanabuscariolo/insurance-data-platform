"""Gera dados sintéticos de seguros, com sujeira proposital, na pasta data/raw/."""
from pathlib import Path
from datetime import date, timedelta
import random
import string

from faker import Faker
import pandas as pd

fake = Faker("pt_BR")
Faker.seed(42)
random.seed(42)

RAW_DIR = Path("data/raw")
RAW_DIR.mkdir(parents=True, exist_ok=True)

N_CLIENTES = 20_000
N_CORRETORES = 500

CIDADES = [
    ("São Paulo", "SP"),
    ("Campinas", "SP"),
    ("Santos", "SP"),
    ("São José dos Campos", "SP"),
    ("Rio de Janeiro", "RJ"),
    ("Niterói", "RJ"),
    ("Petrópolis", "RJ"),
    ("Belo Horizonte", "MG"),
    ("Uberlândia", "MG"),
    ("Juiz de Fora", "MG"),
    ("Curitiba", "PR"),
    ("Londrina", "PR"),
    ("Maringá", "PR"),
    ("Florianópolis", "SC"),
    ("Joinville", "SC"),
    ("Blumenau", "SC"),
    ("Porto Alegre", "RS"),
    ("Caxias do Sul", "RS"),
    ("Pelotas", "RS"),
    ("Salvador", "BA"),
    ("Feira de Santana", "BA"),
    ("Vitória da Conquista", "BA"),
    ("Recife", "PE"),
    ("Caruaru", "PE"),
    ("Petrolina", "PE"),
    ("Fortaleza", "CE"),
    ("Juazeiro do Norte", "CE"),
    ("Natal", "RN"),
    ("Mossoró", "RN"),
    ("João Pessoa", "PB"),
    ("Campina Grande", "PB"),
    ("Maceió", "AL"),
    ("Arapiraca", "AL"),
    ("Aracaju", "SE"),
    ("Teresina", "PI"),
    ("Parnaíba", "PI"),
    ("São Luís", "MA"),
    ("Imperatriz", "MA"),
    ("Belém", "PA"),
    ("Santarém", "PA"),
    ("Manaus", "AM"),
    ("Parintins", "AM"),
    ("Macapá", "AP"),
    ("Boa Vista", "RR"),
    ("Porto Velho", "RO"),
    ("Ji-Paraná", "RO"),
    ("Rio Branco", "AC"),
    ("Palmas", "TO"),
    ("Araguaína", "TO"),
    ("Goiânia", "GO"),
    ("Anápolis", "GO"),
    ("Cuiabá", "MT"),
    ("Rondonópolis", "MT"),
    ("Campo Grande", "MS"),
    ("Dourados", "MS"),
    ("Brasília", "DF"),
    ("Vitória", "ES"),
    ("Vila Velha", "ES"),
]

REGIOES = ["Sudeste", "Sul", "Nordeste", "Norte", "Centro-Oeste"]

COBERTURAS_POR_TIPO = {
    "auto": ["colisao", "roubo_furto", "terceiros", "vidros"],
    "residencial": ["incendio", "roubo", "danos_eletricos", "responsabilidade_civil"],
    "saude": ["consultas", "internacao", "exames", "odontologico"],
}

STATUS_SINISTRO_VARIANTES = {
    "pendente": ["pendente", "Pendente", "PENDENTE", "pending"],
    "em_analise": ["em_analise", "Em Análise", "EM ANALISE", "in_review"],
    "aprovado": ["aprovado", "Aprovado", "APROVADO", "approved"],
    "rejeitado": ["rejeitado", "Rejeitado", "REJEITADO", "rejected"],
}

CANAL_VARIANTES = {
    "app": ["app", "App", "APP"],
    "telefone": ["telefone", "Telefone", "TELEFONE", "phone"],
    "presencial": ["presencial", "Presencial", "PRESENCIAL"],
    "email": ["email", "e-mail", "Email", "EMAIL"],
}

METODO_PAGAMENTO_VARIANTES = {
    "pix": ["pix", "Pix", "PIX"],
    "boleto": ["boleto", "Boleto", "BOLETO"],
    "transferencia": ["transferencia", "Transferência", "TED/DOC"],
    "cartao": ["cartao", "Cartão", "cartao_credito"],
}

STATUS_PAGAMENTO_VARIANTES = {
    "concluido": ["concluido", "Concluído", "CONCLUIDO", "completed"],
    "pendente": ["pendente", "Pendente", "PENDING"],
    "estornado": ["estornado", "Estornado", "refunded"],
}

def cpf_falso() -> str:
    return "".join(random.choices(string.digits, k=11))

def telefone_sujo()-> str:
    ddd = random.randint(11, 99)
    numero = "9" + "".join(random.choices(string.digits, k=8))
    formato = random.choice(["plain","parens","spaces"])
    if formato == "plain":
        return f"{ddd}{numero}"
    elif formato == "parens":
        return f"({ddd}) {numero[:5]}-{numero[5:]}"
    else:
        return f"{ddd} {numero[:5]} {numero[5:]}"

def cidade_suja(cidade: str) -> str:
    r = random.random()
    if r < 0.1:
        return cidade.upper()
    elif r < 0.2:
        return cidade.lower()
    elif r < 0.3:
        return f" {cidade} "
    else:
        return cidade
    
def data_suja(d: date) -> str:
    if random.random() < 0.5:
        return d.strftime("%Y-%m-%d")
    return d.strftime("%d/%m/%Y")

def bool_sujo(valor: bool):
    if valor:
        return random.choice(["True", "1", "sim", "S", "Sim"])
    return random.choice(["False", "0", "nao", "N", "Nao"])

def categoria_suja(valor_base: str, variantes: dict) -> str:
    return random.choice(variantes[valor_base])

def gerar_clientes(n: int) -> pd.DataFrame:
    registros = []
    cpfs_usados = []
    for i in range(n):
        cpf = cpf_falso()
        if cpfs_usados and random.random() < 0.02:
            cpf = random.choice(cpfs_usados)
        cpfs_usados.append(cpf)

        nascimento = fake.date_of_birth(minimum_age=18, maximum_age=90)
        cidade, estado = random.choice(CIDADES)
        registros.append({
            "id": i + 1,
            "nome": fake.name(),
            "cpf": cpf,
            "email": None if random.random() < 0.08 else fake.email(),
            "telefone": telefone_sujo(),
            "data_nascimento": data_suja(nascimento),
            "cidade": cidade_suja(cidade),
            "estado": estado,
        })
    return pd.DataFrame(registros)

def gerar_apolices(n_apolices: int, clientes: pd.DataFrame, corretores: pd.DataFrame) -> pd.DataFrame:
    tipos = ["auto", "residencial", "saude"]
    registros = []
    for i in range(n_apolices):
        cliente_id = int(clientes.sample(1)["id"].iloc[0])
        if random.random() < 0.01:
            cliente_id = clientes["id"].max() + random.randint(1, 100)
        
        corretor_id = int(corretores.sample(1)["id"].iloc[0])
        if random.random() < 0.01:
            corretor_id = int(corretores["id"].max()) + random.randint(1, 100)

        inicio = fake.date_between(start_date="-3y", end_date="today")
        fim = inicio + timedelta(days=365)
        if random.random() < 0.01:
            fim = inicio - timedelta(days=30)

        premio = round(random.uniform(80, 1200), 2)
        if random.random() < 0.01:
            premio = round(random.uniform(50000, 99999), 2)

        registros.append({
            "id": i + 1,
            "numero_apolice": f"POL-{2021 + i % 4}-{i:05d}",
            "cliente_id": cliente_id,
            "corretor_id": corretor_id,
            "tipo": random.choice(tipos),
            "data_inicio": data_suja(inicio),
            "data_fim": data_suja(fim),
            "premio_mensal": premio,
        })
    return pd.DataFrame(registros)

def gerar_corretores(n: int) -> pd.DataFrame:
    registros = []
    emails_usados = []
    for i in range(n):
        email = fake.email()
        if emails_usados and random.random() < 0.01:
            email = random.choice(emails_usados)
        emails_usados.append(email)
        
        taxa = round(random.uniform(0.03, 0.15), 4)
        if random.random() < 0.01:
            taxa = round(random.uniform(-0.1, 0.9), 4)
        
        registros.append({
            "id": i + 1,
            "nome": fake.name(),
            "email": email,
            "regiao": random.choice(REGIOES),
            "taxa_comissao": taxa,
            "data_contratacao": data_suja(fake.date_between(start_date="-10y", end_date="-30d")),
            "ativo": bool_sujo(random.random() > 0.1),
        })
    return pd.DataFrame(registros)

def gerar_coberturas(apolices: pd.DataFrame) -> pd.DataFrame:
    registros = []
    id_seq = 1
    for _, apolice in apolices.iterrows():
        opcoes = COBERTURAS_POR_TIPO[apolice["tipo"]]
        n_coberturas = random.randint(1, len(opcoes))
        escolhidas = random.sample(opcoes, k=n_coberturas)

        apolice_id = int(apolice["id"])
        if random.random() < 0.01:
            apolice_id = int(apolices["id"].max()) + random.randint(1, 100)

        for tipo_cobertura in escolhidas:
            limite = None if random.random() < 0.02 else round(random.uniform(5_000, 200_000), 2)
            registros.append({
                "id": id_seq,
                "apolice_id": apolice_id,
                "tipo_cobertura": tipo_cobertura,
                "limite": limite,
                "ativo": bool_sujo(random.random() > 0.05),
            })
            id_seq += 1
    return pd.DataFrame(registros)

def gerar_sinistros(n: int, apolices: pd.DataFrame) -> pd.DataFrame:
    canais = list(CANAL_VARIANTES.keys())
    registros = []
    for i in range(n):
        apolice = apolices.sample(1).iloc[0]
        numero_apolice = apolice["numero_apolice"]
        if random.random() < 0.01:
            numero_apolice = f"POL-9999-{random.randint(0, 999):05d}"
        
        tipo = apolice["tipo"]
        if random.random() < 0.02:
            tipo = random.choice(["auto", "residencial", "saude"])
        
        status_base = random.choices(
            ["pendente", "em_analise", "aprovado", "rejeitado"],
            weights=[0.15, 0.15, 0.55, 0.15],
        )[0]

        valor_reclamado = round(random.uniform(500, 30_000), 2)
        valor_aprovado = None
        valor_resolucao = None

        if status_base == "aprovado":
            valor_aprovado = round(valor_reclamado * random.uniform(0.5, 1.0), 2)
            if random.random() < 0.01:
                valor_aprovado = round(valor_reclamado * random.uniform(1.1, 1.5), 2)
            dias_resolucao = random.randint(1, 90)
        elif status_base == "rejeitado":
            valor_aprovado = 0.0
            dias_resolucao = random.randint(1, 60)
        
        registros.append({
            "id": f"SIN-{i:06d}",
            "numero_apolice": numero_apolice,
            "nome_segurado": fake.name(),
            "tipo": tipo,
            "descricao": fake.sentence(nb_words=10),
            "data_sinistro": data_suja(fake.date_between(start_date="-2y", end_date="today")),
            "valor_reclamado": valor_reclamado,
            "valor_aprovado": valor_aprovado,
            "status": categoria_suja(status_base, STATUS_SINISTRO_VARIANTES),
            "dias_resolucao": dias_resolucao,
            "regiao": random.choice(REGIOES),
            "canal": categoria_suja(random.choice(canais), CANAL_VARIANTES),
            "_status_base": status_base,
        })
    return pd.DataFrame(registros)

def gerar_pagamentos(sinistros: pd.DataFrame) -> pd.DataFrame:
    aprovados = sinistros[sinistros["_status_base"] == "aprovado"]
    metodos = list(METODO_PAGAMENTO_VARIANTES.keys())
    registros = []
    id_seq = 1

    for _, sinistro in aprovados.iterrows():
        n_parcelas = random.choices([1, 2, 3], weights=[0.7, 0.2, 0.1])[0]
        valor_parcela = round(sinistro["valor_aprovado"] / n_parcelas, 2)
        data_base = fake.date_between(start_date="-2y", end_date="today")

        sinistro_id = sinistro["id"]
        if random.random() < 0.01:
            sinistro_id = "SIN-999999"
        
        for parcela in range(n_parcelas):
            data_pagamento = data_base + timedelta(days=15 * (parcela + 1))
            if random.random() < 0.01:
                data_pagamento = data_base - timedelta(days=30)

            registros.append({
                "id": id_seq,
                "sinistro_id": sinistro_id,
                "valor": valor_parcela,
                "data_pagamento": data_suja(data_pagamento),
                "metodo": categoria_suja(random.choice(metodos), METODO_PAGAMENTO_VARIANTES),
                "status": categoria_suja("concluido", STATUS_PAGAMENTO_VARIANTES),
                "observacao": None if random.random() < 0.7 else fake.sentence(nb_words=6),
            })
            id_seq += 1
    return pd.DataFrame(registros)

if __name__ == "__main__":
    print(f"Gerando {N_CLIENTES} clientes...")
    clientes = gerar_clientes(N_CLIENTES)
    clientes.to_parquet(RAW_DIR / "clientes.parquet", index=False)

    print(f"Gerando {N_CORRETORES} corretores...")
    corretores = gerar_corretores(N_CORRETORES)
    corretores.to_parquet(RAW_DIR / "corretores.parquet", index=False)

    print("Gerando apólices...")
    apolices = gerar_apolices(int(N_CLIENTES * 1.4), clientes, corretores)
    apolices.to_parquet(RAW_DIR / "apolices.parquet", index=False)

    print("Gerando coberturas...")
    coberturas = gerar_coberturas(apolices)
    coberturas.to_parquet(RAW_DIR / "coberturas.parquet", index=False)

    print("Gerando sinistros...")
    sinistros = gerar_sinistros(int(len(apolices)*0.4), apolices)
    sinistros_final = sinistros.drop(columns=["_status_base"])
    sinistros_final.to_parquet(RAW_DIR / "sinistros.parquet", index=False)

    print("Gerando pagamentos...")
    pagamentos = gerar_pagamentos(sinistros) # usa a versão COM _status_base
    pagamentos.to_parquet(RAW_DIR / "pagamentos.parquet", index=False)

    print("\nOK - arquivos em data/raw/\n")
    
    print("--- Verificação rápida ---")
    tabelas = {
        "clientes": clientes,
        "corretores": corretores,
        "apolices": apolices,
        "coberturas": coberturas,
        "sinistros": sinistros_final,
        "pagamentos": pagamentos,
    }

    for nome, df in tabelas.items():
        print(f"\n{nome}: {len(df)} linhas")
        print(df.isna().sum())

#TESTE
import pandas as pd
sinistros = pd.read_parquet("data/raw/sinistros.parquet")
print(sinistros["status"].unique())     # deve mostrar várias grafias de cada status
print(sinistros["valor_aprovado"].isna().sum())  # nulos = pendente/em_analise, esperado

corretores = pd.read_parquet("data/raw/corretores.parquet")
print(corretores["ativo"].apply(type).value_counts())  # deve mostrar bool, int e str misturados