
import pandas as pd
import streamlit as st
import altair as alt

# Definir o título fixo para o painel
st.title("Acidentes-Recife (2015 a 2023)")

#Carregando os dados
df_final = pd.read_csv('acidentes_2015_2023_preprocessado.csv', sep=',', decimal='.', parse_dates=['data'])

# Preencher os valores ausentes na coluna 'natureza_acidente' com 'NÃO INFORMADO'
df_final['natureza_acidente'].fillna('NÃO INFORMADO', inplace=True)

# Preencher os valores ausentes na coluna 'tipo' com 'NÃO INFORMADO'
df_final['tipo'].fillna('NÃO INFORMADO', inplace=True)


# Adiciona uma caixa de seleção no sidebar
ano_selecionado = st.sidebar.selectbox(
    'Qual o ano deseja visualizar?',
    ('geral', '2015', '2016', '2017', '2018', '2019', '2020', '2021', '2022', '2023')
)

# Adiciona um checkbox
permite_horario_nao_informado = st.sidebar.checkbox('Considerar acidentes com horário não informado? ', value=True)

# Add a slider to the sidebar:
horario_acidente = st.sidebar.slider(
    'Horário do acidente:',
    0, 24, (0, 24)
)

lim_inferior, lim_superior = horario_acidente;

# Filtrar pelo ano selecionado
if ano_selecionado=='geral':
    df_filtrado = df_final
else:
    df_filtrado = df_final[df_final["Ano"]== int(ano_selecionado) ]

# Filtro Atores --------------------------------------------------------------------------------------------------------------------
# Definir listas de atores e suas legendas
atores = ['auto', 'moto', 'ciclom', 'ciclista', 'pedestre', 'onibus', 'caminhao', 'viatura']
atores_legenda = ['Automóvel', 'Motocicleta', 'Ciclomotor', 'Ciclista', 'Pedestre', 'Ônibus', 'Caminhão', 'Viatura']

# Criar a lista de seleção na Sidebar
atores_selecionados = st.sidebar.multiselect(
    'Selecione os envolvidos a serem filtrados:',
    atores_legenda
    )

# Filtrar os nomes das colunas com base nas legendas selecionadas
colunas_filtradas = [atores[atores_legenda.index(ator)] for ator in atores_selecionados]

# Filtrar se tiver itens selecionados. Não filtra se todos foram selecionados ou se nenhum foi selecionado
if ( len(atores_selecionados) != len(atores_legenda) ) and ( len(atores_selecionados) > 0 ):

    # Criar uma lista de condições para cada coluna selecionada
    condicoes = [(df_filtrado[col].notnull()) & (df_filtrado[col] > 0) for col in colunas_filtradas]

    # Combinar as condições usando operadores lógicos (AND)
    condicao_final = pd.concat(condicoes, axis=1).any(axis=1)

    # Filtrar o DataFrame df_final com base na condição final
    df_filtrado = df_filtrado[condicao_final]

#  --------------------------------------------------------------------------------------------------------------------

# Filtrar pelo hora inicial e final
df_filtrado = df_filtrado.fillna('')
df_hora_nao_informada = df_filtrado[df_filtrado['hora']=='']
df_filtrado = df_filtrado[df_filtrado['hora']!='']
df_filtrado = df_filtrado[ (df_filtrado['hora'].str[:2].astype(int) >= lim_inferior) & (df_filtrado['hora'].str[:2].astype(int) <= lim_superior) ]

if permite_horario_nao_informado :
    df_filtrado = pd.concat([df_filtrado, df_hora_nao_informada])

#Definição de abas
tab01, tab02, tab03, tab04, tab05, tab06 = st.tabs(["Natureza", "Tipo", "Envolvidos", "Tipo Acidentes", "Top 10 Bairros", "Mapa-Semáforos"])

