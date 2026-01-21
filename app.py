import pandas as pd
import streamlit as st
from pathlib import Path

st.set_page_config(page_title="Assistente DW Vendas", layout="wide")

# =========================
# CONFIG
# =========================
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"

FILES = {
    "vendas_nf": "vw_vendas_nf.csv",
    "vendas_mensais": "vw_vendas_mensais.csv",
    "margem_30_mes": "vw_margem_30_mes.csv",
    "cliente_resumo": "vw_cliente_resumo.csv",
    "ativos_inativos": "vw_clientes_ativos_inativos.csv",
    "vendas_diarias": "vw_vendas_diarias.csv",
    "mix_cliente_tipo_vendedor": "vw_mix_cliente_tipo_por_vendedor.csv",
    "frequencia_cliente": "vw_frequencia_cliente.csv",
}


# =========================
# HELPERS
# =========================
@st.cache_data
def load_csv(path: Path) -> pd.DataFrame:
    for sep in [",", ";"]:
        try:
            df = pd.read_csv(path, sep=sep)
            if df.shape[1] > 1:
                return df
        except Exception:
            pass
    return pd.read_csv(path)


def ensure_file(key: str) -> Path:
    p = DATA_DIR / FILES[key]
    if not p.exists():
        st.error(f"Arquivo não encontrado: {p}")
        st.stop()
    return p


def detect_value_col(df: pd.DataFrame):
    if "valor_venda" in df.columns:
        return "valor_venda"
    if "valor" in df.columns:
        return "valor"
    return None


def safe_to_datetime(series: pd.Series) -> pd.Series:
    return pd.to_datetime(series, errors="coerce")


def fmt_money(x):
    try:
        return f"R$ {float(x):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except Exception:
        return str(x)


def load_nf():
    df = load_csv(ensure_file("vendas_nf"))
    val_col = detect_value_col(df)
    if val_col is None:
        st.error("Não encontrei a coluna de valor (esperado: valor_venda ou valor).")
        st.stop()
    return df, val_col


# =========================
# MENU
# =========================
MENU = {
    0:  "Ajuda / Menu",
    1:  "KPIs gerais (faturamento, quantidade de vendas, ticket médio)",
    2:  "Maior venda e menor venda (valor, NF e data)",
    3:  "Mês com maior faturamento (Top 12)",
    4:  "Mês com menor faturamento (Bottom 12)",
    5:  "Série mensal de faturamento (tabela + gráfico)",
    6:  "Série diária de faturamento (tabela + gráfico)",
    7:  "Forma de pagamento que mais fatura (Top 10)",
    8:  "Forma de pagamento com mais vendas (Top 10)",
    9:  "Top 5 vendedores por faturamento",
    10: "Top 5 vendedores por quantidade de vendas",
    11: "Clientes distintos por vendedor (Top 10)",
    12: "Mix PF/PJ por vendedor (participação %)",
    13: "Top 10 clientes por total comprado",
    14: "Top 10 clientes por quantidade de compras",
    15: "Clientes inativos (Top 20) + última compra",
    16: "Clientes ativos vs inativos (contagem)",
    17: "Clientes inativos com alto valor (Top 10) (reativação)",
    18: "Clientes com maior tempo médio entre compras (Top 15) (risco churn)",
}


# =========================
# LAYOUT
# =========================
st.title("Assistente DW de Vendas")
st.caption(f"Fonte: {DATA_DIR}")

with st.expander("Menu"):
    st.markdown("\n".join([f"**{k}** — {v}  " for k, v in MENU.items()]))

left, right = st.columns([1, 2])
with left:
    op = st.selectbox(
        "Escolha uma opção",
        options=list(MENU.keys()),
        format_func=lambda k: f"{k} — {MENU[k]}",
        index=0
    )
with right:
    pergunta = st.text_input(
        "Opcional: digite uma pergunta",
        placeholder="Ex.: top vendedores, forma pagamento, mês maior faturamento"
    )

