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
N_CORRETORES = 500  # bem menos que clientes: poucos corretores atendem muitos clientes

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

def gerar_apolices(n_apolices: int, clientes: pd.DataFrame) -> pd.DataFrame:
    tipos = ["auto", "residencial", "saude"]
    registros = []
    for i in range(n_apolices):
        cliente_id = int(clientes.sample(1)["id"].iloc[0])
        if random.random() < 0.01:
            cliente_id = clientes["id"].max() + random.randint(1, 100)

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
            "tipo": random.choice(tipos),
            "data_inicio": data_suja(inicio),
            "data_fim": data_suja(fim),
            "premio_mensal": premio,
        })
    return pd.DataFrame(registros)

if __name__ == "__main__":
    print(f"Gerando {N_CLIENTES} clientes...")
    clientes = gerar_clientes(N_CLIENTES)
    clientes.to_parquet(RAW_DIR / "clientes.parquet", index=False)

    print("Gerando apólices...")
    apolices = gerar_apolices(int(N_CLIENTES * 1.4), clientes)
    apolices.to_parquet(RAW_DIR / "apolices.parquet", index=False)

    print("OK - arquivos em data/raw/")
    print(clientes.head())

#Teste
import pandas as pd
df = pd.read_parquet("data/raw/clientes.parquet")
print(df.isna().sum())
import pandas as pd
print(df["cpf"].duplicated().sum())
print(df["cidade"].unique()[:20])
