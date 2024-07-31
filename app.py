import streamlit as st
import requests
import pandas as pd
from datetime import date

st.image('logo.jpg')

email = st.text_input('Email')
valor_bem = st.number_input('Valor', min_value=0.0, format='%f')
entrada = st.number_input('Entrada', min_value=0.0, format='%f')

if st.button('Simular'):
    # Get URL and API Key
    url = st.secrets["api"]["url"]
    api_key = st.secrets["api"]["api_key"]

    # Define the headers including the API key
    headers = {
        "access_token": api_key,
        "Content-Type": "application/json"
    }
    
    # Call the API with all parameters
    data = {
        "data_inicial": date.today().strftime("%Y-%m-%d"),
        "valor_bem": valor_bem,
        "entrada": entrada,
        "vencimento_primeira_parcela": st.secrets["api"]["vencimento_primeira_parcela"],
        "vencimento_segunda_parcela": st.secrets["api"]["vencimento_segunda_parcela"],
        "taxa_seguro": st.secrets["api"]["taxa_seguro"],
        "custo_rastreador": st.secrets["api"]["custo_rastreador"],
        "capitalizacao_ano": st.secrets["api"]["capitalizacao_ano"],
        "numero_parcelas": st.secrets["api"]["numero_parcelas"],
        "taxa_desagio": st.secrets["api"]["taxa_desagio"],
        "data_desconto": st.secrets["api"]["data_desconto"]
    }
    
    response = requests.post(url, headers=headers, json=data)

    def format_currency(value):
        return 'R$ ' + f'{value:,.2f}'.replace(',', 'X').replace('.', ',').replace('X', '.')
    
    def format_number(value):
        return f'{value:,.2f}'.replace(',', 'X').replace('.', ',').replace('X', '.')

    if response.status_code == 200:
        df = pd.DataFrame(response.json())
        df = df.round(2)

        # Calcular a taxa de estruturação e adicionar ao DataFrame
        taxa_estruturacao = 0.04  # 4%
        valor_financiado = valor_bem - entrada
        valor_taxa_estruturacao = valor_financiado * taxa_estruturacao
        linha_taxa_estruturacao = {
            'pmt': '<strong>Taxa de Estruturação (4%)</strong>',
            'Peridiocidade': '',
            'Parcela': format_currency(valor_taxa_estruturacao)
        }

        # Adiciona a linha da taxa de estruturação ao final do DataFrame
        #linha_taxa_estruturacao_df = pd.DataFrame([linha_taxa_estruturacao])
        #df = pd.concat([df, linha_taxa_estruturacao_df], ignore_index=True)

        df = df[['pmt', 'Periodicidade', 'Parcela']]
        df.rename(columns={'pmt': 'Parcela', 'Periodicidade': 'Vencimento', 'Parcela': 'Valor da Parcela'}, inplace=True)
        df['Vencimento'] = pd.to_datetime(df['Vencimento'], errors='ignore').dt.strftime('%d/%m/%Y')
        df['Valor da Parcela'] = df['Valor da Parcela'].apply(lambda x: format_currency(x) if isinstance(x, (int, float)) else x)

        # Antes de converter o DataFrame para HTML:
        df = df.replace({pd.NaT: "", pd.NA: "", "nan": "", "NaN": ""})

        # Aplicando estilos CSS com o Styler
        styler = df.style.hide(axis="index").set_table_attributes('style="width:100%;"').set_properties(**{'text-align': 'center',}).set_table_styles([{
            'selector': 'th',
            'props': [('text-align', 'center')]
        }])

        # Renderiza o DataFrame como HTML
        html = styler.to_html(index=False)

        # Usa o markdown do Streamlit para exibir o HTML com o estilo
        st.markdown(html, unsafe_allow_html=True)

        st.markdown(
            """
            <small><br>Taxas de juros podem ser alteradas sem aviso prévio.<br></small>
            <small><br>Liberação dos recursos somente após:</small>
            <small><ul><li>Pagamento da Estruturação</li><li>Pagamento da Entrada (caso haja)</li></ul></small>
            """,
            unsafe_allow_html=True
        )

        # Adiciona a pergunta de aprovação e abre a URL em outra aba
        st.markdown(f'<a href="https://form.jotform.com/232605403546653" target="_blank">Clique aqui para aprovar a simulação</a>', unsafe_allow_html=True)

    
    else:
        st.error(f'Error: {response.status_code}')