# Mapeamento simples por texto
text = (pergunta or "").strip().lower()
if text:
    if "kpi" in text or "gerais" in text:
        op = 1
    elif "maior venda" in text or "menor venda" in text:
        op = 2
    elif ("mês" in text or "mes" in text) and ("maior" in text or "melhor" in text) and ("fatur" in text):
        op = 3
    elif ("mês" in text or "mes" in text) and ("menor" in text or "pior" in text) and ("fatur" in text):
        op = 4
    elif "mensal" in text:
        op = 5
    elif "diaria" in text or "diária" in text:
        op = 6
    elif "forma" in text and ("pag" in text or "pagamento" in text) and ("fatura" in text or "faturamento" in text):
        op = 7
    elif "forma" in text and ("pag" in text or "pagamento" in text) and ("quantidade" in text or "qtd" in text or "mais vendas" in text):
        op = 8
    elif "top" in text and "vendedor" in text and ("fatur" in text or "valor" in text):
        op = 9
    elif "top" in text and "vendedor" in text and ("qtd" in text or "quantidade" in text or "vendas" in text):
        op = 10
    elif "cliente" in text and "vendedor" in text:
        op = 11
    elif "mix" in text or ("pf" in text and "pj" in text):
        op = 12
    elif "top" in text and "cliente" in text and ("valor" in text or "comprado" in text or "total" in text):
        op = 13
    elif "mais compras" in text or ("top" in text and "compras" in text):
        op = 14
    elif "inativo" in text and ("lista" in text or "clientes" in text):
        op = 15
    elif "ativos" in text and "inativos" in text:
        op = 16
    elif "reativa" in text or ("alto valor" in text and "inativo" in text):
        op = 17
    elif "tempo" in text and ("entre compras" in text or "dias" in text):
        op = 18

st.divider()


# =========================
# OPTION 0
# =========================
if op == 0:
    st.subheader("Ajuda")
    st.markdown(
        """
Este app responde perguntas do BI usando arquivos CSV exportados das views.

Como usar:
- Selecione uma opção no menu
- Ou digite uma pergunta no campo de texto

Exemplos de perguntas:
- "top 5 vendedores"
- "forma de pagamento que mais fatura"
- "mês com maior faturamento"
- "clientes inativos"
"""
    )
    st.stop()


# =========================
# 1) KPIs gerais
# =========================
if op == 1:
    st.subheader("KPIs gerais")
    df_nf, valor_col = load_nf()

    faturamento = df_nf[valor_col].sum()
    qtd = len(df_nf)
    ticket = faturamento / qtd if qtd else 0

    c1, c2, c3 = st.columns(3)
    c1.metric("Faturamento total", fmt_money(faturamento))
    c2.metric("Quantidade de vendas", f"{qtd:,}".replace(",", "."))
    c3.metric("Ticket médio", fmt_money(ticket))

    st.caption("Base: vw_vendas_nf.csv")
    st.dataframe(df_nf.head(25), use_container_width=True)


# =========================
# 2) Maior/menor venda
# =========================
elif op == 2:
    st.subheader("Maior venda e menor venda")
    df_nf, valor_col = load_nf()

    nf_col = "numero_nf" if "numero_nf" in df_nf.columns else None
    data_col = "data_venda" if "data_venda" in df_nf.columns else None

    df_nf2 = df_nf.copy()
    if data_col:
        df_nf2[data_col] = safe_to_datetime(df_nf2[data_col])

    maior = df_nf2.sort_values(valor_col, ascending=False).head(1)
    menor = df_nf2.sort_values(valor_col, ascending=True).head(1)

    left, right = st.columns(2)
    with left:
        st.markdown("Maior venda")
        st.write({
            "valor": fmt_money(maior.iloc[0][valor_col]),
            "nota_fiscal": maior.iloc[0][nf_col] if nf_col else "(coluna numero_nf ausente)",
            "data": str(maior.iloc[0][data_col]) if data_col else "(coluna data_venda ausente)"
        })
    with right:
        st.markdown("Menor venda")
        st.write({
            "valor": fmt_money(menor.iloc[0][valor_col]),
            "nota_fiscal": menor.iloc[0][nf_col] if nf_col else "(coluna numero_nf ausente)",
            "data": str(menor.iloc[0][data_col]) if data_col else "(coluna data_venda ausente)"
        })

    st.dataframe(pd.concat([maior, menor], ignore_index=True), use_container_width=True)


