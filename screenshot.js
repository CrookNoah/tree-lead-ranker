const puppeteer = require("puppeteer");

(async () => {
  try {
    const browser = await puppeteer.launch({ 
      args: ["--no-sandbox", "--disable-setuid-sandbox"],
      headless: "new" 
    });
    const page = await browser.newPage();
    await page.setViewport({ width: 1280, height: 720 });
    await page.goto("http://localhost:3000/dashboard_v2.html", { 
      waitUntil: "networkidle2",
      timeout: 15000 
    });
    await page.screenshot({ path: "/tmp/dashboard.png", fullPage: false });
    console.log("✅ Screenshot saved to /tmp/dashboard.png");
    await browser.close();
  } catch (error) {
    console.error("Error:", error.message);
  }
})();
