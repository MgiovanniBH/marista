# Project Specification: Web Consultation Skill (Marista Brasil)

## Environment & Infrastructure
- **Operating System**: Windows
- **Shell**: PowerShell (syntax must be compatible; use `;` or separate lines instead of `&&`).
- **Dependencies**: `playwright`, `python-dotenv`.
- **Output Format**: `.json`.
- **Execution**: Triggered via **slash command** `/marista-consult` (or natural language).

## Navigation & Action Flow
1. **Login**: Authenticate at target URL.
2. **Menu Navigation**:
   - `COMPONENTE` (Top level)
   - `DIARIO ELETRONICO` (Sub-menu)
   - `CAMPOS DE EXPERIENCIA` (Specific option)
3. **Data Entry**:
   - Locate specific date.
   - Click "Alterar" link.
   - Mark "Aula" item.
   - Fill "Conteúdo Programático" with provided info.
4. **Output**: Generate `.json` log of actions and results.

## Notifications & Logging
- Execution logs shown in terminal/chat.
- Results stored in local JSON artifacts.

## Technical Details
- **Target URL**: `https://academico.maristabrasil.org/DOnline/DOnline/avisos/TDOL303D.tp`
- **Authentication**: Form-based (Matrícula/CPF/E-mail and Password).
- **Selectors Reference**: [selectors.md](file:///c:/Repo/Teste%20Agente/references/selectors.md)
- **Core Script**: [consult.py](file:///c:/Repo/Teste%20Agente/scripts/consult.py)

## Deployment (Skill Pattern)
- The project is structured to be moved to the global `skills/` directory once verified.
- Must include `SKILL.md` for discovery and usage instructions.