# =========================
# 3) Mês maior faturamento
# =========================
elif op == 3:
    st.subheader("Mês com maior faturamento (Top 12)")
    df = load_csv(ensure_file("vendas_mensais"))
    required = {"ano", "mes", "mes_extenso", "faturamento", "ticket_medio"}
    if not required.issubset(set(df.columns)):
        st.error(f"Colunas esperadas não encontradas em vw_vendas_mensais.csv: {required}")
        st.stop()

    df2 = df.copy()
    df2["periodo"] = df2["ano"].astype(str) + "-" + df2["mes"].astype(str).str.zfill(2)
    top = df2.sort_values("faturamento", ascending=False).head(12)
    st.dataframe(top[["periodo", "mes_extenso", "faturamento", "ticket_medio"]], use_container_width=True)


# =========================
# 4) Mês menor faturamento
# =========================
elif op == 4:
    st.subheader("Mês com menor faturamento (Bottom 12)")
    df = load_csv(ensure_file("vendas_mensais"))
    required = {"ano", "mes", "mes_extenso", "faturamento", "ticket_medio"}
    if not required.issubset(set(df.columns)):
        st.error(f"Colunas esperadas não encontradas em vw_vendas_mensais.csv: {required}")
        st.stop()

    df2 = df.copy()
    df2["periodo"] = df2["ano"].astype(str) + "-" + df2["mes"].astype(str).str.zfill(2)
    bot = df2.sort_values("faturamento", ascending=True).head(12)
    st.dataframe(bot[["periodo", "mes_extenso", "faturamento", "ticket_medio"]], use_container_width=True)


# =========================
# 5) Série mensal
# =========================
elif op == 5:
    st.subheader("Série mensal de faturamento")
    df = load_csv(ensure_file("vendas_mensais"))
    required = {"ano", "mes", "mes_extenso", "faturamento", "ticket_medio"}
    if not required.issubset(set(df.columns)):
        st.error(f"Colunas esperadas não encontradas em vw_vendas_mensais.csv: {required}")
        st.stop()

    df2 = df.copy()
    df2["periodo"] = df2["ano"].astype(str) + "-" + df2["mes"].astype(str).str.zfill(2)
    df2 = df2.sort_values(["ano", "mes"])

    st.dataframe(df2[["periodo", "mes_extenso", "faturamento", "ticket_medio"]], use_container_width=True)
    st.line_chart(df2.set_index("periodo")["faturamento"])


# =========================
# 6) Série diária
# =========================
elif op == 6:
    st.subheader("Série diária de faturamento")
    df = load_csv(ensure_file("vendas_diarias"))
    required = {"data", "faturamento", "qtd_vendas", "ticket_medio"}
    if not required.issubset(set(df.columns)):
        st.error(f"Colunas esperadas não encontradas em vw_vendas_diarias.csv: {required}")
        st.stop()

    df2 = df.copy()
    df2["data"] = safe_to_datetime(df2["data"])
    df2 = df2.sort_values("data")

    st.dataframe(df2.head(60), use_container_width=True)
    st.line_chart(df2.set_index("data")["faturamento"])


# =========================
# 7) Forma de pagamento que mais fatura
# =========================
elif op == 7:
    st.subheader("Forma de pagamento que mais fatura (Top 10)")
    df_nf, valor_col = load_nf()

    col_fp = "forma_pagamento" if "forma_pagamento" in df_nf.columns else None
    if col_fp is None:
        st.error("Não encontrei a coluna de forma de pagamento (esperado: forma_pagamento).")
        st.stop()

    top = (df_nf.groupby(col_fp, as_index=False)
           .agg(faturamento=(valor_col, "sum"), qtd_vendas=(valor_col, "size"))
           .sort_values("faturamento", ascending=False)
           .head(10))
    st.dataframe(top, use_container_width=True)


