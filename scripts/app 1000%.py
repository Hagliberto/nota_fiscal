import pandas as pd
import streamlit as st
import tempfile
from PyPDF2 import PdfReader

def extract_data_from_pdf(uploaded_files):
    # Inicializar variáveis para armazenar dados e valor total
    all_data = []
    total_value = 0

    for uploaded_file in uploaded_files:
        # Salvar o arquivo temporariamente
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file.write(uploaded_file.read())
            temp_file.seek(0)

            # Usar PdfReader para ler o PDF
            pdf_reader = PdfReader(temp_file.name)

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
                            all_data.append([item, descricao, qtde, unidade, vl_unidade, vl_total])
                            last_item = int(item)

    # Adicionar uma linha com o valor total
    all_data.append(['', '', '', '', '', f'Total: {total_value:.2f}'])

    return all_data

def main():
    st.title("Extrair dados de PDF e visualizar com Streamlit")

    uploaded_files = st.file_uploader("Carregar PDF(s)", type="pdf", accept_multiple_files=True)

    if uploaded_files:
        data = extract_data_from_pdf(uploaded_files)
        st.write("Dados extraídos dos PDFs:")
        st.write(data)

        excel_file = st.button("Salvar como Excel")
        if excel_file:
            df = pd.DataFrame(data, columns=["Item", "Descrição", "Qtde.", "Unid.", "Vl. unid.", "Vl. total"])
            file_name = "dados_extraidos.xlsx"
            df.to_excel(file_name, index=False)
            st.success(f"Arquivo Excel '{file_name}' gerado com sucesso!")

if __name__ == "__main__":
    main()
