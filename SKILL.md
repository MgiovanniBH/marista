---
name: web-consultant
description: Automates website consultations that require authentication (user and password). Use when needing to extract data or perform queries on sites that are protected by a login wall.
---

# Web Consultant Skill

This skill provides a reusable framework for automating website consultations with authentication.

## Workflows (Comandos /)

Esta automação pode ser executada via comandos no chat:

- `/baixar-agenda`: Baixa a agenda atual do portal para Excel.
- `/extrair-word`: Extrai as tabelas do arquivo Word de planejamento.
- `/resumir-planejamento`: A IA resume o planejamento e gera o mapa de distribuição.
- `/preencher-planilha`: Grava os resumos da IA na planilha Excel.
- `/atualizar-portal`: Envia as informações da planilha para o portal Marista.

## Configuração de Credenciais
Configure o arquivo `scripts/.env` (não versionado):
```env
SITE_URL=https://academico.maristabrasil.org/DOnline/DOnline/avisos/TDOL303D.tp
USER_NAME=seu_usuario
USER_PASSWORD=sua_senha
```

## Recursos
- `scripts/`: Contém os scripts Python numerados (00 a 03).
- `.agent/workflows/`: Contém as definições dos comandos slash.
