import pandas as pd
import streamlit as st
import tempfile
from PyPDF2 import PdfReader
import plotly.express as px

st.set_page_config(layout="wide")

def extract_data_from_pdf(uploaded_file):
    # Inicializar variáveis para armazenar dados e valor total
    data = []
    total_value = 0

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
                        data.append([item, descricao, qtde, unidade, vl_unidade, vl_total])
                        last_item = int(item)

    # Adicionar uma linha com o valor total
    data.append(['', '', '', '', '', f'Total: {total_value:.2f}'])

    # Filtrar linhas com item vazio
    data_filtered = [row for row in data if row[0] != '']
            
    return data_filtered, total_value

def main():
    st.success("Extrair dados de PDF e visualizar na interface WEB, de NFC-e DANFE do site: https://notapotiguar.set.rn.gov.br/hotsite/#/login")
    
    col1, col2= st.columns(2)
    
    with col1:
        uploaded_files = st.file_uploader("Carregar PDF(s)", type="pdf", accept_multiple_files=True)

        if uploaded_files:
            all_data = []
            total_values = []

            # Expander para cada PDF
            for idx, uploaded_file in enumerate(uploaded_files):
                data, total_value = extract_data_from_pdf(uploaded_file)
                df = pd.DataFrame(data, columns=["Item", "Descrição", "Qtde.", "Unid.", "Vl. unid.", "Vl. total"])
                all_data.extend(data)
                total_values.append(total_value)

                with st.expander(f"`{idx+1}ª NFC-e DANFE R$ {total_value:.2f}`"):
                    st.data_editor(df[:-1], use_container_width=True, num_rows="fixed", hide_index=True)  # Exclui a última linha ("Total")
                    st.success(f"Total: {total_value:.2f}")
    
    # Expander com todos os PDFs juntos
    with col2:
        if uploaded_files:
            with st.expander(f"`Valor Total dos Produtos em todos os PDFs:`"):
                if total_values:
                    st.write(f"R$ {sum(total_values):.2f}")
                    df_all = pd.DataFrame(all_data, columns=["Item", "Descrição", "Qtde.", "Unid.", "Vl. unid.", "Vl. total"])
                    st.data_editor(df_all[:-1], use_container_width=True, num_rows="fixed", hide_index=True)  # Exclui a última linha ("Total")
                    st.info(f"Total: {sum(total_values):.2f}")
                    
                    
                else:
                    st.warning("Nenhum arquivo PDF carregado ainda.")
                    
    with col2:                    
        # Expander com estatísticas e gráficos
        with st.expander("📊 `Estatísticas e Gráficos`"):
            st.write(f"Total de PDFs carregados: {len(uploaded_files)}")
            st.write(f"Valor Total dos Produtos em todos os PDFs: R${sum(total_values):.2f}")
            st.write(f"Número Total de Itens em todos os PDFs: {sum(len(df) - 1 for df in all_data)}")
            st.write(f"Média dos Valores Totais: R${sum(total_values)/len(total_values):.2f}")
            st.write(f"Valor Mínimo Total: R${min(total_values):.2f}")
            st.write(f"Valor Máximo Total: R${max(total_values):.2f}")
            # Gráfico de barras com o valor total de cada PDF
            df_values = pd.DataFrame({"PDF": [f"PDF {i+1}" for i in range(len(total_values))], "Valor Total (R$)": total_values})
            fig1 = px.bar(df_values, x="PDF", y="Valor Total (R$)", title="Valor Total de cada PDF")
            st.plotly_chart(fig1, use_container_width=True)
            # Gráfico de pizza com a contribuição percentual de cada PDF para o valor total
            total_sum = sum(total_values)
            contributions = [(val / total_sum) * 100 for val in total_values]
            df_contributions = pd.DataFrame({"PDF": [f"PDF {i+1}" for i in range(len(total_values))], "Contribuição (%)": contributions})
            fig2 = px.pie(df_contributions, values="Contribuição (%)", names="PDF", title="Contribuição Percentual de cada PDF para o Valor Total")
            st.plotly_chart(fig2, use_container_width=True)
                        

if __name__ == "__main__":
    main()
