import streamlit as st
import pandas as pd
import sqlite3
import matplotlib.pyplot as plt
import seaborn as sns
from faker import Faker
import random
import datetime

# Função para conectar ao banco de dados
def get_connection():
    return sqlite3.connect("erp_finance.db", detect_types=sqlite3.PARSE_DECLTYPES)

# Interface Streamlit
def main():
    st.title("ERP Financeiro com Streamlit")
    menu = ["Clientes", "Contas a Pagar", "Contas a Receber", "Lançamentos", "Relatórios"]
    choice = st.sidebar.selectbox("Selecione uma opção", menu)
    conn = get_connection()
    cursor = conn.cursor()

    if choice == "Clientes":
        st.subheader("Cadastro de Clientes")
        df = pd.read_sql_query("SELECT * FROM clientes", conn)
        st.dataframe(df)
    
    elif choice == "Contas a Pagar":
        st.subheader("Contas a Pagar")
        df = pd.read_sql_query("SELECT * FROM contas_pagar", conn)
        st.dataframe(df)
    
    elif choice == "Contas a Receber":
        st.subheader("Contas a Receber")
        df = pd.read_sql_query("SELECT * FROM contas_receber", conn)
        st.dataframe(df)
    
    elif choice == "Lançamentos":
        st.subheader("Lançamentos Financeiros")
        df = pd.read_sql_query("SELECT * FROM lancamentos", conn)
        st.dataframe(df)
    
    elif choice == "Relatórios":
        st.subheader("Relatórios Financeiros")
        
        # Fluxo de Caixa por Mês
        df = pd.read_sql_query("SELECT data, tipo, SUM(valor) as total FROM lancamentos GROUP BY data, tipo", conn)
        df['data'] = pd.to_datetime(df['data'])
        df = df.pivot(index='data', columns='tipo', values='total').fillna(0)
        st.subheader("Fluxo de Caixa por Mês")
        st.line_chart(df)
        
        # Distribuição das Contas a Pagar por Fornecedor
        df = pd.read_sql_query("SELECT fornecedor, SUM(valor) as total FROM contas_pagar GROUP BY fornecedor", conn)
        st.subheader("Distribuição das Contas a Pagar por Fornecedor")
        fig, ax = plt.subplots()
        ax.pie(df['total'], labels=df['fornecedor'], autopct='%1.1f%%', startangle=90)
        st.pyplot(fig)
        
        # Status das Contas a Pagar e Receber
        df_pagar = pd.read_sql_query("SELECT status, SUM(valor) as total FROM contas_pagar GROUP BY status", conn)
        df_receber = pd.read_sql_query("SELECT status, SUM(valor) as total FROM contas_receber GROUP BY status", conn)
        st.subheader("Status das Contas a Pagar e Receber")
        df_status = pd.concat([df_pagar, df_receber])
        st.bar_chart(df_status.set_index('status'))
        
        # Top 5 Clientes com Maior Receita
        df = pd.read_sql_query("SELECT c.nome, SUM(cr.valor) as total FROM contas_receber cr JOIN clientes c ON cr.cliente_id = c.id GROUP BY c.nome ORDER BY total DESC LIMIT 5", conn)
        st.subheader("Top 5 Clientes com Maior Receita")
        st.dataframe(df)
        st.bar_chart(df.set_index('nome'))
        
        # Comparação Receita vs Despesa
        df = pd.read_sql_query("SELECT tipo, SUM(valor) as total FROM lancamentos GROUP BY tipo", conn)
        st.subheader("Comparação Receita vs Despesa")
        st.bar_chart(df.set_index('tipo'))
        
        # Previsão de Fluxo de Caixa
        df_pagar = pd.read_sql_query("SELECT SUM(valor) as total FROM contas_pagar WHERE vencimento BETWEEN date('now') AND date('now', '+30 days')", conn)
        df_receber = pd.read_sql_query("SELECT SUM(valor) as total FROM contas_receber WHERE vencimento BETWEEN date('now') AND date('now', '+30 days')", conn)
        saldo_futuro = df_receber['total'].sum() - df_pagar['total'].sum()
        st.subheader("Previsão de Fluxo de Caixa")
        st.write(f"Saldo estimado para os próximos 30 dias: R$ {saldo_futuro:.2f}")
    
    conn.close()

if __name__ == "__main__":
    main()