with tab01:

    # Calcular a contagem de ocorrências para cada ano e natureza do acidente
    contagem_anos_natureza = df_filtrado.groupby(['Ano', 'natureza_acidente']).size().reset_index(name='Quantidade')

    #escala_cores = alt.Scale(domain=lista_acidentes['bairro'].unique(),
    #                      range=['#007bff', '#28a745', '#ffc107', '#dc3545', '#6c757d', '#d95b43', '#5bc0de', '#4caf50', '#ffeb3b', '#c497d9'])

    # Criar o gráfico de barras empilhadas com Altair
    grafico_barras_empilhadas = alt.Chart(contagem_anos_natureza).mark_bar().encode(
        x=alt.X('Ano:N', title='Ano'),
        y=alt.Y('sum(Quantidade):Q', title='Quantidade de Registros'),
        #color=alt.Color('natureza_acidente:N', title='Natureza do Acidente', scale=alt.Scale(scheme='yellowgreenblue') ),
        #                                                                                           ['#d7191c','#fdae61','#abd9e9','#2c7bb6']  
        #color=alt.Color('natureza_acidente:N', title='Natureza do Acidente', scale=alt.Scale(range=['#007bff', '#28a745', '#ffc107', '#dc3545']) ),
        color=alt.Color('natureza_acidente:N', title='Natureza do Acidente', scale=alt.Scale(range=['#d7191c','#fdae61','#abd9e9','#2c7bb6']) ),
        tooltip=['Ano', 'natureza_acidente', 'Quantidade']
    ).properties(
        width=800,
        height=600,
        title=f'Quantidade de Registros por Ano e Natureza do Acidente ({ano_selecionado})'
    ).configure_axis(
        labelFontSize=12,
        titleFontSize=14
    ).configure_title(
        fontSize=16
    )

    # Exibir o gráfico de barras empilhadas
    st.altair_chart(grafico_barras_empilhadas )

with tab02:

    # Calcular a contagem de ocorrências para cada variação da natureza do acidente
    contagem_natureza_acidente = df_filtrado['tipo'].value_counts().reset_index()
    contagem_natureza_acidente.columns = ['Tipo do Acidente', 'Quantidade']

    # Criar o gráfico de barras horizontais com Altair
    grafico = alt.Chart(contagem_natureza_acidente).mark_bar().encode(
        y=alt.Y('Tipo do Acidente:N', title='Tipo do Acidente', sort='-x', axis=alt.Axis(labelLimit=200)),
        x=alt.X('Quantidade:Q', title='Quantidade de Registros'),
        tooltip=['Tipo do Acidente', 'Quantidade']
    )

    # Adicionar os valores de quantidade nas barras
    texto = grafico.mark_text(
        align='left',
        baseline='middle',
        dx=3  # Deslocamento horizontal do texto
    ).encode(
        text='Quantidade:Q'  # Usar a coluna 'Quantidade' para o texto
    )

    # Combinar o gráfico de barras com os textos
    grafico_com_texto = grafico + texto

    # Configurações adicionais do gráfico
    grafico_final = grafico_com_texto.properties(
        width=800,
        height=600,
        title=f'Acidentes por Tipo ({ano_selecionado})'
    ).configure_axis(
        labelFontSize=12,
        titleFontSize=14
    ).configure_title(
        fontSize=16
    )

    st.altair_chart(grafico_final)

with tab03:

    #Não é afetado pelo filtro de horário

    # Carregar os dados
    def carregar_dados(ano):
        arquivo = f'correlacao_acidentes_{ano}.csv'
        return pd.read_csv(arquivo)

    df_envolvidos = carregar_dados(ano_selecionado)

    # Define os dados
    dados = df_envolvidos.set_index('tipo').T.reset_index().melt(id_vars='index', var_name='tipo', value_name='value')

    # Cria o gráfico de calor
    heatmap = alt.Chart(dados).mark_rect().encode(
        x=alt.X('index:O', title=None, axis=alt.Axis(orient='top')),  # Define a orientação do eixo x como 'top'
        y=alt.Y('tipo:O', title=None),
        color=alt.Color('value:Q', scale=alt.Scale(scheme='yellowgreenblue')),
    )

    # Adiciona o texto dentro de cada célula com o valor real e ajusta a cor do texto
    text = alt.Chart(dados).mark_text(baseline='middle', fontSize=10).encode(
        x='index:O',
        y='tipo:O',
        text=alt.Text('value:Q', format='.0f'),
        color=alt.condition(
            alt.datum['value'] > (dados['value'].max() - dados['value'].min()) / 2,
            alt.value('white'),
            alt.value('black')
        )
    )

    # Combina o gráfico de calor com o texto
    heatmap_with_text = (heatmap + text).properties(
        width=800,
        height=600,
        title=f'Mapa de Calor dos Envolvidos nos acidentes ({ano_selecionado})'
    )

    # Exibe o gráfico
    st.altair_chart(heatmap_with_text)

