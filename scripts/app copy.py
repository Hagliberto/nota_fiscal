import pandas as pd
import streamlit as st
import tempfile
from PyPDF2 import PdfReader
import plotly.express as px

st.set_page_config(layout="wide")

def extract_data_from_pdf(uploaded_files):
    # Inicializar variáveis para armazenar dados e valor total
    all_data = []
    total_values = []

    for uploaded_file in uploaded_files:
        # Salvar o arquivo temporariamente
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file.write(uploaded_file.read())
            temp_file.seek(0)

            # Usar PdfReader para ler o PDF
            pdf_reader = PdfReader(temp_file.name)

            # Inicializar variáveis para armazenar dados e valor total
            data = []
            total_value = 0

            # Iterar sobre todas as páginas do PDF
            for page in pdf_reader.pages:
                # Extrair texto da página atual
                text = page.extract_text()

                # Processar o texto extraído para obter os dados da tabela
                lines = text.split('\n')

                # Encontrar o índice de início das linhas de dados
                start_index = None
                for line_index, line in enumerate(lines):
                    if "Item Descrição Qtde. Unid. Vl. unid. Vl. total" in line:
                        start_index = line_index + 1
                        break

                # Iterar sobre as linhas de dados e preencher as colunas
                last_item = None  # Último item processado
                for line in lines[start_index:]:
                    if line.strip():
                        fields = line.split()
                        if len(fields) >= 6 and fields[0].isdigit():
                            item = fields[0]
                            if len(item) == 3 and item.isdigit():
                                if last_item is not None:
                                    # Verificar se o próximo item é sequencial ao último item processado
                                    next_item = int(item)
                                    if next_item != last_item + 1:
                                        # Se não for sequencial, não processar a linha
                                        continue
                            descricao = ' '.join(fields[1:-4])
                            qtde = fields[-4]
                            unidade = fields[-3]
                            vl_unidade = fields[-2]
                            vl_total = fields[-1]
                            try:
                                vl_total_float = float(vl_total.replace(',', '.'))  # Converta o valor total para float
                                total_value += vl_total_float  # Adicionar o valor total
                            except ValueError:
                                pass  # Ignorar valores não numéricos
                            data.append([item, descricao, qtde, unidade, vl_unidade, vl_total])
                            last_item = int(item)

            # Adicionar uma linha com o valor total
            data.append(['', '', '', '', '', f'Total: {total_value:.2f}'])
            all_data.append(data)
            total_values.append(total_value)

    # Combina todos os dados dos PDFs em um único DataFrame
    combined_data = [item for sublist in all_data for item in sublist]
    combined_df = pd.DataFrame(combined_data, columns=["Item", "Descrição", "Qtde.", "Unid.", "Vl. unid.", "Vl. total"])

    return all_data, total_values, combined_df

def main():
    st.title("Extrair dados de PDF e visualizar com Streamlit")

    uploaded_files = st.file_uploader("Carregar PDF(s)", type="pdf", accept_multiple_files=True)

    if uploaded_files:
        data, total_values, combined_df = extract_data_from_pdf(uploaded_files)
        st.write("Dados extraídos dos PDFs:")

        # Expander para cada PDF
        for idx, df_data in enumerate(data):
            with st.expander(f"PDF {idx+1}"):
                df = pd.DataFrame(df_data, columns=["Item", "Descrição", "Qtde.", "Unid.", "Vl. unid.", "Vl. total"])
                st.data_editor(df, use_container_width=True, num_rows="dynamic", key={idx+1})

        # Expander total com estatísticas e gráficos
        with st.expander("Total com Estatísticas e Gráficos"):
            st.write(f"Total de PDFs carregados: {len(data)}")
            st.write(f"Valor Total dos Produtos em todos os PDFs: R${sum(total_values):.2f}")
            st.write(f"Número Total de Itens em todos os PDFs: {len(combined_df) - len(data)}")
            st.write(f"Média dos Valores Totais: R${sum(total_values)/len(total_values):.2f}")
            st.write(f"Valor Mínimo Total: R${min(total_values):.2f}")
            st.write(f"Valor Máximo Total: R${max(total_values):.2f}")

            # Gráfico de Pizza com a Contribuição Percentual de cada PDF para o Valor Total
            total_sum = sum(total_values)
            contributions = [(val / total_sum) * 100 for val in total_values]
            df_contributions = pd.DataFrame({"PDF": [f"PDF {i+1}" for i in range(len(total_values))], "Contribuição (%)": contributions})
            fig2 = px.pie(df_contributions, values="Contribuição (%)", names="PDF", title="Contribuição Percentual de cada PDF para o Valor Total")
            st.plotly_chart(fig2, use_container_width=True)

        # Expander com todos os PDFs juntos
        with st.expander("Todos os PDFs Juntos"):
            st.data_editor(combined_df, use_container_width=True, num_rows="dynamic")

        excel_file = st.button("Salvar como Excel")
        if excel_file:
            file_name = "dados_extraidos.xlsx"
            writer = pd.ExcelWriter(file_name, engine='xlsxwriter')

            for idx, df_data in enumerate(data):
                total_value = total_values[idx]
                sheet_name = f"{idx+1}_NFC-e DANFE_R$ {total_value:.2f}"
                df = pd.DataFrame(df_data, columns=["Item", "Descrição", "Qtde.", "Unid.", "Vl. unid.", "Vl. total"])
                df.to_excel(writer, sheet_name=sheet_name, index=False)

            # Adicionar uma planilha com todos os dados combinados
            combined_df.to_excel(writer, sheet_name="Todos os PDFs", index=False)

            writer.save()  # Salvar e fechar o arquivo Excel
            st.success(f"Arquivo Excel '{file_name}' gerado com sucesso!")

if __name__ == "__main__":
    main()
