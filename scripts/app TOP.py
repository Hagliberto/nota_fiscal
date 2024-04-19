import pandas as pd
import streamlit as st
import tempfile
from PyPDF2 import PdfReader

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

    return all_data, total_values

def main():
    st.title("Extrair dados de PDF e visualizar com Streamlit")

    uploaded_files = st.file_uploader("Carregar PDF(s)", type="pdf", accept_multiple_files=True)

    if uploaded_files:
        data, total_values = extract_data_from_pdf(uploaded_files)
        st.write("Dados extraídos dos PDFs:")

        # Expander para cada PDF
        for idx, df_data in enumerate(data):
            with st.expander(f"PDF {idx+1}"):
                df = pd.DataFrame(df_data, columns=["Item", "Descrição", "Qtde.", "Unid.", "Vl. unid.", "Vl. total"])
                st.dataframe(df, height=300)

        # Expander total com estatísticas
        with st.expander("Total com Estatísticas"):
            st.write(f"Total de PDFs carregados: {len(data)}")
            st.write(f"Valor Total dos Produtos em todos os PDFs: R${sum(total_values):.2f}")
            st.write(f"Número Total de Itens em todos os PDFs: {sum(len(df) for df in data)}")
            st.write(f"Média dos Valores Totais: R${sum(total_values)/len(total_values):.2f}")
            st.write(f"Valor Mínimo Total: R${min(total_values):.2f}")
            st.write(f"Valor Máximo Total: R${max(total_values):.2f}")

        excel_file = st.button("Salvar como Excel")
        if excel_file:
            file_name = "dados_extraidos.xlsx"
            writer = pd.ExcelWriter(file_name, engine='xlsxwriter')

            for idx, df_data in enumerate(data):
                total_value = total_values[idx]
                sheet_name = f"Sheet{idx+1}_Total_{total_value:.2f}"
                df = pd.DataFrame(df_data, columns=["Item", "Descrição", "Qtde.", "Unid.", "Vl. unid.", "Vl. total"])
                df.to_excel(writer, sheet_name=sheet_name, index=False)

            writer.save()  # Salvar o arquivo Excel
            st.success(f"Arquivo Excel '{file_name}' gerado com sucesso!")

if __name__ == "__main__":
    main()
