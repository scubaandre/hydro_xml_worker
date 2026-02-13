import asyncio
import os
import logging
import requests
import json
from pyppeteer import connect

# --- VERSIONING ---
VERSION = "00.01.03"
OPTIONS_PATH = "/data/options.json"
DOWNLOAD_DIR = "/share/hydro_ottawa"

# --- LOGGER SETUP ---
logging.basicConfig(
    level=logging.INFO, 
    format=f'%(asctime)s - [v{VERSION}] - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def download_hydro_data():
    # Reload config inside the function for live updates
    if os.path.exists(OPTIONS_PATH):
        with open(OPTIONS_PATH, 'r') as f:
            conf = json.load(f)
        user_email = conf.get('user_email')
        user_pass = conf.get('user_pass')
        browser_url = conf.get('browser_url', 'ws://homeassistant:3000')
        login_timeout = conf.get('login_timeout', 30)
        debug_mode = conf.get('debug_mode', False)
    else:
        logger.error("Config file not found. Using defaults.")
        return

    logger.info(f"--- MILESTONE: Starting Scrape Process ---")
    
    try:
        logger.info(f"DEBUG: Connecting to Browserless at {browser_url}")
        browser = await connect(browserWSEndpoint=browser_url)
        page = await browser.newPage()
        await page.setViewport({'width': 1280, 'height': 800})

        cdp = await page.target.createCDPSession()
        await cdp.send('Page.setDownloadBehavior', {
            'behavior': 'allow',
            'downloadPath': DOWNLOAD_DIR
        })

        # 1. Login
        logger.info(f"DEBUG: Opening portal for {user_email}...")
        await page.goto("https://hydroottawa.savagedata.com/Connect/Authorize?returnUrl=https%3A%2F%2Fhydroottawa.savagedata.com%2F", 
                        {"waitUntil": "networkidle2"})
        
        logger.info("DEBUG: Waiting for #userName selector...")
        await page.waitForSelector('#userName', {'timeout': login_timeout * 1000})
        
        # 2. Login Injection
        logger.info("DEBUG: Injecting credentials...")
        await page.evaluate(f"""() => {{
            const e = document.querySelector('#userName');
            const p = document.querySelector('#exampleInputPassword');
            const btn = document.querySelector('a.btn-primary');
            if (e && p && btn) {{
                e.value = '{user_email}';
                p.value = '{user_pass}';
                ['input', 'change', 'blur'].forEach(v => e.dispatchEvent(new Event(v, {{bubbles:true}})));
                ['input', 'change', 'blur'].forEach(v => p.dispatchEvent(new Event(v, {{bubbles:true}})));
                btn.click();
            }}
        }}""")
        
        await asyncio.sleep(10) 

        # 3. Navigate to Download Page
        logger.info("DEBUG: Looking for DownloadMyData link...")
        nav_success = await page.evaluate("""() => {
            const link = document.querySelector('a[href="DownloadMyData"]');
            if (link) { link.click(); return true; }
            return false;
        }""")
        
        if not nav_success:
            raise Exception(f"Navigation failed. URL: {page.url}")

        await asyncio.sleep(8) 

        # 4. Wiretap setup
        download_status = {"success": False}
        async def intercept_request(request):
            if "api/Data/GetUsageData" in request.url:
                auth = request.headers.get('authorization')
                if auth:
                    logger.info("DEBUG: Intercepted API call. Fetching XML...")
                    try:
                        resp = requests.get(request.url, headers={'Authorization': auth})
                        if resp.status_code == 200:
                            path = os.path.join(DOWNLOAD_DIR, "hydro_data.xml")
                            with open(path, 'wb') as f:
                                f.write(resp.content)
                            download_status["success"] = True
                            logger.info(f"--- MILESTONE: SUCCESS: File saved to {path} ---")
                    except Exception as e:
                        logger.error(f"Interception failed: {e}")

        await page.setRequestInterception(True)
        page.on('request', lambda req: asyncio.ensure_future(intercept_request(req)) or asyncio.ensure_future(req.continue_()))

        # 5. Trigger Green Button Download
        logger.info("DEBUG: Clicking Usage/Billing and Green Button...")
        await page.evaluate("""async () => {
            const clickRadzenCheck = (inputId) => {
                const input = document.getElementById(inputId);
                if (input) {
                    const container = input.closest('.rz-chkbox');
                    const box = container ? container.querySelector('.rz-chkbox-box') : null;
                    if (box && !box.classList.contains('rz-state-active')) {
                        box.click();
                    }
                }
            };
            clickRadzenCheck('chkElectUsageData');
            clickRadzenCheck('chkBillingData');

            await new Promise(r => {
                const i = setInterval(() => {
                    if (!document.querySelector('.rz-progressbar')) { 
                        clearInterval(i); 
                        r(); 
                    }
                }, 500);
            });

            const btn = Array.from(document.querySelectorAll('button'))
                             .find(b => b.querySelector('img[src*="gb_logo.png"]'));
            if (btn) btn.click();
        }""")

        for i in range(25):
            if download_status["success"]: break
            if i % 5 == 0: logger.info(f"DEBUG: Waiting for download ({i}/25)...")
            await asyncio.sleep(1)

    except Exception as e:
        logger.error(f"--- MILESTONE: WORKER FAILED ---")
        logger.error(f"Error Detail: {e}")
        if debug_mode:
            await page.screenshot({'path': f'{DOWNLOAD_DIR}/error_latest.png'})
    finally:
        if 'browser' in locals():
            logger.info("DEBUG: Closing browser.")
            await browser.close()

async def main_loop():
    if not os.path.exists(DOWNLOAD_DIR):
        os.makedirs(DOWNLOAD_DIR)

    logger.info(f"Hydro Ottawa Continuous Service v{VERSION} Ready.")

    while True:
        try:
            # Refresh frequency from config
            if os.path.exists(OPTIONS_PATH):
                with open(OPTIONS_PATH, 'r') as f:
                    conf = json.load(f)
                scrapes_per_day = conf.get('scrapes_per_day', 4)
            else:
                scrapes_per_day = 4
            
            # Execute
            await download_hydro_data()
            
            # Sleep logic
            sleep_seconds = 86400 / scrapes_per_day
            logger.info(f"Zzz... Next scrape in {sleep_seconds/3600:.1f} hours.")
            await asyncio.sleep(sleep_seconds)

        except Exception as e:
            logger.error(f"CRITICAL: Main Loop Crash: {e}")
            # SAFETY SLEEP: Prevents 25% CPU busy-loop if something breaks
            logger.info("Sleeping for 10 minutes before retry...")
            await asyncio.sleep(600)

if __name__ == "__main__":
    asyncio.run(main_loop())