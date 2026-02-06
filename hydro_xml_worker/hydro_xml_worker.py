import asyncio
import os
import logging
import requests
import json
from pyppeteer import connect

# --- VERSIONING ---
VERSION = "00.01.00"
OPTIONS_PATH = "/data/options.json"

# --- CONFIGURATION LOADING ---
if os.path.exists(OPTIONS_PATH):
    with open(OPTIONS_PATH, 'r') as f:
        conf = json.load(f)
    USER_EMAIL = conf.get('user_email')
    USER_PASS = conf.get('user_pass')
    BROWSER_URL = conf.get('browser_url', 'ws://homeassistant:3000')
    LOGIN_TIMEOUT = conf.get('login_timeout', 30)
    DEBUG_MODE = conf.get('debug_mode', False)
else:
    USER_EMAIL = os.getenv('USER_EMAIL', 'placeholder@example.com')
    USER_PASS = os.getenv('USER_PASS', 'placeholder')
    BROWSER_URL = os.getenv('BROWSER_URL', 'ws://localhost:3000')
    LOGIN_TIMEOUT = 30
    DEBUG_MODE = True

DOWNLOAD_DIR = "/share/hydro_ottawa"
if not os.path.exists(DOWNLOAD_DIR):
    os.makedirs(DOWNLOAD_DIR)

logging.basicConfig(
    level=logging.INFO, 
    format=f'%(asctime)s - [v{VERSION}] - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def download_hydro_data():
    logger.info(f"Connecting to Browserless at {BROWSER_URL} (Debug: {DEBUG_MODE})")
    try:
        browser = await connect(browserWSEndpoint=BROWSER_URL)
        page = await browser.newPage()
        await page.setViewport({'width': 1280, 'height': 800})

        cdp = await page.target.createCDPSession()
        await cdp.send('Page.setDownloadBehavior', {
            'behavior': 'allow',
            'downloadPath': DOWNLOAD_DIR
        })

        # 1. Login
        logger.info(f"Opening portal for {USER_EMAIL}...")
        await page.goto("https://hydroottawa.savagedata.com/Connect/Authorize?returnUrl=https%3A%2F%2Fhydroottawa.savagedata.com%2F", 
                        {"waitUntil": "networkidle2"})
        
        await page.waitForSelector('#userName', {'timeout': LOGIN_TIMEOUT * 1000})
        if DEBUG_MODE: await page.screenshot({'path': f'{DOWNLOAD_DIR}/debug_1_login.png'})
        
        # 2. Login Injection
        await page.evaluate(f"""() => {{
            const e = document.querySelector('#userName');
            const p = document.querySelector('#exampleInputPassword');
            const btn = document.querySelector('a.btn-primary');
            if (e && p && btn) {{
                e.value = '{USER_EMAIL}';
                p.value = '{USER_PASS}';
                ['input', 'change', 'blur'].forEach(v => e.dispatchEvent(new Event(v, {{bubbles:true}})));
                ['input', 'change', 'blur'].forEach(v => p.dispatchEvent(new Event(v, {{bubbles:true}})));
                btn.click();
            }}
        }}""")
        
        await asyncio.sleep(10) 
        if DEBUG_MODE: await page.screenshot({'path': f'{DOWNLOAD_DIR}/debug_2_dashboard.png'})

        # 3. Navigate to Download Page
        nav_success = await page.evaluate("""() => {
            const link = document.querySelector('a[href="DownloadMyData"]');
            if (link) { link.click(); return true; }
            return false;
        }""")
        
        if not nav_success:
            raise Exception(f"Failed to find navigation link. URL: {page.url}")

        await asyncio.sleep(8) 
        if DEBUG_MODE: await page.screenshot({'path': f'{DOWNLOAD_DIR}/debug_3_export_screen.png'})

        # 4. Wiretap setup
        download_status = {"success": False}
        async def intercept_request(request):
            if "api/Data/GetUsageData" in request.url:
                auth = request.headers.get('authorization')
                if auth:
                    logger.info("!! Usage Data Intercepted !!")
                    try:
                        resp = requests.get(request.url, headers={'Authorization': auth})
                        if resp.status_code == 200:
                            path = os.path.join(DOWNLOAD_DIR, "hydro_data.xml")
                            with open(path, 'wb') as f:
                                f.write(resp.content)
                            download_status["success"] = True
                            logger.info(f"SUCCESS: File saved to {path}")
                    except Exception as e:
                        logger.error(f"Interception failed: {e}")

        await page.setRequestInterception(True)
        page.on('request', lambda req: asyncio.ensure_future(intercept_request(req)) or asyncio.ensure_future(req.continue_()))

        # 5. Trigger
        logger.info("Triggering XML export...")
        await page.evaluate("""async () => {
            const cb = document.querySelector('.rz-chkbox-box');
            if (cb) cb.click();
            
            await new Promise(r => {
                const i = setInterval(() => {
                    if (!document.querySelector('.rz-progressbar')) { clearInterval(i); r(); }
                }, 500);
            });
            const btn = Array.from(document.querySelectorAll('button'))
                             .find(b => b.querySelector('img[src*="gb_logo.png"]'));
            if (btn) btn.click();
        }""")

        for _ in range(25):
            if download_status["success"]: break
            await asyncio.sleep(1)

    except Exception as e:
        logger.error(f"Worker failed: {e}")
        await page.screenshot({'path': f'{DOWNLOAD_DIR}/error_v{VERSION}.png'})
    finally:
        if 'browser' in locals():
            await browser.close()

if __name__ == "__main__":
    asyncio.run(download_hydro_data())