# =========================
# 8) Forma de pagamento com mais vendas
# =========================
elif op == 8:
    st.subheader("Forma de pagamento com mais vendas (Top 10)")
    df_nf, valor_col = load_nf()

    col_fp = "forma_pagamento" if "forma_pagamento" in df_nf.columns else None
    if col_fp is None:
        st.error("Não encontrei a coluna de forma de pagamento (esperado: forma_pagamento).")
        st.stop()

    top = (df_nf.groupby(col_fp, as_index=False)
           .agg(qtd_vendas=(valor_col, "size"), faturamento=(valor_col, "sum"))
           .sort_values("qtd_vendas", ascending=False)
           .head(10))
    st.dataframe(top, use_container_width=True)


# =========================
# 9) Top 5 vendedores por faturamento
# =========================
elif op == 9:
    st.subheader("Top 5 vendedores por faturamento")
    df_nf, valor_col = load_nf()

    if "nome_vendedor" not in df_nf.columns:
        st.error("Coluna esperada não encontrada: nome_vendedor")
        st.stop()

    top = (df_nf.groupby("nome_vendedor", as_index=False)
           .agg(faturamento=(valor_col, "sum"), qtd_vendas=(valor_col, "size"))
           .sort_values("faturamento", ascending=False)
           .head(5))
    st.dataframe(top, use_container_width=True)


# =========================
# 10) Top 5 vendedores por quantidade de vendas
# =========================
elif op == 10:
    st.subheader("Top 5 vendedores por quantidade de vendas")
    df_nf, valor_col = load_nf()

    if "nome_vendedor" not in df_nf.columns:
        st.error("Coluna esperada não encontrada: nome_vendedor")
        st.stop()

    top = (df_nf.groupby("nome_vendedor", as_index=False)
           .agg(qtd_vendas=(valor_col, "size"), faturamento=(valor_col, "sum"))
           .sort_values("qtd_vendas", ascending=False)
           .head(5))
    st.dataframe(top, use_container_width=True)


# =========================
# 11) Clientes distintos por vendedor
# =========================
elif op == 11:
    st.subheader("Clientes distintos por vendedor (Top 10)")
    df_nf, valor_col = load_nf()

    required_cols = {"nome_vendedor", "id_cliente"}
    if not required_cols.issubset(set(df_nf.columns)):
        st.error(f"Colunas esperadas não encontradas: {required_cols}")
        st.stop()

    resumo = (df_nf.groupby("nome_vendedor", as_index=False)
              .agg(clientes_distintos=("id_cliente", "nunique"),
                   qtd_vendas=("id_cliente", "size"),
                   faturamento=(valor_col, "sum"))
              .sort_values("clientes_distintos", ascending=False)
              .head(10))
    st.dataframe(resumo, use_container_width=True)


# =========================
# 12) Mix PF/PJ por vendedor (view pronta)
# =========================
elif op == 12:
    st.subheader("Mix PF/PJ por vendedor (participação %)")
    df = load_csv(ensure_file("mix_cliente_tipo_vendedor"))
    required = {"nome_vendedor", "tipo_pessoa", "qtd_vendas", "faturamento", "participacao_pct"}
    if not required.issubset(set(df.columns)):
        st.error(f"Colunas esperadas não encontradas em vw_mix_cliente_tipo_por_vendedor.csv: {required}")
        st.stop()

    st.dataframe(df.head(50), use_container_width=True)


# =========================
# 13) Top clientes por valor
# =========================
elif op == 13:
    st.subheader("Top 10 clientes por total comprado")
    df = load_csv(ensure_file("cliente_resumo"))
    required = {"nome_cliente", "total_comprado", "qtd_compras", "ultima_compra"}
    if not required.issubset(set(df.columns)):
        st.error(f"Colunas esperadas não encontradas em vw_cliente_resumo.csv: {required}")
        st.stop()

    topc = df.sort_values("total_comprado", ascending=False).head(10).copy()
    st.dataframe(topc, use_container_width=True)


