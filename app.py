import streamlit as st
import requests
import pandas as pd
from datetime import date

st.image('logo.jpg')

email = st.text_input('Email')
valor_bem = st.number_input('Valor', min_value=0.0, format='%f')

if st.button('Simular'):
    # Call the API with all parameters
    data = {
        "data_inicial": date.today().strftime("%Y-%m-%d"),
        "valor_bem": valor_bem,
        "entrada": st.secrets["api"]["entrada"],
        "vencimento_primeira_parcela": st.secrets["api"]["vencimento_primeira_parcela"],
        "vencimento_segunda_parcela": st.secrets["api"]["vencimento_segunda_parcela"],
        "taxa_seguro": st.secrets["api"]["taxa_seguro"],
        "custo_rastreador": st.secrets["api"]["custo_rastreador"],
        "capitalizacao_ano": st.secrets["api"]["capitalizacao_ano"],
        "numero_parcelas": st.secrets["api"]["numero_parcelas"],
        "taxa_desagio": st.secrets["api"]["taxa_desagio"],
        "data_desconto": st.secrets["api"]["data_desconto"]
    }
    
    response = requests.post('https://api-ksh6.onrender.com/simulador', json=data)

    def format_currency(value):
        return 'R$ ' + f'{value:,.2f}'.replace(',', 'X').replace('.', ',').replace('X', '.')
    
    def format_number(value):
        return f'{value:,.2f}'.replace(',', 'X').replace('.', ',').replace('X', '.')

    if response.status_code == 200:
        df = pd.DataFrame(response.json())
        df = df.round(2)

        df = df[['pmt', 'Periodicidade', 'Parcela']]
        df.rename(columns={'pmt': 'Parcela', 'Periodicidade': 'Vencimento', 'Parcela': 'Valor da Parcela'}, inplace=True)
        df['Vencimento'] = pd.to_datetime(df['Vencimento']).dt.strftime('%d/%m/%Y')
        df['Valor da Parcela'] = df['Valor da Parcela'].apply(format_currency)

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
            <small>Liberação dos recursos somente após:<br></small>
            <small>- Pagamento da Estruturação<br></small>
            <small>- Pagamento da Entrada, caso haja</small>
            """,
            unsafe_allow_html=True
        )

        # Adiciona a pergunta de aprovação e abre a URL em outra aba
        st.markdown(f'<a href="https://form.jotform.com/232605403546653" target="_blank">Clique aqui para aprovar a simulação</a>', unsafe_allow_html=True)

    
    else:
        st.error(f'Error: {response.status_code}')