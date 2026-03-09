# Selectors for Web Consultation

## Login Page (Marista)
- **Username Field**: `#username` (Matrícula/CPF/E-mail)
- **Password Field**: `#password`
- **Submit Button**: `#sendCredentials`
- **Error Message**: `#helpmsg`

## Internal Navigation (ExtJS based)
- **Menu COMPONENTE**: `button:has-text("COMPONENTE")`
- **Menu DIARIO ELETRONICO**: `text="DIÁRIO ELETRÔNICO"` (Needs verification after clicking COMPONENTE)
- **Menu CAMPOS DE EXPERIENCIA**: `text="CAMPOS DE EXPERIÊNCIA"`
- **Link Alterar**: `text="Alterar"`
- **Item Aula**: `label:has-text("Aula")` or specific checkbox
- **Conteúdo Programático**: `textarea` or `input` associated with the field
