# Imports
import pandas as pd
import streamlit as st
import seaborn as sns
import matplotlib.pyplot as plt
from PIL import Image
from io import BytesIO

# Configuração inicial da página
st.set_page_config(
    page_title="Telemarketing Analysis",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilo do Seaborn
custom_params = {"axes.spines.right": False, "axes.spines.top": False}
sns.set_theme(style="ticks", rc=custom_params)


# Função para ler os dados
@st.cache_data
def load_data(file_data):
    try:
        return pd.read_csv(file_data, sep=";")
    except Exception as e:
        return pd.read_excel(file_data)


# Função para filtrar baseado na multiseleção de categorias
@st.cache_data
def multiselect_filter(relatorio, col, selecionados):
    if "all" in selecionados:
        return relatorio
    else:
        return relatorio[relatorio[col].isin(selecionados)].reset_index(drop=True)


# Função para converter o df para CSV
@st.cache_data
def convert_df(df):
    return df.to_csv(index=False).encode("utf-8")


# Função para converter o df para Excel
@st.cache_data
def to_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False, sheet_name="Sheet1")
    return output.getvalue()


# Função principal da aplicação
def main():
    st.title("Telemarketing Analysis")
    st.markdown("---")

    # Carregando imagem no sidebar
    image = Image.open("Bank-Branding.jpg")
    st.sidebar.image(image)

    st.sidebar.write("## Upload de Arquivo")
    data_file = st.sidebar.file_uploader("Selecione um arquivo (.csv ou .xlsx)", type=["csv", "xlsx"])

    if data_file:
        bank_raw = load_data(data_file)
        bank = bank_raw.copy()

        st.write("## Dados Brutos")
        st.write(bank_raw.head())

        with st.sidebar.form(key="filters_form"):
            graph_type = st.radio("Tipo de Gráfico", ["Barras", "Pizza"])

            # Filtros
            idades = st.slider("Idade", int(bank.age.min()), int(bank.age.max()), (int(bank.age.min()), int(bank.age.max())))
            jobs_selected = st.multiselect("Profissões", ["all"] + bank.job.unique().tolist(), ["all"])
            marital_selected = st.multiselect("Estado Civil", ["all"] + bank.marital.unique().tolist(), ["all"])
            default_selected = st.multiselect("Default", ["all"] + bank.default.unique().tolist(), ["all"])
            housing_selected = st.multiselect("Financiamento", ["all"] + bank.housing.unique().tolist(), ["all"])
            loan_selected = st.multiselect("Empréstimo", ["all"] + bank.loan.unique().tolist(), ["all"])
            contact_selected = st.multiselect("Contato", ["all"] + bank.contact.unique().tolist(), ["all"])
            month_selected = st.multiselect("Mês", ["all"] + bank.month.unique().tolist(), ["all"])
            day_of_week_selected = st.multiselect("Dia da Semana", ["all"] + bank.day_of_week.unique().tolist(), ["all"])

            # Aplicando Filtros
            bank = (
                bank.query("age >= @idades[0] and age <= @idades[1]")
                .pipe(multiselect_filter, "job", jobs_selected)
                .pipe(multiselect_filter, "marital", marital_selected)
                .pipe(multiselect_filter, "default", default_selected)
                .pipe(multiselect_filter, "housing", housing_selected)
                .pipe(multiselect_filter, "loan", loan_selected)
                .pipe(multiselect_filter, "contact", contact_selected)
                .pipe(multiselect_filter, "month", month_selected)
                .pipe(multiselect_filter, "day_of_week", day_of_week_selected)
            )

            submit_button = st.form_submit_button("Aplicar Filtros")

        if submit_button:
            st.write("## Dados Filtrados")
            st.write(bank.head())

            st.download_button(
                label="📥 Download Tabela Filtrada (Excel)",
                data=to_excel(bank),
                file_name="filtered_data.xlsx",
            )

        # Plots
        st.write("## Proporções")
        fig, ax = plt.subplots(1, 2, figsize=(10, 5))

        bank_raw_target_perc = bank_raw.y.value_counts(normalize=True) * 100
        bank_target_perc = bank.y.value_counts(normalize=True) * 100

        if graph_type == "Barras":
            sns.barplot(x=bank_raw_target_perc.index, y=bank_raw_target_perc.values, ax=ax[0])
            ax[0].set_title("Dados Brutos")
            sns.barplot(x=bank_target_perc.index, y=bank_target_perc.values, ax=ax[1])
            ax[1].set_title("Dados Filtrados")
        else:
            bank_raw_target_perc.plot(kind="pie", autopct="%.2f%%", ax=ax[0], title="Dados Brutos")
            bank_target_perc.plot(kind="pie", autopct="%.2f%%", ax=ax[1], title="Dados Filtrados")

        st.pyplot(fig)


if __name__ == "__main__":
    main()
