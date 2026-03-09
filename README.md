# Guia de Automação: Portal Marista Brasil

Esta automação simplifica o processo de preenchimento do Diário Eletrônico (Conteúdo Programático) a partir de um planejamento em formato Word (.docx).

## Pré-requisitos
- Python 3.10+ instalado.
- Dependências instaladas: `pip install -r requirements.txt`
- Arquivo `.env` configurado em `scripts/.env` com as credenciais do portal.

---

## Fluxo de Trabalho (Passo a Passo)

### Passo 0: Baixar Agenda Atual
Se você ainda não tem a planilha `diary_schedule.xlsx` ou quer atualizar com os dados mais recentes do site:
```bash
python scripts/00_baixar_agenda_site.py
```

### Passo 1: Extrair Dados do Word
Coloque o seu arquivo de planejamento na pasta raiz e execute:
```bash
python scripts/01_extrair_planejamento_docx.py
```
Isso criará um arquivo `planning_data.json` com os dados brutos extraídos das tabelas do Word.

### Passo 2: Gerar Resumos com IA (Manual)
1. Abra o arquivo `planning_data.json`.
2. Copie o conteúdo e envie para o Gemini com o seguinte prompt:
   > "Organize e resuma este planejamento em objetivos de aula concisos (máximo 250 caracteres) para o portal escolar. Gere um arquivo JSON no formato de mapeamento (Data e Aula ID) chamado `ai_distribution_map.json`."
3. Salve a resposta do Gemini como `ai_distribution_map.json` na pasta raiz.

### Passo 3: Preencher Planilha Excel
Com o arquivo `ai_distribution_map.json` pronto, aplique os resumos na planilha:
```bash
python scripts/02_preencher_resumo_planilha.py
```

### Passo 4: Atualizar o Site
Envie os dados da planilha para o portal Marista:
```bash
python scripts/03_atualizar_site_marista.py
```
*Dica: O script filtrará automaticamente as datas pendentes e atualizará o status na planilha ao finalizar.*

---

## Atalhos Rápidos (Scripts)

| Comando | Descrição |
| :--- | :--- |
| `python scripts/00_baixar_agenda_site.py` | Baixa a agenda do portal para Excel |
| `python scripts/01_extrair_planejamento_docx.py` | Lê o arquivo Word |
| `python scripts/02_preencher_resumo_planilha.py` | Grava IA na planilha |
| `python scripts/03_atualizar_site_marista.py` | Grava planilha no Site |

---

## Solução de Problemas
- **Erro de Login**: Verifique as credenciais no arquivo `scripts/.env`.
- **Elemento não encontrado**: O site pode estar lento. Os scripts possuem mecanismos de retentativa automática.
- **Data não encontrada**: Certifique-se de que a data no Word coincide com a data na agenda do portal.