with tab04:

    # Calcular a contagem de ocorrências para cada ano e natureza do acidente
    contagem_anos_natureza = df_filtrado.groupby(['Ano', 'tipo']).size().reset_index(name='Quantidade')

    # Criar o gráfico de calor com Altair
    grafico_calor = alt.Chart(contagem_anos_natureza).mark_rect().encode(
        x=alt.X('Ano:N', title='Ano'),
        y=alt.Y('tipo:N', title='Tipo do Acidente', sort='-x'),
        color=alt.Color('Quantidade:Q', title='Quantidade de Registros', scale=alt.Scale(scheme='yellowgreenblue')),
        tooltip=['Ano', 'tipo', 'Quantidade']
    ).properties(
        width=800,
        height=600,
        title=f'Quantidade de Registros por Ano e tipo do Acidente ({ano_selecionado})'

    ).configure_axis(
        labelFontSize=12,
        titleFontSize=14
    ).configure_title(
        fontSize=16
    )

    # Exibir o gráfico de calor
    st.altair_chart(grafico_calor)

with tab05:


    #========================================================
    def lista_agrupamento_acidentes_ano(df_acidentes, qtd_registros):
      df_agrupado = df_acidentes.groupby(['bairro']).size().reset_index(name='qtd_acidentes')
      df_ordenado = df_agrupado.sort_values(by=['qtd_acidentes'], ascending=False)
      return df_ordenado[:qtd_registros]
    #========================================================

    # Ano Selecionado
    lista_acidentes = lista_agrupamento_acidentes_ano(df_filtrado, 10)

    # Criação da escala de cores
    escala_cores = alt.Scale(domain=lista_acidentes['bairro'].unique(),
                          range=['#007bff', '#28a745', '#ffc107', '#dc3545', '#6c757d', '#d95b43', '#5bc0de', '#4caf50', '#ffeb3b', '#c497d9'])

    # ====================================================
    titulo=f'Acidentes Agrupados por Bairros -Top 10 ({ano_selecionado})'

    graf_bairros = alt.Chart(lista_acidentes, title=titulo).mark_bar(color='green').encode(
        y=alt.Y('bairro:N', title='Bairro', sort='-x'),
        x=alt.X('qtd_acidentes:Q', title='Quantidade de Acidentes'),
        color=alt.Color('bairro:N', scale=escala_cores)
    ).properties(
        width=800, height=600
    )

    # ====================================================

    # Exibir o gráfico de calor
    st.altair_chart(graf_bairros)

with tab06:

    #Não é afetado pelo filtro de horário

    # Função para mapear os valores de acidentes para cores
    def definir_cor(acidentes):
        if acidentes == 0:
            return '#00FF00'  # Verde
        elif 1 <= acidentes <= 10:
            return '#FFFF00'  # Amarelo
        else:
            return '#FF0000'  # Vermelho


    if ano_selecionado=='geral':
       coluna_dados = 'acidentes_total'
    else:
       coluna_dados = f'acidentes_{ano_selecionado}'

    # Exibir o quadro com as legendas
    titulo = f'<b>Acidentes reportados em Semáforos ({ano_selecionado})</b><br>'
    st.markdown(titulo, unsafe_allow_html=True)

    # Conteúdo HTML das legendas
    legendas = ['<span style="display:inline-block;width:20px;height:20px;border-radius:50%;background:#00FF00;margin-right:5px;"></span> Nenhum acidente reportado',
                '<span style="display:inline-block;width:20px;height:20px;border-radius:50%;background:#FFFF00;margin-right:5px;"></span> Entre 1 e 10 acidentes',
                '<span style="display:inline-block;width:20px;height:20px;border-radius:50%;background:#FF0000;margin-right:5px;"></span> Mais de 10 acidentes']

    # Exibir o quadro com as legendas
    st.markdown('<br>'.join(legendas), unsafe_allow_html=True)

    df_semaforos = pd.read_csv('semaforos-geo-acidentes.csv', sep=';', decimal='.')

    # Aplicar a função para criar a nova coluna 'cor'
    df_semaforos['cor'] = df_semaforos[coluna_dados].apply(definir_cor)

    st.map(df_semaforos,
        latitude='latitude',
        longitude='longitude',
        size=coluna_dados,
        color='cor',
        use_container_width=False)

