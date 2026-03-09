import asyncio
import os
from openpyxl import Workbook
from playwright.async_api import async_playwright
from dotenv import load_dotenv

load_dotenv()

async def extract_diary():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        site_url = os.getenv("SITE_URL", "https://academico.maristabrasil.org/DOnline/DOnline/avisos/TDOL303D.tp")
        username = os.getenv("USER_NAME")
        password = os.getenv("USER_PASSWORD")

        print(f"Logging in to {site_url}...")
        await page.goto(site_url)

        # Login
        await page.fill('#username', username or "")
        await page.fill('#password', password or "")
        await page.click('#sendCredentials')
        await page.wait_for_load_state("networkidle")

        print("Navigating to Diário Eletrônico...")
        # 1. Click COMPONENTE Menu
        await page.click('button:has-text("COMPONENTE")')
        
        # 2. Click DIARIO ELETRONICO
        await page.wait_for_selector('.x-menu-list-item:has-text("DIÁRIO ELETRÔNICO")')
        await page.click('.x-menu-list-item:has-text("DIÁRIO ELETRÔNICO")')
        
        # 3. Get Discipline Name and Click CAMPOS DE EXPERIÊNCIA link
        print("Looking for Discipline and CAMPOS DE EXPERIÊNCIA link...")
        await asyncio.sleep(2) # Wait for table
        await page.screenshot(path="debug_class_list.png")
        with open("class_list.html", "w", encoding="utf-8") as f:
            f.write(await page.content())
            
        # The discipline name is in the same row as the link
        discipline_row = page.locator('tr:has-text("CAMPOS DE EXPERIÊNCIA")')
        discipline_name = "CAMPOS DE EXPERIÊNCIA" # Fallback
        if await discipline_row.count() > 0:
            cells = await discipline_row.locator('td').all_inner_texts()
            if len(cells) > 1:
                # Based on debug output: ['102015079', 'CAMPOS DE EXPERIÊNCIA', 'EI5DV', ...]
                # The name is likely in index 1
                discipline_name = cells[1].strip()
            print(f"Final Discipline Name: {discipline_name}")

        await page.wait_for_selector('text="CAMPOS DE EXPERIÊNCIA"', timeout=10000)
        await page.click('text="CAMPOS DE EXPERIÊNCIA"')
        
        print("Scraping grid data...")
        await page.wait_for_load_state("networkidle")
        # Buffer for ExtJS grid to render
        await asyncio.sleep(2)

        # The grid is grouped by date.
        # We'll find all rows in the grid.
        rows_selector = '.x-grid3-row'
        try:
            await page.wait_for_selector(rows_selector, timeout=10000)
        except Exception:
            print("Row selector not found. Checking page content...")
            await page.screenshot(path="debug_grid_error.png")
            return

        rows = await page.query_selector_all(rows_selector)
        diary_data = []

        print(f"Found {len(rows)} entries in the diary.")

        for row in rows:
            try:
                # Use a more flexible approach to find columns by checking common ExtJS classes or text patterns
                # Based on previous successful scripts, these columns often have these specific classes
                # If they fail, we use a fallback to get all cells and try to map them by index
                
                async def get_text(selector):
                    try:
                        el = await row.query_selector(selector)
                        if el:
                            return (await el.inner_text()).strip()
                        return ""
                    except Exception:
                        return ""

                date = await get_text('.x-grid3-col-gpfDataAgenda')
                aula = await get_text('.x-grid3-col-gpfAulaAgenda')
                inicio = await get_text('.x-grid3-col-gpfHorarioInicio')
                fim = await get_text('.x-grid3-col-gpfHorarioFim')
                conteudo = await get_text('.x-grid3-col-fldComentario')

                # Fallback: if data is still empty, let's try to grab all TD elements
                if not date:
                    cells = await row.query_selector_all('td')
                    cell_texts = [await c.inner_text() for c in cells]
                    # Attempt mapping by common index patterns if specific classes failed
                    if len(cell_texts) >= 5:
                        date = cell_texts[0].strip()
                        aula = cell_texts[1].strip()
                        inicio = cell_texts[2].strip()
                        fim = cell_texts[3].strip()
                        conteudo = cell_texts[4].strip()

                # We are interested in rows where content is needed (empty or placeholder)
                # Keep them all for now to let the user decide, or filter as requested
                diary_data.append({
                    'Disciplina': discipline_name.strip(),
                    'Data': date,
                    'Aula': aula,
                    'Início': inicio,
                    'Fim': fim,
                    'Conteúdo': conteudo,
                    'Status': 'Pendente' if not conteudo else 'Preenchido'
                })
            except Exception as e:
                print(f"Error processing row: {e}")

        # Save to XLSX
        output_file = 'diary_schedule.xlsx'
        if diary_data:
            wb = Workbook()
            ws = wb.active
            ws.title = "Diário"

            # Header
            headers = list(diary_data[0].keys())
            ws.append(headers)

            # Rows
            for entry in diary_data:
                ws.append(list(entry.values()))

            wb.save(output_file)
            print(f"Successfully exported {len(diary_data)} entries to {output_file}")
        else:
            print("No diary entries found to export.")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(extract_diary())
