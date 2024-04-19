import pandas as pd
import streamlit as st
import tempfile
from PyPDF2 import PdfReader

def extract_data_from_pdf(uploaded_file):
    # Salvar o arquivo temporariamente
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        temp_file.write(uploaded_file.read())
        temp_file.seek(0)

        # Usar PdfReader para ler o PDF
        pdf_reader = PdfReader(temp_file.name)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()

    # Processar o texto extraído para obter os dados da tabela (você pode precisar ajustar esta parte)
    lines = text.split('\n')
    start_index = None
    data = []
    total_value = 0  # Inicializar o valor total
    for line in lines:
        if "Item Descrição Qtde. Unid. Vl. unid. Vl. total" in line:
            start_index = lines.index(line) + 1
            break
    
    for line in lines[start_index:]:
        if line.strip():
            fields = line.split()
            if len(fields) >= 6 and fields[0].isdigit():  # Verificar se há pelo menos 6 campos e se o primeiro é um dígito
                item = fields[0]
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

    # Adicionar uma linha com o valor total
    data.append(['', '', '', '', '', f'Total: {total_value:.2f}'])
            
    return data

def main():
    st.title("Extrair dados de PDF e visualizar com Streamlit")

    uploaded_file = st.file_uploader("Carregar PDF", type="pdf")

    if uploaded_file is not None:
        data = extract_data_from_pdf(uploaded_file)
        st.write("Dados extraídos do PDF:")
        st.write(data)

        excel_file = st.button("Salvar como Excel")
        if excel_file:
            df = pd.DataFrame(data, columns=["Item", "Descrição", "Qtde.", "Unid.", "Vl. unid.", "Vl. total"])
            file_name = "dados_extraidos.xlsx"
            df.to_excel(file_name, index=False)
            st.success(f"Arquivo Excel '{file_name}' gerado com sucesso!")

if __name__ == "__main__":
    main()