# =========================
# 14) Top clientes por qtd compras
# =========================
elif op == 14:
    st.subheader("Top 10 clientes por quantidade de compras")
    df = load_csv(ensure_file("cliente_resumo"))
    required = {"nome_cliente", "total_comprado", "qtd_compras", "ultima_compra"}
    if not required.issubset(set(df.columns)):
        st.error(f"Colunas esperadas não encontradas em vw_cliente_resumo.csv: {required}")
        st.stop()

    topc = df.sort_values("qtd_compras", ascending=False).head(10).copy()
    st.dataframe(topc, use_container_width=True)


# =========================
# 15) Clientes inativos
# =========================
elif op == 15:
    st.subheader("Clientes inativos (Top 20) + última compra")
    df = load_csv(ensure_file("ativos_inativos"))
    required = {"nome_cliente", "data_ultima_compra", "status_cliente"}
    if not required.issubset(set(df.columns)):
        st.error(f"Colunas esperadas não encontradas em vw_clientes_ativos_inativos.csv: {required}")
        st.stop()

    inativos = (df[df["status_cliente"].astype(str).str.lower() == "inativo"]
                .sort_values("data_ultima_compra", ascending=False)
                .head(20))
    st.dataframe(inativos, use_container_width=True)


# =========================
# 16) Contagem ativos vs inativos
# =========================
elif op == 16:
    st.subheader("Clientes ativos vs inativos (contagem)")
    df = load_csv(ensure_file("ativos_inativos"))
    if "status_cliente" not in df.columns:
        st.error("Coluna esperada não encontrada: status_cliente")
        st.stop()

    counts = (df["status_cliente"].astype(str).str.strip().str.title()
              .value_counts()
              .reset_index())
    counts.columns = ["status_cliente", "qtd_clientes"]

    st.dataframe(counts, use_container_width=True)
    st.bar_chart(counts.set_index("status_cliente")["qtd_clientes"])


# =========================
# 17) Alto valor e inativos (reativação)
# =========================
elif op == 17:
    st.subheader("Clientes inativos com alto valor (Top 10) (reativação)")
    df_res = load_csv(ensure_file("cliente_resumo"))
    df_ai = load_csv(ensure_file("ativos_inativos"))

    if not {"id_cliente", "nome_cliente", "total_comprado"}.issubset(df_res.columns):
        st.error("vw_cliente_resumo.csv precisa ter: id_cliente, nome_cliente, total_comprado")
        st.stop()
    if not {"id_cliente", "status_cliente"}.issubset(df_ai.columns):
        st.error("vw_clientes_ativos_inativos.csv precisa ter: id_cliente, status_cliente")
        st.stop()

    merged = df_res.merge(df_ai[["id_cliente", "status_cliente"]], on="id_cliente", how="left")
    inativos = merged[merged["status_cliente"].astype(str).str.lower() == "inativo"]
    top = inativos.sort_values("total_comprado", ascending=False).head(10)

    cols = [c for c in ["id_cliente", "nome_cliente", "total_comprado", "qtd_compras", "ultima_compra", "status_cliente"] if c in top.columns]
    st.dataframe(top[cols], use_container_width=True)


# =========================
# 18) Maior tempo médio entre compras
# =========================
elif op == 18:
    st.subheader("Clientes com maior tempo médio entre compras (Top 15) (risco churn)")
    df = load_csv(ensure_file("frequencia_cliente"))
    required = {"id_cliente", "nome_cliente", "qtd_compras", "faturamento_total", "dias_medios_entre_compras"}
    if not required.issubset(set(df.columns)):
        st.error(f"Colunas esperadas não encontradas em vw_frequencia_cliente.csv: {required}")
        st.stop()

    df2 = df.copy()
    df2["dias_medios_entre_compras"] = pd.to_numeric(df2["dias_medios_entre_compras"], errors="coerce")
    df2 = df2[df2["dias_medios_entre_compras"].notna()]

    top = df2.sort_values("dias_medios_entre_compras", ascending=False).head(15)
    st.dataframe(top, use_container_width=True)

else:
    st.info("Opção não implementada. Selecione outra no menu.")
