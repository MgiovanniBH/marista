import os
import asyncio
import pandas as pd
import re
from playwright.async_api import async_playwright, TimeoutError
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

async def bulk_clear_diary():
    xlsx_file = 'diary_schedule.xlsx'
    
    if not os.path.exists(xlsx_file):
        print(f"XLSX file {xlsx_file} not found.")
        return

    # Read XLSX using pandas
    df = pd.read_excel(xlsx_file)
    
    # Filter rows: February 2026. Clear regardless of content/status.
    def is_target(row):
        try:
            date_val = row['Data']
            if isinstance(date_val, datetime):
                dt = date_val
            else:
                dt = datetime.strptime(str(date_val), "%d/%m/%Y")
            
            # Check if February 2026
            if dt.month != 2 or dt.year != 2026:
                return False
            
            return True
        except Exception:
            return False

    indices_to_process = [i for i, row in df.iterrows() if is_target(row)]

    if not indices_to_process:
        print("No February 2026 entries found to clear.")
        return

    print(f"Starting bulk clear for {len(indices_to_process)} February entries.")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        site_url = os.getenv("SITE_URL", "https://academico.maristabrasil.org/DOnline/DOnline/avisos/TDOL303D.tp")
        username = os.getenv("USER_NAME")
        password = os.getenv("USER_PASSWORD")

        async def login_and_navigate():
            for attempt in range(3):
                print(f"Connecting to {site_url} (Attempt {attempt+1})...")
                try:
                    await page.goto(site_url, timeout=60000)
                    await asyncio.sleep(5)
                    
                    if await page.locator('button:has-text("COMPONENTE")').count() > 0:
                        print("Already logged in. Proceeding to navigation.")
                    else:
                        print("Login required. Filling credentials...")
                        try:
                            await page.wait_for_selector('#username', timeout=15000)
                            await page.fill('#username', username or "")
                            await page.fill('#password', password or "")
                            await page.click('#sendCredentials')
                        except Exception as el:
                            print(f"Login elements not found or already past login: {el}")

                    print("Waiting for main page elements...")
                    await page.wait_for_selector('button:has-text("COMPONENTE")', timeout=60000)
                    
                    print("Navigating to Diário Eletrônico...")
                    await page.click('button:has-text("COMPONENTE")')
                    await page.wait_for_selector('.x-menu-list-item:has-text("DIÁRIO ELETRÔNICO")', timeout=30000)
                    await page.click('.x-menu-list-item:has-text("DIÁRIO ELETRÔNICO")')
                    
                    await asyncio.sleep(2)
                    await page.wait_for_selector('text="CAMPOS DE EXPERIÊNCIA"', timeout=30000)
                    await page.click('text="CAMPOS DE EXPERIÊNCIA"')
                    
                    print("Waiting for grid load (this may take a while)...")
                    await page.wait_for_selector('.x-grid3-row', timeout=60000)
                    await asyncio.sleep(10)
                    return True
                except Exception as e:
                    print(f"Login/Navigation Error (Attempt {attempt+1}): {e}")
                    await page.screenshot(path=f"login_fail_clear_att_{attempt+1}.png")
                    await page.goto("about:blank")
                    await asyncio.sleep(5)
            return False

        if not await login_and_navigate():
            print("Initial login failed. Exiting.")
            await browser.close()
            return

        for idx in indices_to_process:
            row = df.iloc[idx]
            try:
                date_val = row['Data']
                if isinstance(date_val, datetime):
                    target_date = date_val.strftime("%d/%m/%Y")
                else:
                    target_date = str(date_val)
                    
                target_aula = str(int(row['Aula']))
                print(f"\n--- Clearing: {target_date} - Aula {target_aula} ---")

                await page.mouse.wheel(0, 500)
                await asyncio.sleep(1)

                group_selector = f'.x-grid-group-hd:has-text("{target_date}"), .x-grid3-group-hd:has-text("{target_date}")'
                group_locator = page.locator(group_selector).first
                
                if await group_locator.count() > 0:
                    await group_locator.scroll_into_view_if_needed()
                    is_collapsed = await group_locator.evaluate('el => el.classList.contains("x-grid-group-collapsed")')
                    if is_collapsed:
                        print(f"Expanding group {target_date}...")
                        await group_locator.click()
                        await asyncio.sleep(2)
                else:
                    print(f"Warning: Group header for {target_date} not found. Scanning all rows anyway.")
                
                found_row = None
                for scroll_attempt in range(5):
                    rows_locator = page.locator('.x-grid3-row')
                    count = await rows_locator.count()
                    
                    for i in range(count):
                        r_loc = rows_locator.nth(i)
                        try:
                            aula_cell = r_loc.locator('.x-grid3-td-gpfAulaAgenda')
                            if await aula_cell.count() > 0:
                                aula_val = (await aula_cell.inner_text()).strip()
                                header_text = await page.evaluate(f'''(idx) => {{
                                    let r = document.querySelectorAll('.x-grid3-row')[idx];
                                    if (!r) return "ROW_NOT_FOUND";
                                    let p = r.previousElementSibling;
                                    while (p && !p.classList.contains('x-grid-group-hd') && !p.classList.contains('x-grid3-group-hd')) p = p.previousElementSibling;
                                    if (p) return p.innerText;
                                    let parent = r.closest('.x-grid-group') || r.closest('.x-grid3-group');
                                    if (parent) {{
                                        let hd = parent.querySelector('.x-grid-group-hd') || parent.querySelector('.x-grid3-group-hd');
                                        if (hd) return hd.innerText;
                                    }}
                                    return "NO_HEADER_FOUND";
                                }}''', i)
                                
                                found_date = re.search(r'\d{2}/\d{2}/\d{4}', header_text)
                                date_str = found_date.group(0) if found_date else ""
                                
                                if aula_val == target_aula and date_str == target_date:
                                    found_row = r_loc
                                    break
                        except Exception: 
                            continue
                    
                    if found_row: break
                    print(f"Row for {target_date} Aula {target_aula} not found in this viewport, scrolling down...")
                    await page.mouse.wheel(0, 1000)
                    await asyncio.sleep(2)

                if not found_row:
                    print(f"Not found: {target_date} Aula {target_aula}")
                    df.at[idx, 'Status'] = 'Erro ao Limpar: Não encontrado'
                    continue

                await found_row.scroll_into_view_if_needed()
                await found_row.locator('text="Alterar"').click()
                await page.wait_for_selector('iframe', timeout=30000)
                iframe_element = await page.query_selector('iframe')
                iframe = await iframe_element.content_frame()
                await iframe.wait_for_load_state("networkidle")
                await asyncio.sleep(5)

                print(f"Clearing content...")
                js_result = await iframe.evaluate(
                    """(textToSave) => {
                        try {
                            var grid = null, recAula = null;
                            var items = [];
                            var all = Ext.ComponentMgr.all;
                            if (all.items && Array.isArray(all.items)) items = all.items;
                            else if (all.map) for (var k in all.map) items.push(all.map[k]);
                            
                            for (var c of items) {
                                if (!c || typeof c.getXType !== 'function') continue;
                                if (String(c.getXType()).indexOf('grid') === -1) continue;
                                var store = c.getStore ? c.getStore() : null;
                                if (!store || !store.getCount) continue;
                                for (var i = 0; i < store.getCount(); i++) {
                                    var rec = store.getAt(i);
                                    if (!rec || !rec.data) continue;
                                    for (var fld in rec.data) {
                                        if (String(rec.data[fld]).toUpperCase() === 'AULA') {
                                            grid = c; recAula = rec; break;
                                        }
                                    }
                                    if (recAula) break;
                                }
                                if (recAula) break;
                            }
                            if (!recAula || !grid) return 'ERRO: registro AULA não encontrado';
                            if (grid.stopEditing) grid.stopEditing(true);
                            recAula.set('comentarios', textToSave);
                            return 'OK';
                        } catch (e) { return 'ERRO JS: ' + e.toString(); }
                    }""",
                    "_"
                )
                print(f"   -> JS Result: {js_result}")
                
                if 'OK' in js_result:
                    salvar_btn = iframe.locator('.x-btn:has-text("Salvar"), button:has-text("Salvar")').first
                    await salvar_btn.click(force=True)
                    
                    try:
                        await page.wait_for_selector('iframe', state='hidden', timeout=30000)
                    except Exception as wait_e:
                        print(f"Warning: Iframe hide timeout, continuing anyway: {wait_e}")
                    print(f"DONE CLEARING: {target_date} Aula {target_aula}")
                    df.at[idx, 'Status'] = 'Limpo'
                else:
                    df.at[idx, 'Status'] = f"Erro ao Limpar: {js_result}"

            except Exception as e:
                print(f"Error at {row['Data']}: {e}")
                df.at[idx, 'Status'] = f'Erro ao Limpar: {str(e)[:50]}'
                await page.screenshot(path=f"err_clear_{target_date.replace('/', '-')}.png")
                await page.reload()
                await asyncio.sleep(5)
                await login_and_navigate()

            df.to_excel(xlsx_file, index=False)

        await browser.close()

if __name__ == "__main__":
    asyncio.run(bulk_clear_diary())
