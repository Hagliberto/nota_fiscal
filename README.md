# Extrator e Visualizador de Dados de PDF de NFC-e DANFE

Este aplicativo permite extrair dados de Notas Fiscais Eletrônicas (NFC-e) no formato DANFE (Documento Auxiliar da Nota Fiscal Eletrônica) e visualizá-los em uma interface web interativa. Ele foi desenvolvido para facilitar a análise e o acompanhamento de informações contidas em múltiplos arquivos PDF.

## Funcionalidades

1. **Leitura de PDFs:** Carregue um ou mais arquivos PDF contendo Notas Fiscais Eletrônicas (NFC-e) no formato DANFE.

2. **Visualização Individual de PDFs:** Cada PDF carregado é apresentado em um expander separado, exibindo os dados da nota fiscal, incluindo item, descrição, quantidade, unidade, valor unitário e valor total.

3. **Visualização de Todos os PDFs Juntos:** Os dados de todos os PDFs carregados são combinados e exibidos em um único expander, permitindo uma visão consolidada de todas as notas fiscais.

4. **Estatísticas:** Um expander dedicado exibe estatísticas agregadas sobre os dados extraídos, incluindo o número total de PDFs carregados, o valor total dos produtos em todos os PDFs, o número total de itens, a média dos valores totais, o valor mínimo e o valor máximo.

5. **Exportação para Excel:** Os dados consolidados podem ser exportados para um arquivo Excel (.xlsx) clicando no botão "Salvar planilha".

## Como Usar

1. Certifique-se de ter o Python e as bibliotecas necessárias instaladas. Você pode instalá-las executando `pip install -r requirements.txt`.

2. Execute o script `app.py`.

3. No navegador, acesse o URL fornecido pelo Streamlit.

4. Carregue os arquivos PDF contendo as NFC-e DANFE clicando no botão "Carregar PDF(s)".

5. Explore os dados de cada PDF individualmente ou em conjunto usando os expanders fornecidos.

6. Exporte os dados consolidados para um arquivo Excel clicando no botão "Salvar planilha".

## Requisitos

- Python 3
- Bibliotecas listadas em `requirements.txt`

## Licença

Este projeto está licenciado sob a Licença MIT - veja o arquivo [LICENSE](LICENSE) para mais detalhes.
